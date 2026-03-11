"""AI analysis module for real-time race insights.

Provides:
- Tyre overheat detection
- Grip loss detection
- Fuel risk alerts
- Lap time trend analysis
- Strategy suggestions

Uses heuristic rules for MVP, with hooks for ML models later.
"""

import logging
from dataclasses import dataclass
from enum import StrEnum

from app.models.telemetry import TelemetryFrame

logger = logging.getLogger(__name__)


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(StrEnum):
    TYRE_OVERHEAT = "tyre_overheat"
    GRIP_LOSS = "grip_loss"
    FUEL_RISK = "fuel_risk"
    LAP_DEGRADATION = "lap_degradation"
    STRATEGY_SUGGESTION = "strategy_suggestion"


@dataclass
class Alert:
    """An AI-generated alert for the manager."""
    type: AlertType
    severity: AlertSeverity
    message: str
    details: dict | None = None


class AIAnalyzer:
    """Analyzes telemetry data and generates alerts.

    Maintains a rolling window of recent frames for trend analysis.
    """

    # Thresholds
    TYRE_TEMP_WARNING = 105  # °C
    TYRE_TEMP_CRITICAL = 115  # °C
    FUEL_WARNING_LAPS = 3
    FUEL_CRITICAL_LAPS = 1
    LAP_DEGRADATION_THRESHOLD = 0.5  # seconds slower than best

    def __init__(self) -> None:
        self._recent_laps: list[float] = []
        self._best_lap: float | None = None
        self._last_alert_lap: dict[AlertType, int] = {}

    def analyze(self, frame: TelemetryFrame) -> list[Alert]:
        """Analyze a telemetry frame and return any triggered alerts.

        Args:
            frame: Current telemetry data.

        Returns:
            List of alerts (may be empty).
        """
        alerts: list[Alert] = []
        current_lap = frame.lap.current

        # Track best lap
        if frame.lap.best and (self._best_lap is None or frame.lap.best < self._best_lap):
            self._best_lap = frame.lap.best

        # ── Tyre overheat detection ──
        temps = [frame.tyres.temp.fl, frame.tyres.temp.fr, frame.tyres.temp.rl, frame.tyres.temp.rr]
        labels = ["FL", "FR", "RL", "RR"]
        for temp, label in zip(temps, labels):
            if temp > self.TYRE_TEMP_CRITICAL:
                if self._should_alert(AlertType.TYRE_OVERHEAT, current_lap):
                    alerts.append(Alert(
                        type=AlertType.TYRE_OVERHEAT,
                        severity=AlertSeverity.CRITICAL,
                        message=f"CRITICAL: {label} tyre at {temp:.0f}°C — blistering risk!",
                        details={"tyre": label, "temp": temp},
                    ))
            elif temp > self.TYRE_TEMP_WARNING:
                if self._should_alert(AlertType.TYRE_OVERHEAT, current_lap):
                    alerts.append(Alert(
                        type=AlertType.TYRE_OVERHEAT,
                        severity=AlertSeverity.WARNING,
                        message=f"Warning: {label} tyre running hot ({temp:.0f}°C)",
                        details={"tyre": label, "temp": temp},
                    ))

        # ── Grip loss detection (based on tyre wear) ──
        wear_values = [frame.tyres.wear.fl, frame.tyres.wear.fr, frame.tyres.wear.rl, frame.tyres.wear.rr]
        max_wear = max(wear_values)
        if max_wear > 0.8:
            if self._should_alert(AlertType.GRIP_LOSS, current_lap):
                worst_tyre = labels[wear_values.index(max_wear)]
                alerts.append(Alert(
                    type=AlertType.GRIP_LOSS,
                    severity=AlertSeverity.WARNING,
                    message=f"Grip loss likely — {worst_tyre} wear at {max_wear:.0%}",
                    details={"tyre": worst_tyre, "wear": max_wear},
                ))

        # ── Fuel risk ──
        if frame.fuel_per_lap > 0:
            fuel_laps = frame.fuel_level / frame.fuel_per_lap
            if fuel_laps < self.FUEL_CRITICAL_LAPS:
                if self._should_alert(AlertType.FUEL_RISK, current_lap):
                    alerts.append(Alert(
                        type=AlertType.FUEL_RISK,
                        severity=AlertSeverity.CRITICAL,
                        message=f"FUEL CRITICAL: {fuel_laps:.1f} laps remaining!",
                        details={"fuel_laps": fuel_laps},
                    ))
            elif fuel_laps < self.FUEL_WARNING_LAPS:
                if self._should_alert(AlertType.FUEL_RISK, current_lap):
                    alerts.append(Alert(
                        type=AlertType.FUEL_RISK,
                        severity=AlertSeverity.WARNING,
                        message=f"Fuel warning: {fuel_laps:.1f} laps remaining",
                        details={"fuel_laps": fuel_laps},
                    ))

        # ── Lap time degradation ──
        if frame.lap.delta > self.LAP_DEGRADATION_THRESHOLD:
            if self._should_alert(AlertType.LAP_DEGRADATION, current_lap):
                alerts.append(Alert(
                    type=AlertType.LAP_DEGRADATION,
                    severity=AlertSeverity.INFO,
                    message=f"Lap time degrading: +{frame.lap.delta:.3f}s vs best",
                    details={"delta": frame.lap.delta},
                ))

        return alerts

    def _should_alert(self, alert_type: AlertType, current_lap: int) -> bool:
        """Rate-limit alerts to once per lap per type."""
        last = self._last_alert_lap.get(alert_type, -1)
        if current_lap > last:
            self._last_alert_lap[alert_type] = current_lap
            return True
        return False

    def get_trend_summary(self) -> dict:
        """Get a summary of lap time trends."""
        if len(self._recent_laps) < 3:
            return {"trend": "insufficient_data"}

        last_3 = self._recent_laps[-3:]
        avg_recent = sum(last_3) / len(last_3)

        if self._best_lap:
            degradation = avg_recent - self._best_lap
        else:
            degradation = 0

        # Simple trend: improving, stable, or degrading
        if len(self._recent_laps) >= 5:
            first_3 = self._recent_laps[-5:-2]
            avg_earlier = sum(first_3) / len(first_3)
            diff = avg_recent - avg_earlier
            if diff < -0.2:
                trend = "improving"
            elif diff > 0.3:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "avg_recent_3": round(avg_recent, 3),
            "best_lap": self._best_lap,
            "degradation_from_best": round(degradation, 3),
        }
