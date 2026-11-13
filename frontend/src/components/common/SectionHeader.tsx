import React from "react";
import { Badge } from "./Badge";

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  badge?: string;
  badgeVariant?: "teal" | "cyan" | "emerald" | "amber" | "coral" | "slate" | "blue" | "violet" | "indigo" | "sky";
  action?: React.ReactNode;
  className?: string;
}

export function SectionHeader({
  title,
  subtitle,
  badge,
  badgeVariant = "blue",
  action,
  className = "",
}: SectionHeaderProps) {
  return (
    <div className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-1 ${className}`}>
      <div>
        <div className="flex items-center space-x-3">
          <h2 className="text-xl md:text-2xl font-black text-white tracking-tight">
            {title}
          </h2>
          {badge && <Badge variant={badgeVariant}>{badge}</Badge>}
        </div>
        {subtitle && (
          <p className="text-xs text-[#94A3B8] mt-1 font-normal leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="flex items-center space-x-2 shrink-0">{action}</div>}
    </div>
  );
}
