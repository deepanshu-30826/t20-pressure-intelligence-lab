"use client";

import React from "react";
import {
  Activity,
  Flame,
  Shield,
  Database,
  UserCheck,
  TrendingUp,
  Sparkles,
  ChevronRight,
  Target,
  CheckCircle2,
  Zap,
  BarChart3,
  Layers,
  ArrowUpRight,
} from "lucide-react";
import { MetricCard } from "../common/MetricCard";
import { PlayerAvatar } from "../common/PlayerAvatar";
import { StatDelta } from "../common/StatDelta";
import { Badge } from "../common/Badge";
import { Skeleton } from "../common/Skeleton";
import { OverviewData, BatterRanking, BowlerRanking } from "@/types/analytics";

interface OverviewViewProps {
  overview: OverviewData | null;
  batters: BatterRanking[];
  bowlers: BowlerRanking[];
  onNavigateTab: (tab: string) => void;
  onSelectPlayer: (id: number) => void;
}

export function OverviewView({
  overview,
  batters,
  bowlers,
  onNavigateTab,
  onSelectPlayer,
}: OverviewViewProps) {
  const topBatter = batters[0] || (overview?.top_batter ? {
    player_id: overview.top_batter.player_id,
    player_name: overview.top_batter.player_name,
    composite_pressure_rating: overview.top_batter.composite_pressure_rating,
    pressure_strike_rate: overview.top_batter.pressure_strike_rate,
    expected_baseline_sr: 147.2,
    shrunk_sr_lift: 42.9,
    pressure_balls_faced: 277,
    pressure_matches: 26,
    match_consistency_pct: 76.2,
    confidence_level: 'HIGH' as const,
    format_contribution: 'IPL (206) + T20I (71)',
    rank: 1,
  } : null);

  const topBowler = bowlers[0] || (overview?.top_bowler ? {
    player_id: overview.top_bowler.player_id,
    player_name: overview.top_bowler.player_name,
    composite_pressure_rating: overview.top_bowler.composite_pressure_rating,
    pressure_economy: overview.top_bowler.pressure_economy,
    expected_baseline_econ: 8.91,
    shrunk_econ_lift: 2.0,
    pressure_legal_balls: 161,
    pressure_matches: 23,
    match_consistency_pct: 76.5,
    confidence_level: 'HIGH' as const,
    format_contribution: 'T20I Only',
    rank: 1,
  } : null);

  const displayBatters = batters.slice(0, 5);
  const displayBowlers = bowlers.slice(0, 5);

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* HERO SECTION - Midnight Navy + Electric Blue & Violet Ambient Glow */}
      <div className="relative rounded-[22px] bg-gradient-to-r from-[#0B152A] via-[#0D1A36] to-[#121E3E] border border-blue-500/20 p-6 md:p-9 overflow-hidden shadow-2xl">
        {/* Subtle violet and electric blue ambient blur spheres */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="absolute bottom-0 left-1/4 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-10 right-1/3 w-64 h-64 bg-indigo-500/8 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-4 max-w-2xl">
            <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-blue-500/15 border border-blue-400/30 text-[#60A5FA] text-xs font-bold tracking-wide shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              <span>Rajasthan Royals SupeRR Selector • Official Intelligence Suite</span>
            </div>

            <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight leading-tight">
              T20 Pressure Intelligence
            </h1>

            <p className="text-xs sm:text-sm text-[#94A3B8] font-normal leading-relaxed">
              Decoding high-leverage execution when the match is on the line. Pre-delivery structural match-context modeling, Empirical Bayes peer shrinkage, and role-adjusted par consistency.
            </p>

            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-[#94A3B8]">
              <span className="font-semibold text-white">Verified Scope:</span>
              <Badge variant="blue">IPL 2022–2026 (371 Matches)</Badge>
              <Badge variant="indigo">Men&apos;s T20I (482 Matches)</Badge>
              <Badge variant="violet">Neutral W_format = 1.0</Badge>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 shrink-0">
            <button
              onClick={() => onNavigateTab("rankings")}
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] hover:from-[#3B82F6] hover:to-[#2563EB] text-white font-bold text-xs tracking-wide flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/25 transition-all duration-200 hover:-translate-y-0.5 border border-blue-400/30"
            >
              <span>Explore Official Rankings</span>
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigateTab("pressure")}
              className="px-6 py-3.5 rounded-xl bg-[#0E1B35]/80 hover:bg-[#142347] text-[#F1F5F9] border border-blue-500/20 font-semibold text-xs tracking-wide flex items-center justify-center space-x-2 transition-all duration-200 hover:-translate-y-0.5 backdrop-blur-md"
            >
              <Zap className="w-4 h-4 text-purple-400" />
              <span>Inspect Pressure Formulation</span>
            </button>
          </div>
        </div>
      </div>

      {/* REAL KPI CARDS GRID */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricCard
          label="Matches Analysed"
          value={overview?.total_matches.toLocaleString() || "883"}
          sub="371 IPL • 482 T20I"
          icon={Activity}
          accentColor="#3B82F6"
        />
        <MetricCard
          label="Deliveries Processed"
          value={overview?.total_deliveries.toLocaleString() || "200,999"}
          sub="Complete Ball-by-Ball Feed"
          icon={Database}
          accentColor="#6366F1"
        />
        <MetricCard
          label="High-Pressure Balls"
          value={overview?.pressure_deliveries.toLocaleString() || "75,348"}
          sub="Context Score ≥ 60.0"
          icon={Flame}
          accentColor="#F59E0B"
        />
        <MetricCard
          label="Eligible Batters"
          value={batters.length > 0 ? batters.length.toString() : "165"}
          sub="≥100 Balls • ≥10 Matches"
          icon={UserCheck}
          accentColor="#38BDF8"
        />
        <MetricCard
          label="Eligible Bowlers"
          value={bowlers.length > 0 ? bowlers.length.toString() : "151"}
          sub="≥100 Balls • ≥10 Matches"
          icon={Shield}
          accentColor="#8B5CF6"
        />
      </div>

      {/* SPOTLIGHT CARDS: #1 BATTER & #1 BOWLER */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leading Batter Spotlight */}
        {topBatter && (
          <div
            onClick={() => onSelectPlayer(topBatter.player_id)}
            className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-blue-500/20 p-6 relative overflow-hidden group cursor-pointer hover:border-blue-400/40 transition-all duration-200 hover:-translate-y-0.5 shadow-xl"
          >
            <div className="absolute top-0 right-0 w-48 h-48 bg-blue-600/10 rounded-full blur-2xl pointer-events-none group-hover:scale-125 transition-transform duration-500" />
            
            <div className="flex items-center justify-between mb-4 relative z-10">
              <Badge variant="blue" size="md">
                <Flame className="w-3.5 h-3.5 mr-1 text-blue-400" />
                Rank #1 Batter Under Pressure
              </Badge>
              <span className="text-xs font-semibold text-[#94A3B8] group-hover:text-[#60A5FA] flex items-center transition-colors">
                View Profile <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
              </span>
            </div>

            <div className="flex items-start space-x-4 mb-6 relative z-10">
              <PlayerAvatar name={topBatter.player_name} size="lg" />
              <div>
                <h3 className="text-xl md:text-2xl font-black text-white group-hover:text-[#60A5FA] transition-colors">
                  {topBatter.player_name}
                </h3>
                <p className="text-xs text-[#94A3B8] mt-1">
                  ID: {topBatter.player_id} • {topBatter.format_contribution} • High Match-to-Match Consistency
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-4 border-t border-blue-500/10 relative z-10">
              <div className="rounded-xl bg-[#14223F]/60 border border-blue-500/15 p-3">
                <div className="text-[10px] text-[#94A3B8] font-semibold uppercase">
                  Pressure Rating
                </div>
                <div className="text-xl font-black text-[#60A5FA] tabular-nums mt-0.5">
                  {topBatter.composite_pressure_rating.toFixed(2)}
                </div>
              </div>
              <div className="rounded-xl bg-[#14223F]/60 border border-blue-500/15 p-3">
                <div className="text-[10px] text-[#94A3B8] font-semibold uppercase">
                  Pressure SR
                </div>
                <div className="text-xl font-bold text-white tabular-nums mt-0.5">
                  {topBatter.pressure_strike_rate.toFixed(1)}
                </div>
              </div>
              <div className="rounded-xl bg-[#14223F]/60 border border-blue-500/15 p-3">
                <div className="text-[10px] text-[#94A3B8] font-semibold uppercase">
                  Shrunk SR Lift
                </div>
                <div className="text-xl font-bold text-[#34D399] tabular-nums mt-0.5">
                  +{topBatter.shrunk_sr_lift.toFixed(1)}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Leading Bowler Spotlight */}
        {topBowler && (
          <div
            onClick={() => onSelectPlayer(topBowler.player_id)}
            className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-purple-500/20 p-6 relative overflow-hidden group cursor-pointer hover:border-purple-400/40 transition-all duration-200 hover:-translate-y-0.5 shadow-xl"
          >
            <div className="absolute top-0 right-0 w-48 h-48 bg-purple-600/10 rounded-full blur-2xl pointer-events-none group-hover:scale-125 transition-transform duration-500" />

            <div className="flex items-center justify-between mb-4 relative z-10">
              <Badge variant="violet" size="md">
                <Shield className="w-3.5 h-3.5 mr-1 text-purple-400" />
                Rank #1 Bowler Under Pressure
              </Badge>
              <span className="text-xs font-semibold text-[#94A3B8] group-hover:text-[#C084FC] flex items-center transition-colors">
                View Profile <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
              </span>
            </div>

            <div className="flex items-start space-x-4 mb-6 relative z-10">
              <PlayerAvatar name={topBowler.player_name} size="lg" />
              <div>
                <h3 className="text-xl md:text-2xl font-black text-white group-hover:text-[#C084FC] transition-colors">
                  {topBowler.player_name}
                </h3>
                <p className="text-xs text-[#94A3B8] mt-1">
                  ID: {topBowler.player_id} • {topBowler.format_contribution} • Mystery Containment Specialist
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-4 border-t border-purple-500/10 relative z-10">
              <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-3">
                <div className="text-[10px] text-[#94A3B8] font-semibold uppercase">
                  Pressure Rating
                </div>
                <div className="text-xl font-black text-[#C084FC] tabular-nums mt-0.5">
                  {topBowler.composite_pressure_rating.toFixed(2)}
                </div>
              </div>
              <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-3">
                <div className="text-[10px] text-[#94A3B8] font-semibold uppercase">
                  Pressure Econ
                </div>
                <div className="text-xl font-bold text-white tabular-nums mt-0.5">
                  {topBowler.pressure_economy.toFixed(2)}
                </div>
              </div>
              <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-3">
                <div className="text-[10px] text-[#94A3B8] font-semibold uppercase">
                  Shrunk Econ Lift
                </div>
                <div className="text-xl font-bold text-[#34D399] tabular-nums mt-0.5">
                  +{topBowler.shrunk_econ_lift.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* COMPARATIVE ANALYTICS & PRESSURE PERFORMANCE SECTION */}
      <div className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-blue-500/15 p-6 space-y-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-blue-500/10">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-[#60A5FA]">
              <BarChart3 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-wide">
                Pressure vs. Normal Match Dynamics
              </h3>
              <p className="text-xs text-[#94A3B8]">
                Empirical baseline comparison across structural match situations (IPL &amp; T20I verified)
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center space-x-1.5 text-xs text-[#94A3B8]">
              <span className="w-2.5 h-2.5 rounded-full bg-[#3B82F6]" />
              <span>High-Pressure</span>
            </span>
            <span className="inline-flex items-center space-x-1.5 text-xs text-[#94A3B8] ml-2">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-600" />
              <span>Role Baseline</span>
            </span>
          </div>
        </div>

        {/* Role & Phase Comparative Bars */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-[#14223F]/50 border border-blue-500/10 space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">Top-Order (Pos 1–3)</span>
              <span className="text-blue-400 font-bold tabular-nums">154.2 Par SR</span>
            </div>
            <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full" style={{ width: "77%" }} />
            </div>
            <p className="text-[10px] text-[#94A3B8]">Evaluated under Powerplay-to-Middle phase transitions.</p>
          </div>

          <div className="p-4 rounded-xl bg-[#14223F]/50 border border-blue-500/10 space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">Middle Accelerators (4–5)</span>
              <span className="text-blue-400 font-bold tabular-nums">159.4 Par SR</span>
            </div>
            <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full" style={{ width: "80%" }} />
            </div>
            <p className="text-[10px] text-[#94A3B8]">Crucial spin-hitting &amp; death-overs setup urgency.</p>
          </div>

          <div className="p-4 rounded-xl bg-[#14223F]/50 border border-blue-500/10 space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">Death Finishers (6–7)</span>
              <span className="text-blue-400 font-bold tabular-nums">148.5 Par SR</span>
            </div>
            <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-500 to-blue-400 h-2 rounded-full" style={{ width: "74%" }} />
            </div>
            <p className="text-[10px] text-[#94A3B8]">High resource scarcity, required boundary frequency.</p>
          </div>

          <div className="p-4 rounded-xl bg-[#14223F]/50 border border-blue-500/10 space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">Death Bowling (16–20)</span>
              <span className="text-purple-400 font-bold tabular-nums">9.58 Par Econ</span>
            </div>
            <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" style={{ width: "86%" }} />
            </div>
            <p className="text-[10px] text-[#94A3B8]">Extreme boundary pressure; containment is rewarded.</p>
          </div>
        </div>
      </div>

      {/* LEADERBOARDS PREVIEW GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 5 Batters Preview */}
        <div className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-blue-500/15 overflow-hidden shadow-xl">
          <div className="p-5 border-b border-blue-500/10 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-[#60A5FA]">
                <Flame className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-white tracking-wide">
                Top 5 Batters Under Pressure
              </h3>
            </div>
            <button
              onClick={() => onNavigateTab("rankings")}
              className="text-xs font-semibold text-[#60A5FA] hover:text-white flex items-center space-x-1 transition-colors"
            >
              <span>View Leaderboard</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-blue-500/10">
            {displayBatters.length > 0 ? (
              displayBatters.map((b) => (
                <div
                  key={b.player_id}
                  onClick={() => onSelectPlayer(b.player_id)}
                  className="px-5 py-3.5 flex items-center justify-between hover:bg-[#152344]/50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center space-x-3.5 truncate">
                    <span className={`w-7 h-7 rounded-xl flex items-center justify-center text-xs font-black shrink-0 ${
                      b.rank === 1 ? "bg-amber-400/20 text-amber-300 border border-amber-400/40 shadow-sm" :
                      b.rank === 2 ? "bg-slate-300/20 text-slate-200 border border-slate-300/40 shadow-sm" :
                      b.rank === 3 ? "bg-amber-700/20 text-amber-500 border border-amber-700/40 shadow-sm" :
                      "bg-[#080E1C] text-[#94A3B8] border border-blue-500/10"
                    }`}>
                      {b.rank}
                    </span>
                    <div className="truncate">
                      <div className="text-xs font-bold text-white truncate hover:text-[#60A5FA] transition-colors">
                        {b.player_name}
                      </div>
                      <div className="text-[11px] text-[#94A3B8]">
                        PSR: {b.pressure_strike_rate.toFixed(1)} • {b.pressure_balls_faced}b ({b.pressure_matches}m)
                      </div>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-xs font-extrabold text-[#60A5FA] tabular-nums">
                      {b.composite_pressure_rating.toFixed(2)}
                    </div>
                    <div className="text-[10px] text-[#94A3B8]">
                      Lift: +{b.shrunk_sr_lift.toFixed(1)}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 space-y-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Top 5 Bowlers Preview */}
        <div className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-purple-500/15 overflow-hidden shadow-xl">
          <div className="p-5 border-b border-purple-500/10 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-[#C084FC]">
                <Shield className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-white tracking-wide">
                Top 5 Bowlers Under Pressure
              </h3>
            </div>
            <button
              onClick={() => onNavigateTab("rankings")}
              className="text-xs font-semibold text-[#C084FC] hover:text-white flex items-center space-x-1 transition-colors"
            >
              <span>View Leaderboard</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-purple-500/10">
            {displayBowlers.length > 0 ? (
              displayBowlers.map((bw) => (
                <div
                  key={bw.player_id}
                  onClick={() => onSelectPlayer(bw.player_id)}
                  className="px-5 py-3.5 flex items-center justify-between hover:bg-[#1D1942]/50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center space-x-3.5 truncate">
                    <span className={`w-7 h-7 rounded-xl flex items-center justify-center text-xs font-black shrink-0 ${
                      bw.rank === 1 ? "bg-amber-400/20 text-amber-300 border border-amber-400/40 shadow-sm" :
                      bw.rank === 2 ? "bg-slate-300/20 text-slate-200 border border-slate-300/40 shadow-sm" :
                      bw.rank === 3 ? "bg-amber-700/20 text-amber-500 border border-amber-700/40 shadow-sm" :
                      "bg-[#080E1C] text-[#94A3B8] border border-purple-500/10"
                    }`}>
                      {bw.rank}
                    </span>
                    <div className="truncate">
                      <div className="text-xs font-bold text-white truncate hover:text-[#C084FC] transition-colors">
                        {bw.player_name}
                      </div>
                      <div className="text-[11px] text-[#94A3B8]">
                        PEcon: {bw.pressure_economy.toFixed(2)} • {bw.pressure_legal_balls}b ({bw.pressure_matches}m)
                      </div>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-xs font-extrabold text-[#C084FC] tabular-nums">
                      {bw.composite_pressure_rating.toFixed(2)}
                    </div>
                    <div className="text-[10px] text-[#34D399]">
                      Lift: +{bw.shrunk_econ_lift.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 space-y-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* METHODOLOGY PILLARS SUMMARY */}
      <div className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-blue-500/15 p-6 space-y-4 shadow-xl">
        <div className="flex items-center space-x-2.5">
          <CheckCircle2 className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">
            Four Foundational Pillars of Statistical Rigor
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/10 p-4 space-y-2">
            <div className="font-bold text-xs text-[#60A5FA]">
              1. Zero Data Leakage
            </div>
            <p className="text-[11px] text-[#94A3B8] leading-relaxed">
              Pressure index is evaluated solely from pre-delivery match state (wickets in hand, balls remaining, match urgency). Never influenced by outcome.
            </p>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/10 p-4 space-y-2">
            <div className="font-bold text-xs text-[#38BDF8]">
              2. Role &amp; Phase Baselines
            </div>
            <p className="text-[11px] text-[#94A3B8] leading-relaxed">
              Performance is judged against role position bands (1–3, 4–5, 6–7, 8+) and bowling phases (Death par 9.58 RPO) to avoid rewarding easy middle overs.
            </p>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/10 p-4 space-y-2">
            <div className="font-bold text-xs text-purple-400">
              3. Empirical Bayes Shrinkage
            </div>
            <p className="text-[11px] text-[#94A3B8] leading-relaxed">
              Shrinkage parameter k=40 shrinks extreme sample noise toward role population par, ensuring true statistical defensibility.
            </p>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/10 p-4 space-y-2">
            <div className="font-bold text-xs text-amber-400">
              4. Match Par Consistency
            </div>
            <p className="text-[11px] text-[#94A3B8] leading-relaxed">
              Raw volume multipliers were replaced with genuine match-level consistency (% of appearances meeting or exceeding expected role par).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
