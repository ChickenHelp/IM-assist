/**
 * Tab 3 — Performance
 *
 * Features:
 * - Throttle / Brake trace chart
 * - Sector delta comparison
 * - Lap comparison
 * - Braking heatmap (placeholder)
 * - Grip loss analysis
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Area,
  AreaChart,
  Tooltip,
} from 'recharts';
import { useTelemetryStore } from '../../store/telemetryStore';
import { DataCard } from '../common/DataCard';

export function Performance() {
  const history = useTelemetryStore((s) => s.history);
  const frame = useTelemetryStore((s) => s.frame);

  // Prepare chart data from history (downsample to ~100 points)
  const step = Math.max(1, Math.floor(history.length / 100));
  const chartData = history
    .filter((_, i) => i % step === 0)
    .map((f, i) => ({
      idx: i,
      throttle: Math.round(f.throttle * 100),
      brake: Math.round(f.brake * 100),
      speed: Math.round(f.speed),
      steering: Math.round(f.steering * 100),
    }));

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* Throttle / Brake trace */}
      <div className="col-span-8">
        <DataCard title="Throttle & Brake Trace">
          <div className="h-64">
            {chartData.length > 2 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="throttleGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#00D26A" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#00D26A" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="brakeGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#E10600" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#E10600" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                  <XAxis dataKey="idx" hide />
                  <YAxis domain={[0, 100]} stroke="#48484A" fontSize={10} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121A',
                      border: '1px solid #1E1E2E',
                      borderRadius: '8px',
                      fontSize: 12,
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="throttle"
                    stroke="#00D26A"
                    fill="url(#throttleGrad)"
                    strokeWidth={1.5}
                    dot={false}
                    name="Throttle %"
                  />
                  <Area
                    type="monotone"
                    dataKey="brake"
                    stroke="#E10600"
                    fill="url(#brakeGrad)"
                    strokeWidth={1.5}
                    dot={false}
                    name="Brake %"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-pitwall-text-dim text-sm">
                Collecting data...
              </div>
            )}
          </div>
        </DataCard>
      </div>

      {/* Speed trace */}
      <div className="col-span-4">
        <DataCard title="Speed Trace">
          <div className="h-64">
            {chartData.length > 2 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                  <XAxis dataKey="idx" hide />
                  <YAxis stroke="#48484A" fontSize={10} />
                  <Line
                    type="monotone"
                    dataKey="speed"
                    stroke="#0A84FF"
                    strokeWidth={1.5}
                    dot={false}
                    name="Speed (km/h)"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-pitwall-text-dim text-sm">
                Collecting data...
              </div>
            )}
          </div>
        </DataCard>
      </div>

      {/* Sector Analysis */}
      <div className="col-span-6">
        <DataCard title="Sector Analysis">
          {frame?.sectors && frame.sectors.length > 0 ? (
            <div className="space-y-3">
              {frame.sectors.map((time, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-xs text-pitwall-text-dim w-12">S{i + 1}</span>
                  <div className="flex-1 h-8 bg-pitwall-bg rounded overflow-hidden flex items-center">
                    <div
                      className="h-full bg-pitwall-purple/30 flex items-center px-2"
                      style={{ width: `${Math.min((time / 40) * 100, 100)}%` }}
                    >
                      <span className="font-mono text-xs">{time.toFixed(3)}s</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-pitwall-text-dim">Waiting for sector data...</p>
          )}
        </DataCard>
      </div>

      {/* Grip Analysis */}
      <div className="col-span-6">
        <DataCard title="Grip Analysis">
          {frame ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'FL', wear: frame.tyres.wear.fl, temp: frame.tyres.temp.fl },
                  { label: 'FR', wear: frame.tyres.wear.fr, temp: frame.tyres.temp.fr },
                  { label: 'RL', wear: frame.tyres.wear.rl, temp: frame.tyres.temp.rl },
                  { label: 'RR', wear: frame.tyres.wear.rr, temp: frame.tyres.temp.rr },
                ].map((tyre) => {
                  const gripPct = Math.max(0, (1 - tyre.wear) * 100);
                  const gripColor =
                    gripPct > 60 ? '#00D26A' : gripPct > 30 ? '#FFD60A' : '#E10600';
                  return (
                    <div key={tyre.label} className="bg-pitwall-bg rounded-lg p-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-pitwall-text-dim">{tyre.label}</span>
                        <span className="font-mono" style={{ color: gripColor }}>
                          {gripPct.toFixed(0)}%
                        </span>
                      </div>
                      <div className="h-1.5 bg-pitwall-border rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{ width: `${gripPct}%`, backgroundColor: gripColor }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="text-xs text-pitwall-text-dim mt-2">
                {frame.lap.delta > 0.3
                  ? 'Possible grip loss detected — lap times degrading'
                  : 'Grip levels nominal'}
              </div>
            </div>
          ) : (
            <p className="text-sm text-pitwall-text-dim">Waiting for data...</p>
          )}
        </DataCard>
      </div>

      {/* Steering trace */}
      <div className="col-span-12">
        <DataCard title="Steering Input">
          <div className="h-32">
            {chartData.length > 2 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                  <XAxis dataKey="idx" hide />
                  <YAxis domain={[-100, 100]} stroke="#48484A" fontSize={10} />
                  <Line
                    type="monotone"
                    dataKey="steering"
                    stroke="#BF5AF2"
                    strokeWidth={1}
                    dot={false}
                    name="Steering %"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-pitwall-text-dim text-sm">
                Collecting data...
              </div>
            )}
          </div>
        </DataCard>
      </div>
    </div>
  );
}
