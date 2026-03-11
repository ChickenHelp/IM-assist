"""PitWall Backend — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.report_routes import router as report_router
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.core.config import settings
from app.core.database import init_db, close_db
from app.services.telemetry_service import TelemetryService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    await init_db()
    telemetry_service = TelemetryService()
    app.state.telemetry_service = telemetry_service
    telemetry_service.start()

    yield

    # Shutdown
    telemetry_service.stop()
    await close_db()


app = FastAPI(
    title="PitWall",
    description="iRacing Race Engineer — Real-time telemetry and race management",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow LAN connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(report_router, prefix="/api/v1")
app.include_router(ws_router)
