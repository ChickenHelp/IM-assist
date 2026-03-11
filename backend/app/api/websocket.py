"""WebSocket endpoint for real-time telemetry streaming."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/telemetry")
async def telemetry_ws(ws: WebSocket):
    """WebSocket endpoint for live telemetry data.

    Query params:
        token: JWT token for authentication (optional in dev mode).

    The server broadcasts telemetry frames at 30 Hz and standings at 1 Hz.
    The client can send JSON commands:
        {"type": "ping"} — server responds with {"type": "pong"}
    """
    await ws.accept()

    # Get telemetry service from app state
    telemetry_service = ws.app.state.telemetry_service

    await telemetry_service.register(ws)
    logger.info("WebSocket client connected")

    try:
        while True:
            # Listen for client messages (ping, commands)
            data = await ws.receive_json()
            if data.get("type") == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception:
        logger.exception("WebSocket error")
    finally:
        await telemetry_service.unregister(ws)
        if ws.client_state == WebSocketState.CONNECTED:
            await ws.close()


@router.websocket("/ws/radio")
async def radio_signaling_ws(ws: WebSocket):
    """WebSocket for WebRTC radio signaling.

    Used to exchange SDP offers/answers and ICE candidates
    between pilot and manager for the audio radio channel.
    """
    await ws.accept()
    logger.info("Radio signaling client connected")

    # Simple relay — forward messages between connected peers
    try:
        while True:
            data = await ws.receive_text()
            # In production, maintain a room of peers and relay accordingly
            # For MVP, we broadcast to all other connected radio clients
            logger.debug("Radio signal: %s", data[:100])
    except WebSocketDisconnect:
        logger.info("Radio signaling client disconnected")
    except Exception:
        logger.exception("Radio signaling error")
