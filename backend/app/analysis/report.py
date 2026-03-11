"""Post-race report generation.

Generates a PDF report with:
- Session summary
- Lap time chart
- Sector analysis
- Incident log
- Strategy summary
- Performance suggestions
"""

import io
import logging
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.session import LapRecord, SessionInfo

logger = logging.getLogger(__name__)


def generate_report(session: SessionInfo, laps: list[LapRecord]) -> bytes:
    """Generate a PDF post-race report.

    Args:
        session: Session metadata.
        laps: List of lap records.

    Returns:
        PDF file content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "PitWallTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=colors.HexColor("#E10600"),
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "PitWallHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1A1A2E"),
        spaceAfter=10,
    )

    elements = []

    # Title
    elements.append(Paragraph("PitWall — Post-Race Report", title_style))
    elements.append(Spacer(1, 10))

    # Session summary
    elements.append(Paragraph("Session Summary", heading_style))
    summary_data = [
        ["Track", session.track_name],
        ["Car", session.car_name],
        ["Date", datetime.fromtimestamp(session.started_at, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")],
        ["Total Laps", str(session.total_laps)],
        ["Best Lap", f"{session.best_lap:.3f}s" if session.best_lap else "N/A"],
        ["Status", session.status.upper()],
    ]
    summary_table = Table(summary_data, colWidths=[5 * cm, 10 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F0F0")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Lap times table
    if laps:
        elements.append(Paragraph("Lap Times", heading_style))
        lap_header = ["Lap", "Time", "S1", "S2", "S3", "Fuel", "Incidents"]
        lap_data = [lap_header]
        for lap in laps:
            lap_data.append([
                str(lap.lap_number),
                f"{lap.lap_time:.3f}",
                f"{lap.sector1:.3f}" if lap.sector1 else "-",
                f"{lap.sector2:.3f}" if lap.sector2 else "-",
                f"{lap.sector3:.3f}" if lap.sector3 else "-",
                f"{lap.fuel_used:.2f}L" if lap.fuel_used else "-",
                str(lap.incidents),
            ])

        lap_table = Table(lap_data, colWidths=[2 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2 * cm, 2 * cm])
        lap_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A1A2E")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F8F8")]),
                ]
            )
        )
        elements.append(lap_table)
        elements.append(Spacer(1, 20))

        # Performance analysis
        elements.append(Paragraph("Performance Analysis", heading_style))
        if laps:
            best = min(laps, key=lambda l: l.lap_time)
            worst = max(laps, key=lambda l: l.lap_time)
            avg = sum(l.lap_time for l in laps) / len(laps)
            consistency = worst.lap_time - best.lap_time

            analysis_data = [
                ["Best Lap", f"Lap {best.lap_number}: {best.lap_time:.3f}s"],
                ["Worst Lap", f"Lap {worst.lap_number}: {worst.lap_time:.3f}s"],
                ["Average", f"{avg:.3f}s"],
                ["Consistency (range)", f"{consistency:.3f}s"],
                ["Total Incidents", str(sum(l.incidents for l in laps))],
            ]
            analysis_table = Table(analysis_data, colWidths=[5 * cm, 10 * cm])
            analysis_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F0F0")),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("PADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            elements.append(analysis_table)

    # Build PDF
    doc.build(elements)
    return buffer.getvalue()
