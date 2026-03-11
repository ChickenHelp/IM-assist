"""Telemetry data models."""

from pydantic import BaseModel, Field


class TyreTemps(BaseModel):
    fl: float = Field(description="Front-left tyre temperature (°C)")
    fr: float = Field(description="Front-right tyre temperature (°C)")
    rl: float = Field(description="Rear-left tyre temperature (°C)")
    rr: float = Field(description="Rear-right tyre temperature (°C)")


class TyreWear(BaseModel):
    fl: float = Field(ge=0, le=1, description="Front-left wear (0=new, 1=worn)")
    fr: float = Field(ge=0, le=1)
    rl: float = Field(ge=0, le=1)
    rr: float = Field(ge=0, le=1)


class TyreData(BaseModel):
    temp: TyreTemps
    wear: TyreWear


class LapData(BaseModel):
    current: int
    best: float | None = None
    delta: float = 0.0


class IntervalData(BaseModel):
    ahead: float | None = None
    behind: float | None = None


class ConditionsData(BaseModel):
    track_temp: float
    air_temp: float


class FlagData(BaseModel):
    yellow: bool = False
    blue: bool = False
    black: bool = False


class DriverPosition(BaseModel):
    """Position of a driver on track for the live map."""
    car_idx: int
    driver_name: str
    position: int
    lap_pct: float = Field(ge=0, le=1, description="Track position 0-1")
    is_player: bool = False
    class_color: str = "#FFFFFF"


class TelemetryFrame(BaseModel):
    """Single telemetry frame at a point in time."""
    speed: float = Field(ge=0, description="Speed in km/h")
    rpm: int = Field(ge=0)
    gear: int = Field(ge=-1, le=8)
    throttle: float = Field(ge=0, le=1)
    brake: float = Field(ge=0, le=1)
    steering: float = Field(ge=-1, le=1)
    fuel_level: float = Field(ge=0)
    fuel_per_lap: float = Field(ge=0)
    tyres: TyreData
    lap: LapData
    sectors: list[float] = []
    position: int = 0
    interval: IntervalData = IntervalData()
    incidents: int = 0
    conditions: ConditionsData = ConditionsData(track_temp=30, air_temp=22)
    flags: FlagData = FlagData()


class TelemetryMessage(BaseModel):
    """WebSocket message wrapping a telemetry frame."""
    type: str = "telemetry"
    timestamp: float
    session_id: str
    data: TelemetryFrame


class StandingsEntry(BaseModel):
    """Single entry in the live standings."""
    position: int
    car_idx: int
    driver_name: str
    car_number: str
    lap: int
    last_lap: float | None = None
    best_lap: float | None = None
    gap_to_leader: float | None = None
    interval: float | None = None
    incidents: int = 0
    in_pit: bool = False
    class_color: str = "#FFFFFF"


class StandingsMessage(BaseModel):
    """WebSocket message with full standings."""
    type: str = "standings"
    timestamp: float
    session_id: str
    entries: list[StandingsEntry]
    positions: list[DriverPosition] = []
