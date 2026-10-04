import { isAxiosError } from "axios";
import { apiClient } from "../../../services/apiClient";
import type { CreateTicketData, Ticket } from "../../../types/ticket";

export async function getTickets(): Promise<Ticket[]> {
  const { data } = await apiClient.get<Ticket[]>("/tickets/");
  return data;
}

export async function getTicket(id: number): Promise<Ticket> {
  try {
    const { data } = await apiClient.get<Ticket>(`/tickets/${id}/`);
    return data;
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 404) {
      throw new Error("Ticket inexistente o no autorizado");
    }
    throw error;
  }
}

export async function createTicket(payload: CreateTicketData): Promise<Ticket> {
  const { data } = await apiClient.post<Ticket>("/tickets/", payload);
  return data;
}