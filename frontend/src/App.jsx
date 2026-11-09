import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import TelemetryCards from "./components/TelemetryCards";
import VideoFeed from "./components/VideoFeed";
import MaterialBreakdown from "./components/MaterialBreakdown";
import WarmCalculatorModal from "./components/WarmCalculatorModal";
import {
  Shield,
  Sparkles,
  Terminal,
  BookOpen,
  ExternalLink,
  Activity,
} from "lucide-react";

export default function App() {
  const [telemetry, setTelemetry] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isCalculatorOpen, setIsCalculatorOpen] = useState(false);

  const fetchTelemetry = async () => {
    try {
      const res = await fetch("/api/stream/telemetry");
      if (res.ok) {
        const data = await res.json();
        setTelemetry(data);
        setIsConnected(true);
      } else {
        setIsConnected(false);
      }
    } catch (err) {
      setIsConnected(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleReset = async () => {
    try {
      await fetch("/api/stream/reset", { method: "POST" });
      await fetchTelemetry();
    } catch (err) {
      console.error("Failed to reset stream:", err);
    }
  };

  return (
    <div className="min-h-screen bg-[#090a0f] text-zinc-100 flex flex-col">
      <Navbar
        isConnected={isConnected}
        onOpenCalculator={() => setIsCalculatorOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Top Strip: Real-time Telemetry Metrics */}
        <TelemetryCards telemetry={telemetry} />

        {/* Center Grid: Live Video Feed (Left) & Material Breakdown (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          <div className="lg:col-span-7 flex flex-col">
            <VideoFeed onReset={handleReset} />
          </div>
          <div className="lg:col-span-5 flex flex-col">
            <MaterialBreakdown telemetry={telemetry} />
          </div>
        </div>

        {/* Bottom Banner: Hackathon & Architecture Overview */}
        <div className="rounded-xl border border-zinc-800/80 bg-zinc-950/60 p-5 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                Arbiter Hacks V1 • Theme Track: Rethinking Waste
              </h2>
              <p className="text-xs text-zinc-300 mt-0.5">
                SortStream AI directly addresses MRF conveyor contamination and
                quantifies life-cycle carbon reductions using EPA WARM v16.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 w-full md:w-auto justify-end">
            <a
              href="https://github.com/diusazzad/sortstream-ai"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-xs text-zinc-200 border border-zinc-700 transition-colors"
            >
              <span>GitHub Repository</span>
              <ExternalLink className="w-3.5 h-3.5 text-zinc-300" />
            </a>

            <button
              onClick={() => setIsCalculatorOpen(true)}
              aria-label="Launch Interactive EPA WARM Calculator"
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-400 hover:bg-emerald-300 text-xs font-bold text-zinc-950 shadow-lg shadow-emerald-500/25 transition-colors focus:ring-2 focus:ring-emerald-400"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Launch Calculator</span>
            </button>
          </div>
        </div>
      </main>

      {/* Accessible Footer with High Contrast */}
      <footer className="border-t border-zinc-900 bg-[#07080c] py-4 text-center text-xs text-zinc-300 font-mono-code">
        SortStream AI • Industrial Conveyor Sorting & EPA WARM v16 Accounting
        Engine • Arbiter Hacks V1
      </footer>

      {/* Interactive Modal */}
      <WarmCalculatorModal
        isOpen={isCalculatorOpen}
        onClose={() => setIsCalculatorOpen(false)}
      />
    </div>
  );
}
