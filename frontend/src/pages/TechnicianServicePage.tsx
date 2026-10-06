import { ChevronLeft } from "lucide-react";
import { Link, useParams } from "react-router";
import Alert from "@/components/ui/Alert";
import QueryBoundary from "@/components/ui/QueryBoundary";
import ServiceWorkflow from "@/features/technician/components/ServiceWorkflow";
import TechnicianRouteMap from "@/features/technician/components/TechnicianRouteMap";
import TicketInfo from "@/features/tickets/components/TicketInfo";
import { useTicket } from "@/features/tickets/hooks/useTickets";
import VisitCard from "@/features/visits/components/VisitCard";
import { PATHS } from "@/routes/paths";

export default function TechnicianServicePage() {
  const id = Number(useParams().ticketId);
  const query = useTicket(id);

  return (
    <>
      <h1 className="visually-hidden">Servicio asignado</h1>

      <Link className="back-link" to={PATHS.technician}>
        <ChevronLeft size={18} aria-hidden="true" /> Mis servicios
      </Link>

      {!Number.isFinite(id) ? (
        <Alert tone="error" title="Servicio no encontrado" />
      ) : (
        <QueryBoundary
          query={query}
          title="No se pudo cargar el servicio"
          lines={5}
        >
          {(ticket) => (
            <div className="stack">
              <TicketInfo ticket={ticket} />
              <VisitCard ticketId={ticket.id} />
              <TechnicianRouteMap ticket={ticket} />
              <ServiceWorkflow ticket={ticket} />
            </div>
          )}
        </QueryBoundary>
      )}
    </>
  );
}