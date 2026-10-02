import { Navigate } from "react-router";
import LoginForm from "../components/LoginForm";
import { useAuth } from "../features/auth/useAuth";
import { ROLE_HOME } from "../routes/paths";

export default function LoginPage() {
  const { user } = useAuth();

  if (user) return <Navigate to={ROLE_HOME[user.role]} replace />;

  return (
    <>
      <h2>Iniciar sesión</h2>
      <LoginForm />
    </>
  );
}