import React from "react";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: LucideIcon;
  accentColor?: string;
  delta?: {
    value: number;
    suffix?: string;
    inverted?: boolean;
    label?: string;
  };
  className?: string;
}

export function MetricCard({
  label,
  value,
  sub,
  icon: Icon,
  accentColor = "#3B82F6",
  delta,
  className = "",
}: MetricCardProps) {
  return (
    <div
      className={`relative overflow-hidden rounded-[18px] bg-[#0E182D]/75 backdrop-blur-md border border-blue-500/15 p-5 group hover:border-blue-400/35 hover:-translate-y-0.5 transition-all duration-200 shadow-lg shadow-black/20 ${className}`}
    >
      {/* Subtle radial corner glow */}
      <div
        className="absolute -top-12 -right-12 w-28 h-28 rounded-full pointer-events-none opacity-25 group-hover:opacity-45 transition-opacity duration-300"
        style={{
          background: `radial-gradient(circle, ${accentColor} 0%, transparent 70%)`,
        }}
      />

      <div className="flex items-center justify-between mb-3 relative z-10">
        <span className="text-[11px] font-bold text-[#94A3B8] uppercase tracking-wider">
          {label}
        </span>
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center border shrink-0 transition-transform duration-200 group-hover:scale-110 shadow-sm"
          style={{
            backgroundColor: `${accentColor}18`,
            borderColor: `${accentColor}35`,
            color: accentColor,
          }}
        >
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="flex items-baseline space-x-2 relative z-10">
        <div className="text-2xl xl:text-3xl font-black text-white tracking-tight tabular-nums">
          {value}
        </div>
      </div>

      {sub && (
        <div className="text-[11px] text-[#94A3B8] mt-2 font-medium flex items-center justify-between relative z-10">
          <span>{sub}</span>
        </div>
      )}
    </div>
  );
}
