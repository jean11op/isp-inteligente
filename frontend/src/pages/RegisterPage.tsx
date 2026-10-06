import RegisterForm from "@/features/auth/components/RegisterForm";

export default function RegisterPage() {
  return (
    <>
      <header className="auth-head">
        <h1>Crear cuenta</h1>
        <p className="muted">Regístrate para reportar fallas de tu servicio.</p>
      </header>
      <RegisterForm />
    </>
  );
}
