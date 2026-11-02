#!/usr/bin/env python3
"""CLI runner for the live Elite Dangerous telemetry ingestion and audit harness."""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path

from ed_integration_smoke.daemon import (
    TelemetryIngressClient,
    TelemetryPipeline,
    TelemetryStorageEngine,
    build_all_targets,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("telemetry_harness")


def print_summary(storage: TelemetryStorageEngine) -> None:
    """Print formatted summary of current target coverage."""
    summary = storage.get_coverage_summary()
    print("\n" + "=" * 65)
    print("  ELITE DANGEROUS FLEET TELEMETRY AUDIT SUMMARY")
    print("=" * 65)
    print(f"  Total Targets Registered:  {summary['total_targets']}")
    print(f"  Achieved in Gameplay:      {summary['achieved_targets']}")
    print(f"  Coverage Completion:       {summary['percentage']:.2f}%")
    print(f"  Total Processed Hits:      {summary['total_hits']:,}")
    print("-" * 65)
    print("  Chapter Breakdown:")
    for ch, stats in sorted(summary["by_chapter"].items()):
        bar_len = int(stats["percentage"] / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        pct = stats["percentage"]
        ach = stats["achieved"]
        tot = stats["total"]
        print(f"    {ch:<12} [{bar}] {ach:>3}/{tot:<3} ({pct:>6.2f}%)")
    print("=" * 65 + "\n")


async def run_harness(
    host: str,
    port: int,
    db_path: Path,
    poll_interval: float,
) -> None:
    """Run async ingestion loop polling ed-telemetry and checking off targets."""
    base_url = f"http://{host}:{port}"
    storage = TelemetryStorageEngine(db_path)
    storage.seed_targets(build_all_targets())
    pipeline = TelemetryPipeline(storage=storage)
    client = TelemetryIngressClient(base_url=base_url)

    logger.info("Connecting to ed-telemetry at %s", base_url)
    logger.info("Using SQLite ledger at %s (WAL mode)", db_path)

    print_summary(storage)

    stop_event = asyncio.Event()

    def handle_signal() -> None:
        logger.info("Shutdown signal received. Stopping harness...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal)
        except NotImplementedError:
            pass

    processed_count = 0

    try:
        while not stop_event.is_set():
            status = await client.fetch_current_status()
            if status:
                res = pipeline.process_envelope(status)
                processed_count += 1
                if res.is_mismatch:
                    logger.warning(
                        "Mismatch on target '%s': %s", res.target_id, res.error_message
                    )
                else:
                    logger.debug(
                        "Processed envelope #%d: target '%s'", processed_count, res.target_id
                    )

                if processed_count % 20 == 0:
                    summary = storage.get_coverage_summary()
                    logger.info(
                        "Progress: %d/%d targets achieved (%.2f%%) | Envelopes: %d",
                        summary["achieved_targets"],
                        summary["total_targets"],
                        summary["percentage"],
                        processed_count,
                    )
            await asyncio.sleep(poll_interval)
    finally:
        await client.aclose()
        print_summary(storage)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Elite Dangerous Live Telemetry Ingestion and Coverage Audit Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Remote host or IP address of the gaming machine running ed-telemetry",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port of the remote ed-telemetry service",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/fleet_telemetry_smoke.db"),
        help="Path to local SQLite persistence database",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Cadence in seconds for polling status endpoint",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print existing target coverage summary and exit immediately",
    )

    args = parser.parse_args()

    if args.summary:
        storage = TelemetryStorageEngine(args.db)
        storage.seed_targets(build_all_targets())
        print_summary(storage)
        sys.exit(0)

    try:
        asyncio.run(
            run_harness(
                host=args.host,
                port=args.port,
                db_path=args.db,
                poll_interval=args.poll_interval,
            )
        )
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")


if __name__ == "__main__":
    main()
