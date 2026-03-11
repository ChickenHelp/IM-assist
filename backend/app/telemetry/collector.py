"""iRacing telemetry collector using irsdk.

This module reads data from iRacing's shared memory via pyirsdk
and produces normalized TelemetryFrame objects at configurable Hz.
"""

import logging
import time
from collections import deque
from threading import Event, Thread

from app.core.config import settings
from app.models.telemetry import (
    ConditionsData,
    DriverPosition,
    FlagData,
    IntervalData,
    LapData,
    StandingsEntry,
    TelemetryFrame,
    TyreData,
    TyreTemps,
    TyreWear,
)

logger = logging.getLogger(__name__)

# Try to import irsdk — will fail on non-Windows or without iRacing
try:
    import irsdk

    IRSDK_AVAILABLE = True
except ImportError:
    IRSDK_AVAILABLE = False
    logger.warning("pyirsdk not available — running in simulation mode")


class TelemetryCollector:
    """Collects telemetry from iRacing at the configured frequency.

    Attributes:
        buffer: Ring buffer of recent TelemetryFrame objects.
        standings: Current race standings.
        positions: Current driver positions on track.
    """

    def __init__(self) -> None:
        self.buffer: deque[TelemetryFrame] = deque(maxlen=settings.telemetry_buffer_size)
        self.standings: list[StandingsEntry] = []
        self.positions: list[DriverPosition] = []
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._ir = None
        self._connected = False
        self._interval = 1.0 / settings.telemetry_hz

    def start(self) -> None:
        """Start the telemetry collection thread."""
        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True, name="telemetry-collector")
        self._thread.start()
        logger.info("Telemetry collector started at %d Hz", settings.telemetry_hz)

    def stop(self) -> None:
        """Stop the telemetry collection thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        if self._ir:
            self._ir.shutdown()
        logger.info("Telemetry collector stopped")

    @property
    def latest(self) -> TelemetryFrame | None:
        """Get the most recent telemetry frame."""
        return self.buffer[-1] if self.buffer else None

    def _run(self) -> None:
        """Main collection loop."""
        if IRSDK_AVAILABLE:
            self._run_irsdk()
        else:
            self._run_simulation()

    def _run_irsdk(self) -> None:
        """Collect real data from iRacing via irsdk."""
        self._ir = irsdk.IRSDK()

        while not self._stop_event.is_set():
            # Try to connect
            if not self._connected:
                if self._ir.startup():
                    self._connected = True
                    logger.info("Connected to iRacing")
                else:
                    time.sleep(1)
                    continue

            # Check if still connected
            if not self._ir.is_connected:
                self._connected = False
                logger.warning("Lost connection to iRacing — reconnecting...")
                time.sleep(1)
                continue

            # Read telemetry
            try:
                frame = self._read_iracing_frame()
                self.buffer.append(frame)
                self._update_standings()
            except Exception:
                logger.exception("Error reading telemetry")

            time.sleep(self._interval)

    def _read_iracing_frame(self) -> TelemetryFrame:
        """Read a single frame from iRacing shared memory."""
        ir = self._ir

        return TelemetryFrame(
            speed=ir["Speed"] * 3.6 if ir["Speed"] else 0,  # m/s -> km/h
            rpm=int(ir["RPM"] or 0),
            gear=int(ir["Gear"] or 0),
            throttle=float(ir["Throttle"] or 0),
            brake=float(ir["Brake"] or 0),
            steering=float(ir["SteeringWheelAngle"] or 0) / 7.0,  # normalize to -1..1
            fuel_level=float(ir["FuelLevel"] or 0),
            fuel_per_lap=float(ir["FuelUsePerHour"] or 0),  # will be calculated more precisely
            tyres=TyreData(
                temp=TyreTemps(
                    fl=ir["LFtempCL"] or 0,
                    fr=ir["RFtempCL"] or 0,
                    rl=ir["LRtempCL"] or 0,
                    rr=ir["RRtempCL"] or 0,
                ),
                wear=TyreWear(
                    fl=1.0 - (ir["LFwearL"] or 1),
                    fr=1.0 - (ir["RFwearL"] or 1),
                    rl=1.0 - (ir["LRwearL"] or 1),
                    rr=1.0 - (ir["RRwearL"] or 1),
                ),
            ),
            lap=LapData(
                current=int(ir["Lap"] or 0),
                best=float(ir["LapBestLapTime"] or 0) if ir["LapBestLapTime"] else None,
                delta=float(ir["LapDeltaToBestLap"] or 0),
            ),
            sectors=[],  # Sectors are accumulated per lap
            position=int(ir["PlayerCarPosition"] or 0),
            interval=IntervalData(),
            incidents=int(ir["PlayerCarMyIncidentCount"] or 0),
            conditions=ConditionsData(
                track_temp=float(ir["TrackTempCrew"] or 30),
                air_temp=float(ir["AirTemp"] or 22),
            ),
            flags=FlagData(
                yellow=bool(ir["SessionFlags"] and ir["SessionFlags"] & 0x4),
                blue=bool(ir["SessionFlags"] and ir["SessionFlags"] & 0x80),
                black=bool(ir["SessionFlags"] and ir["SessionFlags"] & 0x1000),
            ),
        )

    def _update_standings(self) -> None:
        """Update live standings from iRacing session data."""
        if not self._ir or not self._connected:
            return

        ir = self._ir
        entries = []
        positions = []

        drivers = ir["DriverInfo"]["Drivers"] if ir["DriverInfo"] else []
        for driver in drivers:
            idx = driver["CarIdx"]
            entries.append(
                StandingsEntry(
                    position=int(ir["CarIdxPosition"][idx] or 0),
                    car_idx=idx,
                    driver_name=driver.get("UserName", f"Car {idx}"),
                    car_number=str(driver.get("CarNumber", "")),
                    lap=int(ir["CarIdxLap"][idx] or 0),
                    last_lap=float(ir["CarIdxLastLapTime"][idx] or 0) or None,
                    best_lap=float(ir["CarIdxBestLapTime"][idx] or 0) or None,
                    in_pit=bool(ir["CarIdxOnPitRoad"][idx]),
                )
            )
            positions.append(
                DriverPosition(
                    car_idx=idx,
                    driver_name=driver.get("UserName", f"Car {idx}"),
                    position=int(ir["CarIdxPosition"][idx] or 0),
                    lap_pct=float(ir["CarIdxLapDistPct"][idx] or 0),
                    is_player=(idx == ir["PlayerCarIdx"]),
                )
            )

        entries.sort(key=lambda e: e.position if e.position > 0 else 999)
        self.standings = entries
        self.positions = positions

    # ── Simulation mode ──────────────────────────────────────────────

    def _run_simulation(self) -> None:
        """Generate simulated telemetry for development/testing."""
        import math
        import random

        lap = 1
        lap_pct = 0.0
        fuel = 100.0
        incidents = 0
        t = 0.0

        while not self._stop_event.is_set():
            t += self._interval
            lap_pct += 0.003  # ~5.5s per lap at 30hz... simplified

            if lap_pct >= 1.0:
                lap_pct = 0.0
                lap += 1
                fuel -= 2.5 + random.uniform(-0.3, 0.3)
                if random.random() < 0.05:
                    incidents += 1

            # Simulate speed profile around a lap
            phase = lap_pct * 2 * math.pi
            base_speed = 200 + 60 * math.sin(phase * 3)
            speed = max(60, base_speed + random.uniform(-5, 5))

            throttle = max(0, min(1, 0.5 + 0.5 * math.sin(phase * 3)))
            brake = max(0, min(1, -0.5 * math.sin(phase * 3)))

            frame = TelemetryFrame(
                speed=speed,
                rpm=int(speed * 40 + random.uniform(-200, 200)),
                gear=min(7, max(1, int(speed / 50) + 1)),
                throttle=throttle,
                brake=brake,
                steering=0.3 * math.sin(phase * 5),
                fuel_level=max(0, fuel),
                fuel_per_lap=2.5,
                tyres=TyreData(
                    temp=TyreTemps(
                        fl=90 + random.uniform(-3, 8),
                        fr=92 + random.uniform(-3, 8),
                        rl=88 + random.uniform(-3, 6),
                        rr=89 + random.uniform(-3, 6),
                    ),
                    wear=TyreWear(
                        fl=max(0, 1 - lap * 0.015),
                        fr=max(0, 1 - lap * 0.017),
                        rl=max(0, 1 - lap * 0.012),
                        rr=max(0, 1 - lap * 0.013),
                    ),
                ),
                lap=LapData(
                    current=lap,
                    best=82.345 if lap > 1 else None,
                    delta=random.uniform(-0.5, 0.5),
                ),
                sectors=[27.0 + random.uniform(-0.5, 0.5)] if lap_pct > 0.33 else [],
                position=3,
                interval=IntervalData(
                    ahead=1.2 + random.uniform(-0.3, 0.3),
                    behind=2.5 + random.uniform(-0.5, 0.5),
                ),
                incidents=incidents,
                conditions=ConditionsData(
                    track_temp=38 + random.uniform(-1, 1),
                    air_temp=24 + random.uniform(-0.5, 0.5),
                ),
                flags=FlagData(),
            )

            self.buffer.append(frame)

            # Simulated standings
            self.standings = [
                StandingsEntry(
                    position=i + 1,
                    car_idx=i,
                    driver_name=name,
                    car_number=str(i + 1),
                    lap=lap + (1 if i < 2 else 0),
                    last_lap=82.0 + random.uniform(-1, 2),
                    best_lap=81.5 + i * 0.3,
                    interval=round(random.uniform(0.3, 2.0), 3) if i > 0 else None,
                    in_pit=False,
                )
                for i, name in enumerate(
                    ["L. Hamilton", "M. Verstappen", "You", "C. Leclerc", "L. Norris"]
                )
            ]

            self.positions = [
                DriverPosition(
                    car_idx=i,
                    driver_name=name,
                    position=i + 1,
                    lap_pct=(lap_pct + i * 0.15) % 1.0,
                    is_player=(i == 2),
                )
                for i, name in enumerate(
                    ["L. Hamilton", "M. Verstappen", "You", "C. Leclerc", "L. Norris"]
                )
            ]

            time.sleep(self._interval)
