import React from "react";

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-blue-950/40 border border-blue-500/10 rounded-xl ${className}`}
    />
  );
}

export function TableSkeleton({ rows = 5, cols = 8 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-2.5 p-4">
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex space-x-3 items-center">
          {Array.from({ length: cols }).map((_, c) => (
            <Skeleton
              key={c}
              className={`h-7 ${c === 0 ? "w-10" : c === 1 ? "w-44" : "flex-1"}`}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
