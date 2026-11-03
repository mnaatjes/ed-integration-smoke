"""Tests for Behavioral Abstraction Archetypes (ADR 0003)."""

from datetime import UTC, datetime

from ed_integration_smoke.patterns import (
    BitfieldEdgeDetector,
    ContextSetDiffer,
    EdgeType,
    EnvironmentMilestoneContext,
    MetricQuantizer,
)


def test_bitfield_edge_detector_transitions() -> None:
    detector = BitfieldEdgeDetector(initial_flags=0)

    # Transition 1: Deploy landing gear (bit 2 -> 0x04) and shields (bit 3 -> 0x08)
    events_1 = detector.evaluate(0x0C)
    assert len(events_1) == 2
    assert all(e.edge_type == EdgeType.RISING for e in events_1)
    bits_rising = {e.flag_bit for e in events_1}
    assert bits_rising == {0x04, 0x08}

    # Transition 2: Same flags repeated (1 Hz steady state polling) -> no edge events
    events_2 = detector.evaluate(0x0C)
    assert events_2 == []

    # Transition 3: Stow landing gear (drop bit 2), deploy hardpoints (bit 6 -> 0x40)
    events_3 = detector.evaluate(0x48)  # 0x08 | 0x40
    assert len(events_3) == 2

    falling = [e for e in events_3 if e.edge_type == EdgeType.FALLING]
    rising = [e for e in events_3 if e.edge_type == EdgeType.RISING]

    assert len(falling) == 1
    assert falling[0].flag_bit == 0x04  # Landing gear stowed

    assert len(rising) == 1
    assert rising[0].flag_bit == 0x40  # Hardpoints deployed


def test_metric_quantizer_hysteresis() -> None:
    # Fuel tank quantizer: Critical (<10%), Low (<25%), Nominal (>=25%)
    quantizer = MetricQuantizer(thresholds=[10.0, 25.0], labels=["CRITICAL", "LOW", "NOMINAL"])

    # Initial state
    assert quantizer.update(32.0) == "NOMINAL"
    # Small fluctuation above 25% does not emit change
    assert quantizer.update(28.0) is None
    # Drop below 25% emits change
    assert quantizer.update(21.5) == "LOW"
    # Continual drift within 10-25% does not emit
    assert quantizer.update(18.0) is None
    # Drop below 10% emits change
    assert quantizer.update(8.2) == "CRITICAL"


def test_environment_milestone_context_idempotence() -> None:
    context = EnvironmentMilestoneContext()
    now = datetime.now(UTC)

    # Docking event sets state directly
    context.apply_milestone(
        "Docked", {"StationName": "Jameson Memorial", "StarSystem": "Shinrarta Dezhra"}, now
    )
    assert context.is_docked is True
    assert context.current_station == "Jameson Memorial"
    assert context.current_system == "Shinrarta Dezhra"
    assert context.flight_mode == "DOCKED"

    # Out-of-order / direct jump applies cleanly without prior undocking
    context.apply_milestone("FSDJump", {"StarSystem": "Sol"}, now)
    assert context.current_system == "Sol"
    assert context.flight_mode == "SUPERCRUISE"


def test_context_set_differ_mutations() -> None:
    differ = ContextSetDiffer(initial_items={"PulseLaser", "ShieldGenerator", "CargoRack"})

    # Swap PulseLaser for BeamLaser
    delta = differ.update({"BeamLaser", "ShieldGenerator", "CargoRack"})
    assert delta is not None
    assert delta.added == frozenset({"BeamLaser"})
    assert delta.removed == frozenset({"PulseLaser"})

    # Identical state returns None
    assert differ.update({"BeamLaser", "ShieldGenerator", "CargoRack"}) is None
