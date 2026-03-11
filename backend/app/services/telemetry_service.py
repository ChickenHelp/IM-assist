"""Telemetry service — bridges the collector to WebSocket clients.

Also handles session lifecycle (create/update/end sessions in DB)
and integrates the AI analysis module for real-time alerts.
"""

import asyncio
import json
import logging
import time
from collections.abc import Set

from fastapi import WebSocket

from app.analysis.ai_module import AIAnalyzer
from app.models.telemetry import StandingsMessage, TelemetryMessage
from app.telemetry.collector import TelemetryCollector

logger = logging.getLogger(__name__)


class TelemetryService:
    """Manages telemetry collection, DB persistence, AI alerts, and WebSocket broadcasting."""

    def __init__(self) -> None:
        self.collector = TelemetryCollector()
        self._clients: Set[WebSocket] = set()
        self._broadcast_task: asyncio.Task | None = None
        self._session_id: str = ""
        self._ai = AIAnalyzer()
        self._last_lap: int = 0
        self._lap_start_time: float = 0.0
        self._session_created: bool = False
        self._prev_fuel: float = 0.0

    def start(self) -> None:
        """Start the telemetry collector."""
        import uuid

        self._session_id = str(uuid.uuid4())[:8]
        self._session_created = False
        self._last_lap = 0
        self._lap_start_time = time.time()
        self._prev_fuel = 0.0
        self.collector.start()
        logger.info("TelemetryService started — session %s", self._session_id)

    def stop(self) -> None:
        """Stop the collector and broadcast task."""
        self.collector.stop()
        if self._broadcast_task:
            self._broadcast_task.cancel()
        # End session in DB
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self._end_session())
            else:
                loop.run_until_complete(self._end_session())
        except RuntimeError:
            pass

    async def _create_session(self) -> None:
        """Create a new session record in the database."""
        if self._session_created:
            return
        try:
            from app.core.database import get_db

            db = await get_db()
            await db.execute(
                "INSERT INTO sessions (id, track_name, car_name, started_at, status) VALUES (?, ?, ?, ?, ?)",
                (self._session_id, "Unknown Track", "Unknown Car", time.time(), "active"),
            )
            await db.commit()
            self._session_created = True
            logger.info("Session %s created in DB", self._session_id)
        except Exception:
            logger.exception("Failed to create session in DB")

    async def _end_session(self) -> None:
        """Mark the current session as ended in the database."""
        if not self._session_created:
            return
        try:
            from app.core.database import get_db

            db = await get_db()
            await db.execute(
                "UPDATE sessions SET ended_at = ?, status = ? WHERE id = ?",
                (time.time(), "completed", self._session_id),
            )
            await db.commit()
            logger.info("Session %s ended", self._session_id)
        except Exception:
            logger.exception("Failed to end session in DB")

    async def _persist_lap(self, lap_number: int, lap_time: float, frame) -> None:
        """Write a completed lap to the database."""
        try:
            from app.core.database import get_db

            wear = frame.tyres.wear
            avg_wear = (wear.fl + wear.fr + wear.rl + wear.rr) / 4
            sectors = frame.sectors if frame.sectors else []

            db = await get_db()
            await db.execute(
                """INSERT INTO laps
                   (session_id, lap_number, lap_time, sector1, sector2, sector3,
                    fuel_used, tyre_wear_avg, incidents, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self._session_id,
                    lap_number,
                    lap_time,
                    sectors[0] if len(sectors) > 0 else None,
                    sectors[1] if len(sectors) > 1 else None,
                    sectors[2] if len(sectors) > 2 else None,
                    self._prev_fuel - frame.fuel_level if self._prev_fuel > 0 else None,
                    round(avg_wear, 4),
                    frame.incidents,
                    time.time(),
                ),
            )
            # Update session best lap and total laps
            await db.execute(
                """UPDATE sessions SET total_laps = ?,
                   best_lap = CASE WHEN best_lap IS NULL OR ? < best_lap THEN ? ELSE best_lap END
                   WHERE id = ?""",
                (lap_number, lap_time, lap_time, self._session_id),
            )
            await db.commit()
            logger.info("Lap %d persisted (%.3fs)", lap_number, lap_time)
        except Exception:
            logger.exception("Failed to persist lap %d", lap_number)

    async def _save_telemetry_snapshot(self, frame) -> None:
        """Save a telemetry snapshot to the database (1 Hz)."""
        try:
            from app.core.database import get_db

            db = await get_db()
            await db.execute(
                "INSERT INTO telemetry_snapshots (session_id, timestamp, data) VALUES (?, ?, ?)",
                (self._session_id, time.time(), frame.model_dump_json()),
            )
            await db.commit()
        except Exception:
            logger.exception("Failed to save telemetry snapshot")

    async def register(self, ws: WebSocket) -> None:
        """Register a new WebSocket client for telemetry updates."""
        self._clients.add(ws)
        logger.info("Client registered (%d total)", len(self._clients))

        # Start broadcast loop if not running
        if self._broadcast_task is None or self._broadcast_task.done():
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())

    async def unregister(self, ws: WebSocket) -> None:
        """Unregister a WebSocket client."""
        self._clients.discard(ws)
        logger.info("Client unregistered (%d total)", len(self._clients))

    async def _broadcast_loop(self) -> None:
        """Broadcast telemetry and standings to all connected clients.

        Also handles:
        - Session creation on first frame
        - Lap detection and persistence
        - AI alerts injected into telemetry messages
        - Telemetry snapshots at 1 Hz
        """
        interval = 1.0 / 30  # 30 Hz
        standings_counter = 0
        snapshot_counter = 0

        while self._clients:
            frame = self.collector.latest
            if frame:
                now = time.time()

                # Create session on first frame
                if not self._session_created:
                    await self._create_session()
                    self._last_lap = frame.lap.current
                    self._lap_start_time = now
                    self._prev_fuel = frame.fuel_level

                # Detect lap change and persist
                if frame.lap.current > self._last_lap and self._last_lap > 0:
                    lap_time = now - self._lap_start_time
                    # Use best lap if available and reasonable
                    if frame.lap.best and frame.lap.best > 0:
                        lap_time = frame.lap.best
                    await self._persist_lap(self._last_lap, lap_time, frame)
                    self._prev_fuel = frame.fuel_level
                    self._lap_start_time = now
                    self._last_lap = frame.lap.current

                # AI analysis
                alerts = self._ai.analyze(frame)
                alert_dicts = [
                    {"type": a.type.value, "severity": a.severity.value, "message": a.message}
                    for a in alerts
                ]

                # Telemetry — every tick (30 Hz)
                msg = TelemetryMessage(
                    timestamp=now,
                    session_id=self._session_id,
                    data=frame,
                )
                # Inject alerts into message
                payload = msg.model_dump()
                if alert_dicts:
                    payload["alerts"] = alert_dicts
                await self._send_all(json.dumps(payload))

                # Standings — every 30 ticks (1 Hz)
                standings_counter += 1
                if standings_counter >= 30:
                    standings_counter = 0
                    standings_msg = StandingsMessage(
                        timestamp=now,
                        session_id=self._session_id,
                        entries=self.collector.standings,
                        positions=self.collector.positions,
                    )
                    await self._send_all(standings_msg.model_dump_json())

                # Telemetry snapshot — every 30 ticks (1 Hz)
                snapshot_counter += 1
                if snapshot_counter >= 30:
                    snapshot_counter = 0
                    await self._save_telemetry_snapshot(frame)

            await asyncio.sleep(interval)

    async def _send_all(self, data: str) -> None:
        """Send data to all connected clients, removing dead ones."""
        dead: list[WebSocket] = []
        for ws in self._clients:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._clients.discard(ws)
