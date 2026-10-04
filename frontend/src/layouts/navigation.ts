import { House, Plus, Ticket, type LucideIcon } from "lucide-react";
import { PATHS } from "@/routes/paths";
import type { Role } from "@/types/roles";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
  primary?: boolean;
  isActive?: (pathname: string) => boolean;
}

export const NAV_BY_ROLE: Record<Role, NavItem[]> = {
  CLIENTE: [
    { to: PATHS.client, label: "Inicio", icon: House, end: true },
    { to: PATHS.clientNewTicket, label: "Reportar", icon: Plus, primary: true, end: true },
    {
      to: PATHS.clientTickets,
      label: "Mis tickets",
      icon: Ticket,
      isActive: (pathname) =>
        pathname.startsWith(PATHS.clientTickets) && pathname !== PATHS.clientNewTicket,
    },
  ],
  ESPECIALISTA: [{ to: PATHS.specialist, label: "Inicio", icon: House, end: true }],
  TECNICO: [{ to: PATHS.technician, label: "Inicio", icon: House, end: true }],
  ADMINISTRADOR: [{ to: PATHS.admin, label: "Inicio", icon: House, end: true }],
};