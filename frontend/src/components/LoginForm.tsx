import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router";

import TextField from "./ui/TextField";
import { env } from "../config/env";
import { PATHS } from "../routes/paths";
import { getErrorMessage } from "../utils/getErrorMessage";
import { useAuth } from "../features/auth/useAuth";

const loginSchema = z.object({
  username: z.string().min(1, "Ingresa tu usuario"),
  password: z.string().min(1, "Ingresa tu contraseña"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginForm() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginFormValues) {
    setError(null);
    try {
      await login(values);
      // La redirección la hace LoginPage cuando detecta al usuario.
    } catch (e) {
      setError(getErrorMessage(e, "No se pudo iniciar sesión"));
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <TextField
        label="Usuario"
        autoComplete="username"
        error={errors.username?.message}
        {...register("username")}
      />
      <TextField
        label="Contraseña"
        type="password"
        autoComplete="current-password"
        error={errors.password?.message}
        {...register("password")}
      />
      {error && <p className="form-error">{error}</p>}
      <button className="btn" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Ingresando..." : "Ingresar"}
      </button>
      {env.useMockAuth && (
        <p className="hint">
          Modo demo: usuario cliente, especialista, tecnico o admin. Clave: 123456
        </p>
      )}
      <p>
        ¿No tienes cuenta? <Link to={PATHS.register}>Regístrate</Link>
      </p>
    </form>
  );
}