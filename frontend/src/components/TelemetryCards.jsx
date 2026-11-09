import React from "react";
import { Layers, Zap, Leaf, CheckCircle2, TrendingUp } from "lucide-react";

export default function TelemetryCards({ telemetry }) {
  const totalItems = telemetry?.items_total ?? 0;
  const itemsPerMin = telemetry?.items_per_minute ?? 0;
  const avoidedCo2eKg = telemetry?.total_avoided_co2e_kg ?? 0;
  const energyKwh = telemetry?.total_energy_saved_kwh ?? 0;
  const purity = telemetry?.sorting_purity_percent ?? 100.0;
  const totalMassKg = telemetry?.total_mass_kg ?? 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Avoided GHG Emissions */}
      <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-950/40 via-zinc-900/60 to-zinc-900/90 border border-emerald-500/30 shadow-lg relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
          <Leaf className="w-16 h-16 text-emerald-400" />
        </div>
        <div className="flex items-center justify-between text-xs font-semibold text-emerald-400 font-mono-code mb-2">
          <span>NET AVOIDED GHG</span>
          <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/30">
            EPA WARM v16
          </span>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-white tracking-tight font-mono-code">
            {avoidedCo2eKg.toFixed(4)}
          </span>
          <span className="text-sm font-semibold text-emerald-300">
            kg CO₂e
          </span>
        </div>
        <div className="mt-2 text-xs text-zinc-300 flex items-center justify-between pt-2 border-t border-zinc-800/80">
          <span>Metric Tons: {(avoidedCo2eKg / 1000).toFixed(6)} MT</span>
          <span className="text-emerald-400 font-medium">100% Verified</span>
        </div>
      </div>

      {/* 2. Total Count & Conveyor Speed */}
      <div className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800 shadow-lg relative overflow-hidden">
        <div className="flex items-center justify-between text-xs font-semibold text-zinc-300 font-mono-code mb-2">
          <span>SORTED UNITS</span>
          <div className="flex items-center space-x-1 text-sky-400">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{itemsPerMin.toFixed(1)}/min</span>
          </div>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-white tracking-tight font-mono-code">
            {totalItems}
          </span>
          <span className="text-sm font-semibold text-zinc-300">items</span>
        </div>
        <div className="mt-2 text-xs text-zinc-300 flex items-center justify-between pt-2 border-t border-zinc-800/80">
          <span>Mass Diverted: {totalMassKg.toFixed(3)} kg</span>
          <span className="text-sky-400 font-mono-code">ByteTrack ID</span>
        </div>
      </div>

      {/* 3. Energy Saved */}
      <div className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800 shadow-lg relative overflow-hidden">
        <div className="flex items-center justify-between text-xs font-semibold text-amber-400 font-mono-code mb-2">
          <span>OFFSET EMBODIED ENERGY</span>
          <Zap className="w-3.5 h-3.5 text-amber-400" />
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-white tracking-tight font-mono-code">
            {energyKwh.toFixed(3)}
          </span>
          <span className="text-sm font-semibold text-amber-300">kWh</span>
        </div>
        <div className="mt-2 text-xs text-zinc-300 flex items-center justify-between pt-2 border-t border-zinc-800/80">
          <span>Thermal: {(energyKwh * 3412.142).toFixed(0)} BTU</span>
          <span className="text-amber-400 font-mono-code">Life-Cycle Net</span>
        </div>
      </div>

      {/* 4. Sorting Purity */}
      <div className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800 shadow-lg relative overflow-hidden">
        <div className="flex items-center justify-between text-xs font-semibold text-teal-400 font-mono-code mb-2">
          <span>CONVEYOR PURITY RATE</span>
          <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-white tracking-tight font-mono-code">
            {purity.toFixed(1)}%
          </span>
          <span className="text-sm font-semibold text-teal-300">purity</span>
        </div>
        <div className="mt-2 text-xs text-zinc-300 flex items-center justify-between pt-2 border-t border-zinc-800/80">
          <span>
            Landfill Saved:{" "}
            {(telemetry?.landfill_volume_diverted_m3 ?? 0).toFixed(4)} m³
          </span>
          <span className="text-teal-400 font-medium">Industrial MRF</span>
        </div>
      </div>
    </div>
  );
}
