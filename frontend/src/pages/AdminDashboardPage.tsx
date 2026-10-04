import EmptyState from "@/components/ui/EmptyState";
import PageHeader from "@/components/ui/PageHeader";

export default function AdminDashboardPage() {
  return (
    <>
      <PageHeader eyebrow="Administrador" title="Panel de administración" />
      <EmptyState
        title="Este panel está en construcción"
        description="Aquí gestionarás clientes, técnicos, tickets e inventario."
      />
    </>
  );
}