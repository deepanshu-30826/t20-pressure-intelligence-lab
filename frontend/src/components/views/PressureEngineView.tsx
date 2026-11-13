"use client";

import React, { useState } from "react";
import {
  Layers,
  Zap,
  Activity,
  Sliders,
  ShieldAlert,
  CheckCircle2,
  Lock,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { SectionHeader } from "../common/SectionHeader";
import { Badge } from "../common/Badge";

export function PressureEngineView() {
  // Interactive match context simulator state
  const [ballsRemaining, setBallsRemaining] = useState<number>(30); // 5 overs
  const [wicketsLost, setWicketsLost] = useState<number>(5);
  const [isKnockout, setIsKnockout] = useState<boolean>(false);

  // Compute live simulated pressure score based on exact formula
  const wicketsInHand = Math.max(0, 10 - wicketsLost);
  const resourceRatio = (wicketsInHand / 10.0) * (ballsRemaining / 120.0);
  const resourceScarcity = Math.max(0, Math.min(1.0, 1.0 - resourceRatio));

  const matchUrgency = Math.max(0, Math.min(1.0, 1.0 - Math.pow(ballsRemaining / 120.0, 1.5)));
  const wicketScarcity = Math.max(0, Math.min(1.0, Math.pow(wicketsLost / 10.0, 1.2)));

  const knockoutMultiplier = isKnockout ? 1.10 : 1.0;

  const rawScore = (0.45 * resourceScarcity + 0.35 * matchUrgency + 0.20 * wicketScarcity) * 100 * knockoutMultiplier;
  const simulatedPressure = Math.min(100.0, Math.max(0.0, rawScore));
  const isHighPressure = simulatedPressure >= 60.0;

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <SectionHeader
        title="Pre-Delivery Pressure Engine"
        subtitle="Context-only structural pressure architecture. Formulated strictly prior to ball execution to guarantee zero data leakage."
        badge="Threshold P ≥ 60.0"
        badgeVariant="blue"
      />

      {/* CORE FORMULATION CARD */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/20 p-6 md:p-8 space-y-6 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-blue-500/10 relative z-10">
          <div>
            <div className="text-xs font-bold text-[#60A5FA] uppercase tracking-wider mb-1">
              Mathematical Specification
            </div>
            <h3 className="text-xl font-black text-white">
              The Context-Only Structural Pressure Equation
            </h3>
          </div>
          <Badge variant="blue" size="md">
            Leakage-Proof • Pre-Delivery Only
          </Badge>
        </div>

        {/* Formula Box */}
        <div className="p-5 rounded-2xl bg-[#080E1C] border border-blue-500/30 font-mono text-center text-sm md:text-base text-white space-y-2 shadow-lg shadow-blue-500/10 relative z-10">
          <div className="text-[#60A5FA] font-black tracking-wide">
            Pressure_context = (0.45 × Resource_Scarcity + 0.35 × Match_Urgency + 0.20 × Wicket_Scarcity) × 100 × M_knockout
          </div>
          <div className="text-[11px] text-[#94A3B8] font-sans">
            Where Pressure ≥ 60.0 categorizes a delivery as High-Pressure (Tier 1 Qualification).
          </div>
        </div>

        {/* 3 Component Breakdown Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-black text-[#60A5FA]">Component 1</span>
              <span className="text-xs font-extrabold text-white">Weight: 45%</span>
            </div>
            <h4 className="text-sm font-bold text-white">Resource Scarcity</h4>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Captures the joint depletion of remaining legal balls and wickets in hand:
              <code className="block bg-[#080E1C] p-2 rounded-lg mt-2 text-[#60A5FA] text-[11px] border border-blue-500/10">
                1.0 - (W_hand / 10) × (Balls / 120)
              </code>
            </p>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-black text-[#38BDF8]">Component 2</span>
              <span className="text-xs font-extrabold text-white">Weight: 35%</span>
            </div>
            <h4 className="text-sm font-bold text-white">Match Urgency</h4>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Models the non-linear compression of match time approaching death overs:
              <code className="block bg-[#080E1C] p-2 rounded-lg mt-2 text-[#38BDF8] text-[11px] border border-blue-500/10">
                1.0 - (Balls / 120)^1.5
              </code>
            </p>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-black text-[#C084FC]">Component 3</span>
              <span className="text-xs font-extrabold text-white">Weight: 20%</span>
            </div>
            <h4 className="text-sm font-bold text-white">Wicket Scarcity</h4>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Exponential pressure escalation as batting depth collapses:
              <code className="block bg-[#080E1C] p-2 rounded-lg mt-2 text-[#C084FC] text-[11px] border border-purple-500/10">
                (Wickets_Lost / 10)^1.2
              </code>
            </p>
          </div>
        </div>
      </div>

      {/* INTERACTIVE PRESSURE CALCULATOR / SIMULATOR */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 md:p-8 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-blue-500/10">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-[#60A5FA]">
              <Sliders className="w-4 h-4" />
            </div>
            <h3 className="text-base font-extrabold text-white uppercase tracking-wider">
              Interactive Match Context Simulator
            </h3>
          </div>
          <span className="text-xs text-[#94A3B8]">Test any match scenario live</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
          {/* Controls */}
          <div className="lg:col-span-2 space-y-5">
            {/* Balls Remaining Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#94A3B8] font-semibold">Balls Remaining:</span>
                <span className="font-mono font-bold text-white">
                  {ballsRemaining} balls ({Math.floor(ballsRemaining / 6)}.{ballsRemaining % 6} overs)
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="120"
                value={ballsRemaining}
                onChange={(e) => setBallsRemaining(Number(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-[#94A3B8]">
                <span>1 ball (Final delivery)</span>
                <span>60 balls (10th over)</span>
                <span>120 balls (Ball 1)</span>
              </div>
            </div>

            {/* Wickets Lost Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#94A3B8] font-semibold">Wickets Lost:</span>
                <span className="font-mono font-bold text-white">
                  {wicketsLost} down ({wicketsInHand} wickets in hand)
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="9"
                value={wicketsLost}
                onChange={(e) => setWicketsLost(Number(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-[#94A3B8]">
                <span>0 wickets (Full depth)</span>
                <span>5 wickets (Half side)</span>
                <span>9 wickets (Last pair)</span>
              </div>
            </div>

            {/* Knockout Match Toggle */}
            <div className="flex items-center space-x-3 pt-2">
              <input
                type="checkbox"
                id="knockoutToggle"
                checked={isKnockout}
                onChange={(e) => setIsKnockout(e.target.checked)}
                className="w-4 h-4 rounded accent-blue-500 cursor-pointer"
              />
              <label htmlFor="knockoutToggle" className="text-xs font-semibold text-white cursor-pointer">
                Knockout / Playoff Fixture Multiplier (M_knockout = 1.10)
              </label>
            </div>
          </div>

          {/* Real-Time Live Pressure Score Output */}
          <div className="rounded-xl bg-[#14223F]/60 border border-blue-500/20 p-6 text-center space-y-4 shadow-xl">
            <div className="text-[11px] text-[#94A3B8] uppercase font-bold tracking-wider">
              Calculated Pressure Score
            </div>

            <div
              className={`text-5xl font-black tabular-nums transition-colors ${
                isHighPressure ? "text-[#60A5FA]" : "text-[#94A3B8]"
              }`}
            >
              {simulatedPressure.toFixed(1)}
            </div>

            <div className="inline-flex">
              <Badge
                variant={isHighPressure ? "blue" : "slate"}
                size="md"
              >
                {isHighPressure ? "High-Pressure Delivery (≥60.0)" : "Standard Match Condition (<60.0)"}
              </Badge>
            </div>

            <div className="text-[11px] text-[#94A3B8] pt-3 border-t border-blue-500/10 space-y-1.5 text-left">
              <div className="flex justify-between">
                <span>Resource Scarcity:</span>
                <span className="font-mono text-white">{(resourceScarcity * 100).toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span>Match Urgency:</span>
                <span className="font-mono text-white">{(matchUrgency * 100).toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span>Wicket Scarcity:</span>
                <span className="font-mono text-white">{(wicketScarcity * 100).toFixed(1)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
