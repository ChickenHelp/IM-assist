/**
 * Zustand store for telemetry state.
 * Single source of truth for all real-time race data.
 */

import { create } from 'zustand';
import type {
  TelemetryFrame,
  StandingsEntry,
  DriverPosition,
} from '../types/telemetry';

export interface AIAlert {
  type: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
}

interface TelemetryState {
  /** Current telemetry frame. */
  frame: TelemetryFrame | null;
  /** Race standings. */
  standings: StandingsEntry[];
  /** Driver positions on track. */
  positions: DriverPosition[];
  /** Connection status. */
  connected: boolean;
  /** Session ID. */
  sessionId: string | null;
  /** History of recent frames for charts (last 300 = 10s at 30Hz). */
  history: TelemetryFrame[];
  /** Current AI alerts. */
  alerts: AIAlert[];

  // Actions
  setFrame: (frame: TelemetryFrame) => void;
  setStandings: (entries: StandingsEntry[], positions: DriverPosition[]) => void;
  setConnected: (connected: boolean) => void;
  setSessionId: (id: string) => void;
  setAlerts: (alerts: AIAlert[]) => void;
}

const HISTORY_SIZE = 300;

export const useTelemetryStore = create<TelemetryState>((set) => ({
  frame: null,
  standings: [],
  positions: [],
  connected: false,
  sessionId: null,
  history: [],
  alerts: [],

  setFrame: (frame) =>
    set((state) => {
      const history = [...state.history, frame];
      if (history.length > HISTORY_SIZE) {
        history.splice(0, history.length - HISTORY_SIZE);
      }
      return { frame, history };
    }),

  setStandings: (entries, positions) => set({ standings: entries, positions }),
  setConnected: (connected) => set({ connected }),
  setSessionId: (sessionId) => set({ sessionId }),
  setAlerts: (alerts) => set({ alerts }),
}));
