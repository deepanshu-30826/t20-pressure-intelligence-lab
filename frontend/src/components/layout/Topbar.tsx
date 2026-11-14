"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Search,
  Menu,
  Activity,
  Layers,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  User,
} from "lucide-react";
import { Badge } from "../common/Badge";
import { BatterRanking, BowlerRanking } from "@/types/analytics";
import { api } from "@/lib/api";

interface TopbarProps {
  activeTab: string;
  setMobileOpen: (open: boolean) => void;
  onSelectPlayer: (playerId: number) => void;
  batters: BatterRanking[];
  bowlers: BowlerRanking[];
}

export function Topbar({
  activeTab,
  setMobileOpen,
  onSelectPlayer,
  batters,
  bowlers,
}: TopbarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Array<{ id: number; name: string; role: string; rating: number; rank: number }>>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  // Ping actual backend health check
  useEffect(() => {
    api.getHealth().then((res) => {
      setApiConnected(res.data ? true : false);
    });
  }, []);

  // Filter player results on search query change
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsDropdownOpen(false);
      return;
    }

    const q = searchQuery.toLowerCase();
    const matchedBatters = batters
      .filter((b) => b.player_name.toLowerCase().includes(q))
      .slice(0, 4)
      .map((b) => ({
        id: b.player_id,
        name: b.player_name,
        role: "Batter",
        rating: b.composite_pressure_rating,
        rank: b.rank,
      }));

    const matchedBowlers = bowlers
      .filter((bw) => bw.player_name.toLowerCase().includes(q))
      .slice(0, 4)
      .map((bw) => ({
        id: bw.player_id,
        name: bw.player_name,
        role: "Bowler",
        rating: bw.composite_pressure_rating,
        rank: bw.rank,
      }));

    const combined = [...matchedBatters, ...matchedBowlers];
    setSearchResults(combined);
    setIsDropdownOpen(combined.length > 0);
  }, [searchQuery, batters, bowlers]);

  // Click outside search dismisses dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const tabLabels: Record<string, string> = {
    overview: "Overview Dashboard",
    rankings: "Player Rankings & Leaderboard",
    batters: "Batter Pressure Analytics",
    bowlers: "Bowler Pressure Analytics",
    profile: "Player Performance Profile",
    pressure: "Pressure Engine Architecture",
    audit: "Data Intelligence & Audit",
    methodology: "Methodology & Mathematics",
  };

  return (
    <header className="h-16 px-4 md:px-8 border-b border-blue-500/10 bg-[#080E1C]/90 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between">
      {/* Left: Mobile Toggle & Page Breadcrumb */}
      <div className="flex items-center space-x-3 md:space-x-4">
        <button
          onClick={() => setMobileOpen(true)}
          className="lg:hidden p-2 rounded-xl bg-[#0F1C36] text-[#94A3B8] hover:text-[#60A5FA] border border-blue-500/15"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2.5">
          <h1 className="text-sm md:text-base font-bold text-white tracking-tight">
            {tabLabels[activeTab] || "Analytics Hub"}
          </h1>
          <span className="hidden sm:inline-flex text-blue-400/40">•</span>
          <span className="hidden sm:inline-flex px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-500/10 text-[#60A5FA] border border-blue-500/20">
            IPL 2022–2026 + T20I
          </span>
        </div>
      </div>

      {/* Right: Search Bar & System Status */}
      <div className="flex items-center space-x-3 md:space-x-5">
        {/* Global Player Search */}
        <div ref={searchRef} className="relative w-44 sm:w-64 md:w-72">
          <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder="Search candidate player..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => {
              if (searchResults.length > 0) setIsDropdownOpen(true);
            }}
            className="w-full bg-[#0D1629] border border-blue-500/15 rounded-xl pl-9 pr-3 py-1.5 text-xs text-[#F1F5F9] placeholder-[#94A3B8]/60 focus:outline-none focus:border-[#3B82F6] focus:ring-1 focus:ring-blue-500/30 transition-all"
          />

          {/* Autocomplete Dropdown */}
          {isDropdownOpen && (
            <div className="absolute left-0 right-0 mt-1.5 bg-[#0D1629] border border-blue-500/30 rounded-xl shadow-2xl overflow-hidden z-50 divide-y divide-blue-500/10 backdrop-blur-xl">
              {searchResults.map((item) => (
                <button
                  key={`${item.role}-${item.id}`}
                  onClick={() => {
                    onSelectPlayer(item.id);
                    setIsDropdownOpen(false);
                    setSearchQuery("");
                  }}
                  className="w-full px-3.5 py-2.5 text-left flex items-center justify-between hover:bg-[#142347] transition-colors"
                >
                  <div className="flex items-center space-x-2.5 truncate">
                    <User className="w-3.5 h-3.5 text-[#60A5FA] shrink-0" />
                    <div className="truncate">
                      <div className="text-xs font-bold text-white truncate">
                        {item.name}
                      </div>
                      <div className="text-[10px] text-[#94A3B8]">
                        {item.role} • Rank #{item.rank}
                      </div>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="text-xs font-extrabold text-[#60A5FA] tabular-nums">
                      {item.rating.toFixed(2)}
                    </div>
                    <div className="text-[9px] text-[#94A3B8] uppercase">Rating</div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Backend Connectivity Status Indicator */}
        <div className="hidden md:flex items-center space-x-2 pl-3 border-l border-blue-500/15 text-xs">
          {apiConnected === true ? (
            <div className="flex items-center space-x-1.5 text-[#34D399]">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span className="font-semibold text-[11px]">API Online</span>
            </div>
          ) : apiConnected === false ? (
            <div className="flex items-center space-x-1.5 text-[#EF4444]">
              <AlertCircle className="w-3.5 h-3.5" />
              <span className="font-semibold text-[11px]">Offline</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 text-[#94A3B8]">
              <span className="w-2 h-2 rounded-full bg-[#94A3B8]" />
              <span className="text-[11px]">Connecting...</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
