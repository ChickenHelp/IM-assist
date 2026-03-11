"""JWT authentication and role-based access control."""

from datetime import datetime, timedelta, timezone
from enum import StrEnum

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

security = HTTPBearer()


class Role(StrEnum):
    PILOT = "pilot"
    MANAGER = "manager"
    STRATEGIST = "strategist"
    OBSERVER = "observer"


# Permissions per role
ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.PILOT: {"telemetry:read", "radio:use", "session:read"},
    Role.MANAGER: {
        "telemetry:read",
        "strategy:read",
        "strategy:write",
        "radio:use",
        "session:read",
        "session:write",
        "analysis:read",
    },
    Role.STRATEGIST: {
        "telemetry:read",
        "strategy:read",
        "strategy:write",
        "session:read",
        "analysis:read",
    },
    Role.OBSERVER: {"telemetry:read", "session:read"},
}


class TokenPayload(BaseModel):
    sub: str
    role: Role
    exp: datetime


def create_token(username: str, role: Role) -> str:
    """Create a JWT token for the given user and role."""
    payload = {
        "sub": username,
        "role": role.value,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.token_expiry_hours),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenPayload:
    """Verify JWT token from Authorization header."""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        return TokenPayload(
            sub=payload["sub"],
            role=Role(payload["role"]),
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except (JWTError, KeyError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )


def require_permission(permission: str):
    """Dependency that checks if the current user has a specific permission."""

    def checker(token: TokenPayload = Depends(verify_token)) -> TokenPayload:
        if permission not in ROLE_PERMISSIONS.get(token.role, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{token.role}' lacks permission '{permission}'",
            )
        return token

    return checker
