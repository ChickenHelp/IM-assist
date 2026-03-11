/**
 * React hook for telemetry WebSocket connection.
 * Manages the lifecycle of the WebSocket connection.
 */

import { useEffect, useRef } from 'react';
import { createTelemetryWS } from '../services/websocket';

export function useTelemetryConnection(host?: string) {
  const wsRef = useRef<ReturnType<typeof createTelemetryWS> | null>(null);

  useEffect(() => {
    const ws = createTelemetryWS(host);
    wsRef.current = ws;
    ws.connect();

    return () => {
      ws.disconnect();
    };
  }, [host]);

  return wsRef;
}
