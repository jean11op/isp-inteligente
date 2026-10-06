import { useEffect, useState, type ReactNode } from "react";
import { AUTH_LOGOUT_EVENT, tokenStorage } from "../../services/tokenStorage";
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

  function clearSession() {
    localStorage.removeItem(STORAGE_KEY);
    tokenStorage.clear();
    setUser(null);
  }

  useEffect(() => {
    window.addEventListener(AUTH_LOGOUT_EVENT, clearSession);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, clearSession);
  }, []);

  async function login(credentials: LoginCredentials) {
    const loggedUser = await loginRequest(credentials);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(loggedUser));
    setUser(loggedUser);
    return loggedUser;
  }

  return <AuthContext value={{ user, login, logout: clearSession }}>{children}</AuthContext>;
}
