export type TicketStatus =
  | "NUEVO"
  | "EN_REVISION"
  | "ESPERANDO_ESPECIALISTA"
  | "DIAGNOSTICADO"
  | "REQUIERE_VISITA"
  | "TECNICO_ASIGNADO"
  | "EN_CAMINO"
  | "EN_DOMICILIO"
  | "EN_ATENCION"
  | "RESUELTO"
  | "CERRADO"
  | "NO_RESUELTO"
  | "ESCALADO"
  | "SEGUNDA_VISITA";

export type TicketPriority = "BAJA" | "MEDIA" | "ALTA" | "CRITICA";

export interface Ticket {
  id: number;
  client: number;
  service: number | null;
  titulo: string;
  descripcion: string;
  prioridad: TicketPriority;
  estado: TicketStatus;
  diagnostico: string;
  solucion: string;
  specialist: number | null;
  technician: number | null;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface CreateTicketData {
  client: number;
  titulo: string;
  descripcion: string;
  prioridad: TicketPriority;
}