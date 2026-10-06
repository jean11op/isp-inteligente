import axios from "axios";
import { env } from "../../../config/env";
import { apiClient } from "../../../services/apiClient";
import { tokenStorage } from "../../../services/tokenStorage";
import type { User } from "../../../types/user";
import type { LoginCredentials, RegisterData } from "../types";

const MOCK_PASSWORD = "123456";

const MOCK_USERS: Record<string, User> = {
  cliente: {
    id: 1,
    username: "cliente",
    email: "cliente@demo.com",
    role: "CLIENTE",
    fullName: "Cliente Demo",
  },
  especialista: {
    id: 2,
    username: "especialista",
    email: "especialista@demo.com",
    role: "ESPECIALISTA",
    fullName: "Especialista Demo",
  },
  tecnico: {
    id: 3,
    username: "tecnico",
    email: "tecnico@demo.com",
    role: "TECNICO",
    fullName: "Técnico Demo",
  },
  admin: {
    id: 4,
    username: "admin",
    email: "admin@demo.com",
    role: "ADMINISTRADOR",
    fullName: "Administrador",
  },
};

interface MeResponse {
  id: number;
  username: string;
  email: string;
  role: User["role"];
  full_name: string;
  client_id: number | null;
}

export async function login({
  username,
  password,
}: LoginCredentials): Promise<User> {
  if (env.useMockAuth) {
    const user = MOCK_USERS[username.trim().toLowerCase()];

    if (!user || password !== MOCK_PASSWORD) {
      throw new Error("Usuario o contraseña incorrectos");
    }

    return user;
  }

  try {
    const { data } = await axios.post<{
      access: string;
      refresh: string;
    }>(`${env.apiUrl}/auth/token/`, {
      username: username.trim(),
      password,
    });

    tokenStorage.set(data.access, data.refresh);

    const { data: me } = await apiClient.get<MeResponse>("/auth/me/");

    return {
      id: me.id,
      username: me.username,
      email: me.email,
      role: me.role,
      fullName: me.full_name,
      clientId: me.client_id,
    };
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