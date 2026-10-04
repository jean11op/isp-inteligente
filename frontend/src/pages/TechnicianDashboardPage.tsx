import EmptyState from "@/components/ui/EmptyState";
import PageHeader from "@/components/ui/PageHeader";

export default function TechnicianDashboardPage() {
  return (
    <>
      <PageHeader eyebrow="Técnico" title="Servicios asignados" />
      <EmptyState
        title="Esta bandeja está en construcción"
        description="Aquí verás tus visitas, la ubicación del cliente y la ruta."
      />
    </>
  );
}