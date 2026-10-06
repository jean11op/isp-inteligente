import axios, { isAxiosError, type InternalAxiosRequestConfig } from "axios";
import { env } from "../config/env";
import { AUTH_LOGOUT_EVENT, tokenStorage } from "./tokenStorage";

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };
let refreshing: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStorage.getRefresh();
  if (!refresh) throw new Error("Sin refresh token");
  const { data } = await axios.post<{ access: string }>(`${env.apiUrl}/auth/token/refresh/`, { refresh });
  tokenStorage.set(data.access);
  return data.access;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!isAxiosError(error) || error.response?.status !== 401 || !error.config) throw error;
    const original = error.config as RetriableConfig;
    if (original._retry || original.url?.includes("/auth/token")) throw error;
    original._retry = true;
    try {
      refreshing ??= refreshAccessToken().finally(() => (refreshing = null));
      const access = await refreshing;
      original.headers.Authorization = `Bearer ${access}`;
      return apiClient(original);
    } catch {
      tokenStorage.clear();
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
      throw error;
    }
  },
);
