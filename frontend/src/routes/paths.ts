import type { Role } from "../types/roles";

export const PATHS = {
  home: "/",
  login: "/login",
  register: "/registro",
  client: "/cliente",
  specialist: "/especialista",
  technician: "/tecnico",
  admin: "/admin",
} as const;

export const ROLE_HOME: Record<Role, string> = {
  CLIENTE: PATHS.client,
  ESPECIALISTA: PATHS.specialist,
  TECNICO: PATHS.technician,
  ADMINISTRADOR: PATHS.admin,
};