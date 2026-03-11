"""REST API routes."""

from fastapi import APIRouter, Depends

from app.core.auth import Role, TokenPayload, create_token, require_permission, verify_token
from app.models.session import PitStrategy
from app.services.strategy_service import calculate_pit_window, simulate_undercut

router = APIRouter()


# ── Auth ──────────────────────────────────────────────────────────────


class LoginRequest:
    """Simple login — in production, use proper credentials."""

    def __init__(self, username: str, role: str = "observer"):
        self.username = username
        self.role = role


@router.post("/auth/token")
async def login(username: str, role: str = "observer"):
    """Generate a session token.

    In production this would validate credentials.
    For LAN use, role-based access is sufficient.
    """
    try:
        user_role = Role(role)
    except ValueError:
        user_role = Role.OBSERVER

    token = create_token(username, user_role)
    return {"access_token": token, "token_type": "bearer", "role": user_role.value}


@router.get("/auth/me")
async def me(token: TokenPayload = Depends(verify_token)):
    """Get current user info from token."""
    return {"username": token.sub, "role": token.role}


# ── Sessions ──────────────────────────────────────────────────────────


@router.get("/sessions")
async def list_sessions(token: TokenPayload = Depends(require_permission("session:read"))):
    """List all recorded sessions."""
    from app.core.database import get_db

    db = await get_db()
    cursor = await db.execute("SELECT * FROM sessions ORDER BY started_at DESC")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str, token: TokenPayload = Depends(require_permission("session:read"))
):
    """Get details of a specific session."""
    from app.core.database import get_db

    db = await get_db()
    cursor = await db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = await cursor.fetchone()
    if not row:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Session not found")
    return dict(row)


@router.get("/sessions/{session_id}/laps")
async def get_session_laps(
    session_id: str, token: TokenPayload = Depends(require_permission("session:read"))
):
    """Get all laps for a session."""
    from app.core.database import get_db

    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM laps WHERE session_id = ? ORDER BY lap_number", (session_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


# ── Strategy ──────────────────────────────────────────────────────────


@router.post("/strategy/pit-window")
async def compute_pit_window(
    strategy: PitStrategy,
    token: TokenPayload = Depends(require_permission("strategy:read")),
):
    """Calculate the optimal pit window."""
    return calculate_pit_window(strategy)


@router.post("/strategy/undercut")
async def compute_undercut(
    strategy: PitStrategy,
    gap_ahead: float = 1.5,
    token: TokenPayload = Depends(require_permission("strategy:read")),
):
    """Simulate an undercut scenario."""
    return simulate_undercut(strategy, gap_ahead)


# ── Health ────────────────────────────────────────────────────────────


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "pitwall"}
