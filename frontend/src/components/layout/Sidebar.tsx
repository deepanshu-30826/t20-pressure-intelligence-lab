"use client";

import React from "react";
import {
  Activity,
  Flame,
  Shield,
  Award,
  BookOpen,
  Layers,
  Database,
  Crosshair,
  UserCheck,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}

export function Sidebar({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  mobileOpen,
  setMobileOpen,
}: SidebarProps) {
  const navItems = [
    { id: "overview", label: "Overview", icon: Activity, badge: "Live" },
    { id: "rankings", label: "Player Rankings", icon: Award },
    { id: "batters", label: "Batter Analytics", icon: Flame },
    { id: "bowlers", label: "Bowler Analytics", icon: Shield },
    { id: "profile", label: "Player Profiles", icon: UserCheck },
    { id: "pressure", label: "Pressure Engine", icon: Layers },
    { id: "audit", label: "Data Intelligence", icon: Database },
    { id: "methodology", label: "Methodology", icon: BookOpen },
  ];

  const handleNavClick = (id: string) => {
    setActiveTab(id);
    if (mobileOpen) {
      setMobileOpen(false);
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-40 lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-50 flex flex-col justify-between bg-[#080E1C]/95 backdrop-blur-xl border-r border-blue-500/10 transition-all duration-300 ease-in-out ${
          collapsed ? "w-20" : "w-64"
        } ${
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div>
          {/* Brand Header */}
          <div className="h-16 px-5 border-b border-blue-500/10 flex items-center justify-between">
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#3B82F6] via-[#6366F1] to-[#8B5CF6] p-[1.5px] shrink-0 shadow-lg shadow-blue-500/20">
                <div className="w-full h-full bg-[#080E1C] rounded-[10px] flex items-center justify-center text-[#60A5FA]">
                  <Crosshair className="w-5 h-5 animate-spin-slow" />
                </div>
              </div>
              {!collapsed && (
                <div className="truncate">
                  <div className="font-black text-sm tracking-wide text-white flex items-center space-x-1.5">
                    <span>T20 PRESSURE</span>
                  </div>
                  <div className="text-[10px] text-[#60A5FA] uppercase tracking-widest font-bold">
                    Intelligence Lab
                  </div>
                </div>
              )}
            </div>

            {/* Collapse toggle button on desktop */}
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="hidden lg:flex w-7 h-7 rounded-lg bg-[#0F1C36] hover:bg-blue-600/20 text-[#94A3B8] hover:text-[#60A5FA] items-center justify-center transition-colors border border-blue-500/15"
              title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {collapsed ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronLeft className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  title={collapsed ? item.label : undefined}
                  className={`w-full flex items-center rounded-xl text-xs font-semibold transition-all duration-200 group relative ${
                    collapsed ? "justify-center p-3" : "px-3.5 py-2.5 space-x-3"
                  } ${
                    isActive
                      ? "bg-gradient-to-r from-blue-600/20 to-violet-600/10 text-[#60A5FA] border border-blue-500/30 shadow-md shadow-blue-500/10"
                      : "text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#0E1A33]/60 border border-transparent"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 shrink-0 transition-transform duration-200 group-hover:scale-110 ${
                      isActive ? "text-[#60A5FA]" : "text-[#94A3B8] group-hover:text-[#60A5FA]"
                    }`}
                  />
                  {!collapsed && (
                    <span className="truncate text-left flex-1">{item.label}</span>
                  )}
                  {!collapsed && item.badge && (
                    <span className="text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full bg-blue-500/20 text-[#60A5FA] border border-blue-500/30">
                      {item.badge}
                    </span>
                  )}

                  {/* Active Indicator Bar on left */}
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-gradient-to-b from-[#3B82F6] to-[#8B5CF6] rounded-r-full shadow-sm shadow-blue-400" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer Info */}
        <div className={`p-4 border-t border-blue-500/10 ${collapsed ? "px-2 text-center" : ""}`}>
          {!collapsed ? (
            <div className="p-3 rounded-xl bg-[#0D1629]/80 border border-blue-500/15 space-y-2">
              <div className="flex items-center space-x-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#3B82F6] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#3B82F6]"></span>
                </span>
                <span className="text-[11px] font-bold text-[#F1F5F9]">Engine Online</span>
              </div>
              <p className="text-[10px] text-[#94A3B8] leading-tight">
                IPL 2022–2026 + T20I Context-Only Structural Model
              </p>
            </div>
          ) : (
            <div className="flex justify-center">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#3B82F6] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#3B82F6]"></span>
              </span>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
