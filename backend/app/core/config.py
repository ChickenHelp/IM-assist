"""Application configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """PitWall configuration — loaded from environment or .env file."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8400
    debug: bool = False

    # Security
    secret_key: str = Field(default="pitwall-dev-secret-change-in-production")
    token_expiry_hours: int = 24

    # Telemetry
    telemetry_hz: int = 30
    telemetry_buffer_size: int = 18000  # 10 min at 30 Hz

    # Database
    db_path: str = "pitwall.db"

    # LAN — "*" allows any origin (safe for LAN-only use)
    allowed_origins: list[str] = ["*"]
    lan_subnet: str = "192.168.0.0/16"

    # WebRTC
    webrtc_enabled: bool = True

    model_config = {"env_prefix": "PITWALL_", "env_file": ".env"}


settings = Settings()
