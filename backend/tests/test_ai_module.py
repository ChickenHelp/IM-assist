"""Tests for the AI analysis module."""

from app.analysis.ai_module import AIAnalyzer, AlertSeverity, AlertType
from app.models.telemetry import (
    ConditionsData,
    FlagData,
    IntervalData,
    LapData,
    TelemetryFrame,
    TyreData,
    TyreTemps,
    TyreWear,
)


def _make_frame(**overrides) -> TelemetryFrame:
    """Create a telemetry frame with sensible defaults."""
    defaults = dict(
        speed=200,
        rpm=8000,
        gear=5,
        throttle=0.8,
        brake=0.0,
        steering=0.0,
        fuel_level=50.0,
        fuel_per_lap=2.5,
        tyres=TyreData(
            temp=TyreTemps(fl=90, fr=92, rl=88, rr=89),
            wear=TyreWear(fl=0.3, fr=0.3, rl=0.3, rr=0.3),
        ),
        lap=LapData(current=5, best=82.0, delta=0.1),
        position=3,
        interval=IntervalData(ahead=1.0, behind=2.0),
        incidents=0,
        conditions=ConditionsData(track_temp=35, air_temp=22),
        flags=FlagData(),
    )
    defaults.update(overrides)
    return TelemetryFrame(**defaults)


def test_no_alerts_normal_conditions():
    analyzer = AIAnalyzer()
    frame = _make_frame()
    alerts = analyzer.analyze(frame)
    assert len(alerts) == 0


def test_tyre_overheat_warning():
    analyzer = AIAnalyzer()
    frame = _make_frame(
        tyres=TyreData(
            temp=TyreTemps(fl=110, fr=92, rl=88, rr=89),
            wear=TyreWear(fl=0.3, fr=0.3, rl=0.3, rr=0.3),
        )
    )
    alerts = analyzer.analyze(frame)
    tyre_alerts = [a for a in alerts if a.type == AlertType.TYRE_OVERHEAT]
    assert len(tyre_alerts) >= 1
    assert tyre_alerts[0].severity == AlertSeverity.WARNING


def test_tyre_overheat_critical():
    analyzer = AIAnalyzer()
    frame = _make_frame(
        tyres=TyreData(
            temp=TyreTemps(fl=120, fr=92, rl=88, rr=89),
            wear=TyreWear(fl=0.3, fr=0.3, rl=0.3, rr=0.3),
        )
    )
    alerts = analyzer.analyze(frame)
    tyre_alerts = [a for a in alerts if a.type == AlertType.TYRE_OVERHEAT]
    assert len(tyre_alerts) >= 1
    assert tyre_alerts[0].severity == AlertSeverity.CRITICAL


def test_fuel_critical():
    analyzer = AIAnalyzer()
    frame = _make_frame(fuel_level=2.0, fuel_per_lap=2.5)
    alerts = analyzer.analyze(frame)
    fuel_alerts = [a for a in alerts if a.type == AlertType.FUEL_RISK]
    assert len(fuel_alerts) >= 1
    assert fuel_alerts[0].severity == AlertSeverity.CRITICAL


def test_grip_loss_warning():
    analyzer = AIAnalyzer()
    frame = _make_frame(
        tyres=TyreData(
            temp=TyreTemps(fl=95, fr=95, rl=95, rr=95),
            wear=TyreWear(fl=0.85, fr=0.7, rl=0.7, rr=0.7),
        )
    )
    alerts = analyzer.analyze(frame)
    grip_alerts = [a for a in alerts if a.type == AlertType.GRIP_LOSS]
    assert len(grip_alerts) >= 1


def test_alert_rate_limiting():
    analyzer = AIAnalyzer()
    frame = _make_frame(fuel_level=2.0, fuel_per_lap=2.5)

    # First call triggers
    alerts1 = analyzer.analyze(frame)
    assert len([a for a in alerts1 if a.type == AlertType.FUEL_RISK]) >= 1

    # Second call on same lap does not
    alerts2 = analyzer.analyze(frame)
    assert len([a for a in alerts2 if a.type == AlertType.FUEL_RISK]) == 0

    # New lap triggers again
    frame2 = _make_frame(fuel_level=2.0, fuel_per_lap=2.5, lap=LapData(current=6, best=82.0, delta=0.1))
    alerts3 = analyzer.analyze(frame2)
    assert len([a for a in alerts3 if a.type == AlertType.FUEL_RISK]) >= 1
