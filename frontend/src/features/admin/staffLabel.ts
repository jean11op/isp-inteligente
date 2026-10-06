import type { AppUser, StaffProfile } from "@/types/domain";

export function staffLabel(profile: StaffProfile, users: AppUser[] | undefined): string {
  const name = users?.find((u) => u.id === profile.user)?.username ?? `usuario #${profile.user}`;
  return profile.especialidad ? `${name} · ${profile.especialidad}` : name;
}
