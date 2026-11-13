import React from "react";

interface PlayerAvatarProps {
  name: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function PlayerAvatar({ name, size = "md", className = "" }: PlayerAvatarProps) {
  const getInitials = (n: string) => {
    if (!n) return "P";
    const parts = n.trim().split(" ");
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  const sizeClasses = {
    sm: "w-7 h-7 text-[11px]",
    md: "w-9 h-9 text-xs",
    lg: "w-14 h-14 text-lg",
  };

  return (
    <div
      className={`relative inline-flex items-center justify-center rounded-xl bg-gradient-to-br from-[#1E325A] to-[#0E1A33] border border-blue-500/30 text-white font-extrabold tracking-wider shadow-inner shrink-0 ${sizeClasses[size]} ${className}`}
    >
      <span>{getInitials(name)}</span>
      <span className="absolute inset-0 rounded-xl bg-blue-500/10 pointer-events-none" />
    </div>
  );
}
