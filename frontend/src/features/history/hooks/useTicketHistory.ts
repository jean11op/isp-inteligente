import { useQuery } from "@tanstack/react-query";
import { listResource } from "@/services/resource";
import { queryKeys } from "@/services/queryKeys";
import type { TicketHistoryEntry } from "@/types/domain";

export function useTicketHistory(ticketId: number) {
  return useQuery({
    queryKey: [...queryKeys.history, ticketId],
    queryFn: async () =>
      (await listResource<TicketHistoryEntry>("/history/"))
        .filter((entry) => entry.ticket === ticketId)
        .sort((a, b) => b.fecha.localeCompare(a.fecha)),
  });
}
