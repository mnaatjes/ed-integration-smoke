"""Telemetry and journal event processing pipeline using ed-models and SQLite."""

from __future__ import annotations

import json
import logging
import traceback
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
    ) -> None:
        self.storage = storage
        self.facade = facade or ed_models.create_domain_facade()

    def process_envelope(self, payload: dict[str, Any]) -> ProcessingResult:
        """Process an arbitrary incoming telemetry or journal event payload."""
        # Check if telemetry status snapshot (Flags or Pips present)
        if "Flags" in payload or "Pips" in payload:
            return self._process_telemetry_status(payload)

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
        self.storage.record_raw_event(event_name, payload)

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

            self.storage.record_target_hit(event_name)
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
        self.storage.record_raw_event("StatusTelemetry", payload)

        raw_flags = payload.get("Flags", 0)
        raw_flags2 = payload.get("Flags2", 0)
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
