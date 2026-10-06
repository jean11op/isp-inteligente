import { isAxiosError } from "axios";
import { apiClient } from "@/services/apiClient";
import { createResource, listResource, patchResource } from "@/services/resource";
import type { CreateTicketData, Ticket, TicketPatch } from "@/types/ticket";

export const getTickets = () => listResource<Ticket>("/tickets/");

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

export const createTicket = (payload: CreateTicketData) => createResource<Ticket>("/tickets/", payload);
export const updateTicket = (id: number, patch: TicketPatch) => patchResource<Ticket>(`/tickets/${id}/`, patch);
export const requestSpecialist = (id: number) =>
  apiClient.post<Ticket>(`/tickets/${id}/request-specialist/`).then(({ data }) => data);
