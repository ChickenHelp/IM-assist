/**
 * Tab 1 — Live Race
 *
 * Displays:
 * - Track map with driver positions
 * - Live standings table
 * - Gauges (speed, RPM, gear)
 * - Tyre indicator
 * - Fuel bar
 * - Flag indicator
 * - AI alerts
 */

import { useTelemetryStore } from '../../store/telemetryStore';
import { DataCard } from '../common/DataCard';
import { GaugeRing } from '../common/GaugeRing';
import { TyreIndicator } from '../common/TyreIndicator';
import { FuelBar } from '../common/FuelBar';
import { FlagIndicator } from '../common/FlagIndicator';
import { TrackMap } from './TrackMap';
import { Standings } from './Standings';

export function LiveRace() {
  const frame = useTelemetryStore((s) => s.frame);
  const standings = useTelemetryStore((s) => s.standings);
  const positions = useTelemetryStore((s) => s.positions);
  const alerts = useTelemetryStore((s) => s.alerts);

  if (!frame) {
    return (
      <div className="flex items-center justify-center h-96 text-pitwall-text-dim">
        <div className="text-center">
          <div className="text-4xl mb-4 opacity-20">PW</div>
          <p>Waiting for telemetry data...</p>
          <p className="text-xs mt-2">Connect to the PitWall server on the pilot's PC</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* Left column — Track map + Standings */}
      <div className="col-span-5 space-y-4">
        <DataCard title="Track Map">
          <TrackMap positions={positions} />
        </DataCard>
        <DataCard title="Standings">
          <Standings entries={standings} />
        </DataCard>
      </div>

      {/* Center column — Main telemetry */}
      <div className="col-span-4 space-y-4">
        {/* Speed + RPM gauges + Gear */}
        <DataCard title="Telemetry">
          <div className="flex items-center justify-around">
            <GaugeRing
              value={frame.speed}
              max={350}
              label="Speed"
              unit="km/h"
              size={110}
              color="#30D158"
              warningThreshold={280}
              criticalThreshold={320}
            />
            {/* Gear */}
            <div className="text-center">
              <div
                className="font-mono text-6xl font-black"
                style={{ color: frame.gear === 0 ? '#FFD60A' : '#F5F5F7' }}
              >
                {frame.gear === -1 ? 'R' : frame.gear === 0 ? 'N' : frame.gear}
              </div>
              <div className="text-xs text-pitwall-text-dim">Gear</div>
            </div>
            <GaugeRing
              value={frame.rpm}
              max={12000}
              label="RPM"
              unit="rpm"
              size={110}
              color="#E10600"
              warningThreshold={9000}
              criticalThreshold={10500}
            />
          </div>

          {/* Throttle / Brake bars */}
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-3">
              <span className="text-xs text-pitwall-text-dim w-10">THR</span>
              <div className="flex-1 h-3 bg-pitwall-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-pitwall-green rounded-full transition-all duration-75"
                  style={{ width: `${frame.throttle * 100}%` }}
                />
              </div>
              <span className="font-mono text-xs w-10 text-right">
                {Math.round(frame.throttle * 100)}%
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-pitwall-text-dim w-10">BRK</span>
              <div className="flex-1 h-3 bg-pitwall-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-pitwall-accent rounded-full transition-all duration-75"
                  style={{ width: `${frame.brake * 100}%` }}
                />
              </div>
              <span className="font-mono text-xs w-10 text-right">
                {Math.round(frame.brake * 100)}%
              </span>
            </div>
          </div>
        </DataCard>

        {/* Lap delta */}
        <DataCard title="Lap Time">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-pitwall-text-dim">Current Lap</div>
              <div className="font-mono text-lg">{frame.lap.current}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-pitwall-text-dim">Delta</div>
              <div
                className={`font-mono text-2xl font-bold ${
                  frame.lap.delta < 0 ? 'text-pitwall-green' : 'text-pitwall-accent'
                }`}
              >
                {frame.lap.delta >= 0 ? '+' : ''}{frame.lap.delta.toFixed(3)}
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs text-pitwall-text-dim">Best</div>
              <div className="font-mono text-lg text-pitwall-purple">
                {frame.lap.best ? frame.lap.best.toFixed(3) : '--.--.---'}
              </div>
            </div>
          </div>
        </DataCard>

        {/* Intervals */}
        <DataCard title="Intervals">
          <div className="flex justify-between">
            <div>
              <div className="text-xs text-pitwall-text-dim">Gap Ahead</div>
              <div className="font-mono text-lg">
                {frame.interval.ahead !== null ? `+${frame.interval.ahead.toFixed(3)}` : '---'}
              </div>
            </div>
            <div className="text-center font-mono text-3xl font-black text-pitwall-accent">
              P{frame.position}
            </div>
            <div className="text-right">
              <div className="text-xs text-pitwall-text-dim">Gap Behind</div>
              <div className="font-mono text-lg">
                {frame.interval.behind !== null ? `+${frame.interval.behind.toFixed(3)}` : '---'}
              </div>
            </div>
          </div>
        </DataCard>
      </div>

      {/* Right column — Tyres, Fuel, Conditions, Alerts */}
      <div className="col-span-3 space-y-4">
        <DataCard title="Tyres">
          <TyreIndicator tyres={frame.tyres} />
        </DataCard>

        <DataCard title="Fuel">
          <FuelBar
            level={frame.fuel_level}
            perLap={frame.fuel_per_lap}
          />
        </DataCard>

        <DataCard title="Flags">
          <FlagIndicator flags={frame.flags} />
        </DataCard>

        <DataCard title="Conditions">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-pitwall-text-dim">Track</span>
              <span className="font-mono">{frame.conditions.track_temp.toFixed(1)}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-pitwall-text-dim">Air</span>
              <span className="font-mono">{frame.conditions.air_temp.toFixed(1)}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-pitwall-text-dim">Steering</span>
              <span className="font-mono">{(frame.steering * 100).toFixed(0)}%</span>
            </div>
          </div>
        </DataCard>

        {/* AI Alerts */}
        {alerts.length > 0 && (
          <DataCard title="AI Alerts">
            <div className="space-y-2">
              {alerts.map((alert, i) => (
                <div
                  key={i}
                  className={`text-xs px-3 py-2 rounded-lg border ${
                    alert.severity === 'critical'
                      ? 'bg-red-500/10 border-red-500/30 text-red-400'
                      : alert.severity === 'warning'
                        ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                        : 'bg-blue-500/10 border-blue-500/30 text-blue-400'
                  }`}
                >
                  <span className="font-bold uppercase mr-2">{alert.severity}</span>
                  {alert.message}
                </div>
              ))}
            </div>
          </DataCard>
        )}
      </div>
    </div>
  );
}
