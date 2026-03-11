"""Report generation API routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.core.auth import require_permission
from app.core.database import get_db
from app.analysis.report import generate_report
from app.models.session import LapRecord, SessionInfo

router = APIRouter()


@router.get("/sessions/{session_id}/report")
async def download_report(
    session_id: str,
    _=Depends(require_permission("analysis:read")),
):
    """Generate and download a post-race PDF report."""
    db = await get_db()

    # Fetch session
    cursor = await db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    session = SessionInfo(**dict(row))

    # Fetch laps
    cursor = await db.execute(
        "SELECT * FROM laps WHERE session_id = ? ORDER BY lap_number", (session_id,)
    )
    lap_rows = await cursor.fetchall()
    laps = [LapRecord(**dict(r)) for r in lap_rows]

    # Generate PDF
    pdf_bytes = generate_report(session, laps)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="pitwall_report_{session_id}.pdf"'
        },
    )
