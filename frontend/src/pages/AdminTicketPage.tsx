import { ChevronLeft } from "lucide-react";
import { Link, useParams } from "react-router";
import Alert from "@/components/ui/Alert";
import QueryBoundary from "@/components/ui/QueryBoundary";
import AssignmentPanel from "@/features/admin/components/AssignmentPanel";
import HistoryTimeline from "@/features/history/components/HistoryTimeline";
import TicketInfo from "@/features/tickets/components/TicketInfo";
import { useTicket } from "@/features/tickets/hooks/useTickets";
import VisitCard from "@/features/visits/components/VisitCard";
import { PATHS } from "@/routes/paths";

export default function AdminTicketPage() {
  const id = Number(useParams().ticketId);
  const query = useTicket(id);
  return (
    <>
      <h1 className="visually-hidden">Gestión del ticket</h1>
      <Link className="back-link" to={PATHS.adminTickets}>
        <ChevronLeft size={18} aria-hidden="true" /> Tickets
      </Link>
      {!Number.isFinite(id) ? (
        <Alert tone="error" title="Ticket no encontrado" />
      ) : (
        <QueryBoundary query={query} title="No se pudo cargar el ticket" lines={5}>
          {(ticket) => (
            <div className="stack">
              <TicketInfo ticket={ticket} />
              <AssignmentPanel key={ticket.fecha_actualizacion} ticket={ticket} />
              <VisitCard ticketId={ticket.id} />
              <HistoryTimeline ticketId={ticket.id} />
            </div>
          )}
        </QueryBoundary>
      )}
    </>
  );
}
