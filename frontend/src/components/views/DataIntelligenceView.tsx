"use client";

import React, { useState, useEffect } from "react";
import {
  Database,
  ShieldCheck,
  AlertTriangle,
  FileText,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Layers,
  ArrowRight,
} from "lucide-react";
import { SectionHeader } from "../common/SectionHeader";
import { Badge } from "../common/Badge";
import { MetricCard } from "../common/MetricCard";
import { DataAuditSummary } from "@/types/analytics";
import { api } from "@/lib/api";

export function DataIntelligenceView() {
  const [audit, setAudit] = useState<DataAuditSummary | null>(null);

  useEffect(() => {
    api.getDataAudit().then((res) => {
      if (res.data) setAudit(res.data);
    });
  }, []);

  const excludedCompetitions = [
    {
      id: 2670,
      name: "Men's T20 Emerging Teams Asia Cup 2024",
      matches: 15,
      deliveries: 3492,
      reason: "Development Tier fixture with non-comparable associate/A-team competitiveness.",
    },
    {
      id: 2671,
      name: "Rising Stars T20 Championship 2024",
      matches: 15,
      deliveries: 3493,
      reason: "Regional development tournament lacking tier-1 international or IPL pedigree.",
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <SectionHeader
        title="Data Intelligence & Audit Verification"
        subtitle="Full provenance of the ball-by-ball archive, competition boundaries, and transparent data quality audit disclosures."
        badge="Independent Phase 2 Audit"
        badgeVariant="blue"
      />

      {/* Dataset Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Archive Matches"
          value="883"
          sub="200,999 Deliveries Processed"
          icon={Database}
          accentColor="#3B82F6"
        />
        <MetricCard
          label="Primary Included Matches"
          value="853"
          sub="194,014 Validated Deliveries"
          icon={ShieldCheck}
          accentColor="#6366F1"
        />
        <MetricCard
          label="IPL Match Deliveries"
          value="87,687"
          sub="371 Matches (2022–2026)"
          icon={Layers}
          accentColor="#38BDF8"
        />
        <MetricCard
          label="T20I Match Deliveries"
          value="106,327"
          sub="482 Matches (2022 Onward)"
          icon={Layers}
          accentColor="#8B5CF6"
        />
      </div>

      {/* Transparent Scope & Exclusions Section */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-blue-500/15 p-6 space-y-4 shadow-xl">
        <div className="flex items-center space-x-2.5 pb-3 border-b border-blue-500/10">
          <Database className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-extrabold text-white uppercase tracking-wider">
            Dataset Partitioning &amp; Competition Scope Boundaries
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Primary Tier (Included) */}
          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/15 p-5 space-y-3">
            <div className="flex items-center space-x-2 text-[#34D399]">
              <CheckCircle2 className="w-4 h-4" />
              <h4 className="text-xs font-black uppercase tracking-wider">
                Primary Ranking Scope (Included in Official Engine)
              </h4>
            </div>
            <ul className="text-xs text-[#94A3B8] space-y-2.5 leading-relaxed">
              <li className="flex items-start space-x-2">
                <span className="text-blue-400 font-bold">•</span>
                <span>
                  <strong className="text-white">Indian Premier League (IPL):</strong> 371 matches across seasons 2022 to 2026. Complete high-intensity franchise cricket.
                </span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-400 font-bold">•</span>
                <span>
                  <strong className="text-white">Men&apos;s T20 Internationals (T20I):</strong> 482 official ICC matches from 2022 onward, including T20 World Cups and bilateral series.
                </span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-400 font-bold">•</span>
                <span>
                  <strong className="text-white">Neutral Format Weighting:</strong> Applied neutrally (W_format = 1.0) across all qualifying candidates.
                </span>
              </li>
            </ul>
          </div>

          {/* Excluded Development Competitions */}
          <div className="rounded-xl bg-[#14223F]/50 border border-amber-500/20 p-5 space-y-3">
            <div className="flex items-center space-x-2 text-amber-400">
              <XCircle className="w-4 h-4" />
              <h4 className="text-xs font-black uppercase tracking-wider">
                Excluded Development Fixtures (30 Matches / 6,985 Balls)
              </h4>
            </div>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Development tournaments were excluded from primary rankings to prevent inflated averages against non-tier-1 opposition:
            </p>
            <div className="space-y-2 pt-1">
              {excludedCompetitions.map((comp) => (
                <div key={comp.id} className="p-3 rounded-lg bg-[#080E1C] border border-blue-500/10 text-xs">
                  <div className="font-bold text-white">
                    Comp ID {comp.id}: {comp.name}
                  </div>
                  <div className="text-[11px] text-[#94A3B8] mt-1">
                    {comp.matches} matches ({comp.deliveries} balls) • {comp.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* CRITICAL AUDIT DISCLOSURE: EXTRAS & RECONSTRUCTION */}
      <div className="rounded-[20px] bg-[#0E182D]/85 backdrop-blur-md border border-amber-500/25 p-6 space-y-4 shadow-xl border-l-4 border-l-amber-500">
        <div className="flex items-center space-x-2.5">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h3 className="text-sm font-extrabold text-white uppercase tracking-wider">
            Critical Statistical Audit Findings &amp; Architectural Mitigations
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-[#94A3B8] leading-relaxed pt-2">
          <div className="rounded-xl bg-[#14223F]/50 border border-amber-500/20 p-4 space-y-2">
            <h4 className="font-bold text-white">1. Incomplete Extras in Ball-by-Ball Feed</h4>
            <p>
              An independent delivery-level audit discovered that the supplied archive does not exhaustively tag field extras (byes, leg-byes, and unclassified penalty extras). Reconstructing exact cumulative scores on ball 110 of run chases yielded cumulative discrepancies.
            </p>
            <div className="p-2.5 rounded-lg bg-[#080E1C] text-amber-300 font-mono text-[11px] border border-amber-500/20">
              Exact Match-Margin Agreement: 31.7% in raw reconstruction.
            </div>
          </div>

          <div className="rounded-xl bg-[#14223F]/50 border border-blue-500/20 p-4 space-y-2">
            <h4 className="font-bold text-white">2. Context-Only Architectural Insulation</h4>
            <p>
              To completely eliminate run-chase scoreboard distortion from contaminating rankings, our primary pressure engine was converted to a <strong className="text-white">Context-Only Structural Pressure Engine</strong> (P_context).
            </p>
            <div className="p-2.5 rounded-lg bg-[#080E1C] text-[#60A5FA] font-mono text-[11px] border border-blue-500/20">
              Dependent only on balls remaining, wickets in hand, and stage.
            </div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#080E1C] border border-blue-500/15 text-xs text-[#94A3B8] leading-relaxed">
          <strong className="text-white">Audit Conclusion:</strong> By decoupling the primary pressure classification from reconstructed chasing scores, the final rankings are statistically robust, mathematically reproducible, and free from score drift artifacts.
        </div>
      </div>
    </div>
  );
}
