import React from "react";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface StatDeltaProps {
  value: number;
  suffix?: string;
  prefix?: string;
  inverted?: boolean;
  decimals?: number;
  label?: string;
  className?: string;
}

export function StatDelta({
  value,
  suffix = "",
  prefix = "",
  inverted = false,
  decimals = 1,
  label,
  className = "",
}: StatDeltaProps) {
  if (value === undefined || value === null || isNaN(value)) {
    return <span className="text-[#94A3B8] text-xs font-mono">-</span>;
  }

  const isZero = Math.abs(value) < 0.001;
  const isPositive = value > 0;
  
  const isGood = inverted ? !isPositive : isPositive;

  const colorClass = isZero
    ? "text-[#94A3B8]"
    : isGood
    ? "text-[#34D399]"
    : "text-[#EF4444]";

  const Icon = isZero ? Minus : isPositive ? ArrowUpRight : ArrowDownRight;
  const displaySign = isPositive ? "+" : "";

  return (
    <span className={`inline-flex items-center space-x-0.5 tabular-nums font-semibold text-xs ${colorClass} ${className}`}>
      <Icon className="w-3.5 h-3.5 shrink-0" />
      <span>
        {prefix}
        {displaySign}
        {value.toFixed(decimals)}
        {suffix}
      </span>
      {label && <span className="text-[10px] text-[#94A3B8] ml-1 font-normal">{label}</span>}
    </span>
  );
}
