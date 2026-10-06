import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/services/queryKeys";
import type { TicketPatch, TicketPriority } from "@/types/ticket";
import { useAuth } from "../../auth/useAuth";
import { createTicket, getTicket, getTickets, requestSpecialist, updateTicket } from "../services/ticketService";

export interface NewTicketInput {
  titulo: string;
  descripcion: string;
  prioridad: TicketPriority;
}

/** El backend ya filtra los tickets según el rol de quien consulta. */
export function useTickets() {
  const { user } = useAuth();
  return useQuery({
    queryKey: [...queryKeys.tickets, "list", user?.id],
    enabled: user !== null,
    queryFn: async () => (await getTickets()).sort((a, b) => b.fecha_creacion.localeCompare(a.fecha_creacion)),
  });
}

export const useMyTickets = useTickets;

export function useTicket(id: number) {
  const { user } = useAuth();
  return useQuery({
    queryKey: [...queryKeys.ticket(id), user?.id],
    enabled: user !== null && Number.isFinite(id),
    queryFn: () => getTicket(id),
  });
}

export function useCreateTicket() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: NewTicketInput) => createTicket(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.tickets }),
  });
}

export function useUpdateTicket(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (patch: TicketPatch) => updateTicket(id, patch),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.tickets });
      void queryClient.invalidateQueries({ queryKey: queryKeys.history });
    },
  });
}

export function useRequestSpecialist(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => requestSpecialist(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.tickets });
      void queryClient.invalidateQueries({ queryKey: queryKeys.ticket(id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.history });
    },
  });
}
