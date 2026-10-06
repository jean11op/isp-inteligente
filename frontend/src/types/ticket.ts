export type TicketStatus =
  | "NUEVO" | "EN_REVISION" | "ESPERANDO_ESPECIALISTA" | "DIAGNOSTICADO" | "REQUIERE_VISITA"
  | "TECNICO_ASIGNADO" | "EN_CAMINO" | "EN_DOMICILIO" | "EN_ATENCION" | "RESUELTO" | "CERRADO"
  | "NO_RESUELTO" | "ESCALADO" | "SEGUNDA_VISITA";

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
  client_info: {
    nombres: string;
    apellidos: string;
    telefono: string;
    addresses: Array<{
      direccion: string;
      referencia: string;
      latitud: string;
      longitud: string;
      principal: boolean;
    }>;
  };
  fecha_creacion: string;
  fecha_actualizacion: string;
}

/** El backend rechaza cualquier otro campo cuando quien crea es un cliente. */
export interface CreateTicketData {
  titulo: string;
  descripcion: string;
  prioridad: TicketPriority;
}

export type TicketPatch = Partial<Pick<Ticket, "estado" | "diagnostico" | "solucion" | "specialist" | "technician">>;
