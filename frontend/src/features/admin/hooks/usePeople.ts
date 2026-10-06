import { useQuery } from "@tanstack/react-query";
import { listResource } from "@/services/resource";
import { queryKeys } from "@/services/queryKeys";
import type { AppUser, ClientProfile, StaffProfile } from "@/types/domain";

export const useClients = () =>
  useQuery({ queryKey: queryKeys.people("clients"), queryFn: () => listResource<ClientProfile>("/clients/") });
export const useTechnicians = () =>
  useQuery({ queryKey: queryKeys.people("technicians"), queryFn: () => listResource<StaffProfile>("/technicians/") });
export const useSpecialists = () =>
  useQuery({ queryKey: queryKeys.people("specialists"), queryFn: () => listResource<StaffProfile>("/specialists/") });
export const useUsers = () =>
  useQuery({ queryKey: queryKeys.people("users"), queryFn: () => listResource<AppUser>("/users/") });
