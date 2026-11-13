"use client";

import React, { useState } from "react";
import {
  Shield,
  Activity,
  BarChart3,
  Layers,
  CheckCircle2,
  ChevronRight,
  Crosshair,
  Award,
  Zap,
} from "lucide-react";
import { SectionHeader } from "../common/SectionHeader";
import { PlayerAvatar } from "../common/PlayerAvatar";
import { Badge } from "../common/Badge";
import { StatDelta } from "../common/StatDelta";
import { BowlerRanking } from "@/types/analytics";

interface BowlerAnalyticsViewProps {
  bowlers: BowlerRanking[];
  onSelectPlayer: (id: number) => void;
}

export function BowlerAnalyticsView({
  bowlers,
  onSelectPlayer,
}: BowlerAnalyticsViewProps) {
  const [selectedBowlerId, setSelectedBowlerId] = useState<number>(
    bowlers[0]?.player_id || 5979
  );

  const selectedBowler =
    bowlers.find((bw) => bw.player_id === selectedBowlerId) || bowlers[0];

  const phaseBenchmarks = [
    { phase: "Powerplay (Overs 1–6)", parEcon: 7.79, wicketRate: "4.8%", dotRate: "49.2%", desc: "Evaluated under field restriction pressure. Wicket taking vs boundary prevention balance." },
    { phase: "Middle Overs (Overs 7–15)", parEcon: 7.82, wicketRate: "4.2%", dotRate: "38.5%", desc: "Evaluated during rotational middle phases. Spin choke and singles restriction." },
    { phase: "Death Overs (Overs 16–20)", parEcon: 9.58, wicketRate: "7.1%", dotRate: "28.4%", desc: "Evaluated under extreme boundary hunting. High baseline economy par (9.58 RPO)." },
  ];

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <SectionHeader
        title="Bowler Pressure Intelligence"
        subtitle="Phase-adjusted economy lift, boundary suppression, pressure wicket rate, and match par consistency. Lower economy reflects superior performance."
        badge="Phase-Par Normalized"
        badgeVariant="violet"
      />

      {/* Bowler Selector Toolbar */}
      <div className="rounded-[18px] bg-[#0E182D]/80 backdrop-blur-md border border-purple-500/15 p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-[#C084FC]">
            <Shield className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Select Bowler for Deep-Dive:
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedBowler?.player_id}
            onChange={(e) => setSelectedBowlerId(Number(e.target.value))}
            className="bg-[#080E1C] border border-purple-500/20 rounded-xl px-4 py-2 text-xs font-bold text-white focus:outline-none focus:border-purple-400 transition-all"
          >
            {bowlers.map((bw) => (
              <option key={bw.player_id} value={bw.player_id}>
                #{bw.rank} {bw.player_name} (Rating: {bw.composite_pressure_rating.toFixed(1)})
              </option>
            ))}
          </select>

          {selectedBowler && (
            <button
              onClick={() => onSelectPlayer(selectedBowler.player_id)}
              className="px-4 py-2 rounded-xl bg-purple-500/15 hover:bg-purple-500/25 text-[#C084FC] border border-purple-500/30 text-xs font-bold transition-all shadow-sm"
            >
              Full Profile
            </button>
          )}
        </div>
      </div>

      {/* Selected Bowler Spotlight Overview */}
      {selectedBowler && (
        <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-purple-500/20 p-6 relative overflow-hidden shadow-2xl">
          <div className="absolute top-0 right-0 w-64 h-64 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-purple-500/10 relative z-10">
            <div className="flex items-start space-x-4">
              <PlayerAvatar name={selectedBowler.player_name} size="lg" />
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <Badge variant="violet">Rank #{selectedBowler.rank}</Badge>
                  <Badge variant="emerald">{selectedBowler.confidence_level} Confidence</Badge>
                  <span className="text-[11px] text-[#94A3B8] font-mono">
                    ID: {selectedBowler.player_id}
                  </span>
                </div>
                <h3 className="text-2xl font-black text-white">
                  {selectedBowler.player_name}
                </h3>
                <p className="text-xs text-[#94A3B8] mt-1 max-w-xl leading-relaxed">
                  {selectedBowler.analytical_justification ||
                    "Demonstrated outstanding run-suppression execution under match urgency."}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-4 text-center min-w-[130px]">
                <div className="text-[10px] text-[#94A3B8] uppercase font-bold tracking-wider">
                  Pressure Rating
                </div>
                <div className="text-2xl font-black text-[#C084FC] tabular-nums mt-1">
                  {selectedBowler.composite_pressure_rating.toFixed(2)}
                </div>
              </div>
              <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-4 text-center min-w-[130px]">
                <div className="text-[10px] text-[#94A3B8] uppercase font-bold tracking-wider">
                  Consistency
                </div>
                <div className="text-2xl font-black text-white tabular-nums mt-1">
                  {selectedBowler.match_consistency_pct.toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Metric KPI Row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-6 relative z-10">
            <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Pressure Econ</div>
              <div className="text-lg font-black text-white tabular-nums mt-1">
                {selectedBowler.pressure_economy.toFixed(2)}
              </div>
              <span className="text-[9px] text-[#34D399]">Lower is better</span>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Phase Par Econ</div>
              <div className="text-lg font-black text-[#94A3B8] tabular-nums mt-1">
                {selectedBowler.expected_baseline_econ ? selectedBowler.expected_baseline_econ.toFixed(2) : "-"}
              </div>
              <span className="text-[9px] text-[#94A3B8]">Phase Benchmark</span>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Shrunk Lift</div>
              <div className="text-lg font-black text-[#34D399] tabular-nums mt-1">
                +{selectedBowler.shrunk_econ_lift.toFixed(2)}
              </div>
              <span className="text-[9px] text-[#34D399]">Runs saved / over</span>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Wicket Rate</div>
              <div className="text-lg font-black text-[#C084FC] tabular-nums mt-1">
                {selectedBowler.pressure_wicket_rate?.toFixed(1) || "0.0"}%
              </div>
              <span className="text-[9px] text-[#94A3B8]">Wickets / ball</span>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Boundary Supp.</div>
              <div className="text-lg font-black text-[#38BDF8] tabular-nums mt-1">
                +{selectedBowler.boundary_suppression?.toFixed(1) || "0.0"}%
              </div>
              <span className="text-[9px] text-[#38BDF8]">Concession delta</span>
            </div>
            <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3.5 text-center">
              <div className="text-[10px] text-[#94A3B8] uppercase font-semibold">Pressure Balls</div>
              <div className="text-lg font-black text-white tabular-nums mt-1">
                {selectedBowler.pressure_legal_balls}
              </div>
              <span className="text-[9px] text-[#94A3B8]">{selectedBowler.pressure_matches} matches</span>
            </div>
          </div>
        </div>
      )}

      {/* Phase Par Benchmarks Architecture */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2.5">
          <Layers className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-extrabold text-white tracking-wide uppercase">
            Innings Phase Benchmark Standards
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {phaseBenchmarks.map((phase, idx) => (
            <div key={idx} className="rounded-[18px] bg-[#0E182D]/75 backdrop-blur-md border border-purple-500/15 p-5 space-y-3 shadow-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black text-[#C084FC]">{phase.phase}</span>
                <span className="px-2.5 py-0.5 rounded-lg bg-[#14223F] border border-purple-500/20 text-xs font-extrabold text-white tabular-nums">
                  Par {phase.parEcon} RPO
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-2.5 text-center">
                  <div className="text-[10px] text-[#94A3B8]">Wicket Rate</div>
                  <div className="font-extrabold text-white mt-0.5">{phase.wicketRate}</div>
                </div>
                <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-2.5 text-center">
                  <div className="text-[10px] text-[#94A3B8]">Dot %</div>
                  <div className="font-extrabold text-white mt-0.5">{phase.dotRate}</div>
                </div>
              </div>
              <p className="text-[11px] text-[#94A3B8] leading-relaxed">{phase.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Bowling Comparison Grid */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-purple-500/15 p-6 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-purple-500/10">
          <h3 className="text-sm font-extrabold text-white tracking-wide uppercase flex items-center space-x-2.5">
            <BarChart3 className="w-4 h-4 text-purple-400" />
            <span>Top 10 Pressure Bowlers Comparative Matrix</span>
          </h3>
          <span className="text-xs text-[#94A3B8]">Sorted by Composite Pressure Rating</span>
        </div>

        <div className="divide-y divide-purple-500/10">
          {bowlers.slice(0, 10).map((bw) => (
            <div
              key={bw.player_id}
              onClick={() => onSelectPlayer(bw.player_id)}
              className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-purple-600/10 px-3 rounded-xl cursor-pointer transition-colors group"
            >
              <div className="flex items-center space-x-3.5">
                <span className="w-7 h-7 rounded-xl bg-[#080E1C] border border-purple-500/15 text-[#94A3B8] text-xs font-black flex items-center justify-center shrink-0">
                  {bw.rank}
                </span>
                <div>
                  <div className="text-xs font-bold text-white group-hover:text-[#C084FC] transition-colors">
                    {bw.player_name}
                  </div>
                  <div className="text-[10px] text-[#94A3B8]">
                    Overall Econ: {bw.overall_economy.toFixed(2)} • Balls: {bw.pressure_legal_balls}
                  </div>
                </div>
              </div>

              {/* Visual Relative Economy Bar */}
              <div className="flex items-center space-x-5">
                <div className="w-36 hidden md:block">
                  <div className="flex justify-between text-[10px] text-[#94A3B8] mb-1.5 font-medium">
                    <span>PEcon {bw.pressure_economy.toFixed(2)}</span>
                    <span className="text-[#34D399]">+{bw.shrunk_econ_lift.toFixed(2)} lift</span>
                  </div>
                  <div className="w-full bg-[#080E1C] h-2 rounded-full overflow-hidden border border-purple-500/10">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full rounded-full transition-all duration-300"
                      style={{ width: `${Math.max(20, Math.min(100, 100 - (bw.pressure_economy - 5) * 12))}%` }}
                    />
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <div className="text-xs font-black text-[#C084FC] tabular-nums">
                    {bw.composite_pressure_rating.toFixed(2)}
                  </div>
                  <div className="text-[10px] text-[#94A3B8]">
                    {bw.match_consistency_pct.toFixed(0)}% match par
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
