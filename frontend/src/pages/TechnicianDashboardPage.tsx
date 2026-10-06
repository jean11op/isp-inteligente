import { CheckCircle2, Navigation, Wrench } from "lucide-react";
import EmptyState from "@/components/ui/EmptyState";
import PageHeader from "@/components/ui/PageHeader";
import QueryBoundary from "@/components/ui/QueryBoundary";
import StatCard from "@/components/ui/StatCard";
import TicketQueue from "@/features/tickets/components/TicketQueue";
import { useTickets } from "@/features/tickets/hooks/useTickets";
import { technicianTicketPath } from "@/routes/paths";

export default function TechnicianDashboardPage() {
  const query = useTickets();
  return (
    <>
      <PageHeader eyebrow="Técnico" title="Servicios asignados" />
      <QueryBoundary query={query} title="No pudimos cargar tus servicios">
        {(tickets) => {
          const active = tickets.filter((t) => !["RESUELTO", "CERRADO"].includes(t.estado));
          const onRoute = tickets.filter((t) => ["EN_CAMINO", "EN_DOMICILIO", "EN_ATENCION"].includes(t.estado));
          const done = tickets.filter((t) => ["RESUELTO", "CERRADO"].includes(t.estado));
          return (
            <div className="stack">
              <div className="stat-grid">
                <StatCard label="Pendientes" value={active.length} icon={Wrench} tone="accent" />
                <StatCard label="En curso" value={onRoute.length} icon={Navigation} tone="warn" />
                <StatCard label="Completados" value={done.length} icon={CheckCircle2} tone="ok" />
              </div>
              {active.length === 0 ? (
                <EmptyState title="Sin servicios pendientes" description="Cuando te asignen una visita aparecerá aquí." />
              ) : (
                <TicketQueue tickets={active} pathFor={technicianTicketPath} />
              )}
            </div>
          );
        }}
      </QueryBoundary>
    </>
  );
}
