import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { TicketPriority } from "../../../types/ticket";
import { useAuth } from "../../auth/useAuth";
import { resolveClientId } from "../../client/services/clientService";
import { createTicket, getTicket, getTickets } from "../services/ticketService";

export interface NewTicketInput {
  titulo: string;
  descripcion: string;
  prioridad: TicketPriority;
}

// CU-05: tickets del cliente autenticado (el filtro es local porque
// la API todavía no permite filtrar por cliente).
export function useMyTickets() {
  const { user } = useAuth();

  return useQuery({
    queryKey: ["tickets", "mine", user?.id],
    enabled: user !== null,
    queryFn: async () => {
      if (!user) throw new Error("Sesión no válida");
      const clientId = await resolveClientId(user);
      const tickets = await getTickets();
      return tickets
        .filter((ticket) => ticket.client === clientId)
        .sort((a, b) => b.fecha_creacion.localeCompare(a.fecha_creacion));
    },
  });
}

export function useTicket(id: number) {
  const { user } = useAuth();

  return useQuery({
    queryKey: ["tickets", "detail", id, user?.id],
    enabled: user !== null && Number.isFinite(id),
    queryFn: async () => {
      if (!user) throw new Error("Sesión no válida");
      const [ticket, clientId] = await Promise.all([
        getTicket(id),
        resolveClientId(user),
      ]);
      if (ticket.client !== clientId) {
        throw new Error("Ticket inexistente o no autorizado");
      }
      return ticket;
    },
  });
}

// CU-03: crea el ticket a nombre del cliente autenticado.
export function useCreateTicket() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: NewTicketInput) => {
      if (!user) throw new Error("Sesión no válida");
      const client = await resolveClientId(user);
      return createTicket({ ...input, client });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tickets"] }),
  });
}