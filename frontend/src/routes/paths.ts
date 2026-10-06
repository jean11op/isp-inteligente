import type { Role } from "@/types/roles";

export const PATHS = {
  home: "/",
  login: "/login",
  register: "/registro",
  client: "/cliente",
  clientTickets: "/cliente/tickets",
  clientNewTicket: "/cliente/tickets/nuevo",
  clientAddress: "/cliente/domicilio",
  specialist: "/especialista",
  technician: "/tecnico",
  admin: "/admin",
  adminTickets: "/admin/tickets",
  adminPeople: "/admin/personas",
  adminInventory: "/admin/inventario",
} as const;
export const clientTicketPath = (id: number) => `${PATHS.clientTickets}/${id}`;
export const specialistTicketPath = (id: number) => `${PATHS.specialist}/tickets/${id}`;
export const technicianTicketPath = (id: number) => `${PATHS.technician}/servicios/${id}`;
export const adminTicketPath = (id: number) => `${PATHS.adminTickets}/${id}`;

export const ROLE_HOME: Record<Role, string> = {
  CLIENTE: PATHS.client,
  ESPECIALISTA: PATHS.specialist,
  TECNICO: PATHS.technician,
  ADMINISTRADOR: PATHS.admin,
};
