import type { TicketPriority, TicketStatus } from "@/types/ticket";

export const STATUS_LABEL: Record<TicketStatus, string> = {
  NUEVO: "Nuevo",
  EN_REVISION: "En revisión",
  ESPERANDO_ESPECIALISTA: "Esperando especialista",
  DIAGNOSTICADO: "Diagnosticado",
  REQUIERE_VISITA: "Requiere visita",
  TECNICO_ASIGNADO: "Técnico asignado",
  EN_CAMINO: "En camino",
  EN_DOMICILIO: "En domicilio",
  EN_ATENCION: "En atención",
  RESUELTO: "Resuelto",
  CERRADO: "Cerrado",
  NO_RESUELTO: "No resuelto",
  ESCALADO: "Escalado",
  SEGUNDA_VISITA: "Segunda visita",
};

export const TICKET_FLOW: TicketStatus[] = [
  "NUEVO",
  "EN_REVISION",
  "ESPERANDO_ESPECIALISTA",
  "DIAGNOSTICADO",
  "REQUIERE_VISITA",
  "TECNICO_ASIGNADO",
  "EN_CAMINO",
  "EN_DOMICILIO",
  "EN_ATENCION",
  "RESUELTO",
  "CERRADO",
];

export const OFF_FLOW_STATUSES: TicketStatus[] = ["NO_RESUELTO", "ESCALADO", "SEGUNDA_VISITA"];

export type StatusTone = "open" | "progress" | "field" | "done" | "closed" | "warn" | "danger";

export const STATUS_TONE: Record<TicketStatus, StatusTone> = {
  NUEVO: "open",
  EN_REVISION: "open",
  ESPERANDO_ESPECIALISTA: "open",
  DIAGNOSTICADO: "progress",
  REQUIERE_VISITA: "progress",
  TECNICO_ASIGNADO: "field",
  EN_CAMINO: "field",
  EN_DOMICILIO: "field",
  EN_ATENCION: "field",
  RESUELTO: "done",
  CERRADO: "closed",
  NO_RESUELTO: "danger",
  ESCALADO: "danger",
  SEGUNDA_VISITA: "warn",
};

export const PRIORITY_LABEL: Record<TicketPriority, string> = {
  BAJA: "Baja",
  MEDIA: "Media",
  ALTA: "Alta",
  CRITICA: "Crítica",
};

export const PRIORITY_TONE: Record<TicketPriority, "open" | "warn" | "danger" | "closed"> = {
  BAJA: "closed",
  MEDIA: "open",
  ALTA: "warn",
  CRITICA: "danger",
};

/** Copia de las transiciones válidas del backend (TicketSerializer.VALID_TRANSITIONS). */
export const NEXT_STATUSES: Partial<Record<TicketStatus, TicketStatus[]>> = {
  NUEVO: ["EN_REVISION"],
  EN_REVISION: ["ESPERANDO_ESPECIALISTA", "DIAGNOSTICADO"],
  ESPERANDO_ESPECIALISTA: ["DIAGNOSTICADO", "ESCALADO"],
  DIAGNOSTICADO: ["REQUIERE_VISITA", "RESUELTO"],
  REQUIERE_VISITA: ["TECNICO_ASIGNADO"],
  TECNICO_ASIGNADO: ["EN_CAMINO"],
  EN_CAMINO: ["EN_DOMICILIO"],
  EN_DOMICILIO: ["EN_ATENCION"],
  EN_ATENCION: ["RESUELTO", "NO_RESUELTO"],
  NO_RESUELTO: ["SEGUNDA_VISITA"],
  SEGUNDA_VISITA: ["TECNICO_ASIGNADO"],
  RESUELTO: ["CERRADO"],
};

export const VISIT_LABEL: Record<string, string> = {
  PROGRAMADA: "Programada",
  EN_CAMINO: "En camino",
  EN_DOMICILIO: "En domicilio",
  EN_ATENCION: "En atención",
  COMPLETADA: "Completada",
  CANCELADA: "Cancelada",
};
