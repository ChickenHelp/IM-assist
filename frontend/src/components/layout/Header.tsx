import { useTelemetryStore } from '../../store/telemetryStore';

interface HeaderProps {
  connected: boolean;
}

export function Header({ connected }: HeaderProps) {
  const frame = useTelemetryStore((s) => s.frame);

  return (
    <header className="flex items-center justify-between px-6 py-3 bg-pitwall-surface border-b border-pitwall-border">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-pitwall-accent flex items-center justify-center font-bold text-sm">
          PW
        </div>
        <div>
          <h1 className="text-lg font-semibold tracking-tight">PitWall</h1>
          <p className="text-xs text-pitwall-text-dim">Race Engineer Console</p>
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center gap-6 text-sm">
        {frame && (
          <>
            <div className="flex items-center gap-2">
              <span className="text-pitwall-text-dim">P</span>
              <span className="font-mono font-bold text-lg">{frame.position}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-pitwall-text-dim">Lap</span>
              <span className="font-mono">{frame.lap.current}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-pitwall-text-dim">INC</span>
              <span className={`font-mono ${frame.incidents > 0 ? 'text-pitwall-yellow' : ''}`}>
                {frame.incidents}
              </span>
            </div>
          </>
        )}

        {/* Connection indicator */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              connected ? 'bg-pitwall-green animate-pulse-slow' : 'bg-red-500'
            }`}
          />
          <span className="text-pitwall-text-dim text-xs">
            {connected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>
      </div>
    </header>
  );
}
