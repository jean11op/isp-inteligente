export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("es-PE", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}