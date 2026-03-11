/**
 * Circular gauge component for speed, RPM, fuel, etc.
 * SVG-based ring gauge with animated fill.
 */

interface GaugeRingProps {
  value: number;
  max: number;
  label: string;
  unit?: string;
  size?: number;
  color?: string;
  warningThreshold?: number;
  criticalThreshold?: number;
}

export function GaugeRing({
  value,
  max,
  label,
  unit = '',
  size = 120,
  color = '#E10600',
  warningThreshold,
  criticalThreshold,
}: GaugeRingProps) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct);

  // Dynamic color based on thresholds
  let activeColor = color;
  if (criticalThreshold && value >= criticalThreshold) {
    activeColor = '#FF3B30';
  } else if (warningThreshold && value >= warningThreshold) {
    activeColor = '#FFD60A';
  }

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1E1E2E"
          strokeWidth={6}
        />
        {/* Value ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={activeColor}
          strokeWidth={6}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="gauge-ring"
          strokeLinecap="round"
        />
      </svg>
      {/* Center label */}
      <div className="absolute flex flex-col items-center justify-center" style={{ width: size, height: size }}>
        <span className="font-mono text-xl font-bold">{Math.round(value)}</span>
        <span className="text-xs text-pitwall-text-dim">{unit}</span>
      </div>
      <span className="text-xs text-pitwall-text-dim mt-1">{label}</span>
    </div>
  );
}
