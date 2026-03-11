/** Telemetry data types matching the backend models. */

export interface TyreTemps {
  fl: number;
  fr: number;
  rl: number;
  rr: number;
}

export interface TyreWear {
  fl: number;
  fr: number;
  rl: number;
  rr: number;
}

export interface TyreData {
  temp: TyreTemps;
  wear: TyreWear;
}

export interface LapData {
  current: number;
  best: number | null;
  delta: number;
}

export interface IntervalData {
  ahead: number | null;
  behind: number | null;
}

export interface ConditionsData {
  track_temp: number;
  air_temp: number;
}

export interface FlagData {
  yellow: boolean;
  blue: boolean;
  black: boolean;
}

export interface TelemetryFrame {
  speed: number;
  rpm: number;
  gear: number;
  throttle: number;
  brake: number;
  steering: number;
  fuel_level: number;
  fuel_per_lap: number;
  tyres: TyreData;
  lap: LapData;
  sectors: number[];
  position: number;
  interval: IntervalData;
  incidents: number;
  conditions: ConditionsData;
  flags: FlagData;
}

export interface TelemetryMessage {
  type: 'telemetry';
  timestamp: number;
  session_id: string;
  data: TelemetryFrame;
}

export interface DriverPosition {
  car_idx: number;
  driver_name: string;
  position: number;
  lap_pct: number;
  is_player: boolean;
  class_color: string;
}

export interface StandingsEntry {
  position: number;
  car_idx: number;
  driver_name: string;
  car_number: string;
  lap: number;
  last_lap: number | null;
  best_lap: number | null;
  gap_to_leader: number | null;
  interval: number | null;
  incidents: number;
  in_pit: boolean;
  class_color: string;
}

export interface StandingsMessage {
  type: 'standings';
  timestamp: number;
  session_id: string;
  entries: StandingsEntry[];
  positions: DriverPosition[];
}

export type WSMessage = TelemetryMessage | StandingsMessage;
