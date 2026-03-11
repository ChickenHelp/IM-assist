/**
 * Formatting utilities for telemetry display.
 */

/** Format lap time from seconds to M:SS.mmm */
export function formatLapTime(seconds: number | null | undefined): string {
  if (seconds == null || seconds <= 0) return '--:--.---';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toFixed(3).padStart(6, '0')}`;
}

/** Format a delta time with +/- sign */
export function formatDelta(delta: number): string {
  const sign = delta >= 0 ? '+' : '';
  return `${sign}${delta.toFixed(3)}`;
}

/** Format fuel level */
export function formatFuel(liters: number): string {
  return `${liters.toFixed(1)}L`;
}

/** Format percentage 0-1 to display */
export function formatPct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

/** Format temperature */
export function formatTemp(celsius: number): string {
  return `${celsius.toFixed(1)}°C`;
}
