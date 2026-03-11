import { useState } from 'react';
import { useTelemetryConnection } from './hooks/useTelemetry';
import { useTelemetryStore } from './store/telemetryStore';
import { Header } from './components/layout/Header';
import { LiveRace } from './components/live/LiveRace';
import { Strategy } from './components/strategy/Strategy';
import { Performance } from './components/performance/Performance';
import { Communication } from './components/communication/Communication';

type Tab = 'live' | 'strategy' | 'performance' | 'communication';

export function App() {
  const [activeTab, setActiveTab] = useState<Tab>('live');
  useTelemetryConnection();

  const connected = useTelemetryStore((s) => s.connected);

  const tabs: { id: Tab; label: string; shortcut: string }[] = [
    { id: 'live', label: 'Live Race', shortcut: '1' },
    { id: 'strategy', label: 'Strategy', shortcut: '2' },
    { id: 'performance', label: 'Performance', shortcut: '3' },
    { id: 'communication', label: 'Communication', shortcut: '4' },
  ];

  return (
    <div className="min-h-screen bg-pitwall-bg flex flex-col">
      <Header connected={connected} />

      {/* Tab Bar */}
      <nav className="flex gap-2 px-6 py-3 border-b border-pitwall-border bg-pitwall-surface/50 backdrop-blur-sm">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
          >
            <span>{tab.label}</span>
            <kbd className="ml-2 text-xs opacity-40">{tab.shortcut}</kbd>
          </button>
        ))}
      </nav>

      {/* Content */}
      <main className="flex-1 p-6 overflow-auto">
        {activeTab === 'live' && <LiveRace />}
        {activeTab === 'strategy' && <Strategy />}
        {activeTab === 'performance' && <Performance />}
        {activeTab === 'communication' && <Communication />}
      </main>
    </div>
  );
}
