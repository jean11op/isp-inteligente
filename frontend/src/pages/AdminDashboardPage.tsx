import { Boxes, Headset, Ticket as TicketIcon, Users, Wrench } from "lucide-react";
import { Link } from "react-router";
import PageHeader from "@/components/ui/PageHeader";
import QueryBoundary from "@/components/ui/QueryBoundary";
import StatCard from "@/components/ui/StatCard";
import StatusBreakdown from "@/features/admin/components/StatusBreakdown";
import { useClients, useSpecialists, useTechnicians } from "@/features/admin/hooks/usePeople";
import TicketQueue from "@/features/tickets/components/TicketQueue";
import { useTickets } from "@/features/tickets/hooks/useTickets";
import { PATHS, adminTicketPath } from "@/routes/paths";

export default function AdminDashboardPage() {
  const tickets = useTickets();
  const clients = useClients();
  const technicians = useTechnicians();
  const specialists = useSpecialists();

  return (
    <>
      <PageHeader eyebrow="Administrador" title="Resumen operativo" />
      <QueryBoundary query={tickets} title="No pudimos cargar los tickets">
        {(list) => {
          const open = list.filter((t) => t.estado !== "CERRADO");
          const urgent = open.filter((t) => t.prioridad === "CRITICA" || t.estado === "ESCALADO" || t.estado === "NO_RESUELTO");
          return (
            <div className="stack">
              <div className="stat-grid">
                <StatCard label="Tickets abiertos" value={open.length} icon={TicketIcon} tone="accent" />
                <StatCard label="Requieren atención" value={urgent.length} icon={Wrench} tone={urgent.length ? "danger" : "neutral"} />
                <StatCard label="Clientes" value={clients.data?.length ?? "—"} icon={Users} />
                <StatCard label="Técnicos" value={technicians.data?.length ?? "—"} icon={Boxes} />
                <StatCard label="Especialistas" value={specialists.data?.length ?? "—"} icon={Headset} />
              </div>
              <StatusBreakdown tickets={list} />
              <section className="panel">
                <div className="panel-head">
                  <h3>Últimos tickets</h3>
                  <Link to={PATHS.adminTickets}>Ver todos</Link>
                </div>
                <TicketQueue tickets={list.slice(0, 5)} pathFor={adminTicketPath} />
              </section>
            </div>
          );
        }}
      </QueryBoundary>
    </>
  );
}
