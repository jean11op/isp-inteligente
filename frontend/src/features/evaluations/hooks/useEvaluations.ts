import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createResource, listResource } from "@/services/resource";
import { queryKeys } from "@/services/queryKeys";
import type { Evaluation } from "@/types/domain";

export function useTicketEvaluation(ticketId: number) {
  return useQuery({
    queryKey: [...queryKeys.evaluations, ticketId],
    queryFn: async () => (await listResource<Evaluation>("/evaluations/")).find((e) => e.ticket === ticketId) ?? null,
  });
}

export function useCreateEvaluation(ticketId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { puntuacion: number; comentario: string }) =>
      createResource<Evaluation>("/evaluations/", { ticket: ticketId, ...payload }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.evaluations }),
  });
}
