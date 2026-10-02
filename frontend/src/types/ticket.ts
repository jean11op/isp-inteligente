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