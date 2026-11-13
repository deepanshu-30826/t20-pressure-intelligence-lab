"use client";

import React from "react";
import {
  BookOpen,
  CheckCircle2,
  Layers,
  Zap,
  Percent,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  FileCode,
} from "lucide-react";
import { SectionHeader } from "../common/SectionHeader";
import { Badge } from "../common/Badge";

export function MethodologyView() {
  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <SectionHeader
        title="Methodology & Mathematical Specification"
        subtitle="Complete mathematical formulation, role benchmarks, Empirical Bayes shrinkage, and bootstrap stability protocols."
        badge="Official Version 3.0"
        badgeVariant="blue"
      />

      {/* SECTION 1: STRUCTURAL PRESSURE ENGINE */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 md:p-8 space-y-5 shadow-xl">
        <div className="flex items-center space-x-3 pb-3 border-b border-blue-500/10">
          <div className="w-8 h-8 rounded-xl bg-blue-500/15 border border-blue-500/30 text-[#60A5FA] flex items-center justify-center font-black text-xs">
            1
          </div>
          <div>
            <h3 className="text-base font-extrabold text-white">
              Pre-Delivery Structural Pressure Formulation
            </h3>
            <p className="text-xs text-[#94A3B8]">Formulated strictly prior to delivery execution</p>
          </div>
        </div>

        <p className="text-xs text-[#94A3B8] leading-relaxed">
          To maintain causal integrity and avoid data leakage from delivery outcomes, the pressure index is computed strictly using the pre-delivery match state across legal balls remaining, wickets in hand, and match tournament context:
        </p>

        <div className="p-5 rounded-xl bg-[#080E1C] border border-blue-500/25 font-mono text-xs text-white space-y-2 shadow-inner">
          <div className="text-[#60A5FA] font-bold">
            P_context = (0.45 × Resource_Scarcity + 0.35 × Match_Urgency + 0.20 × Wicket_Scarcity) × 100 × M_knockout
          </div>
          <div className="text-[11px] text-[#94A3B8] font-sans leading-relaxed">
            • Resource_Scarcity = 1.0 - (Wickets_In_Hand / 10) × (Balls_Remaining / 120)<br />
            • Match_Urgency = 1.0 - (Balls_Remaining / 120)^1.5<br />
            • Wicket_Scarcity = (Wickets_Lost / 10)^1.2<br />
            • M_knockout = 1.10 for playoffs/finals, 1.0 for group matches
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#14223F]/50 border border-blue-500/15 text-xs text-white flex items-center space-x-2.5">
          <CheckCircle2 className="w-4 h-4 text-[#34D399] shrink-0" />
          <span>
            <strong className="text-white">Pressure Qualification Threshold:</strong> Any delivery with P_context ≥ 60.0 is classified as high-pressure.
          </span>
        </div>
      </div>

      {/* SECTION 2: ROLE & PHASE BENCHMARKS */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 md:p-8 space-y-5 shadow-xl">
        <div className="flex items-center space-x-3 pb-3 border-b border-blue-500/10">
          <div className="w-8 h-8 rounded-xl bg-purple-500/15 border border-purple-500/30 text-[#C084FC] flex items-center justify-center font-black text-xs">
            2
          </div>
          <div>
            <h3 className="text-base font-extrabold text-white">
              Role &amp; Innings Phase Par Benchmarks
            </h3>
            <p className="text-xs text-[#94A3B8]">Neutralizing structural positional advantages</p>
          </div>
        </div>

        <p className="text-xs text-[#94A3B8] leading-relaxed">
          Comparing a middle-overs batter against a death-overs finisher, or an opening defensive spinner against a death-overs pacer, introduces severe role bias. We compute expected par baselines:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-4 space-y-2">
            <h4 className="font-bold text-[#60A5FA]">Batting Position Bands</h4>
            <ul className="text-[#94A3B8] space-y-1">
              <li>• <strong className="text-white">Positions 1–3:</strong> Expected Par ~ 154.2 SR</li>
              <li>• <strong className="text-white">Positions 4–5:</strong> Expected Par ~ 159.4 SR</li>
              <li>• <strong className="text-white">Positions 6–7:</strong> Expected Par ~ 148.5 SR</li>
              <li>• <strong className="text-white">Positions 8+:</strong> Expected Par ~ 134.8 SR</li>
            </ul>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-4 space-y-2">
            <h4 className="font-bold text-[#C084FC]">Bowling Innings Phases</h4>
            <ul className="text-[#94A3B8] space-y-1">
              <li>• <strong className="text-white">Powerplay (1–6):</strong> Expected Par = 7.79 RPO</li>
              <li>• <strong className="text-white">Middle Overs (7–15):</strong> Expected Par = 7.82 RPO</li>
              <li>• <strong className="text-white">Death Overs (16–20):</strong> Expected Par = 9.58 RPO</li>
            </ul>
          </div>
        </div>
      </div>

      {/* SECTION 3: EMPIRICAL BAYES SHRINKAGE */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 md:p-8 space-y-5 shadow-xl">
        <div className="flex items-center space-x-3 pb-3 border-b border-blue-500/10">
          <div className="w-8 h-8 rounded-xl bg-blue-500/15 border border-blue-500/30 text-[#60A5FA] flex items-center justify-center font-black text-xs">
            3
          </div>
          <div>
            <h3 className="text-base font-extrabold text-white">
              Empirical Bayes Sample Shrinkage (k = 40)
            </h3>
            <p className="text-xs text-[#94A3B8]">Protecting rankings against small-sample variance</p>
          </div>
        </div>

        <p className="text-xs text-[#94A3B8] leading-relaxed">
          To prevent players with barely 100 balls from jumping above established performers on random variance, all raw performance deltas are shrunk toward the population mean:
        </p>

        <div className="p-4 rounded-xl bg-[#080E1C] border border-blue-500/25 font-mono text-xs text-white">
          <div className="text-[#60A5FA] font-bold">
            Delta_shrunk = (N_pressure / (N_pressure + 40)) × (Metric_pressure - Expected_role_par)
          </div>
        </div>
      </div>

      {/* SECTION 4: MATCH-LEVEL CONSISTENCY */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 md:p-8 space-y-5 shadow-xl">
        <div className="flex items-center space-x-3 pb-3 border-b border-blue-500/10">
          <div className="w-8 h-8 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 flex items-center justify-center font-black text-xs">
            4
          </div>
          <div>
            <h3 className="text-base font-extrabold text-white">
              Match-to-Match Par Consistency
            </h3>
            <p className="text-xs text-[#94A3B8]">Measuring repeat execution over raw volume accumulation</p>
          </div>
        </div>

        <p className="text-xs text-[#94A3B8] leading-relaxed">
          Rather than awarding arbitrary multiplicative volume bonuses (which reward mere career length), consistency is calculated as the percentage of qualifying matches in which a player achieved or outperformed expected par:
        </p>

        <div className="p-4 rounded-xl bg-[#080E1C] border border-blue-500/25 font-mono text-xs text-white">
          <div className="text-amber-300 font-bold">
            Match_Consistency_% = (Qualifying_Matches_Exceeding_Par / Total_Qualifying_Matches) × 100
          </div>
          <div className="text-[11px] text-[#94A3B8] font-sans mt-1">
            Qualifying match thresholds: ≥ 5 pressure balls faced for batters, ≥ 6 pressure legal deliveries for bowlers.
          </div>
        </div>
      </div>

      {/* SECTION 5: 1,000-ITERATION BOOTSTRAP VALIDATION */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 md:p-8 space-y-5 shadow-xl">
        <div className="flex items-center space-x-3 pb-3 border-b border-blue-500/10">
          <div className="w-8 h-8 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-[#818CF8] flex items-center justify-center font-black text-xs">
            5
          </div>
          <div>
            <h3 className="text-base font-extrabold text-white">
              1,000-Iteration Cluster Bootstrap Validation
            </h3>
            <p className="text-xs text-[#94A3B8]">Rigorous rank stability and confidence intervals</p>
          </div>
        </div>

        <p className="text-xs text-[#94A3B8] leading-relaxed">
          Matches are resampled with replacement 1,000 times to quantify the empirical probability of retaining a Top 10 rank:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-4">
            <h4 className="font-bold text-[#60A5FA] mb-1.5">Batting Stability Anchors</h4>
            <p className="text-[#94A3B8] leading-relaxed">
              <strong className="text-white">Naman Dhir:</strong> P(Top 10) = 88.1%, 95% CI [174.1, 218.0]<br />
              <strong className="text-white">Suryakumar Yadav:</strong> P(Top 10) = 79.8%, 95% CI [178.6, 210.7]<br />
              <strong className="text-white">Jacob Bethell:</strong> P(Top 10) = 67.4%, 95% CI [150.8, 234.1]
            </p>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-purple-500/15 p-4">
            <h4 className="font-bold text-[#C084FC] mb-1.5">Bowling Stability Anchors</h4>
            <p className="text-[#94A3B8] leading-relaxed">
              <strong className="text-white">Sunil Narine:</strong> P(Top 10) = 96.9%, 95% CI [5.82, 8.01]<br />
              <strong className="text-white">Abrar Ahmed:</strong> P(Top 10) = 96.6%, 95% CI [5.15, 7.93]<br />
              <strong className="text-white">Jasprit Bumrah:</strong> P(Top 10) = 94.3%, 95% CI [6.79, 8.49]
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
