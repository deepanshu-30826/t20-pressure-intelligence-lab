"use client";

import React, { useState } from "react";
import {
  Flame,
  TrendingUp,
  BarChart3,
  Layers,
  Percent,
  CheckCircle2,
  ChevronRight,
  Crosshair,
  Award,
} from "lucide-react";
import { SectionHeader } from "../common/SectionHeader";
import { MetricCard } from "../common/MetricCard";
import { PlayerAvatar } from "../common/PlayerAvatar";
import { Badge } from "../common/Badge";
import { StatDelta } from "../common/StatDelta";
import { BatterRanking } from "@/types/analytics";

interface BatterAnalyticsViewProps {
  batters: BatterRanking[];
  onSelectPlayer: (id: number) => void;
}

export function BatterAnalyticsView({
  batters,
  onSelectPlayer,
}: BatterAnalyticsViewProps) {
  const [selectedBatterId, setSelectedBatterId] = useState<number>(
    batters[0]?.player_id || 37052
  );

  const selectedBatter =
    batters.find((b) => b.player_id === selectedBatterId) || batters[0];

  const roleBands = [
    { band: "Positions 1–3", role: "Top-Order Anchors & Dashers", parSR: 154.2, desc: "Evaluated during initial Powerplay-to-Middle phase transitions under resource security." },
    { band: "Positions 4–5", role: "Middle-Overs Accelerators", parSR: 159.4, desc: "Crucial spin-hitting & boundary acceleration facing death setup pressure." },
    { band: "Positions 6–7", role: "Death Finishers & Enforcers", parSR: 148.5, desc: "High resource scarcity, required boundary frequency from ball one." },
    { band: "Positions 8+", role: "Tail-End Scramblers", parSR: 134.8, desc: "Wicket preservation combined with desperate late-innings striking." },
  ];

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <SectionHeader
        title="Batter Pressure Intelligence"
        subtitle="Role-adjusted strike rate lift, boundary generation, dot-ball reduction, and match par consistency across T20 batting positions."
        badge="Position Band Normalized"
        badgeVariant="blue"
      />

      {/* Batter Selector Toolbar */}
      <div className="rounded-[18px] bg-[#0E182D]/80 backdrop-blur-md border border-blue-500/15 p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-[#60A5FA]">
            <Flame className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Select Batter for Deep-Dive:
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedBatter?.player_id}
            onChange={(e) => setSelectedBatterId(Number(e.target.value))}
            className="bg-[#080E1C] border border-blue-500/20 rounded-xl px-4 py-2 text-xs font-bold text-white focus:outline-none focus:border-[#3B82F6] transition-all"
          >
            {batters.map((b) => (
              <option key={b.player_id} value={b.player_id}>
                #{b.rank} {b.player_name} (Rating: {b.composite_pressure_rating.toFixed(1)})
              </option>
            ))}
          </select>

          {selectedBatter && (
            <button
              onClick={() => onSelectPlayer(selectedBatter.player_id)}
              className="px-4 py-2 rounded-xl bg-blue-500/15 hover:bg-blue-500/25 text-[#60A5FA] border border-blue-500/30 text-xs font-bold transition-all shadow-sm"
            >
              Full Profile
            </button>
          )}
        </div>
      </div>

      {/* Selected Batter Spotlight Overview */}
      {selectedBatter && (
        <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/20 p-6 relative overflow-hidden shadow-2xl">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-blue-500/10 relative z-10">
            <div className="flex items-start space-x-4">
              <PlayerAvatar name={selectedBatter.player_name} size="lg" />
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <Badge variant="blue">Rank #{selectedBatter.rank}</Badge>
                  <Badge variant="emerald">{selectedBatter.confidence_level} Confidence</Badge>
                  <span className="text-[11px] text-[#94A3B8] font-mono">
                    ID: {selectedBatter.player_id}
                  </span>
                </div>
                <h3 className="text-2xl font-black text-white">
                  {selectedBatter.player_name}
                </h3>
                <p className="text-xs text-[#94A3B8] mt-1 max-w-xl leading-relaxed">
                  {selectedBatter.analytical_justification ||
                    "Demonstrated superior strike-rate acceleration over peer baseline."}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="rounded-xl bg-[#14223F]/60 border border-blue-500/15 p-4 text-center min-w-[130px]">
                <div className="text-[10px] text-[#94A3B8] uppercase font-bold tracking-wider">
                  Pressure Rating
                </div>
                <div className="text-2xl font-black text-[#60A5FA] tabular-nums mt-1">
                  {selectedBatter.composite_pressure_rating.toFixed(2)}
                </div>
              </div>
              <div className="rounded-xl bg-[#14223F]/60 border border-blue-500/15 p-4 text-center min-w-[130px]">
                <div className="text-[10px] text-[#94A3B8] uppercase font-bold tracking-wider">
                  Consistency
                </div>
                <div className="text-2xl font-black text-white tabular-nums mt-1">
                  {selectedBatter.match_consistency_pct.toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Metric KPI Row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-6 relative z-10">
            <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Pressure SR</div>
              <div className="text-lg font-black text-white tabular-nums mt-1">
                {selectedBatter.pressure_strike_rate.toFixed(1)}
              </div>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Role Par SR</div>
              <div className="text-lg font-black text-[#94A3B8] tabular-nums mt-1">
                {selectedBatter.expected_baseline_sr ? selectedBatter.expected_baseline_sr.toFixed(1) : "-"}
              </div>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Shrunk Lift</div>
              <div className="text-lg font-black text-[#34D399] tabular-nums mt-1">
                +{selectedBatter.shrunk_sr_lift.toFixed(1)}
              </div>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Boundary Gain</div>
              <div className="text-lg font-black text-[#38BDF8] tabular-nums mt-1">
                +{selectedBatter.boundary_gain?.toFixed(1) || "0.0"}%
              </div>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Dot Reduction</div>
              <div className="text-lg font-black text-[#60A5FA] tabular-nums mt-1">
                +{selectedBatter.dot_reduction?.toFixed(1) || "0.0"}%
              </div>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Pressure Balls</div>
              <div className="text-lg font-black text-white tabular-nums mt-1">
                {selectedBatter.pressure_balls_faced}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Role Benchmark & Position Bands Architecture */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2.5">
          <Layers className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-extrabold text-white tracking-wide uppercase">
            Batting Position Band Par Benchmarks
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {roleBands.map((band, idx) => (
            <div key={idx} className="rounded-[18px] bg-[#0E182D]/75 backdrop-blur-md border border-blue-500/15 p-5 space-y-3 shadow-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black text-[#60A5FA]">{band.band}</span>
                <span className="px-2 py-0.5 rounded-lg bg-[#14223F] border border-blue-500/20 text-xs font-extrabold text-white tabular-nums">
                  Par {band.parSR} SR
                </span>
              </div>
              <div className="text-xs font-bold text-white">{band.role}</div>
              <p className="text-[11px] text-[#94A3B8] leading-relaxed">{band.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Batting Comparison Grid */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-blue-500/10">
          <h3 className="text-sm font-extrabold text-white tracking-wide uppercase flex items-center space-x-2.5">
            <BarChart3 className="w-4 h-4 text-blue-400" />
            <span>Top 10 Pressure Batters Comparative Matrix</span>
          </h3>
          <span className="text-xs text-[#94A3B8]">Sorted by Composite Pressure Rating</span>
        </div>

        <div className="divide-y divide-blue-500/10">
          {batters.slice(0, 10).map((b) => (
            <div
              key={b.player_id}
              onClick={() => onSelectPlayer(b.player_id)}
              className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-blue-600/10 px-3 rounded-xl cursor-pointer transition-colors group"
            >
              <div className="flex items-center space-x-3.5">
                <span className="w-7 h-7 rounded-xl bg-[#080E1C] border border-blue-500/15 text-[#94A3B8] text-xs font-black flex items-center justify-center shrink-0">
                  {b.rank}
                </span>
                <div>
                  <div className="text-xs font-bold text-white group-hover:text-[#60A5FA] transition-colors">
                    {b.player_name}
                  </div>
                  <div className="text-[10px] text-[#94A3B8]">
                    Overall SR: {b.overall_strike_rate.toFixed(1)} • Balls: {b.pressure_balls_faced}
                  </div>
                </div>
              </div>

              {/* Visual Relative SR Bar */}
              <div className="flex items-center space-x-5">
                <div className="w-36 hidden md:block">
                  <div className="flex justify-between text-[10px] text-[#94A3B8] mb-1.5 font-medium">
                    <span>PSR {b.pressure_strike_rate.toFixed(0)}</span>
                    <span className="text-[#34D399]">+{b.shrunk_sr_lift.toFixed(1)}</span>
                  </div>
                  <div className="w-full bg-[#080E1C] h-2 rounded-full overflow-hidden border border-blue-500/10">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (b.pressure_strike_rate / 220) * 100)}%` }}
                    />
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <div className="text-xs font-black text-[#60A5FA] tabular-nums">
                    {b.composite_pressure_rating.toFixed(2)}
                  </div>
                  <div className="text-[10px] text-[#94A3B8]">
                    {b.match_consistency_pct.toFixed(0)}% match par
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
