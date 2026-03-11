/**
 * Tab 2 — Strategy
 *
 * Features:
 * - Pit window calculator
 * - Undercut / overcut simulation
 * - Safety car impact estimation
 * - Position after pit estimation
 */

import { useState } from 'react';
import { useTelemetryStore } from '../../store/telemetryStore';
import { DataCard } from '../common/DataCard';

interface PitWindow {
  earliest_lap: number;
  optimal_lap: number;
  latest_lap: number;
  fuel_laps_remaining: number;
  tyre_laps_remaining: number;
  estimated_pit_stops: number;
  strategy_notes: string[];
}

interface UndercutResult {
  scenario: string;
  pit_lap: number;
  estimated_position_after: number;
  time_delta: number;
  risk_level: string;
  notes: string;
}

const API_BASE = 'http://localhost:8400/api/v1';

export function Strategy() {
  const frame = useTelemetryStore((s) => s.frame);
  const standings = useTelemetryStore((s) => s.standings);
  const [totalLaps, setTotalLaps] = useState(50);
  const [pitLoss, setPitLoss] = useState(25);
  const [pitWindow, setPitWindow] = useState<PitWindow | null>(null);
  const [undercutResult, setUndercutResult] = useState<UndercutResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [simLoading, setSimLoading] = useState(false);

  function getStrategyPayload() {
    if (!frame) return null;
    const avgWear =
      (frame.tyres.wear.fl + frame.tyres.wear.fr + frame.tyres.wear.rl + frame.tyres.wear.rr) / 4;
    return {
      current_lap: frame.lap.current,
      total_laps: totalLaps,
      fuel_level: frame.fuel_level,
      fuel_per_lap: frame.fuel_per_lap,
      tyre_wear_avg: avgWear,
      tyre_wear_rate: 0.02,
      pit_loss_seconds: pitLoss,
    };
  }

  async function calculatePitWindow() {
    const payload = getStrategyPayload();
    if (!payload) return;
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/strategy/pit-window`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        setPitWindow(data);
      }
    } catch (err) {
      console.error('Failed to calculate pit window:', err);
    } finally {
      setLoading(false);
    }
  }

  async function simulateUndercut() {
    const payload = getStrategyPayload();
    if (!payload || !frame) return;
    setSimLoading(true);

    // Get gap to car ahead from standings
    const gapAhead = frame.interval.ahead ?? 1.5;

    try {
      const response = await fetch(`${API_BASE}/strategy/undercut?gap_ahead=${gapAhead}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        setUndercutResult(data);
      }
    } catch (err) {
      console.error('Failed to simulate undercut:', err);
    } finally {
      setSimLoading(false);
    }
  }

  async function simulateOvercut() {
    const payload = getStrategyPayload();
    if (!payload || !frame) return;
    setSimLoading(true);

    const gapAhead = frame.interval.ahead ?? 1.5;

    try {
      // Use same endpoint but with larger gap (overcut = stay out longer)
      const response = await fetch(`${API_BASE}/strategy/undercut?gap_ahead=${gapAhead + pitLoss}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        data.scenario = 'overcut';
        setUndercutResult(data);
      }
    } catch (err) {
      console.error('Failed to simulate overcut:', err);
    } finally {
      setSimLoading(false);
    }
  }

  // Safety car estimation based on current standings and positions
  function getSafetyCarEstimate() {
    if (!frame || standings.length === 0) {
      return { pitNow: frame ? frame.position + 2 : 0, stayOut: frame ? frame.position : 0 };
    }

    // Find cars in pit window range
    const carsAheadInPit = standings.filter(
      (s) => s.position < frame.position && s.in_pit
    ).length;

    // If we pit under SC, we lose fewer positions because the field bunches up
    const posLoss = Math.max(1, Math.floor(pitLoss / 5)); // SC reduces pit loss impact
    const pitNow = Math.min(frame.position + posLoss - carsAheadInPit, standings.length);
    const stayOut = Math.max(frame.position - carsAheadInPit, 1);

    return { pitNow, stayOut };
  }

  const scEstimate = getSafetyCarEstimate();

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* Pit Window Calculator */}
      <div className="col-span-6 space-y-4">
        <DataCard title="Pit Window Calculator">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-pitwall-text-dim block mb-1">Total Laps</label>
                <input
                  type="number"
                  value={totalLaps}
                  onChange={(e) => setTotalLaps(parseInt(e.target.value) || 0)}
                  className="w-full bg-pitwall-bg border border-pitwall-border rounded-lg px-3 py-2 font-mono text-sm"
                />
              </div>
              <div>
                <label className="text-xs text-pitwall-text-dim block mb-1">Pit Loss (s)</label>
                <input
                  type="number"
                  value={pitLoss}
                  onChange={(e) => setPitLoss(parseInt(e.target.value) || 0)}
                  className="w-full bg-pitwall-bg border border-pitwall-border rounded-lg px-3 py-2 font-mono text-sm"
                />
              </div>
            </div>

            <button
              onClick={calculatePitWindow}
              disabled={loading || !frame}
              className="w-full bg-pitwall-accent hover:bg-pitwall-accent-glow text-white py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Calculate Pit Window'}
            </button>
          </div>
        </DataCard>

        {pitWindow && (
          <DataCard title="Pit Window Result">
            <div className="space-y-4">
              {/* Visual timeline */}
              <div className="relative h-12 bg-pitwall-bg rounded-lg overflow-hidden">
                {frame && (
                  <>
                    <div
                      className="absolute h-full bg-pitwall-green/20 border-l border-r border-pitwall-green"
                      style={{
                        left: `${(pitWindow.earliest_lap / totalLaps) * 100}%`,
                        width: `${((pitWindow.latest_lap - pitWindow.earliest_lap) / totalLaps) * 100}%`,
                      }}
                    />
                    <div
                      className="absolute h-full w-0.5 bg-pitwall-accent"
                      style={{ left: `${(pitWindow.optimal_lap / totalLaps) * 100}%` }}
                    />
                    <div
                      className="absolute h-full w-0.5 bg-white"
                      style={{ left: `${(frame.lap.current / totalLaps) * 100}%` }}
                    />
                  </>
                )}
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-xs text-pitwall-text-dim">Earliest</div>
                  <div className="font-mono text-lg text-pitwall-green">L{pitWindow.earliest_lap}</div>
                </div>
                <div>
                  <div className="text-xs text-pitwall-text-dim">Optimal</div>
                  <div className="font-mono text-lg text-pitwall-accent font-bold">
                    L{pitWindow.optimal_lap}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-pitwall-text-dim">Latest</div>
                  <div className="font-mono text-lg text-pitwall-yellow">L{pitWindow.latest_lap}</div>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-pitwall-text-dim">Fuel laps</span>
                  <span className="font-mono">{pitWindow.fuel_laps_remaining}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-pitwall-text-dim">Tyre laps</span>
                  <span className="font-mono">{pitWindow.tyre_laps_remaining}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-pitwall-text-dim">Estimated stops</span>
                  <span className="font-mono font-bold">{pitWindow.estimated_pit_stops}</span>
                </div>
              </div>

              {/* Strategy notes */}
              {pitWindow.strategy_notes.length > 0 && (
                <div className="space-y-1">
                  {pitWindow.strategy_notes.map((note, i) => (
                    <div
                      key={i}
                      className={`text-xs px-3 py-1.5 rounded ${
                        note.includes('CRITICAL')
                          ? 'bg-red-500/10 text-red-400'
                          : note.includes('WARNING')
                            ? 'bg-yellow-500/10 text-yellow-400'
                            : 'bg-pitwall-border text-pitwall-text-dim'
                      }`}
                    >
                      {note}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </DataCard>
        )}
      </div>

      {/* Simulation panels */}
      <div className="col-span-6 space-y-4">
        <DataCard title="Undercut / Overcut Simulation">
          <div className="space-y-3">
            <p className="text-sm text-pitwall-text-dim">
              Simulates the effect of pitting before (undercut) or after (overcut) the car ahead.
            </p>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={simulateUndercut}
                disabled={simLoading || !frame}
                className="bg-pitwall-border hover:bg-pitwall-accent/20 text-sm py-3 rounded-lg transition-colors disabled:opacity-50"
              >
                {simLoading ? 'Simulating...' : 'Simulate Undercut'}
              </button>
              <button
                onClick={simulateOvercut}
                disabled={simLoading || !frame}
                className="bg-pitwall-border hover:bg-pitwall-accent/20 text-sm py-3 rounded-lg transition-colors disabled:opacity-50"
              >
                {simLoading ? 'Simulating...' : 'Simulate Overcut'}
              </button>
            </div>

            {/* Simulation result */}
            {undercutResult && (
              <div className="mt-3 p-3 rounded-lg border border-pitwall-border bg-pitwall-bg space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium capitalize">{undercutResult.scenario}</span>
                  <span
                    className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${
                      undercutResult.risk_level === 'low'
                        ? 'bg-pitwall-green/20 text-pitwall-green'
                        : undercutResult.risk_level === 'medium'
                          ? 'bg-yellow-500/20 text-yellow-400'
                          : 'bg-red-500/20 text-red-400'
                    }`}
                  >
                    {undercutResult.risk_level} risk
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-pitwall-text-dim">Pit on lap</span>
                  <span className="font-mono">L{undercutResult.pit_lap}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-pitwall-text-dim">Time delta</span>
                  <span
                    className={`font-mono font-bold ${
                      undercutResult.time_delta > 0 ? 'text-pitwall-green' : 'text-pitwall-accent'
                    }`}
                  >
                    {undercutResult.time_delta > 0 ? '+' : ''}
                    {undercutResult.time_delta.toFixed(1)}s
                  </span>
                </div>
                <p className="text-xs text-pitwall-text-dim">{undercutResult.notes}</p>
              </div>
            )}
          </div>
        </DataCard>

        <DataCard title="Safety Car Impact">
          <p className="text-sm text-pitwall-text-dim">
            Estimates the position impact if a safety car is deployed now.
          </p>
          <div className="mt-3 grid grid-cols-2 gap-4 text-center">
            <div className="bg-pitwall-bg rounded-lg p-3">
              <div className="text-xs text-pitwall-text-dim">If pit now</div>
              <div className="font-mono text-2xl mt-1">
                P{frame ? scEstimate.pitNow : '--'}
              </div>
              <div className="text-[10px] text-pitwall-text-dim mt-1">
                {frame ? `${scEstimate.pitNow - frame.position} positions lost` : ''}
              </div>
            </div>
            <div className="bg-pitwall-bg rounded-lg p-3">
              <div className="text-xs text-pitwall-text-dim">If stay out</div>
              <div className="font-mono text-2xl mt-1">
                P{frame ? scEstimate.stayOut : '--'}
              </div>
              <div className="text-[10px] text-pitwall-text-dim mt-1">
                {frame && scEstimate.stayOut < frame.position
                  ? `${frame.position - scEstimate.stayOut} positions gained`
                  : 'No change'}
              </div>
            </div>
          </div>
        </DataCard>

        <DataCard title="Race Progress">
          {frame && (
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-pitwall-text-dim">Progress</span>
                <span className="font-mono">
                  {frame.lap.current} / {totalLaps} laps
                </span>
              </div>
              <div className="h-2 bg-pitwall-bg rounded-full overflow-hidden">
                <div
                  className="h-full bg-pitwall-accent rounded-full transition-all"
                  style={{ width: `${(frame.lap.current / totalLaps) * 100}%` }}
                />
              </div>
              <div className="text-xs text-pitwall-text-dim text-right">
                {totalLaps - frame.lap.current} laps remaining
              </div>
            </div>
          )}
        </DataCard>
      </div>
    </div>
  );
}
