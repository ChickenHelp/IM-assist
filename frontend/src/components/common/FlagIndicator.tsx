/**
 * Race flag indicator — shows active flags with appropriate styling.
 */

import type { FlagData } from '../../types/telemetry';

interface FlagIndicatorProps {
  flags: FlagData;
}

export function FlagIndicator({ flags }: FlagIndicatorProps) {
  if (!flags.yellow && !flags.blue && !flags.black) {
    return (
      <div className="flex items-center gap-2 text-xs text-pitwall-text-dim">
        <div className="w-3 h-3 rounded bg-pitwall-green" />
        <span>GREEN</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      {flags.yellow && (
        <div className="flex items-center gap-2 text-pitwall-yellow animate-pulse">
          <div className="w-4 h-4 rounded bg-pitwall-yellow" />
          <span className="text-xs font-bold">YELLOW</span>
        </div>
      )}
      {flags.blue && (
        <div className="flex items-center gap-2 text-pitwall-blue">
          <div className="w-4 h-4 rounded bg-pitwall-blue" />
          <span className="text-xs font-bold">BLUE</span>
        </div>
      )}
      {flags.black && (
        <div className="flex items-center gap-2 text-white">
          <div className="w-4 h-4 rounded bg-black border border-white" />
          <span className="text-xs font-bold">BLACK</span>
        </div>
      )}
    </div>
  );
}
