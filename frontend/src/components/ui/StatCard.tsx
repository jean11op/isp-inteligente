import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  tone?: "neutral" | "accent" | "warn" | "danger" | "ok";
}

export default function StatCard({ label, value, icon: Icon, tone = "neutral" }: StatCardProps) {
  return (
    <div className="stat-card" data-tone={tone}>
      <span className="stat-icon">
        <Icon size={18} aria-hidden="true" />
      </span>
      <p className="stat-value">{value}</p>
      <p className="stat-label">{label}</p>
    </div>
  );
}
