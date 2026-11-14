"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { OverviewView } from "@/components/views/OverviewView";
import { RankingsView } from "@/components/views/RankingsView";
import { BatterAnalyticsView } from "@/components/views/BatterAnalyticsView";
import { BowlerAnalyticsView } from "@/components/views/BowlerAnalyticsView";
import { PlayerProfileView } from "@/components/views/PlayerProfileView";
import { PressureEngineView } from "@/components/views/PressureEngineView";
import { DataIntelligenceView } from "@/components/views/DataIntelligenceView";
import { MethodologyView } from "@/components/views/MethodologyView";
import { EmptyState } from "@/components/common/EmptyState";
import { AlertCircle, RefreshCw } from "lucide-react";
import { OverviewData, BatterRanking, BowlerRanking } from "@/types/analytics";
import { api } from "@/lib/api";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [collapsed, setCollapsed] = useState<boolean>(false);
  const [mobileOpen, setMobileOpen] = useState<boolean>(false);

  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [batters, setBatters] = useState<BatterRanking[]>([]);
  const [bowlers, setBowlers] = useState<BowlerRanking[]>([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  
  const [loading, setLoading] = useState<boolean>(true);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Resilient, sequential data loading with zero dependency array thrash
  const loadData = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);

    try {
      // 1. Fetch overview
      const overviewRes = await api.getOverview();
      if (overviewRes.data) {
        setOverview(overviewRes.data);
      }

      // 2. Fetch all eligible batters
      const battersRes = await api.getBatters(200);
      if (battersRes.data && Array.isArray(battersRes.data) && battersRes.data.length > 0) {
        setBatters(battersRes.data);
        setSelectedPlayerId((prev) => prev ?? battersRes.data![0].player_id);
      }

      // 3. Fetch all eligible bowlers
      const bowlersRes = await api.getBowlers(200);
      if (bowlersRes.data && Array.isArray(bowlersRes.data) && bowlersRes.data.length > 0) {
        setBowlers(bowlersRes.data);
      }

      if (!overviewRes.data && (!battersRes.data || battersRes.data.length === 0) && (!bowlersRes.data || bowlersRes.data.length === 0)) {
        setConnectionError("Analytics engine currently unreachable. Verify that backend service is running and accessible.");
      }
    } catch (err: any) {
      setConnectionError(err.message || "Failed to communicate with analytics backend.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Sync tab with URL query param on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const tabParam = params.get("tab");
      if (tabParam) {
        setActiveTab(tabParam);
      }
    }
    loadData();
  }, [loadData]);

  const handleSelectPlayer = (playerId: number) => {
    setSelectedPlayerId(playerId);
    setActiveTab("profile");
  };

  return (
    <div className="flex h-screen bg-[#060A13] text-[#F1F5F9] overflow-hidden">
      {/* FIXED COLLAPSIBLE SIDEBAR */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      {/* MAIN ANALYTICAL WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* STICKY TOPBAR */}
        <Topbar
          activeTab={activeTab}
          setMobileOpen={setMobileOpen}
          onSelectPlayer={handleSelectPlayer}
          batters={batters}
          bowlers={bowlers}
        />

        {/* VIEW CONTAINER */}
        <main className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
          {connectionError && batters.length === 0 ? (
            <div className="p-8 max-w-2xl mx-auto">
              <EmptyState
                icon={AlertCircle}
                title="Analytics Engine Connection Notice"
                description={connectionError}
                actionText="Retry Connection"
                onAction={loadData}
              />
            </div>
          ) : (
            <>
              {activeTab === "overview" && (
                <OverviewView
                  overview={overview}
                  batters={batters}
                  bowlers={bowlers}
                  onNavigateTab={setActiveTab}
                  onSelectPlayer={handleSelectPlayer}
                />
              )}

              {activeTab === "rankings" && (
                <RankingsView
                  batters={batters}
                  bowlers={bowlers}
                  onSelectPlayer={handleSelectPlayer}
                />
              )}

              {activeTab === "batters" && (
                <BatterAnalyticsView
                  batters={batters}
                  onSelectPlayer={handleSelectPlayer}
                />
              )}

              {activeTab === "bowlers" && (
                <BowlerAnalyticsView
                  bowlers={bowlers}
                  onSelectPlayer={handleSelectPlayer}
                />
              )}

              {activeTab === "profile" && (
                <PlayerProfileView
                  selectedPlayerId={selectedPlayerId}
                  batters={batters}
                  bowlers={bowlers}
                  onSelectPlayer={setSelectedPlayerId}
                />
              )}

              {activeTab === "pressure" && <PressureEngineView />}

              {activeTab === "audit" && <DataIntelligenceView />}

              {activeTab === "methodology" && <MethodologyView />}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
