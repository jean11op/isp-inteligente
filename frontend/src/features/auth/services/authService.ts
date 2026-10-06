import axios from "axios";
import { env } from "../../../config/env";
import { apiClient } from "../../../services/apiClient";
import { tokenStorage } from "../../../services/tokenStorage";
import type { User } from "../../../types/user";
import type { LoginCredentials, RegisterData } from "../types";

const MOCK_PASSWORD = "123456";
const MOCK_USERS: Record<string, User> = {
  cliente: { id: 1, username: "cliente", email: "cliente@demo.com", role: "CLIENTE" },
  especialista: { id: 2, username: "especialista", email: "especialista@demo.com", role: "ESPECIALISTA" },
  tecnico: { id: 3, username: "tecnico", email: "tecnico@demo.com", role: "TECNICO" },
  admin: { id: 4, username: "admin", email: "admin@demo.com", role: "ADMINISTRADOR" },
};

function userIdFromToken(access: string): number {
  const payload = JSON.parse(atob(access.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))) as {
    user_id: number | string;
  };
  return Number(payload.user_id);
}

export async function login({ username, password }: LoginCredentials): Promise<User> {
  if (env.useMockAuth) {
    const user = MOCK_USERS[username.trim().toLowerCase()];
    if (!user || password !== MOCK_PASSWORD) throw new Error("Usuario o contraseña incorrectos");
    return user;
  }

  try {
    const { data } = await axios.post<{ access: string; refresh: string }>(`${env.apiUrl}/auth/token/`, {
      username: username.trim(),
      password,
    });
    tokenStorage.set(data.access, data.refresh);
    // El token solo trae user_id: el rol se obtiene del propio perfil (permitido por el backend).
    const { data: user } = await apiClient.get<User>(`/users/${userIdFromToken(data.access)}/`);
    return { id: user.id, username: user.username, email: user.email, role: user.role };
  } catch (error) {
    tokenStorage.clear();
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      throw new Error("Usuario o contraseña incorrectos");
    }
    throw error;
  }
}

export async function register(data: RegisterData): Promise<void> {
  if (env.useMockAuth) return;
  // OJO: el backend hoy exige ser ADMIN para POST /users/ y /clients/ (ver nota al equipo).
  const { data: user } = await apiClient.post<User>("/users/", {
    username: data.username,
    email: data.email,
    password: data.password,
  });
  await apiClient.post("/clients/", {
    user: user.id,
    nombres: data.nombres,
    apellidos: data.apellidos,
    documento: data.documento,
    telefono: data.telefono,
  });
}
