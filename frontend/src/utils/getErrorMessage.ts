import { isAxiosError } from "axios";

export function getErrorMessage(
  error: unknown,
  fallback = "Ocurrió un error inesperado",
): string {
  if (isAxiosError(error)) {
    if (error.code === "ERR_NETWORK") {
      return "No se pudo conectar con el servidor";
    }
    const data: unknown = error.response?.data;
    if (data && typeof data === "object") {
      const messages = Object.values(data as Record<string, unknown>).flatMap(
        (value) => (Array.isArray(value) ? value.map(String) : [String(value)]),
      );
      if (messages.length > 0) return messages.join(" ");
    }
  }
  if (error instanceof Error) return error.message;
  return fallback;
}