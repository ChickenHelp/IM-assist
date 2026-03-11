/**
 * Fuel level bar with laps remaining estimate.
 */

interface FuelBarProps {
  level: number;
  maxFuel?: number;
  perLap: number;
}

export function FuelBar({ level, maxFuel = 110, perLap }: FuelBarProps) {
  const pct = Math.min(level / maxFuel, 1);
  const lapsRemaining = perLap > 0 ? level / perLap : Infinity;
  const isLow = lapsRemaining < 3;
  const isCritical = lapsRemaining < 1.5;

  const barColor = isCritical
    ? 'bg-red-500'
    : isLow
      ? 'bg-pitwall-yellow'
      : 'bg-pitwall-green';

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs">
        <span className="text-pitwall-text-dim">Fuel</span>
        <span className="font-mono">
          {level.toFixed(1)}L
          <span className="text-pitwall-text-dim ml-2">
            ({lapsRemaining === Infinity ? '--' : lapsRemaining.toFixed(1)} laps)
          </span>
        </span>
      </div>
      <div className="h-2 bg-pitwall-border rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-200 ${barColor}`}
          style={{ width: `${pct * 100}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-pitwall-text-dim">
        <span>{perLap.toFixed(2)} L/lap</span>
        {isCritical && <span className="text-red-500 font-bold animate-pulse">FUEL CRITICAL</span>}
      </div>
    </div>
  );
}
