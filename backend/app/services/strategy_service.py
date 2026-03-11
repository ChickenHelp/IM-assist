"""Race strategy calculation service."""

import math

from app.models.session import PitStrategy, PitWindow, UndercutSimulation


def calculate_pit_window(strategy: PitStrategy) -> PitWindow:
    """Calculate the optimal pit window based on fuel and tyre data.

    Args:
        strategy: Current race state and degradation parameters.

    Returns:
        PitWindow with earliest, optimal, and latest pit laps.
    """
    remaining_laps = strategy.total_laps - strategy.current_lap

    # Fuel calculation
    fuel_laps = (
        strategy.fuel_level / strategy.fuel_per_lap if strategy.fuel_per_lap > 0 else remaining_laps
    )

    # Tyre calculation — estimate laps until critical wear (> 0.85)
    wear_remaining = 0.85 - strategy.tyre_wear_avg
    tyre_laps = (
        wear_remaining / strategy.tyre_wear_rate if strategy.tyre_wear_rate > 0 else remaining_laps
    )

    # Determine limiting factor
    limiting_laps = min(fuel_laps, tyre_laps)

    # Pit window
    latest_lap = strategy.current_lap + int(limiting_laps)
    earliest_lap = max(strategy.current_lap + 1, latest_lap - 5)
    optimal_lap = strategy.current_lap + int(limiting_laps * 0.8)

    # Clamp to race length
    latest_lap = min(latest_lap, strategy.total_laps - 1)
    optimal_lap = min(optimal_lap, latest_lap - 1)
    earliest_lap = min(earliest_lap, optimal_lap)

    # Number of stops
    estimated_stops = max(1, math.ceil(remaining_laps / limiting_laps)) if limiting_laps > 0 else 1

    notes = []
    if fuel_laps < tyre_laps:
        notes.append(f"Fuel-limited: ~{fuel_laps:.1f} laps remaining")
    else:
        notes.append(f"Tyre-limited: ~{tyre_laps:.1f} laps remaining")

    if fuel_laps < 3:
        notes.append("CRITICAL: Fuel dangerously low!")
    if strategy.tyre_wear_avg > 0.75:
        notes.append("WARNING: Tyres heavily worn")

    return PitWindow(
        earliest_lap=max(1, earliest_lap),
        optimal_lap=max(1, optimal_lap),
        latest_lap=max(1, latest_lap),
        fuel_laps_remaining=round(fuel_laps, 1),
        tyre_laps_remaining=round(tyre_laps, 1),
        estimated_pit_stops=estimated_stops,
        strategy_notes=notes,
    )


def simulate_undercut(
    strategy: PitStrategy,
    gap_to_car_ahead: float,
    fresh_tyre_advantage: float = 0.8,
) -> UndercutSimulation:
    """Simulate an undercut scenario.

    Args:
        strategy: Current race state.
        gap_to_car_ahead: Gap in seconds to the car in front.
        fresh_tyre_advantage: Expected lap time gain on fresh tyres.

    Returns:
        UndercutSimulation with expected outcome.
    """
    pit_lap = strategy.current_lap + 1
    pit_loss = strategy.pit_loss_seconds
    tyre_gain_over_stint = fresh_tyre_advantage * 3  # advantage compounds over laps

    net_delta = gap_to_car_ahead - pit_loss + tyre_gain_over_stint

    if net_delta > 0:
        risk = "low"
        notes = f"Undercut likely to succeed. Net gain: {net_delta:.1f}s"
    elif net_delta > -2:
        risk = "medium"
        notes = f"Undercut marginal. Net delta: {net_delta:.1f}s"
    else:
        risk = "high"
        notes = f"Undercut unlikely. Deficit: {abs(net_delta):.1f}s"

    return UndercutSimulation(
        scenario="undercut",
        pit_lap=pit_lap,
        estimated_position_after=strategy.position if hasattr(strategy, "position") else 0,
        time_delta=round(net_delta, 2),
        risk_level=risk,
        notes=notes,
    )
