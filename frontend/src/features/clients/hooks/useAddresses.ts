import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/services/queryKeys";
import {
  createResource,
  listResource,
  patchResource,
} from "@/services/resource";
import type { Address, AddressInput } from "@/types/domain";

export const useAddresses = () =>
  useQuery({
    queryKey: queryKeys.addresses,
    queryFn: () => listResource<Address>("/addresses/"),
  });

export function useSaveAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...payload }: AddressInput & { id?: number }) =>
      id
        ? patchResource<Address>(`/addresses/${id}/`, payload)
        : createResource<Address>("/addresses/", payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.addresses,
      });
      void queryClient.invalidateQueries({
        queryKey: queryKeys.tickets,
      });
    },
  });
}