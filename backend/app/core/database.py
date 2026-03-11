"""SQLite database management with async access."""

import aiosqlite

from app.core.config import settings

_db: aiosqlite.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    track_name TEXT NOT NULL,
    car_name TEXT NOT NULL,
    started_at REAL NOT NULL,
    ended_at REAL,
    total_laps INTEGER DEFAULT 0,
    best_lap REAL,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS laps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    lap_number INTEGER NOT NULL,
    lap_time REAL NOT NULL,
    sector1 REAL,
    sector2 REAL,
    sector3 REAL,
    fuel_used REAL,
    tyre_wear_avg REAL,
    incidents INTEGER DEFAULT 0,
    timestamp REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS telemetry_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    timestamp REAL NOT NULL,
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS strategy_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    event_type TEXT NOT NULL,
    lap_number INTEGER,
    description TEXT,
    timestamp REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_laps_session ON laps(session_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_session ON telemetry_snapshots(session_id);
CREATE INDEX IF NOT EXISTS idx_strategy_session ON strategy_events(session_id);
"""


async def init_db() -> None:
    """Initialize database connection and create schema."""
    global _db
    _db = await aiosqlite.connect(settings.db_path)
    _db.row_factory = aiosqlite.Row
    await _db.executescript(SCHEMA)
    await _db.commit()


async def get_db() -> aiosqlite.Connection:
    """Get the active database connection."""
    if _db is None:
        await init_db()
    return _db  # type: ignore[return-value]


async def close_db() -> None:
    """Close the database connection."""
    global _db
    if _db:
        await _db.close()
        _db = None
