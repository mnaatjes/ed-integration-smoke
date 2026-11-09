#!/usr/bin/env python3
"""Batch telemetry hydration audit script against ed-telemetry events query endpoint.

Paginates events, hydrates records into ed-models domain objects, displays a
live single-line progress indicator, and logs unmapped/failed events to disk.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ed_hydrator.hydrator import TelemetryDomainHydrator
from ed_models import JournalEvent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit ed-models hydration against remote ed-telemetry records."
    )
    parser.add_argument(
        "--endpoint",
        default="http://192.168.1.214:8080",
        help="Base URL of ed-telemetry service (default: http://192.168.1.214:8080)",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=5000,
        help="Maximum records to process (default: 5000, 0 for unlimited)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Records per API query page (default: 500)",
    )
    parser.add_argument(
        "--topic",
        default="telemetry.journal",
        help="Filter by topic (default: telemetry.journal, empty string for all)",
    )
    parser.add_argument(
        "--log-dir",
        default="logs",
        help="Directory to store audit log files (default: logs)",
    )
    return parser.parse_args()


def fetch_page(
    base_url: str,
    topic: str | None,
    since_id: int | None,
    limit: int,
) -> list[dict[str, Any]]:
    params: dict[str, str | int] = {
        "limit": limit,
        "order": "asc",
    }
    if topic:
        params["topic"] = topic
    if since_id is not None:
        params["since_id"] = since_id

    query_str = urllib.parse.urlencode(params)
    url = f"{base_url.rstrip('/')}/api/v1/events/query?{query_str}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ed-integration-smoke-audit/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
        res = json.loads(data.decode("utf-8"))
        if not isinstance(res, list):
            return []
        return [r for r in res if isinstance(r, dict)]


def main() -> int:
    args = parse_args()
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    error_log_path = log_dir / f"hydration_errors_{timestamp_str}.jsonl"
    mappings_log_path = log_dir / f"hydrated_mappings_{timestamp_str}.jsonl"

    print(f"Connecting to ed-telemetry at {args.endpoint}...")
    print(f"Target: topic={args.topic or 'ALL'}, max_records={args.max_records or 'ALL'}")
    print(f"Mappings will be logged to: {mappings_log_path}")
    print(f"Errors and unmapped events will be logged to: {error_log_path}")

    total_processed = 0
    total_hydrated = 0
    total_unmapped = 0
    total_errors = 0
    total_with_dropped_fields = 0
    since_id: int | None = None
    start_time = time.monotonic()
    unmapped_counter: Counter[str] = Counter()
    error_counter: Counter[str] = Counter()
    dropped_fields_counter: Counter[str] = Counter()
    hydrator = TelemetryDomainHydrator()

    with (
        open(error_log_path, "w", encoding="utf-8") as error_file,
        open(mappings_log_path, "w", encoding="utf-8") as mappings_file,
    ):
        try:
            while True:
                remaining = (
                    args.max_records - total_processed
                    if args.max_records > 0
                    else args.batch_size
                )
                if remaining <= 0:
                    break

                batch_limit = min(args.batch_size, remaining)
                try:
                    records = fetch_page(
                        base_url=args.endpoint,
                        topic=args.topic if args.topic else None,
                        since_id=since_id,
                        limit=batch_limit,
                    )
                except Exception as ex:
                    print(f"\n[ERROR] HTTP request failed: {ex}", file=sys.stderr)
                    break

                if not records:
                    break

                for rec in records:
                    total_processed += 1
                    rec_id = rec.get("id")
                    since_id = rec_id
                    raw_payload = rec.get("payload_json")
                    event_id = rec.get("event_id")
                    topic = rec.get("topic")

                    payload: dict[str, Any]
                    try:
                        if isinstance(raw_payload, str):
                            payload = json.loads(raw_payload)
                        elif isinstance(raw_payload, dict):
                            payload = raw_payload
                        else:
                            raise ValueError(f"Unexpected payload type: {type(raw_payload)}")
                    except Exception as err:
                        total_errors += 1
                        error_counter["JSONDecodeError"] += 1
                        log_entry = {
                            "timestamp": datetime.now(UTC).isoformat(),
                            "id": rec_id,
                            "event_id": event_id,
                            "topic": topic,
                            "error_type": "JSONDecodeError",
                            "error_message": str(err),
                            "raw_payload": str(raw_payload)[:500],
                        }
                        error_file.write(json.dumps(log_entry) + "\n")
                        error_file.flush()
                        continue

                    event_name = payload.get("event")
                    if not event_name:
                        # Non-journal payload or missing event name
                        total_errors += 1
                        error_counter["MissingEventField"] += 1
                        log_entry = {
                            "timestamp": datetime.now(UTC).isoformat(),
                            "id": rec_id,
                            "event_id": event_id,
                            "topic": topic,
                            "error_type": "MissingEventField",
                            "error_message": "Missing 'event' key in payload",
                            "raw_payload": payload,
                        }
                        error_file.write(json.dumps(log_entry) + "\n")
                        error_file.flush()
                        continue

                    try:
                        hydrated_obj = hydrator.hydrate_event(payload)
                        if hydrated_obj is None:
                            total_errors += 1
                            error_counter["HydrationReturnedNone"] += 1
                            log_entry = {
                                "timestamp": datetime.now(UTC).isoformat(),
                                "id": rec_id,
                                "event_id": event_id,
                                "topic": topic,
                                "event_name": event_name,
                                "error_type": "HydrationReturnedNone",
                                "error_message": f"Hydrator returned None for event '{event_name}'",
                                "raw_payload": payload,
                            }
                            error_file.write(json.dumps(log_entry) + "\n")
                            error_file.flush()
                            continue

                        domain_class_name = hydrated_obj.__class__.__name__
                        is_fallback = type(hydrated_obj) is JournalEvent

                        model_fields = (
                            {f.name for f in fields(hydrated_obj)}
                            if is_dataclass(hydrated_obj)
                            else set(getattr(hydrated_obj, "__annotations__", {}).keys())
                        )
                        dropped_fields = sorted(list(set(payload.keys()) - model_fields))
                        if dropped_fields:
                            total_with_dropped_fields += 1
                            for df in dropped_fields:
                                dropped_fields_counter[f"{event_name}.{df}"] += 1

                        mapping_entry = {
                            "id": rec_id,
                            "event_id": event_id,
                            "raw_hash": rec.get("raw_hash"),
                            "event_name": event_name,
                            "domain_class": domain_class_name,
                            "is_fallback": is_fallback,
                            "dropped_fields": dropped_fields,
                        }
                        mappings_file.write(json.dumps(mapping_entry) + "\n")

                        # Check if hydrated into generic fallback JournalEvent
                        if is_fallback:
                            total_unmapped += 1
                            unmapped_counter[event_name] += 1
                            log_entry = {
                                "timestamp": datetime.now(UTC).isoformat(),
                                "id": rec_id,
                                "event_id": event_id,
                                "topic": topic,
                                "event_name": event_name,
                                "error_type": "UnmappedEventDomain",
                                "error_message": (
                                    f"Event '{event_name}' hydrated into generic "
                                    "JournalEvent fallback"
                                ),
                                "raw_payload": payload,
                            }
                            error_file.write(json.dumps(log_entry) + "\n")
                            error_file.flush()
                        else:
                            total_hydrated += 1
                    except Exception as err:
                        total_errors += 1
                        error_counter[type(err).__name__] += 1
                        log_entry = {
                            "timestamp": datetime.now(UTC).isoformat(),
                            "id": rec_id,
                            "event_id": event_id,
                            "topic": topic,
                            "event_name": event_name,
                            "error_type": type(err).__name__,
                            "error_message": str(err),
                            "raw_payload": payload,
                        }
                        error_file.write(json.dumps(log_entry) + "\n")
                        error_file.flush()

                elapsed = max(time.monotonic() - start_time, 0.001)
                rate = total_processed / elapsed
                progress_line = (
                    f"\r[Audit] Processed: {total_processed} | "
                    f"Hydrated: {total_hydrated} | "
                    f"Unmapped: {total_unmapped} | "
                    f"Errors: {total_errors} | "
                    f"Last ID: {since_id} ({rate:.1f} rec/s)"
                )
                sys.stdout.write(progress_line)
                sys.stdout.flush()

        except KeyboardInterrupt:
            print("\nAudit interrupted by operator.")

    elapsed = max(time.monotonic() - start_time, 0.001)
    rate = total_processed / elapsed
    pct_hydrated = total_hydrated / max(total_processed, 1) * 100
    pct_unmapped = total_unmapped / max(total_processed, 1) * 100
    pct_errors = total_errors / max(total_processed, 1) * 100
    pct_dropped = total_with_dropped_fields / max(total_processed, 1) * 100
    print("\n" + "=" * 60)
    print("Hydration Audit Summary:")
    print(f"  Total Processed: {total_processed}")
    print(f"  Fully Hydrated:  {total_hydrated} ({pct_hydrated:.1f}%)")
    print(f"  Unmapped Events: {total_unmapped} ({pct_unmapped:.1f}%)")
    print(f"  Hydration Errors:{total_errors} ({pct_errors:.1f}%)")
    print(f"  Field Truncated: {total_with_dropped_fields} ({pct_dropped:.1f}%)")
    print(f"  Duration:        {elapsed:.2f}s ({rate:.1f} rec/s)")
    print(f"  Mappings Log:    {mappings_log_path}")
    print(f"  Error Log:       {error_log_path}")

    if dropped_fields_counter:
        print("\nTop Dropped Fields (Payload keys absent in ed-models):")
        for fld, cnt in dropped_fields_counter.most_common(10):
            print(f"  - {fld}: {cnt}")

    if unmapped_counter:
        print("\nTop Unmapped Events (Generic JournalEvent Fallback):")
        for ev, cnt in unmapped_counter.most_common(10):
            print(f"  - {ev}: {cnt}")

    if error_counter:
        print("\nTop Hydration Error Types:")
        for err_type, cnt in error_counter.most_common(10):
            print(f"  - {err_type}: {cnt}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
