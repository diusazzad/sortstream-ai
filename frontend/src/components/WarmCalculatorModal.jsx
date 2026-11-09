import React, { useState, useEffect } from "react";
import {
  X,
  Calculator,
  Sparkles,
  Leaf,
  Zap,
  Car,
  CheckCircle2,
} from "lucide-react";

const CATEGORIES = [
  { value: "pet_bottle", label: "PET Plastic Bottle (Default: 25g)" },
  { value: "hdpe_jug", label: "HDPE Milk/Detergent Jug (Default: 60g)" },
  { value: "aluminum_can", label: "Aluminum Beverage Can (Default: 14.5g)" },
  { value: "glass_bottle", label: "Glass Container/Jar (Default: 200g)" },
  { value: "cardboard_box", label: "Corrugated Cardboard (Default: 150g)" },
];

export default function WarmCalculatorModal({ isOpen, onClose }) {
  const [category, setCategory] = useState("pet_bottle");
  const [count, setCount] = useState(100);
  const [customMass, setCustomMass] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculate = async () => {
    setLoading(true);
    try {
      const payload = {
        category,
        count: parseInt(count, 10) || 1,
        mass_grams: customMass ? parseFloat(customMass) : null,
      };

      const res = await fetch("/api/warm/calculate-item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error("Calculation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      calculate();
    }
  }, [category, count, customMass, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg rounded-2xl border border-zinc-800 bg-zinc-950 shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white">
                Interactive EPA WARM v16 Calculator
              </h3>
              <p className="text-xs text-zinc-300">
                Deterministic life-cycle carbon and energy impact modeling
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close calculator modal"
            className="p-1 rounded-lg hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-zinc-300 mb-1.5 font-mono-code uppercase">
                Recyclable Class
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500 transition-colors"
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-zinc-300 mb-1.5 font-mono-code uppercase">
                Item Quantity
              </label>
              <input
                type="number"
                min="1"
                max="100000"
                value={count}
                onChange={(e) => setCount(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500 transition-colors font-mono-code"
                placeholder="e.g. 100"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-300 mb-1.5 font-mono-code">
              OPTIONAL: CUSTOM UNIT MASS (GRAMS)
            </label>
            <input
              type="number"
              step="0.1"
              value={customMass}
              onChange={(e) => setCustomMass(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-emerald-500 font-mono-code"
              placeholder="Leave empty for EPA default unit mass"
            />
          </div>

          {/* Results Card */}
          {result && (
            <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-950/50 via-zinc-900/80 to-zinc-900 border border-emerald-500/40 space-y-3">
              <div className="flex items-center justify-between text-xs text-emerald-400 font-mono-code font-semibold">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  DETERMINISTIC RESULT: {count} UNITS
                </span>
                <span>
                  Total Mass: {(result.mass_grams / 1000).toFixed(3)} kg
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2 border-t border-zinc-800">
                <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800">
                  <div className="flex items-center space-x-1.5 text-xs text-zinc-300 mb-1">
                    <Leaf className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Avoided GHG</span>
                  </div>
                  <div className="text-xl font-bold font-mono-code text-white">
                    {result.avoided_co2e_kg.toFixed(4)}{" "}
                    <span className="text-xs font-normal text-emerald-400">
                      kg CO₂e
                    </span>
                  </div>
                  <div className="text-[10px] text-zinc-400 mt-0.5">
                    {(result.avoided_co2e_kg / 1000).toFixed(6)} Metric Tons
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800">
                  <div className="flex items-center space-x-1.5 text-xs text-zinc-300 mb-1">
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    <span>Offset Energy</span>
                  </div>
                  <div className="text-xl font-bold font-mono-code text-white">
                    {result.energy_saved_kwh.toFixed(3)}{" "}
                    <span className="text-xs font-normal text-amber-400">
                      kWh
                    </span>
                  </div>
                  <div className="text-[10px] text-zinc-400 mt-0.5">
                    {(result.energy_saved_kwh * 3412.142).toFixed(0)} BTUs
                  </div>
                </div>
              </div>

              {/* Real World Equivalency */}
              <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center space-x-2">
                <Car className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>
                  Equivalent to avoiding{" "}
                  <strong>
                    {(result.avoided_co2e_kg * 2.48).toFixed(1)} miles
                  </strong>{" "}
                  driven by an average gasoline vehicle.
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-zinc-800/80 bg-zinc-950/60 flex items-center justify-between text-xs text-zinc-300">
          <span>EPA WARM v16 Formula: $\Delta E = M \cdot (EF_L - EF_R)$</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
