"""Telemetry and journal event processing pipeline using ed-models and SQLite."""

from __future__ import annotations

import json
import logging
import traceback
from collections import defaultdict
from typing import Any

import ed_models
from ed_models.adapters.driving.facade import EliteDomainFacade
from ed_models.core.domain.status.flags import StatusFlags, StatusFlags2

from ed_integration_smoke.daemon.models import DomainMismatchRecord, ProcessingResult
from ed_integration_smoke.daemon.storage import TelemetryStorageEngine
from ed_integration_smoke.daemon.tracker import STATUS_FLAGS2_TARGETS, STATUS_FLAGS_TARGETS

logger = logging.getLogger(__name__)


class TelemetryPipeline:
    """Ingests raw dictionaries, validates with ed-models, updates coverage, and logs mismatches."""

    def __init__(
        self,
        storage: TelemetryStorageEngine,
        facade: EliteDomainFacade | None = None,
        max_exemplars_per_event: int = 25,
    ) -> None:
        self.storage = storage
        self.facade = facade or ed_models.create_domain_facade()
        self.max_exemplars_per_event = max_exemplars_per_event
        self._last_status_signature: tuple[int, int, int, str] | None = None
        self._event_sample_counts: dict[str, int] = defaultdict(int)
        self._event_seen_keysets: dict[str, set[frozenset[str]]] = defaultdict(set)
        self._last_seen_event_timestamps: dict[str, str] = {}

    def process_envelope(self, payload: dict[str, Any]) -> ProcessingResult:
        """Process an arbitrary incoming telemetry or journal event payload."""
        # Check if telemetry status snapshot (Flags or Pips present)
        if "Flags" in payload or "Pips" in payload:
            return self._process_telemetry_status(payload)

        # Check if internal service audit event (e.g. action="selected", "part_rollover")
        if "action" in payload and "event" not in payload:
            action_name = str(payload.get("action", "audit"))
            self.storage.record_raw_event(f"Audit_{action_name}", payload)
            target_path = str(payload.get("target_path", ""))
            detail = payload.get("detail", "")
            msg = f"{action_name} -> {target_path} {detail}".strip()
            return ProcessingResult(
                success=True,
                target_id=f"audit.{action_name}",
                chapter="audit",
                error_message=msg,
                is_mismatch=False,
                is_audit=True,
            )

        # Standard Frontier Journal Event
        event_name = payload.get("event")
        if not event_name or not isinstance(event_name, str):
            err_msg = "Payload missing string 'event' discriminator and 'Flags' key"
            mismatch = DomainMismatchRecord(
                target_id="UNKNOWN_PAYLOAD",
                error_class="MalformedPayloadError",
                error_message=err_msg,
                traceback="",
                raw_payload=json.dumps(payload, default=str),
            )
            self.storage.record_mismatch(mismatch)
            return ProcessingResult(
                success=False,
                target_id="UNKNOWN_PAYLOAD",
                chapter="unknown",
                error_message=err_msg,
                is_mismatch=True,
            )

        return self._process_journal_event(event_name, payload)

    def _process_journal_event(self, event_name: str, payload: dict[str, Any]) -> ProcessingResult:
        """Hydrate journal event via ed-models facade."""
        # Exemplar reservoir gating: record raw if under quota or presents new property keys
        payload_keys = frozenset(payload.keys())
        current_count = self._event_sample_counts[event_name]
        is_novel_keyset = payload_keys not in self._event_seen_keysets[event_name]

        if current_count < self.max_exemplars_per_event or is_novel_keyset:
            self.storage.record_raw_event(event_name, payload)
            self._event_sample_counts[event_name] = current_count + 1
            self._event_seen_keysets[event_name].add(payload_keys)

        # Continually track player flight state independently of raw exemplar quotas
        if event_name in ("ShipyardSwap", "ShipyardBuy", "ShipyardNew"):
            ship = (
                payload.get("ShipType_Localised")
                or payload.get("ShipType")
                or payload.get("Ship")
            )
            if ship:
                self.storage.set_session_state("active_ship_type", str(ship))
        elif event_name == "Loadout":
            ship = payload.get("Ship")
            ship_name = payload.get("ShipName", "")
            if ship:
                self.storage.set_session_state("active_ship_type", str(ship))
            if ship_name:
                self.storage.set_session_state("active_ship_name", str(ship_name))
        elif event_name in ("Location", "FSDJump", "Docked", "SupercruiseEntry"):
            sys_name = payload.get("StarSystem")
            st_name = payload.get("StationName")
            body_name = payload.get("Body")
            if sys_name:
                self.storage.set_session_state("active_system", str(sys_name))
            if st_name is not None:
                self.storage.set_session_state("active_station", str(st_name))
            if body_name is not None:
                self.storage.set_session_state("active_body", str(body_name))
        elif event_name == "CarrierStats":
            c_name = payload.get("Name")
            c_call = payload.get("Callsign")
            if c_name:
                self.storage.set_session_state("carrier_name", str(c_name))
            if c_call:
                self.storage.set_session_state("carrier_callsign", str(c_call))

        try:
            hydrated = self.facade.parse_journal_event(payload)
            # Flag fallback to generic base JournalEvent as uncataloged mismatch
            if type(hydrated) is ed_models.JournalEvent and event_name.lower() != "journalevent":
                err_msg = (
                    f"Event '{event_name}' is not in ed-models domain event registry "
                    "(deserialized to generic base JournalEvent)"
                )
                mismatch = DomainMismatchRecord(
                    target_id=event_name,
                    error_class="UncatalogedDomainEventError",
                    error_message=err_msg,
                    traceback="",
                    raw_payload=json.dumps(payload, default=str),
                )
                self.storage.record_mismatch(mismatch)
                return ProcessingResult(
                    success=False,
                    target_id=event_name,
                    chapter="events",
                    hydrated_object=hydrated,
                    error_message=err_msg,
                    is_mismatch=True,
                )

            # De-duplicate target hits if identical historical event is re-read
            event_ts = str(payload.get("timestamp", ""))
            if not event_ts or self._last_seen_event_timestamps.get(event_name) != event_ts:
                self.storage.record_target_hit(event_name)
                if event_ts:
                    self._last_seen_event_timestamps[event_name] = event_ts

            logger.debug("Successfully hydrated journal event: %s", event_name)
            return ProcessingResult(
                success=True,
                target_id=event_name,
                chapter="events",
                hydrated_object=hydrated,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            err_cls = exc.__class__.__name__
            err_msg = str(exc)
            logger.warning("Domain mismatch on event '%s': %s", event_name, err_msg)

            mismatch = DomainMismatchRecord(
                target_id=event_name,
                error_class=err_cls,
                error_message=err_msg,
                traceback=tb,
                raw_payload=json.dumps(payload, default=str),
            )
            self.storage.record_mismatch(mismatch)
            return ProcessingResult(
                success=False,
                target_id=event_name,
                chapter="events",
                error_message=f"{err_cls}: {err_msg}",
                is_mismatch=True,
            )

    def _process_telemetry_status(self, payload: dict[str, Any]) -> ProcessingResult:
        """Parse status.json telemetry snapshot and unpack active bitfield flags."""
        raw_flags = int(payload.get("Flags", 0))
        raw_flags2 = int(payload.get("Flags2", 0))
        raw_focus = int(payload.get("GuiFocus", 0))
        legal_state = str(payload.get("LegalState", "Clean"))

        current_sig = (raw_flags, raw_flags2, raw_focus, legal_state)
        if current_sig != self._last_status_signature:
            self.storage.record_raw_event("StatusTelemetry", payload)
            self._last_status_signature = current_sig

        pips_raw = payload.get("Pips", [4, 4, 4])
        pips_tuple = (
            (int(pips_raw[0]), int(pips_raw[1]), int(pips_raw[2]))
            if isinstance(pips_raw, (list, tuple)) and len(pips_raw) >= 3
            else (4, 4, 4)
        )
        fuel_dict = payload.get("Fuel", {}) if isinstance(payload.get("Fuel"), dict) else {}
        fuel_main = float(fuel_dict.get("FuelMain", 0.0))
        fuel_res = float(fuel_dict.get("FuelReservoir", 0.0))
        cargo = int(payload.get("Cargo", 0))
        legal_state = str(payload.get("LegalState", "Clean"))

        try:
            telemetry = self.facade.parse_telemetry(
                flags=int(raw_flags),
                flags2=int(raw_flags2),
                pips=pips_tuple,
                fuel_main=fuel_main,
                fuel_reservoir=fuel_res,
                cargo=cargo,
                legal_state=legal_state,
            )
            # Record individual status flag hits
            if isinstance(raw_flags, int):
                for flag_target in STATUS_FLAGS_TARGETS:
                    flag_val = getattr(StatusFlags, flag_target.target_id, None)
                    if flag_val is not None and (raw_flags & flag_val.value):
                        self.storage.record_target_hit(flag_target.target_id)

            if isinstance(raw_flags2, int):
                for flag_target in STATUS_FLAGS2_TARGETS:
                    flag_val = getattr(StatusFlags2, flag_target.target_id, None)
                    if flag_val is not None and (raw_flags2 & flag_val.value):
                        self.storage.record_target_hit(flag_target.target_id)

            self.storage.record_target_hit("Status")
            return ProcessingResult(
                success=True,
                target_id="StatusTelemetry",
                chapter="status",
                hydrated_object=telemetry,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            err_cls = exc.__class__.__name__
            err_msg = str(exc)
            logger.warning("Domain mismatch on telemetry status: %s", err_msg)

            mismatch = DomainMismatchRecord(
                target_id="StatusTelemetry",
                error_class=err_cls,
                error_message=err_msg,
                traceback=tb,
                raw_payload=json.dumps(payload, default=str),
            )
            self.storage.record_mismatch(mismatch)
            return ProcessingResult(
                success=False,
                target_id="StatusTelemetry",
                chapter="status",
                error_message=f"{err_cls}: {err_msg}",
                is_mismatch=True,
            )
