/**
 * Live race standings table.
 */

import type { StandingsEntry } from '../../types/telemetry';

interface StandingsProps {
  entries: StandingsEntry[];
}

export function Standings({ entries }: StandingsProps) {
  if (entries.length === 0) {
    return <p className="text-pitwall-text-dim text-sm">No standings data</p>;
  }

  return (
    <div className="overflow-auto max-h-64">
      <table className="w-full text-xs">
        <thead>
          <tr className="text-pitwall-text-dim border-b border-pitwall-border">
            <th className="py-1 text-left w-8">P</th>
            <th className="py-1 text-left">#</th>
            <th className="py-1 text-left">Driver</th>
            <th className="py-1 text-right">Last</th>
            <th className="py-1 text-right">Best</th>
            <th className="py-1 text-right">Int</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr
              key={entry.car_idx}
              className={`border-b border-pitwall-border/30 ${
                entry.driver_name === 'You' ? 'bg-pitwall-accent/10' : ''
              }`}
            >
              <td className="py-1.5 font-mono font-bold">{entry.position}</td>
              <td className="py-1.5 font-mono text-pitwall-text-dim">{entry.car_number}</td>
              <td className="py-1.5">
                <span className={entry.in_pit ? 'text-pitwall-yellow' : ''}>
                  {entry.driver_name}
                </span>
                {entry.in_pit && (
                  <span className="ml-1 text-pitwall-yellow text-[10px]">PIT</span>
                )}
              </td>
              <td className="py-1.5 font-mono text-right">
                {entry.last_lap ? entry.last_lap.toFixed(3) : '-'}
              </td>
              <td className="py-1.5 font-mono text-right text-pitwall-purple">
                {entry.best_lap ? entry.best_lap.toFixed(3) : '-'}
              </td>
              <td className="py-1.5 font-mono text-right">
                {entry.interval !== null ? `+${entry.interval.toFixed(3)}` : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
