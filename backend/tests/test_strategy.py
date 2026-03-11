"""Tests for the strategy service."""

from app.models.session import PitStrategy
from app.services.strategy_service import calculate_pit_window, simulate_undercut


def test_pit_window_fuel_limited():
    strategy = PitStrategy(
        current_lap=10,
        total_laps=50,
        fuel_level=25.0,
        fuel_per_lap=2.5,
        tyre_wear_avg=0.3,
        tyre_wear_rate=0.02,
    )
    window = calculate_pit_window(strategy)
    assert window.earliest_lap > strategy.current_lap
    assert window.earliest_lap <= window.optimal_lap <= window.latest_lap
    assert window.fuel_laps_remaining == 10.0
    assert any("Fuel" in note for note in window.strategy_notes)


def test_pit_window_tyre_limited():
    strategy = PitStrategy(
        current_lap=10,
        total_laps=50,
        fuel_level=100.0,
        fuel_per_lap=2.5,
        tyre_wear_avg=0.7,
        tyre_wear_rate=0.05,
    )
    window = calculate_pit_window(strategy)
    assert window.tyre_laps_remaining == 3.0
    assert any("Tyre" in note for note in window.strategy_notes)


def test_undercut_likely():
    strategy = PitStrategy(
        current_lap=15,
        total_laps=50,
        fuel_level=50.0,
        fuel_per_lap=2.5,
        tyre_wear_avg=0.5,
        tyre_wear_rate=0.03,
        pit_loss_seconds=22.0,
    )
    result = simulate_undercut(strategy, gap_to_car_ahead=25.0)
    assert result.scenario == "undercut"
    assert result.time_delta > 0
    assert result.risk_level == "low"


def test_undercut_unlikely():
    strategy = PitStrategy(
        current_lap=15,
        total_laps=50,
        fuel_level=50.0,
        fuel_per_lap=2.5,
        tyre_wear_avg=0.5,
        tyre_wear_rate=0.03,
        pit_loss_seconds=25.0,
    )
    result = simulate_undercut(strategy, gap_to_car_ahead=1.0, fresh_tyre_advantage=0.3)
    assert result.risk_level in ("medium", "high")
