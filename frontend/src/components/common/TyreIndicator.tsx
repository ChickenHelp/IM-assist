/**
 * Tyre temperature and wear indicator.
 * Shows a car outline with colour-coded tyre states.
 */

import type { TyreData } from '../../types/telemetry';

interface TyreIndicatorProps {
  tyres: TyreData;
}

function tyreColor(temp: number): string {
  if (temp > 115) return '#FF3B30'; // Critical
  if (temp > 105) return '#FF9500'; // Hot
  if (temp > 85) return '#00D26A';  // Optimal
  if (temp > 60) return '#0A84FF';  // Cold
  return '#5E5CE6';                  // Very cold
}

function wearLabel(wear: number): string {
  const pct = Math.round((1 - wear) * 100);
  return `${pct}%`;
}

export function TyreIndicator({ tyres }: TyreIndicatorProps) {
  const corners = [
    { key: 'FL', temp: tyres.temp.fl, wear: tyres.wear.fl, x: 0, y: 0 },
    { key: 'FR', temp: tyres.temp.fr, wear: tyres.wear.fr, x: 1, y: 0 },
    { key: 'RL', temp: tyres.temp.rl, wear: tyres.wear.rl, x: 0, y: 1 },
    { key: 'RR', temp: tyres.temp.rr, wear: tyres.wear.rr, x: 1, y: 1 },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 max-w-[200px]">
      {corners.map((c) => (
        <div
          key={c.key}
          className="rounded-lg p-3 text-center border border-pitwall-border"
          style={{ backgroundColor: `${tyreColor(c.temp)}15` }}
        >
          <div className="text-xs text-pitwall-text-dim mb-1">{c.key}</div>
          <div className="font-mono text-sm font-bold" style={{ color: tyreColor(c.temp) }}>
            {Math.round(c.temp)}°
          </div>
          <div className="text-xs text-pitwall-text-dim mt-1">{wearLabel(c.wear)}</div>
        </div>
      ))}
    </div>
  );
}
