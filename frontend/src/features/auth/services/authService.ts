import { env } from "../../../config/env";
import { apiClient } from "../../../services/apiClient";
import type { User } from "../../../types/user";
import type { LoginCredentials, RegisterData } from "../types";

const MOCK_PASSWORD = "123456";
const MOCK_USERS: Record<string, User> = {
  cliente: { id: 1, username: "cliente", email: "cliente@demo.com", role: "CLIENTE", clientId: env.mockClientId },
  especialista: { id: 2, username: "especialista", email: "especialista@demo.com", role: "ESPECIALISTA" },
  tecnico: { id: 3, username: "tecnico", email: "tecnico@demo.com", role: "TECNICO" },
  admin: { id: 4, username: "admin", email: "admin@demo.com", role: "ADMINISTRADOR" },
};

export async function login({ username, password }: LoginCredentials): Promise<User> {
  if (env.useMockAuth) {
    const user = MOCK_USERS[username.trim().toLowerCase()];
    if (!user || password !== MOCK_PASSWORD) {
      throw new Error("Usuario o contraseña incorrectos");
    }
    return user;
  }
  throw new Error("El login real todavía no está conectado");
}

export async function register(data: RegisterData): Promise<void> {
  if (env.useMockAuth) return;

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