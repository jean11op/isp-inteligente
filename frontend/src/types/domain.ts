import type { Role } from "./roles";

export type VisitStatus = "PROGRAMADA" | "EN_CAMINO" | "EN_DOMICILIO" | "EN_ATENCION" | "COMPLETADA" | "CANCELADA";

export interface Visit {
  id: number;
  ticket: number;
  technician: number;
  estado: VisitStatus;
  fecha_programada: string;
  fecha_inicio: string | null;
  fecha_fin: string | null;
  resultado: string;
  observaciones: string;
  fecha_creacion: string;
}

export interface InventoryItem {
  id: number;
  nombre: string;
  descripcion: string;
  cantidad: number;
  unidad: string;
  activo: boolean;
  fecha_creacion: string;
}

export interface InventoryUsage {
  id: number;
  visit: number;
  item: number;
  cantidad: number;
  fecha_registro: string;
}

export interface Evaluation {
  id: number;
  ticket: number;
  puntuacion: number;
  comentario: string;
  fecha_evaluacion: string;
}

export interface TicketHistoryEntry {
  id: number;
  ticket: number;
  user: number | null;
  estado_anterior: string;
  estado_nuevo: string;
  comentario: string;
  fecha: string;
}

export interface ClientProfile {
  id: number;
  user: number;
  nombres: string;
  apellidos: string;
  documento: string;
  telefono: string;
  servicio_activo: boolean;
  fecha_registro: string;
}

export interface StaffProfile {
  id: number;
  user: number;
  especialidad: string;
  disponible: boolean;
  activo: boolean;
  latitud?: string | null;
  longitud?: string | null;
  carga_trabajo?: number;
  fecha_registro: string;
}

export interface AppUser {
  id: number;
  username: string;
  email: string;
  role: Role;
}

export interface Address {
  id: number;
  client: number;
  direccion: string;
  referencia: string;
  latitud: string;
  longitud: string;
  principal: boolean;
  fecha_registro: string;
}

export interface AddressInput {
  direccion: string;
  referencia: string;
  latitud: string;
  longitud: string;
  principal: boolean;
}
