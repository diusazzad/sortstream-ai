import React from 'react';
import { Activity, ShieldCheck, Cpu, Sparkles } from 'lucide-react';

export default function Navbar({ isConnected, onOpenCalculator }) {
  return (
    <header className="border-b border-zinc-800/80 bg-[#0c0e14]/90 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center space-x-3.5">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 p-0.5 shadow-lg shadow-emerald-500/20 flex items-center justify-center">
          <div className="h-full w-full bg-[#0c0e14] rounded-[10px] flex items-center justify-center">
            <span className="text-xl">🌿</span>
          </div>
        </div>
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              SortStream <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono-code font-semibold border border-emerald-500/30">AI v1.0</span>
            </h1>
            <span className="hidden sm:inline-block text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/50">
              Arbiter Hacks V1 • Waste Track
            </span>
          </div>
          <p className="text-xs text-zinc-400">High-Speed Conveyor Multi-Object Tracking & EPA WARM v16 Accounting</p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenCalculator}
          className="flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-zinc-800/80 hover:bg-zinc-700 text-zinc-200 border border-zinc-700/60 transition-all shadow-sm hover:border-zinc-500"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span className="hidden md:inline">Interactive</span> EPA Calculator
        </button>

        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs font-mono-code text-emerald-400">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="hidden sm:inline">EPA WARM v16</span> Certified
        </div>

        <div className="flex items-center space-x-2 px-2.5 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-mono-code">
          <span className={`inline-block w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span className="text-zinc-400 hidden sm:inline">{isConnected ? 'FEED LIVE' : 'CONNECTING'}</span>
        </div>
      </div>
    </header>
  );
}
