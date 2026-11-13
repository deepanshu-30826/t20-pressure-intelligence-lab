"use client";

import React, { useState, useEffect } from "react";
import {
  UserCheck,
  Flame,
  Shield,
  Activity,
  Layers,
  Calendar,
  Sparkles,
  ChevronRight,
  TrendingUp,
  BarChart3,
  Clock,
  Award,
} from "lucide-react";
import { SectionHeader } from "../common/SectionHeader";
import { PlayerAvatar } from "../common/PlayerAvatar";
import { Badge } from "../common/Badge";
import { StatDelta } from "../common/StatDelta";
import { EmptyState } from "../common/EmptyState";
import { Skeleton } from "../common/Skeleton";
import {
  PlayerProfileResponse,
  PlayerMatchRecord,
  BatterRanking,
  BowlerRanking,
} from "@/types/analytics";
import { api } from "@/lib/api";

interface PlayerProfileViewProps {
  selectedPlayerId: number | null;
  batters: BatterRanking[];
  bowlers: BowlerRanking[];
  onSelectPlayer: (id: number) => void;
}

export function PlayerProfileView({
  selectedPlayerId,
  batters,
  bowlers,
  onSelectPlayer,
}: PlayerProfileViewProps) {
  const [profile, setProfile] = useState<PlayerProfileResponse | null>(null);
  const [matchHistory, setMatchHistory] = useState<PlayerMatchRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // Fetch full profile and match history when player changes
  useEffect(() => {
    if (!selectedPlayerId) return;

    setLoading(true);

    Promise.allSettled([
      api.getPlayerProfile(selectedPlayerId),
      api.getPlayerMatchHistory(selectedPlayerId, 15),
    ]).then(([profileRes, historyRes]) => {
      if (profileRes.status === "fulfilled" && profileRes.value.data) {
        setProfile(profileRes.value.data);
      }
      if (historyRes.status === "fulfilled" && historyRes.value.data) {
        setMatchHistory(historyRes.value.data);
      }
      setLoading(false);
    });
  }, [selectedPlayerId]);

  if (!selectedPlayerId && batters.length > 0) {
    onSelectPlayer(batters[0].player_id);
    return <Skeleton className="h-96 w-full" />;
  }

  const batting = profile?.batting_profile;
  const bowling = profile?.bowling_profile;

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Top Header & Quick Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <SectionHeader
          title="Candidate Profile Deep-Dive"
          subtitle="Comprehensive delivery-level analytics, phase splits, and match history."
          badge={profile ? `ID: ${profile.player_id}` : undefined}
          badgeVariant="blue"
        />

        {/* Quick Dropdown to jump across candidates */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-[#94A3B8]">Switch Candidate:</span>
          <select
            value={selectedPlayerId || ""}
            onChange={(e) => onSelectPlayer(Number(e.target.value))}
            className="bg-[#0E182D] border border-blue-500/20 rounded-xl px-3 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-[#3B82F6] transition-all"
          >
            <optgroup label="Top Batters">
              {batters.slice(0, 15).map((b) => (
                <option key={b.player_id} value={b.player_id}>
                  #{b.rank} {b.player_name} (Rating: {b.composite_pressure_rating.toFixed(1)})
                </option>
              ))}
            </optgroup>
            <optgroup label="Top Bowlers">
              {bowlers.slice(0, 15).map((bw) => (
                <option key={bw.player_id} value={bw.player_id}>
                  #{bw.rank} {bw.player_name} (Rating: {bw.composite_pressure_rating.toFixed(1)})
                </option>
              ))}
            </optgroup>
          </select>
        </div>
      </div>

      {loading && !profile ? (
        <Skeleton className="h-96 w-full" />
      ) : profile ? (
        <div className="space-y-6">
          {/* PLAYER BANNER CARD */}
          <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/20 p-6 relative overflow-hidden shadow-2xl">
            <div className="absolute top-0 right-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-blue-500/10 relative z-10">
              <div className="flex items-start space-x-4">
                <PlayerAvatar name={profile.name} size="lg" />
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    {batting && (
                      <Badge variant="blue">
                        <Flame className="w-3 h-3 mr-1 text-blue-400" />
                        Batter Rank #{batting.rank}
                      </Badge>
                    )}
                    {bowling && (
                      <Badge variant="violet">
                        <Shield className="w-3 h-3 mr-1 text-purple-400" />
                        Bowler Rank #{bowling.rank}
                      </Badge>
                    )}
                    <Badge variant="emerald">
                      {batting?.confidence_level || bowling?.confidence_level || "HIGH"} Reliability
                    </Badge>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-black text-white">
                    {profile.name}
                  </h2>
                  <p className="text-xs text-[#94A3B8] mt-1">
                    {batting?.format_contribution || bowling?.format_contribution || "IPL + T20I Record"}
                  </p>
                </div>
              </div>

              {/* Main Pressure Ratings */}
              <div className="flex items-center space-x-4">
                {batting && (
                  <div className="rounded-xl bg-[#14223F]/60 border border-blue-500/15 p-4 text-center min-w-[130px]">
                    <div className="text-[10px] text-[#94A3B8] uppercase font-bold tracking-wider">
                      Batting Rating
                    </div>
                    <div className="text-2xl font-black text-[#60A5FA] tabular-nums mt-1">
                      {batting.composite_pressure_rating.toFixed(2)}
                    </div>
                    <div className="text-[10px] text-[#34D399] mt-0.5">
                      Lift +{batting.shrunk_sr_lift.toFixed(1)}
                    </div>
                  </div>
                )}
                {bowling && (
                  <div className="rounded-xl bg-[#14223F]/60 border border-purple-500/15 p-4 text-center min-w-[130px]">
                    <div className="text-[10px] text-[#94A3B8] uppercase font-bold tracking-wider">
                      Bowling Rating
                    </div>
                    <div className="text-2xl font-black text-[#C084FC] tabular-nums mt-1">
                      {bowling.composite_pressure_rating.toFixed(2)}
                    </div>
                    <div className="text-[10px] text-[#34D399] mt-0.5">
                      Lift +{bowling.shrunk_econ_lift.toFixed(2)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Justification summary */}
            <div className="pt-4 text-xs text-[#94A3B8] leading-relaxed relative z-10">
              <span className="font-bold text-white mr-2">Analytical Finding:</span>
              {batting?.analytical_justification ||
                bowling?.analytical_justification ||
                "Player meets rigorous context-only statistical qualification thresholds."}
            </div>
          </div>

          {/* BATTING & BOWLING DETAILS */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Batting Card */}
            {batting && (
              <div className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-blue-500/15 p-6 space-y-4 shadow-xl">
                <div className="flex items-center justify-between pb-3 border-b border-blue-500/10">
                  <div className="flex items-center space-x-2">
                    <Flame className="w-5 h-5 text-blue-400" />
                    <h3 className="text-sm font-extrabold text-white uppercase tracking-wider">
                      Batting Pressure Profile
                    </h3>
                  </div>
                  <span className="text-xs text-[#60A5FA] font-bold">
                    Rank #{batting.rank}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Pressure SR</div>
                    <div className="text-lg font-black text-white tabular-nums mt-0.5">
                      {batting.pressure_strike_rate.toFixed(1)}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Role Par SR</div>
                    <div className="text-lg font-black text-[#94A3B8] tabular-nums mt-0.5">
                      {batting.expected_baseline_sr ? batting.expected_baseline_sr.toFixed(1) : "-"}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Overall SR</div>
                    <div className="text-lg font-black text-[#94A3B8] tabular-nums mt-0.5">
                      {batting.overall_strike_rate.toFixed(1)}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Pressure Balls</div>
                    <div className="text-lg font-black text-white tabular-nums mt-0.5">
                      {batting.pressure_balls_faced}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Matches Faced</div>
                    <div className="text-lg font-black text-white tabular-nums mt-0.5">
                      {batting.pressure_matches}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Match Consistency</div>
                    <div className="text-lg font-black text-[#34D399] tabular-nums mt-0.5">
                      {batting.match_consistency_pct.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Bowling Card */}
            {bowling && (
              <div className="rounded-[20px] bg-[#0E182D]/75 backdrop-blur-md border border-purple-500/15 p-6 space-y-4 shadow-xl">
                <div className="flex items-center justify-between pb-3 border-b border-purple-500/10">
                  <div className="flex items-center space-x-2">
                    <Shield className="w-5 h-5 text-purple-400" />
                    <h3 className="text-sm font-extrabold text-white uppercase tracking-wider">
                      Bowling Pressure Profile
                    </h3>
                  </div>
                  <span className="text-xs text-[#C084FC] font-bold">
                    Rank #{bowling.rank}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Pressure Econ</div>
                    <div className="text-lg font-black text-white tabular-nums mt-0.5">
                      {bowling.pressure_economy.toFixed(2)}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Phase Par Econ</div>
                    <div className="text-lg font-black text-[#94A3B8] tabular-nums mt-0.5">
                      {bowling.expected_baseline_econ ? bowling.expected_baseline_econ.toFixed(2) : "-"}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Overall Econ</div>
                    <div className="text-lg font-black text-[#94A3B8] tabular-nums mt-0.5">
                      {bowling.overall_economy.toFixed(2)}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Legal Balls</div>
                    <div className="text-lg font-black text-white tabular-nums mt-0.5">
                      {bowling.pressure_legal_balls}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Matches Bowled</div>
                    <div className="text-lg font-black text-white tabular-nums mt-0.5">
                      {bowling.pressure_matches}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-3">
                    <div className="text-[10px] text-[#94A3B8]">Match Consistency</div>
                    <div className="text-lg font-black text-[#34D399] tabular-nums mt-0.5">
                      {bowling.match_consistency_pct.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* PHASE BREAKDOWN PROGRESS BARS */}
          {profile.batting_phase_split && profile.batting_phase_split.length > 0 && (
            <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 space-y-4 shadow-xl">
              <div className="flex items-center space-x-2 pb-2 border-b border-blue-500/10">
                <Layers className="w-5 h-5 text-blue-400" />
                <h3 className="text-sm font-extrabold text-white uppercase tracking-wider">
                  Innings Phase Distribution &amp; Pressure Execution
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                {profile.batting_phase_split.map((phase) => {
                  const phaseSR = phase.pressure_balls > 0
                    ? ((phase.pressure_runs / phase.pressure_balls) * 100).toFixed(1)
                    : ((phase.runs / (phase.balls || 1)) * 100).toFixed(1);

                  const pressureRatio = phase.balls > 0
                    ? Math.round((phase.pressure_balls / phase.balls) * 100)
                    : 0;

                  return (
                    <div key={phase.innings_phase} className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-black text-white uppercase">
                          {phase.innings_phase}
                        </span>
                        <span className="text-xs font-bold text-[#60A5FA] tabular-nums">
                          {phaseSR} SR
                        </span>
                      </div>

                      <div className="w-full bg-[#080E1C] h-2 rounded-full overflow-hidden border border-blue-500/10">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full"
                          style={{ width: `${pressureRatio}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-[#94A3B8]">
                        <span>{phase.pressure_balls} pressure balls</span>
                        <span>{phase.balls} total balls ({pressureRatio}%)</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* MATCH HISTORY LOG */}
          {matchHistory.length > 0 && (
            <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 overflow-hidden shadow-2xl">
              <div className="p-5 border-b border-blue-500/10 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-blue-400" />
                  <h3 className="text-sm font-extrabold text-white uppercase tracking-wider">
                    Recent Match Performance History
                  </h3>
                </div>
                <span className="text-xs text-[#94A3B8]">Last {matchHistory.length} Matches</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-[#0A1224]/90 text-[#94A3B8] uppercase text-[10px] tracking-wider font-extrabold border-b border-blue-500/15 sticky top-0">
                    <tr>
                      <th className="py-3 px-4">Match Date</th>
                      <th className="py-3 px-4">Tournament / Competition</th>
                      <th className="py-3 px-4 text-right">Balls Faced</th>
                      <th className="py-3 px-4 text-right">Total Runs</th>
                      <th className="py-3 px-4 text-right">Pressure Balls</th>
                      <th className="py-3 px-4 text-right">Pressure Runs</th>
                      <th className="py-3 px-4 text-right">Pressure SR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-blue-500/10">
                    {matchHistory.map((m) => {
                      const pSR = m.pressure_balls > 0
                        ? ((m.pressure_runs / m.pressure_balls) * 100).toFixed(1)
                        : "-";

                      return (
                        <tr key={m.match_id} className="hover:bg-blue-600/10 transition-colors">
                          <td className="py-2.5 px-4 font-mono text-[#94A3B8]">
                            {m.match_date ? m.match_date.split("T")[0] : "-"}
                          </td>
                          <td className="py-2.5 px-4 font-bold text-white truncate max-w-xs">
                            {m.comp_name} ({m.season})
                          </td>
                          <td className="py-2.5 px-4 text-right text-white tabular-nums font-semibold">
                            {m.balls_faced}
                          </td>
                          <td className="py-2.5 px-4 text-right text-white tabular-nums font-semibold">
                            {m.runs}
                          </td>
                          <td className="py-2.5 px-4 text-right text-[#60A5FA] tabular-nums font-black">
                            {m.pressure_balls}
                          </td>
                          <td className="py-2.5 px-4 text-right text-[#60A5FA] tabular-nums font-black">
                            {m.pressure_runs}
                          </td>
                          <td className="py-2.5 px-4 text-right text-white tabular-nums font-bold">
                            {pSR}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          icon={UserCheck}
          title="No Candidate Selected"
          description="Select any candidate from the Player Rankings table or use the global search to view their comprehensive career profile."
        />
      )}
    </div>
  );
}
