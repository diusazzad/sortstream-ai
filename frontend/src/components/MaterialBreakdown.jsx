import React from "react";
import { Box, Layers, Zap, Flame, ShieldAlert, Check } from "lucide-react";

const MATERIAL_META = [
  {
    key: "aluminum_can",
    title: "Aluminum Cans",
    code: "ALU",
    color: "from-sky-500/20 to-sky-600/5",
    borderColor: "border-sky-500/30",
    textColor: "text-sky-300",
    badgeBg: "bg-sky-500/10 text-sky-200 border-sky-500/30",
    factor: "9.15 kg CO₂e/kg",
    energy: "14.0 kWh/kg",
    defaultMass: "14.2g unit",
  },
  {
    key: "pet_plastic",
    title: "PET Plastic (#1)",
    code: "PET #1",
    color: "from-emerald-500/20 to-emerald-600/5",
    borderColor: "border-emerald-500/30",
    textColor: "text-emerald-300",
    badgeBg: "bg-emerald-500/10 text-emerald-200 border-emerald-500/30",
    factor: "1.20 kg CO₂e/kg",
    energy: "6.1 kWh/kg",
    defaultMass: "23.8g unit",
  },
  {
    key: "hdpe_plastic",
    title: "HDPE Plastic (#2)",
    code: "HDPE #2",
    color: "from-amber-500/20 to-amber-600/5",
    borderColor: "border-amber-500/30",
    textColor: "text-amber-300",
    badgeBg: "bg-amber-500/10 text-amber-200 border-amber-500/30",
    factor: "0.96 kg CO₂e/kg",
    energy: "5.4 kWh/kg",
    defaultMass: "35.0g unit",
  },
  {
    key: "corrugated_cardboard",
    title: "Corrugated Cardboard",
    code: "OCC",
    color: "from-orange-500/20 to-orange-600/5",
    borderColor: "border-orange-500/30",
    textColor: "text-orange-300",
    badgeBg: "bg-orange-500/10 text-orange-200 border-orange-500/30",
    factor: "3.34 kg CO₂e/kg",
    energy: "3.9 kWh/kg",
    defaultMass: "65.0g unit",
  },
  {
    key: "e_waste",
    title: "E-Waste & Electronics",
    code: "E-WASTE",
    color: "from-rose-500/20 to-rose-600/5",
    borderColor: "border-rose-500/30",
    textColor: "text-rose-300",
    badgeBg: "bg-rose-500/10 text-rose-200 border-rose-500/30",
    factor: "1.90 kg CO₂e/kg",
    energy: "7.2 kWh/kg",
    defaultMass: "80.0g unit",
  },
];

export default function MaterialBreakdown({ telemetry }) {
  const breakdown = telemetry?.breakdown_by_material || {};
  const totalCount = telemetry?.items_total || 0;

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-5 shadow-2xl flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800/80 mb-4">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold text-white tracking-wide uppercase">
              Material Stream Breakdown
            </h2>
          </div>
          <span className="text-xs font-mono-code text-zinc-300">
            5 Industrial Recyclable Classes
          </span>
        </div>

        <div className="space-y-3">
          {MATERIAL_META.map((meta) => {
            const data = breakdown[meta.key] || {
              count: 0,
              total_mass_kg: 0,
              net_avoided_co2e_kg: 0,
              energy_saved_kwh: 0,
            };
            const percent =
              totalCount > 0 ? (data.count / totalCount) * 100 : 0;

            return (
              <div
                key={meta.key}
                className={`p-3 rounded-lg border ${meta.borderColor} bg-gradient-to-r ${meta.color} transition-all hover:border-zinc-500`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-zinc-100">
                      {meta.title}
                    </span>
                    <span
                      className={`text-[10px] font-mono-code px-1.5 py-0.5 rounded border ${meta.badgeBg}`}
                    >
                      {meta.code}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-base font-extrabold font-mono-code text-white">
                      {data.count}
                    </span>
                    <span className="text-xs text-zinc-300 ml-1">items</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-zinc-900 rounded-full h-1.5 mb-2 overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 transition-all duration-500"
                    style={{ width: `${percent}%` }}
                  />
                </div>

                {/* Metrics detail strip with WCAG AA compliant contrast */}
                <div className="grid grid-cols-3 gap-2 text-[11px] font-mono-code text-zinc-300 pt-1 border-t border-zinc-800/40">
                  <div>
                    <span className="text-zinc-400">Mass: </span>
                    <span className="text-zinc-100 font-semibold">
                      {data.total_mass_kg.toFixed(3)} kg
                    </span>
                  </div>
                  <div>
                    <span className="text-zinc-400">Avoided: </span>
                    <span className={`${meta.textColor} font-semibold`}>
                      {data.net_avoided_co2e_kg.toFixed(3)} kg CO₂e
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-zinc-400">Energy: </span>
                    <span className="text-amber-300 font-semibold">
                      {data.energy_saved_kwh.toFixed(2)} kWh
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 text-xs text-zinc-300">
        <p className="font-semibold text-zinc-200 mb-1 flex items-center gap-1.5">
          <Check className="w-3.5 h-3.5 text-emerald-400" />
          EPA WARM v16 Formula Grounding:
        </p>
        <p className="text-[11px] text-zinc-300 leading-relaxed">
          Avoided carbon factor reflects avoided virgin extraction and smelting
          energy, offset by recycling manufacturing life-cycle factors per
          material class.
        </p>
      </div>
    </div>
  );
}
