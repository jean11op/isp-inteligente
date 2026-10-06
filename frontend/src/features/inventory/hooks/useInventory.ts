import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createResource, listResource } from "@/services/resource";
import { queryKeys } from "@/services/queryKeys";
import type { InventoryItem, InventoryUsage } from "@/types/domain";

export function useInventory() {
  return useQuery({ queryKey: queryKeys.inventory, queryFn: () => listResource<InventoryItem>("/inventory/") });
}

export function useCreateInventoryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Pick<InventoryItem, "nombre" | "descripcion" | "cantidad" | "unidad">) =>
      createResource<InventoryItem>("/inventory/", payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.inventory }),
  });
}

export function useRegisterUsage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { visit: number; item: number; cantidad: number }) =>
      createResource<InventoryUsage>("/inventory-usage/", payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.inventory }),
  });
}

export function useVisitUsage(visitId: number | undefined) {
  return useQuery({
    queryKey: ["inventory-usage", visitId],
    enabled: visitId !== undefined,
    queryFn: async () => (await listResource<InventoryUsage>("/inventory-usage/")).filter((u) => u.visit === visitId),
  });
}
