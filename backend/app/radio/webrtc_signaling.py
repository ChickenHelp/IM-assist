"""WebRTC signaling server for radio and screen sharing.

This module manages WebRTC peer connections for:
1. Audio radio (push-to-talk) between pilot and manager
2. Screen sharing from pilot PC to manager

In a LAN environment, STUN/TURN servers are not needed — peers connect
directly via local IP addresses.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import StrEnum

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ChannelType(StrEnum):
    RADIO = "radio"
    SCREEN = "screen"


@dataclass
class Peer:
    """A connected WebRTC peer."""
    ws: WebSocket
    username: str
    channel: ChannelType
    role: str = "observer"


@dataclass
class SignalingRoom:
    """A room for WebRTC signaling between peers."""
    channel: ChannelType
    peers: dict[str, Peer] = field(default_factory=dict)

    async def broadcast(self, message: str, exclude: str | None = None) -> None:
        """Send a message to all peers except the sender."""
        dead = []
        for username, peer in self.peers.items():
            if username == exclude:
                continue
            try:
                await peer.ws.send_text(message)
            except Exception:
                dead.append(username)
        for username in dead:
            self.peers.pop(username, None)


class SignalingServer:
    """Manages WebRTC signaling rooms for radio and screen sharing."""

    def __init__(self) -> None:
        self.rooms: dict[ChannelType, SignalingRoom] = {
            ChannelType.RADIO: SignalingRoom(channel=ChannelType.RADIO),
            ChannelType.SCREEN: SignalingRoom(channel=ChannelType.SCREEN),
        }

    async def handle_peer(self, ws: WebSocket, username: str, channel: ChannelType) -> None:
        """Handle a WebRTC signaling connection.

        Protocol messages (JSON):
            {"type": "offer", "sdp": "..."}      — SDP offer
            {"type": "answer", "sdp": "..."}     — SDP answer
            {"type": "candidate", "candidate": "...", "sdpMLineIndex": 0}  — ICE candidate
            {"type": "join"}                      — Announce presence
            {"type": "leave"}                     — Disconnect
        """
        room = self.rooms[channel]
        peer = Peer(ws=ws, username=username, channel=channel)
        room.peers[username] = peer

        # Notify others
        await room.broadcast(
            json.dumps({"type": "peer_joined", "username": username}),
            exclude=username,
        )

        logger.info("Peer %s joined %s room (%d peers)", username, channel, len(room.peers))

        try:
            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                msg["from"] = username

                # Forward signaling messages to other peers
                await room.broadcast(json.dumps(msg), exclude=username)

        except Exception:
            pass
        finally:
            room.peers.pop(username, None)
            await room.broadcast(
                json.dumps({"type": "peer_left", "username": username}),
                exclude=username,
            )
            logger.info("Peer %s left %s room", username, channel)


# Global signaling server instance
signaling = SignalingServer()
