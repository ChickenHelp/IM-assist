/**
 * Tab 4 — Communication
 *
 * Features:
 * - Push-to-talk radio (WebRTC)
 * - Predefined message buttons
 * - Radio log
 * - Audio activity indicator
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { DataCard } from '../common/DataCard';

interface RadioMessage {
  id: number;
  from: string;
  text: string;
  timestamp: Date;
  type: 'sent' | 'received' | 'system';
}

const PREDEFINED_MESSAGES = [
  { category: 'Info', messages: ['Box this lap', 'Box next lap', 'Stay out', 'Push now'] },
  { category: 'Warning', messages: ['Yellow flag ahead', 'Car behind closing', 'Fuel saving mode', 'Watch track limits'] },
  { category: 'Strategy', messages: ['Undercut window open', 'Overcut recommended', 'Safety car likely', 'Change tyres next stop'] },
  { category: 'Feedback', messages: ['Good pace', 'Consistent laps', 'Watch sector 2', 'Clean air ahead'] },
];

export function Communication() {
  const [radioLog, setRadioLog] = useState<RadioMessage[]>([
    { id: 0, from: 'System', text: 'Radio channel initialized', timestamp: new Date(), type: 'system' },
  ]);
  const [isPTTActive, setIsPTTActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);
  const nextId = useRef(1);

  // Auto-scroll radio log
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [radioLog]);

  // Push-to-talk keyboard handler
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.code === 'KeyT' && !e.repeat && !isPTTActive) {
        setIsPTTActive(true);
      }
    }
    function handleKeyUp(e: KeyboardEvent) {
      if (e.code === 'KeyT') {
        setIsPTTActive(false);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isPTTActive]);

  const sendPredefined = useCallback((text: string) => {
    const msg: RadioMessage = {
      id: nextId.current++,
      from: 'Engineer',
      text,
      timestamp: new Date(),
      type: 'sent',
    };
    setRadioLog((prev) => [...prev, msg]);
  }, []);

  const connectRadio = useCallback(() => {
    setIsConnected(true);
    setRadioLog((prev) => [
      ...prev,
      {
        id: nextId.current++,
        from: 'System',
        text: 'Connected to radio channel (WebRTC LAN)',
        timestamp: new Date(),
        type: 'system',
      },
    ]);
  }, []);

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* Radio control */}
      <div className="col-span-4 space-y-4">
        <DataCard title="Radio">
          <div className="space-y-4">
            {/* Connection */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-pitwall-green' : 'bg-red-500'}`} />
                <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
              {!isConnected && (
                <button
                  onClick={connectRadio}
                  className="text-xs bg-pitwall-accent hover:bg-pitwall-accent-glow text-white px-3 py-1 rounded transition-colors"
                >
                  Connect
                </button>
              )}
            </div>

            {/* PTT Button */}
            <button
              onMouseDown={() => setIsPTTActive(true)}
              onMouseUp={() => setIsPTTActive(false)}
              onMouseLeave={() => setIsPTTActive(false)}
              disabled={!isConnected}
              className={`w-full py-8 rounded-xl text-sm font-medium transition-all ${
                isPTTActive
                  ? 'bg-pitwall-accent shadow-lg shadow-pitwall-accent/30 scale-95'
                  : 'bg-pitwall-border hover:bg-pitwall-accent/20'
              } disabled:opacity-30`}
            >
              {isPTTActive ? (
                <div className="flex flex-col items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-1 h-4 bg-white rounded animate-pulse" />
                    <div className="w-1 h-6 bg-white rounded animate-pulse" style={{ animationDelay: '0.1s' }} />
                    <div className="w-1 h-3 bg-white rounded animate-pulse" style={{ animationDelay: '0.2s' }} />
                    <div className="w-1 h-5 bg-white rounded animate-pulse" style={{ animationDelay: '0.3s' }} />
                    <div className="w-1 h-4 bg-white rounded animate-pulse" style={{ animationDelay: '0.15s' }} />
                  </div>
                  <span>TRANSMITTING</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1">
                  <span className="text-lg">Push to Talk</span>
                  <kbd className="text-xs text-pitwall-text-dim bg-pitwall-bg px-2 py-0.5 rounded">
                    Hold T
                  </kbd>
                </div>
              )}
            </button>

            {/* Audio indicator */}
            <div className="flex items-center justify-center gap-2 text-xs text-pitwall-text-dim">
              <span>Audio:</span>
              <div className="flex gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-1 rounded-full transition-all ${
                      isPTTActive ? 'bg-pitwall-green' : 'bg-pitwall-border'
                    }`}
                    style={{ height: isPTTActive ? `${8 + Math.random() * 12}px` : '4px' }}
                  />
                ))}
              </div>
            </div>
          </div>
        </DataCard>

        {/* Radio options */}
        <DataCard title="Radio Options">
          <div className="space-y-2 text-xs">
            <div className="flex justify-between text-pitwall-text-dim">
              <span>Mode</span>
              <span className="text-pitwall-green">WebRTC LAN</span>
            </div>
            <div className="flex justify-between text-pitwall-text-dim">
              <span>Effect</span>
              <span>Radio compression</span>
            </div>
            <div className="flex justify-between text-pitwall-text-dim">
              <span>PTT Key</span>
              <kbd className="bg-pitwall-bg px-1.5 py-0.5 rounded">T</kbd>
            </div>
          </div>
        </DataCard>
      </div>

      {/* Predefined messages */}
      <div className="col-span-4 space-y-4">
        <DataCard title="Quick Messages">
          <div className="space-y-4">
            {PREDEFINED_MESSAGES.map((group) => (
              <div key={group.category}>
                <h4 className="text-xs text-pitwall-text-dim mb-2">{group.category}</h4>
                <div className="grid grid-cols-2 gap-2">
                  {group.messages.map((msg) => (
                    <button
                      key={msg}
                      onClick={() => sendPredefined(msg)}
                      className="text-xs bg-pitwall-bg hover:bg-pitwall-accent/10 border border-pitwall-border hover:border-pitwall-accent/30 rounded-lg py-2 px-2 transition-all text-left"
                    >
                      {msg}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </DataCard>
      </div>

      {/* Radio log */}
      <div className="col-span-4">
        <DataCard title="Radio Log" className="h-full">
          <div className="space-y-2 max-h-[500px] overflow-auto">
            {radioLog.map((msg) => (
              <div
                key={msg.id}
                className={`text-xs p-2 rounded-lg ${
                  msg.type === 'system'
                    ? 'bg-pitwall-bg text-pitwall-text-dim italic'
                    : msg.type === 'sent'
                      ? 'bg-pitwall-accent/10 border border-pitwall-accent/20'
                      : 'bg-pitwall-blue/10 border border-pitwall-blue/20'
                }`}
              >
                <div className="flex justify-between mb-1">
                  <span className="font-medium">{msg.from}</span>
                  <span className="text-pitwall-text-muted">
                    {msg.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <p>{msg.text}</p>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </DataCard>
      </div>
    </div>
  );
}
