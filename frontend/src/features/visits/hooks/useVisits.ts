import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createResource, listResource, patchResource } from "@/services/resource";
import { queryKeys } from "@/services/queryKeys";
import type { Visit, VisitStatus } from "@/types/domain";

export function useVisits() {
  return useQuery({ queryKey: queryKeys.visits, queryFn: () => listResource<Visit>("/visits/") });
}

export function useTicketVisit(ticketId: number) {
  const query = useVisits();
  const visit = query.data?.filter((v) => v.ticket === ticketId && v.estado !== "CANCELADA").at(-1);
  return { ...query, visit };
}

export interface VisitPatch {
  estado?: VisitStatus;
  resultado?: string;
  observaciones?: string;
}

export function useUpdateVisit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, patch }: { id: number; patch: VisitPatch }) => patchResource<Visit>(`/visits/${id}/`, patch),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.visits }),
  });
}

export function useCreateVisit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { ticket: number; technician: number; fecha_programada: string }) =>
      createResource<Visit>("/visits/", payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.visits }),
  });
}
