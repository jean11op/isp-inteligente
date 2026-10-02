import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router";
import TextField from "../../../components/ui/TextField";
import { PATHS } from "../../../routes/paths";
import { getErrorMessage } from "../../../utils/getErrorMessage";
import { register as registerRequest } from "../services/authService";

const registerSchema = z
  .object({
    nombres: z.string().min(2, "Ingresa tus nombres"),
    apellidos: z.string().min(2, "Ingresa tus apellidos"),
    documento: z
      .string()
      .min(8, "El documento debe tener al menos 8 caracteres")
      .max(20, "Máximo 20 caracteres"),
    telefono: z
      .string()
      .min(7, "Ingresa un teléfono válido")
      .max(20, "Máximo 20 caracteres"),
    username: z.string().min(3, "Mínimo 3 caracteres"),
    email: z.email("Correo electrónico inválido"),
    password: z.string().min(8, "Mínimo 8 caracteres"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Las contraseñas no coinciden",
    path: ["confirmPassword"],
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterForm() {
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({ resolver: zodResolver(registerSchema) });

  async function onSubmit(values: RegisterFormValues) {
    setError(null);
    try {
      await registerRequest({
        username: values.username,
        email: values.email,
        password: values.password,
        nombres: values.nombres,
        apellidos: values.apellidos,
        documento: values.documento,
        telefono: values.telefono,
      });
      setSuccess(true);
    } catch (e) {
      setError(getErrorMessage(e, "No se pudo crear la cuenta"));
    }
  }

  if (success) {
    return (
      <div className="form">
        <p className="form-success">Cuenta creada. Ya puedes iniciar sesión.</p>
        <Link to={PATHS.login}>Ir a iniciar sesión</Link>
      </div>
    );
  }

  return (
    <form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <TextField label="Nombres" error={errors.nombres?.message} {...register("nombres")} />
      <TextField label="Apellidos" error={errors.apellidos?.message} {...register("apellidos")} />
      <TextField label="Documento de identidad" error={errors.documento?.message} {...register("documento")} />
      <TextField label="Teléfono" type="tel" error={errors.telefono?.message} {...register("telefono")} />
      <TextField label="Usuario" autoComplete="username" error={errors.username?.message} {...register("username")} />
      <TextField label="Correo electrónico" type="email" autoComplete="email" error={errors.email?.message} {...register("email")} />
      <TextField label="Contraseña" type="password" autoComplete="new-password" error={errors.password?.message} {...register("password")} />
      <TextField label="Confirmar contraseña" type="password" autoComplete="new-password" error={errors.confirmPassword?.message} {...register("confirmPassword")} />
      {error && <p className="form-error">{error}</p>}
      <button className="btn" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creando cuenta..." : "Crear cuenta"}
      </button>
      <p>
        ¿Ya tienes cuenta? <Link to={PATHS.login}>Inicia sesión</Link>
      </p>
    </form>
  );
}