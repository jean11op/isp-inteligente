import { apiClient } from "../../../services/apiClient";
import type { User } from "../../../types/user";

interface ClientSummary {
  id: number;
  user: number;
}

export async function resolveClientId(user: User): Promise<number> {
  if (user.clientId) return user.clientId;

  const { data } = await apiClient.get<ClientSummary[]>("/clients/");
  const client = data.find((c) => c.user === user.id);
  if (!client) throw new Error("Tu cuenta no tiene un perfil de cliente");
  return client.id;
}