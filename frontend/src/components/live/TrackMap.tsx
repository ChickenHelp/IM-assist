/**
 * Track Map — SVG-based oval track visualization.
 *
 * Shows driver positions as colored dots on a simplified track layout.
 * The track shape is an oval for MVP; can be replaced with real track
 * SVG paths from iRacing track data later.
 */

import type { DriverPosition } from '../../types/telemetry';

interface TrackMapProps {
  positions: DriverPosition[];
}

function lapPctToXY(pct: number, cx: number, cy: number, rx: number, ry: number) {
  const angle = pct * 2 * Math.PI - Math.PI / 2;
  return {
    x: cx + rx * Math.cos(angle),
    y: cy + ry * Math.sin(angle),
  };
}

export function TrackMap({ positions }: TrackMapProps) {
  const width = 300;
  const height = 200;
  const cx = width / 2;
  const cy = height / 2;
  const rx = 120;
  const ry = 70;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full">
      {/* Track outline */}
      <ellipse
        cx={cx}
        cy={cy}
        rx={rx}
        ry={ry}
        fill="none"
        stroke="#2A2A3E"
        strokeWidth={16}
        strokeLinecap="round"
      />
      <ellipse
        cx={cx}
        cy={cy}
        rx={rx}
        ry={ry}
        fill="none"
        stroke="#1E1E2E"
        strokeWidth={14}
        strokeLinecap="round"
      />

      {/* Start/finish line */}
      <line
        x1={cx}
        y1={cy - ry - 10}
        x2={cx}
        y2={cy - ry + 10}
        stroke="#48484A"
        strokeWidth={2}
        strokeDasharray="3 2"
      />

      {/* Driver positions */}
      {positions.map((driver) => {
        const { x, y } = lapPctToXY(driver.lap_pct, cx, cy, rx, ry);
        const color = driver.is_player ? '#E10600' : driver.class_color;
        const radius = driver.is_player ? 6 : 4;

        return (
          <g key={driver.car_idx}>
            {driver.is_player && (
              <circle cx={x} cy={y} r={10} fill={color} opacity={0.2} />
            )}
            <circle cx={x} cy={y} r={radius} fill={color} />
            <text
              x={x}
              y={y - 10}
              textAnchor="middle"
              fill="#86868B"
              fontSize={8}
              fontFamily="monospace"
            >
              P{driver.position}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
