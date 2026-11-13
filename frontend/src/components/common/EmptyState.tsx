import React from "react";
import { LucideIcon, RefreshCw } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionText,
  onAction,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`card-teal p-12 text-center flex flex-col items-center justify-center space-y-3 ${className}`}
    >
      <div className="w-12 h-12 rounded-2xl bg-[#152D32] border border-[#20C9A0]/20 flex items-center justify-center text-[#20C9A0] shadow-sm mb-1">
        <Icon className="w-6 h-6" />
      </div>
      <h4 className="text-base font-bold text-[#E8F1F2]">{title}</h4>
      <p className="text-xs text-[#91A7AC] max-w-md leading-relaxed">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-3 inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-[#20C9A0]/15 hover:bg-[#20C9A0]/25 text-[#20C9A0] border border-[#20C9A0]/30 text-xs font-semibold transition-all duration-150"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>{actionText}</span>
        </button>
      )}
    </div>
  );
}
