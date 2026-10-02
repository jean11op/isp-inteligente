import { createContext } from "react";
import type { User } from "../../types/user";
import type { LoginCredentials } from "./types";

export interface AuthContextValue {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<User>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);