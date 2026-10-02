import { useState, type ReactNode } from "react";
import type { User } from "../../types/user";
import { AuthContext } from "./AuthContext";
import { login as loginRequest } from "./services/authService";
import type { LoginCredentials } from "./types";

const STORAGE_KEY = "isp_user";

function readStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(readStoredUser);

  async function login(credentials: LoginCredentials) {
    const loggedUser = await loginRequest(credentials);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(loggedUser));
    setUser(loggedUser);
    return loggedUser;
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  }

  return <AuthContext value={{ user, login, logout }}>{children}</AuthContext>;
}