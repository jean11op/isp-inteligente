import type { TicketPriority, TicketStatus } from "../../types/ticket";

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

export const PRIORITY_LABEL: Record<TicketPriority, string> = {
  BAJA: "Baja",
  MEDIA: "Media",
  ALTA: "Alta",
  CRITICA: "Crítica",
};