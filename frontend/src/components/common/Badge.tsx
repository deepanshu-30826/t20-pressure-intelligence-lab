import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "teal" | "cyan" | "emerald" | "amber" | "coral" | "slate" | "blue" | "violet" | "indigo" | "sky";
  size?: "sm" | "md";
  className?: string;
}

export function Badge({ children, variant = "blue", size = "sm", className = "" }: BadgeProps) {
  const variantStyles = {
    blue: "bg-blue-500/15 text-[#60A5FA] border-blue-500/30",
    violet: "bg-purple-500/15 text-[#C084FC] border-purple-500/30",
    indigo: "bg-indigo-500/15 text-[#818CF8] border-indigo-500/30",
    sky: "bg-sky-500/15 text-[#38BDF8] border-sky-500/30",
    teal: "bg-blue-500/15 text-[#60A5FA] border-blue-500/30",
    cyan: "bg-sky-500/15 text-[#38BDF8] border-sky-500/30",
    emerald: "bg-emerald-500/15 text-[#34D399] border-emerald-500/30",
    amber: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    coral: "bg-rose-500/15 text-rose-300 border-rose-500/30",
    slate: "bg-slate-800/60 text-slate-300 border-slate-700/50",
  };

  const sizeStyles = {
    sm: "px-2 py-0.5 text-[11px] font-medium tracking-wide",
    md: "px-2.5 py-1 text-xs font-semibold tracking-wide",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border transition-colors ${variantStyles[variant] || variantStyles.blue} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
}
