import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import TextField from "@/components/ui/TextField";
import { env } from "@/config/env";
import { PATHS } from "@/routes/paths";
import { getErrorMessage } from "@/utils/getErrorMessage";
import { useAuth } from "../useAuth";

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
    } catch (e) {
      setError(getErrorMessage(e, "No se pudo iniciar sesión"));
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <TextField
        label="Usuario"
        autoComplete="username"
        autoCapitalize="none"
        spellCheck={false}
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
      {error && (
        <Alert tone="error" title="No pudimos iniciar tu sesión">
          {error}
        </Alert>
      )}
      <Button type="submit" loading={isSubmitting}>
        {isSubmitting ? "Ingresando…" : "Ingresar"}
      </Button>
      {env.useMockAuth && (
        <p className="hint">Modo demo: cliente, especialista, tecnico o admin · clave 123456</p>
      )}
      <p className="form-aside">
        ¿No tienes cuenta? <Link to={PATHS.register}>Regístrate</Link>
      </p>
    </form>
  );
}