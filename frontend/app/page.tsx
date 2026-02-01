import React from 'react';
import LiveCallMonitor from '@/components/LiveCallMonitor';
import Dashboard from '@/components/Dashboard';
import { Activity } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto">
      {/* Header */}
      <header className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <Activity size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">SentientVoice</h1>
            <p className="text-sm text-slate-500 font-medium tracking-wide uppercase">Dental Mission Control</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-semibold text-slate-900">Dr. Smith</p>
            <p className="text-xs text-slate-500">Smile Care Dental</p>
          </div>
          <div className="w-10 h-10 bg-slate-200 rounded-full overflow-hidden border-2 border-white shadow-sm">
            {/* Avatar Placeholder */}
            <div className="w-full h-full flex items-center justify-center text-slate-400 font-bold">DS</div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="space-y-6">
        {/* Top Row: Live Monitor */}
        <section>
          <LiveCallMonitor />
        </section>

        {/* Bottom Row: Data Dashboard */}
        <section>
          <Dashboard />
        </section>
      </div>
    </main>
  );
}
