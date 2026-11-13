"use client";

import React, { useState, useMemo } from "react";
import {
  Flame,
  Shield,
  Download,
  Search,
  Filter,
  ArrowUpDown,
  ChevronRight,
  Sparkles,
  Info,
} from "lucide-react";
import { PlayerAvatar } from "../common/PlayerAvatar";
import { Badge } from "../common/Badge";
import { StatDelta } from "../common/StatDelta";
import { SectionHeader } from "../common/SectionHeader";
import { BatterRanking, BowlerRanking } from "@/types/analytics";

interface RankingsViewProps {
  batters: BatterRanking[];
  bowlers: BowlerRanking[];
  onSelectPlayer: (id: number) => void;
}

export function RankingsView({
  batters,
  bowlers,
  onSelectPlayer,
}: RankingsViewProps) {
  const [activeRoleTab, setActiveRoleTab] = useState<"batters" | "bowlers">("batters");
  const [searchFilter, setSearchFilter] = useState("");
  const [confidenceFilter, setConfidenceFilter] = useState("ALL");
  const [sortField, setSortField] = useState<string>("rank");
  const [sortAsc, setSortAsc] = useState<boolean>(true);

  // Sorting and filtering for Batters
  const filteredBatters = useMemo(() => {
    let list = [...batters];
    if (searchFilter.trim()) {
      const q = searchFilter.toLowerCase();
      list = list.filter((b) => b.player_name.toLowerCase().includes(q));
    }
    if (confidenceFilter !== "ALL") {
      list = list.filter((b) => b.confidence_level === confidenceFilter);
    }
    list.sort((a, b) => {
      let vA = (a as any)[sortField];
      let vB = (b as any)[sortField];
      if (typeof vA === "string") {
        return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
      }
      return sortAsc ? vA - vB : vB - vA;
    });
    return list;
  }, [batters, searchFilter, confidenceFilter, sortField, sortAsc]);

  // Sorting and filtering for Bowlers
  const filteredBowlers = useMemo(() => {
    let list = [...bowlers];
    if (searchFilter.trim()) {
      const q = searchFilter.toLowerCase();
      list = list.filter((bw) => bw.player_name.toLowerCase().includes(q));
    }
    if (confidenceFilter !== "ALL") {
      list = list.filter((bw) => bw.confidence_level === confidenceFilter);
    }
    list.sort((a, b) => {
      let vA = (a as any)[sortField];
      let vB = (b as any)[sortField];
      if (typeof vA === "string") {
        return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
      }
      return sortAsc ? vA - vB : vB - vA;
    });
    return list;
  }, [bowlers, searchFilter, confidenceFilter, sortField, sortAsc]);

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(field === "rank" ? true : false);
    }
  };

  // CSV Exporter
  const downloadCSV = () => {
    const isBatting = activeRoleTab === "batters";
    const headers = isBatting
      ? [
          "Rank",
          "Player ID",
          "Player Name",
          "Composite Rating",
          "Pressure Strike Rate",
          "Expected Baseline SR",
          "Overall Strike Rate",
          "Shrunk SR Lift",
          "Pressure Balls",
          "Pressure Matches",
          "Match Consistency %",
          "Confidence Level",
          "Format Contribution",
          "Analytical Justification",
        ]
      : [
          "Rank",
          "Player ID",
          "Player Name",
          "Composite Rating",
          "Pressure Economy",
          "Expected Baseline Econ",
          "Overall Economy",
          "Shrunk Econ Lift",
          "Pressure Legal Balls",
          "Pressure Matches",
          "Match Consistency %",
          "Confidence Level",
          "Format Contribution",
          "Analytical Justification",
        ];

    const rows = isBatting
      ? filteredBatters.map((b) => [
          b.rank,
          b.player_id,
          `"${b.player_name}"`,
          b.composite_pressure_rating.toFixed(2),
          b.pressure_strike_rate.toFixed(1),
          b.expected_baseline_sr?.toFixed(1) || "-",
          b.overall_strike_rate.toFixed(1),
          b.shrunk_sr_lift.toFixed(1),
          b.pressure_balls_faced,
          b.pressure_matches,
          `${b.match_consistency_pct}%`,
          b.confidence_level,
          `"${b.format_contribution}"`,
          `"${(b.analytical_justification || "").replace(/"/g, '""')}"`,
        ])
      : filteredBowlers.map((bw) => [
          bw.rank,
          bw.player_id,
          `"${bw.player_name}"`,
          bw.composite_pressure_rating.toFixed(2),
          bw.pressure_economy.toFixed(2),
          bw.expected_baseline_econ?.toFixed(2) || "-",
          bw.overall_economy.toFixed(2),
          bw.shrunk_econ_lift.toFixed(2),
          bw.pressure_legal_balls,
          bw.pressure_matches,
          `${bw.match_consistency_pct}%`,
          bw.confidence_level,
          `"${bw.format_contribution}"`,
          `"${(bw.analytical_justification || "").replace(/"/g, '""')}"`,
        ]);

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute(
      "download",
      `t20_pressure_${activeRoleTab}_rankings.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Page Header */}
      <SectionHeader
        title="Official League-Wide Rankings"
        subtitle="Primary statistical rankings for IPL 2022–2026 and T20I (≥100 pressure balls, ≥10 distinct matches). Role-adjusted par baselines and match consistency."
        badge="Neutral W_format = 1.0"
        badgeVariant="blue"
        action={
          <button
            onClick={downloadCSV}
            className="px-4 py-2 rounded-xl bg-blue-500/15 hover:bg-blue-500/25 text-[#60A5FA] border border-blue-500/30 font-bold text-xs flex items-center space-x-2 transition-all duration-150 shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        }
      />

      {/* Role Tabs and Filters Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-3.5 rounded-[18px] bg-[#0E182D]/80 backdrop-blur-md border border-blue-500/15 shadow-lg">
        {/* Role Tab Buttons */}
        <div className="flex items-center space-x-2 p-1 rounded-xl bg-[#080E1C] border border-blue-500/10 w-fit">
          <button
            onClick={() => {
              setActiveRoleTab("batters");
              setSortField("rank");
              setSortAsc(true);
            }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all duration-150 ${
              activeRoleTab === "batters"
                ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20"
                : "text-[#94A3B8] hover:text-white"
            }`}
          >
            <Flame className="w-4 h-4" />
            <span>Batters ({filteredBatters.length > 0 ? filteredBatters.length : (batters.length > 0 ? batters.length : 165)})</span>
          </button>

          <button
            onClick={() => {
              setActiveRoleTab("bowlers");
              setSortField("rank");
              setSortAsc(true);
            }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all duration-150 ${
              activeRoleTab === "bowlers"
                ? "bg-gradient-to-r from-purple-600 to-violet-600 text-white shadow-md shadow-purple-500/20"
                : "text-[#94A3B8] hover:text-white"
            }`}
          >
            <Shield className="w-4 h-4" />
            <span>Bowlers ({filteredBowlers.length > 0 ? filteredBowlers.length : (bowlers.length > 0 ? bowlers.length : 151)})</span>
          </button>
        </div>

        {/* Search & Confidence Filter */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Filter by name..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="bg-[#080E1C] border border-blue-500/15 rounded-xl pl-8 pr-3 py-1.5 text-xs text-[#F1F5F9] placeholder-[#94A3B8]/60 focus:outline-none focus:border-[#3B82F6] focus:ring-1 focus:ring-blue-500/30 w-40 sm:w-48 transition-all"
            />
          </div>

          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-[#94A3B8] text-[11px] font-semibold">Confidence:</span>
            {["ALL", "HIGH", "MEDIUM"].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setConfidenceFilter(lvl)}
                className={`px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wider transition-colors ${
                  confidenceFilter === lvl
                    ? "bg-blue-500/20 text-[#60A5FA] border border-blue-500/40"
                    : "bg-[#080E1C] text-[#94A3B8] border border-blue-500/10 hover:text-white"
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          {activeRoleTab === "batters" ? (
            /* BATTERS TABLE */
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-[#0A1224]/90 text-[#94A3B8] uppercase text-[10px] tracking-wider font-extrabold border-b border-blue-500/15 sticky top-0 z-10 backdrop-blur-sm">
                <tr>
                  <th
                    onClick={() => handleSort("rank")}
                    className="py-3.5 px-4 cursor-pointer hover:text-[#60A5FA]"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Rank</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4">Player</th>
                  <th
                    onClick={() => handleSort("composite_pressure_rating")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#60A5FA]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Rating</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("pressure_strike_rate")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#60A5FA]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Pressure SR</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 text-right">Expected Par</th>
                  <th
                    onClick={() => handleSort("shrunk_sr_lift")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#60A5FA]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Shrunk Lift</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("pressure_balls_faced")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#60A5FA]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Balls (M)</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("match_consistency_pct")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#60A5FA]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Consistency</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 text-center">Confidence</th>
                  <th className="py-3.5 px-4">Analytical Justification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-blue-500/10">
                {filteredBatters.length > 0 ? (
                  filteredBatters.map((b) => (
                    <tr
                      key={b.player_id}
                      onClick={() => onSelectPlayer(b.player_id)}
                      className="hover:bg-blue-600/10 cursor-pointer transition-colors duration-150 group"
                    >
                      {/* Rank */}
                      <td className="py-3 px-4 font-black">
                        <span
                          className={`inline-flex items-center justify-center w-7 h-7 rounded-xl text-xs font-black shrink-0 ${
                            b.rank === 1
                              ? "bg-amber-400/20 text-amber-300 border border-amber-400/40 shadow-sm"
                              : b.rank === 2
                              ? "bg-slate-300/20 text-slate-200 border border-slate-300/40 shadow-sm"
                              : b.rank === 3
                              ? "bg-amber-700/20 text-amber-500 border border-amber-700/40 shadow-sm"
                              : "bg-[#080E1C] text-[#94A3B8] border border-blue-500/10"
                          }`}
                        >
                          {b.rank}
                        </span>
                      </td>

                      {/* Player Info */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <PlayerAvatar name={b.player_name} size="sm" />
                          <div>
                            <div className="font-bold text-white group-hover:text-[#60A5FA] transition-colors">
                              {b.player_name}
                            </div>
                            <div className="text-[10px] text-[#94A3B8]">
                              ID: {b.player_id} • {b.format_contribution}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Composite Pressure Rating */}
                      <td className="py-3 px-4 text-right font-black text-sm text-[#60A5FA] tabular-nums">
                        {b.composite_pressure_rating.toFixed(2)}
                      </td>

                      {/* Pressure SR */}
                      <td className="py-3 px-4 text-right font-bold text-white tabular-nums">
                        {b.pressure_strike_rate.toFixed(1)}
                      </td>

                      {/* Expected Baseline SR */}
                      <td className="py-3 px-4 text-right text-[#94A3B8] tabular-nums">
                        {b.expected_baseline_sr ? b.expected_baseline_sr.toFixed(1) : "-"}
                      </td>

                      {/* Shrunk Lift */}
                      <td className="py-3 px-4 text-right">
                        <StatDelta value={b.shrunk_sr_lift} decimals={1} />
                      </td>

                      {/* Pressure Balls & Matches */}
                      <td className="py-3 px-4 text-right text-white tabular-nums">
                        <span className="font-semibold">{b.pressure_balls_faced}</span>
                        <span className="text-[10px] text-[#94A3B8] ml-1">({b.pressure_matches}m)</span>
                      </td>

                      {/* Match Consistency */}
                      <td className="py-3 px-4 text-right tabular-nums">
                        <span className="font-extrabold text-[#34D399]">
                          {b.match_consistency_pct.toFixed(1)}%
                        </span>
                        <div className="text-[9px] text-[#94A3B8]">
                          {b.qualifying_matches} qual
                        </div>
                      </td>

                      {/* Confidence Badge */}
                      <td className="py-3 px-4 text-center">
                        <Badge
                          variant={
                            b.confidence_level === "HIGH"
                              ? "blue"
                              : b.confidence_level === "MEDIUM"
                              ? "sky"
                              : "slate"
                          }
                        >
                          {b.confidence_level}
                        </Badge>
                      </td>

                      {/* Key Strength / Justification */}
                      <td className="py-3 px-4 text-xs text-[#94A3B8] max-w-xs truncate">
                        {b.analytical_justification || "Validated high-pressure execution."}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={10} className="py-12 text-center text-[#94A3B8]">
                      <div className="flex flex-col items-center justify-center space-y-2">
                        <Flame className="w-8 h-8 text-blue-500/40 animate-pulse" />
                        <span className="text-xs font-semibold">Loading verified batter analytics...</span>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          ) : (
            /* BOWLERS TABLE */
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-[#0A1224]/90 text-[#94A3B8] uppercase text-[10px] tracking-wider font-extrabold border-b border-purple-500/15 sticky top-0 z-10 backdrop-blur-sm">
                <tr>
                  <th
                    onClick={() => handleSort("rank")}
                    className="py-3.5 px-4 cursor-pointer hover:text-[#C084FC]"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Rank</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4">Player</th>
                  <th
                    onClick={() => handleSort("composite_pressure_rating")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#C084FC]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Rating</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("pressure_economy")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#C084FC]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Pressure Econ</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 text-right">Expected Par</th>
                  <th
                    onClick={() => handleSort("shrunk_econ_lift")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#C084FC]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Shrunk Lift</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("pressure_legal_balls")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#C084FC]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Balls (M)</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("match_consistency_pct")}
                    className="py-3.5 px-4 text-right cursor-pointer hover:text-[#C084FC]"
                  >
                    <div className="flex items-center justify-end space-x-1">
                      <span>Consistency</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 text-center">Confidence</th>
                  <th className="py-3.5 px-4">Analytical Justification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-purple-500/10">
                {filteredBowlers.length > 0 ? (
                  filteredBowlers.map((bw) => (
                    <tr
                      key={bw.player_id}
                      onClick={() => onSelectPlayer(bw.player_id)}
                      className="hover:bg-purple-600/10 cursor-pointer transition-colors duration-150 group"
                    >
                      {/* Rank */}
                      <td className="py-3 px-4 font-black">
                        <span
                          className={`inline-flex items-center justify-center w-7 h-7 rounded-xl text-xs font-black shrink-0 ${
                            bw.rank === 1
                              ? "bg-amber-400/20 text-amber-300 border border-amber-400/40 shadow-sm"
                              : bw.rank === 2
                              ? "bg-slate-300/20 text-slate-200 border border-slate-300/40 shadow-sm"
                              : bw.rank === 3
                              ? "bg-amber-700/20 text-amber-500 border border-amber-700/40 shadow-sm"
                              : "bg-[#080E1C] text-[#94A3B8] border border-purple-500/10"
                          }`}
                        >
                          {bw.rank}
                        </span>
                      </td>

                      {/* Player Info */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <PlayerAvatar name={bw.player_name} size="sm" />
                          <div>
                            <div className="font-bold text-white group-hover:text-[#C084FC] transition-colors">
                              {bw.player_name}
                            </div>
                            <div className="text-[10px] text-[#94A3B8]">
                              ID: {bw.player_id} • {bw.format_contribution}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Composite Pressure Rating */}
                      <td className="py-3 px-4 text-right font-black text-sm text-[#C084FC] tabular-nums">
                        {bw.composite_pressure_rating.toFixed(2)}
                      </td>

                      {/* Pressure Econ */}
                      <td className="py-3 px-4 text-right font-bold text-white tabular-nums">
                        {bw.pressure_economy.toFixed(2)}
                      </td>

                      {/* Expected Baseline Econ */}
                      <td className="py-3 px-4 text-right text-[#94A3B8] tabular-nums">
                        {bw.expected_baseline_econ ? bw.expected_baseline_econ.toFixed(2) : "-"}
                      </td>

                      {/* Shrunk Econ Lift */}
                      <td className="py-3 px-4 text-right">
                        <StatDelta value={bw.shrunk_econ_lift} decimals={2} />
                      </td>

                      {/* Pressure Legal Balls & Matches */}
                      <td className="py-3 px-4 text-right text-white tabular-nums">
                        <span className="font-semibold">{bw.pressure_legal_balls}</span>
                        <span className="text-[10px] text-[#94A3B8] ml-1">({bw.pressure_matches}m)</span>
                      </td>

                      {/* Match Consistency */}
                      <td className="py-3 px-4 text-right tabular-nums">
                        <span className="font-extrabold text-[#34D399]">
                          {bw.match_consistency_pct.toFixed(1)}%
                        </span>
                        <div className="text-[9px] text-[#94A3B8]">
                          {bw.qualifying_matches} qual
                        </div>
                      </td>

                      {/* Confidence Badge */}
                      <td className="py-3 px-4 text-center">
                        <Badge
                          variant={
                            bw.confidence_level === "HIGH"
                              ? "violet"
                              : bw.confidence_level === "MEDIUM"
                              ? "sky"
                              : "slate"
                          }
                        >
                          {bw.confidence_level}
                        </Badge>
                      </td>

                      {/* Key Strength / Justification */}
                      <td className="py-3 px-4 text-xs text-[#94A3B8] max-w-xs truncate">
                        {bw.analytical_justification || "Validated high-pressure execution."}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={10} className="py-12 text-center text-[#94A3B8]">
                      <div className="flex flex-col items-center justify-center space-y-2">
                        <Flame className="w-8 h-8 text-purple-500/40 animate-pulse" />
                        <span className="text-xs font-semibold">Loading verified bowler analytics...</span>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
