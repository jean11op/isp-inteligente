import { ClipboardList, Inbox, Stethoscope, Truck } from "lucide-react";
import EmptyState from "@/components/ui/EmptyState";
import PageHeader from "@/components/ui/PageHeader";
import QueryBoundary from "@/components/ui/QueryBoundary";
import StatCard from "@/components/ui/StatCard";
import TicketQueue from "@/features/tickets/components/TicketQueue";
import { useTickets } from "@/features/tickets/hooks/useTickets";
import { specialistTicketPath } from "@/routes/paths";

export default function SpecialistDashboardPage() {
  const query = useTickets();
  return (
    <>
      <PageHeader eyebrow="Especialista" title="Tickets pendientes" />
      <QueryBoundary query={query} title="No pudimos cargar tus tickets">
        {(tickets) => {
          const pending = tickets.filter((t) => ["NUEVO", "EN_REVISION", "ESPERANDO_ESPECIALISTA"].includes(t.estado));
          const diagnosed = tickets.filter((t) => t.estado === "DIAGNOSTICADO");
          const visit = tickets.filter((t) => t.estado === "REQUIERE_VISITA");
          const open = tickets.filter((t) => t.estado !== "CERRADO");
          return (
            <div className="stack">
              <div className="stat-grid">
                <StatCard label="Por atender" value={pending.length} icon={Inbox} tone="accent" />
                <StatCard label="Diagnosticados" value={diagnosed.length} icon={Stethoscope} />
                <StatCard label="Requieren visita" value={visit.length} icon={Truck} tone="warn" />
                <StatCard label="Asignados en total" value={tickets.length} icon={ClipboardList} />
              </div>
              {open.length === 0 ? (
                <EmptyState title="Bandeja vacía" description="No tienes tickets asignados por ahora." />
              ) : (
                <TicketQueue tickets={open} pathFor={specialistTicketPath} />
              )}
            </div>
          );
        }}
      </QueryBoundary>
    </>
  );
}
