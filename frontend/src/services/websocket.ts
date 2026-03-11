/**
 * WebSocket service for real-time telemetry streaming.
 *
 * Handles connection, reconnection with exponential backoff,
 * and dispatches messages to the Zustand store.
 */

import { useTelemetryStore } from '../store/telemetryStore';
import type { WSMessage } from '../types/telemetry';

const MAX_RECONNECT_DELAY = 10000;
const INITIAL_RECONNECT_DELAY = 500;

class TelemetryWebSocket {
  private ws: WebSocket | null = null;
  private reconnectDelay = INITIAL_RECONNECT_DELAY;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private url: string;
  private shouldReconnect = true;

  constructor(url: string) {
    this.url = url;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);
    const store = useTelemetryStore.getState();

    this.ws.onopen = () => {
      console.log('[PitWall] WebSocket connected');
      store.setConnected(true);
      this.reconnectDelay = INITIAL_RECONNECT_DELAY;
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const msg: WSMessage & { alerts?: Array<{ type: string; severity: string; message: string }> } =
          JSON.parse(event.data);
        const store = useTelemetryStore.getState();

        switch (msg.type) {
          case 'telemetry':
            store.setFrame(msg.data);
            if (msg.session_id && !store.sessionId) {
              store.setSessionId(msg.session_id);
            }
            // Handle AI alerts
            if (msg.alerts && msg.alerts.length > 0) {
              store.setAlerts(
                msg.alerts.map((a) => ({
                  type: a.type,
                  severity: a.severity as 'info' | 'warning' | 'critical',
                  message: a.message,
                })),
              );
            }
            break;
          case 'standings':
            store.setStandings(msg.entries, msg.positions);
            break;
        }
      } catch (err) {
        console.warn('[PitWall] Failed to parse WS message:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('[PitWall] WebSocket disconnected');
      store.setConnected(false);
      this.scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('[PitWall] WebSocket error:', err);
      this.ws?.close();
    };
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    this.ws?.close();
  }

  private scheduleReconnect(): void {
    if (!this.shouldReconnect) return;

    this.reconnectTimer = setTimeout(() => {
      console.log(`[PitWall] Reconnecting (delay: ${this.reconnectDelay}ms)...`);
      this.connect();
    }, this.reconnectDelay);

    this.reconnectDelay = Math.min(this.reconnectDelay * 2, MAX_RECONNECT_DELAY);
  }

  send(data: object): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

// Default instance — connects to the server on the same host
export function createTelemetryWS(host?: string): TelemetryWebSocket {
  const wsHost = host || import.meta.env.VITE_BACKEND_HOST || window.location.hostname;
  const url = `ws://${wsHost}:8400/ws/telemetry`;
  return new TelemetryWebSocket(url);
}
