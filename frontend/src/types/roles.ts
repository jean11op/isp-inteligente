export type Role = "CLIENTE" | "ESPECIALISTA" | "TECNICO" | "ADMINISTRADOR";

export const ROLE_LABEL: Record<Role, string> = {
  CLIENTE: "Cliente",
  ESPECIALISTA: "Especialista",
  TECNICO: "Técnico",
  ADMINISTRADOR: "Administrador",
};