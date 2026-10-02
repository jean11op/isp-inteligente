import { Navigate } from "react-router";
import { useAuth } from "../features/auth/useAuth";
import { PATHS, ROLE_HOME } from "../routes/paths";

export default function HomePage() {
  const { user } = useAuth();
  return <Navigate to={user ? ROLE_HOME[user.role] : PATHS.login} replace />;
}