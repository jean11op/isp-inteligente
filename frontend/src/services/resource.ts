import { apiClient } from "./apiClient";

export async function listResource<T>(path: string): Promise<T[]> {
  const { data } = await apiClient.get<T[]>(path);
  return data;
}

export async function createResource<T>(path: string, payload: unknown): Promise<T> {
  const { data } = await apiClient.post<T>(path, payload);
  return data;
}

export async function patchResource<T>(path: string, payload: unknown): Promise<T> {
  const { data } = await apiClient.patch<T>(path, payload);
  return data;
}
