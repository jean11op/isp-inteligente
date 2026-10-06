import { Navigate } from "react-router";
import LoginForm from "@/features/auth/components/LoginForm";
import { useAuth } from "@/features/auth/useAuth";
import { ROLE_HOME } from "@/routes/paths";

export default function LoginPage() {
  const { user } = useAuth();

  if (user) return <Navigate to={ROLE_HOME[user.role]} replace />;

  return (
    <>
      <header className="auth-head">
        <h1>Iniciar sesión</h1>
        <p className="muted">Ingresa para reportar incidencias y seguir su estado.</p>
      </header>
      <LoginForm />
    </>
  );
}
