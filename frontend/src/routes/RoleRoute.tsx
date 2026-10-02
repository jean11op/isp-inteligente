import { Navigate, Outlet } from "react-router";
import { useAuth } from "../features/auth/useAuth";
import type { Role } from "../types/roles";
import { PATHS, ROLE_HOME } from "./paths";

export default function RoleRoute({ role }: { role: Role }) {
  const { user } = useAuth();

  if (!user) return <Navigate to={PATHS.login} replace />;
  if (user.role !== role) return <Navigate to={ROLE_HOME[user.role]} replace />;

  return <Outlet />;
}