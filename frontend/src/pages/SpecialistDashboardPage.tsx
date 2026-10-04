import EmptyState from "@/components/ui/EmptyState";
import PageHeader from "@/components/ui/PageHeader";

export default function SpecialistDashboardPage() {
  return (
    <>
      <PageHeader eyebrow="Especialista" title="Tickets pendientes" />
      <EmptyState
        title="Esta bandeja está en construcción"
        description="Aquí verás los casos que esperan tu diagnóstico."
      />
    </>
  );
}