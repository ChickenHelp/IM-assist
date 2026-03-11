"""WebSocket endpoints for real-time telemetry and radio signaling."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.radio.webrtc_signaling import ChannelType, signaling

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

    Query params:
        username: The display name of the connecting peer.
    """
    await ws.accept()

    username = ws.query_params.get("username", "anonymous")
    logger.info("Radio peer connected: %s", username)

    await signaling.handle_peer(ws, username, ChannelType.RADIO)


@router.websocket("/ws/screen")
async def screen_signaling_ws(ws: WebSocket):
    """WebSocket for WebRTC screen sharing signaling.

    Query params:
        username: The display name of the connecting peer.
    """
    await ws.accept()

    username = ws.query_params.get("username", "anonymous")
    logger.info("Screen share peer connected: %s", username)

    await signaling.handle_peer(ws, username, ChannelType.SCREEN)
