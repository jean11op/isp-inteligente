import type { Role } from "@/types/roles";

export const PATHS = {
  home: "/",
  login: "/login",
  register: "/registro",
  client: "/cliente",
  clientTickets: "/cliente/tickets",
  clientNewTicket: "/cliente/tickets/nuevo",
  specialist: "/especialista",
  technician: "/tecnico",
  admin: "/admin",
} as const;

export function clientTicketPath(id: number): string {
  return `${PATHS.clientTickets}/${id}`;
}

export function specialistTicketPath(id: number): string {
  return `${PATHS.specialist}/${id}`;
}

export const ROLE_HOME: Record<Role, string> = {
  CLIENTE: PATHS.client,
  ESPECIALISTA: PATHS.specialist,
  TECNICO: PATHS.technician,
  ADMINISTRADOR: PATHS.admin,
};