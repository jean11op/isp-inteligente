import type { Role } from "./roles";

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
}