"""Session and strategy models."""

from pydantic import BaseModel


class SessionInfo(BaseModel):
    id: str
    track_name: str
    car_name: str
    started_at: float
    ended_at: float | None = None
    total_laps: int = 0
    best_lap: float | None = None
    status: str = "active"


class LapRecord(BaseModel):
    lap_number: int
    lap_time: float
    sector1: float | None = None
    sector2: float | None = None
    sector3: float | None = None
    fuel_used: float | None = None
    tyre_wear_avg: float | None = None
    incidents: int = 0


class PitStrategy(BaseModel):
    """Pit stop strategy calculation input."""
    current_lap: int
    total_laps: int
    fuel_level: float
    fuel_per_lap: float
    tyre_wear_avg: float
    tyre_wear_rate: float
    pit_loss_seconds: float = 25.0


class PitWindow(BaseModel):
    """Calculated pit window."""
    earliest_lap: int
    optimal_lap: int
    latest_lap: int
    fuel_laps_remaining: float
    tyre_laps_remaining: float
    estimated_pit_stops: int
    strategy_notes: list[str] = []


class UndercutSimulation(BaseModel):
    """Undercut/overcut simulation result."""
    scenario: str
    pit_lap: int
    estimated_position_after: int
    time_delta: float
    risk_level: str
    notes: str
