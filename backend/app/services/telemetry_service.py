"""Telemetry service — bridges the collector to WebSocket clients."""

import asyncio
import json
import logging
import time
from collections.abc import Set

from fastapi import WebSocket

from app.models.telemetry import StandingsMessage, TelemetryMessage
from app.telemetry.collector import TelemetryCollector

logger = logging.getLogger(__name__)


class TelemetryService:
    """Manages telemetry collection and WebSocket broadcasting."""

    def __init__(self) -> None:
        self.collector = TelemetryCollector()
        self._clients: Set[WebSocket] = set()
        self._broadcast_task: asyncio.Task | None = None
        self._session_id: str = ""

    def start(self) -> None:
        """Start the telemetry collector."""
        import uuid

        self._session_id = str(uuid.uuid4())[:8]
        self.collector.start()
        logger.info("TelemetryService started — session %s", self._session_id)

    def stop(self) -> None:
        """Stop the collector and broadcast task."""
        self.collector.stop()
        if self._broadcast_task:
            self._broadcast_task.cancel()

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
        """Broadcast telemetry and standings to all connected clients."""
        interval = 1.0 / 30  # 30 Hz
        standings_counter = 0

        while self._clients:
            frame = self.collector.latest
            if frame:
                now = time.time()

                # Telemetry — every tick (30 Hz)
                msg = TelemetryMessage(
                    timestamp=now,
                    session_id=self._session_id,
                    data=frame,
                )
                await self._send_all(msg.model_dump_json())

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
