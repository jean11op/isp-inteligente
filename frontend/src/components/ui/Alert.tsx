import type { ReactNode } from "react";
import { CircleAlert, CircleCheck, Info, TriangleAlert, type LucideIcon } from "lucide-react";

type Tone = "info" | "success" | "warning" | "error";

const ICONS: Record<Tone, LucideIcon> = {
  info: Info,
  success: CircleCheck,
  warning: TriangleAlert,
  error: CircleAlert,
};

interface AlertProps {
  tone?: Tone;
  title: string;
  children?: ReactNode;
  action?: ReactNode;
}

export default function Alert({ tone = "info", title, children, action }: AlertProps) {
  const Icon = ICONS[tone];

  return (
    <div className="alert" data-tone={tone} role={tone === "error" ? "alert" : "status"}>
      <Icon size={20} aria-hidden="true" />
      <div className="alert-content">
        <p className="alert-title">{title}</p>
        {children && <p className="alert-body">{children}</p>}
      </div>
      {action}
    </div>
  );
}