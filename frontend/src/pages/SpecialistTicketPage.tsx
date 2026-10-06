import { ChevronLeft } from "lucide-react";
import { Link, useParams } from "react-router";
import Alert from "@/components/ui/Alert";
import QueryBoundary from "@/components/ui/QueryBoundary";
import DiagnosisPanel from "@/features/specialist/components/DiagnosisPanel";
import HistoryTimeline from "@/features/history/components/HistoryTimeline";
import TicketInfo from "@/features/tickets/components/TicketInfo";
import { useTicket } from "@/features/tickets/hooks/useTickets";
import { PATHS } from "@/routes/paths";

export default function SpecialistTicketPage() {
  const id = Number(useParams().ticketId);
  const query = useTicket(id);
  return (
    <>
      <h1 className="visually-hidden">Detalle del ticket</h1>
      <Link className="back-link" to={PATHS.specialist}>
        <ChevronLeft size={18} aria-hidden="true" /> Pendientes
      </Link>
      {!Number.isFinite(id) ? (
        <Alert tone="error" title="Ticket no encontrado" />
      ) : (
        <QueryBoundary query={query} title="No se pudo cargar el ticket" lines={5}>
          {(ticket) => (
            <div className="stack">
              <TicketInfo ticket={ticket} />
              <DiagnosisPanel key={ticket.fecha_actualizacion} ticket={ticket} />
              <HistoryTimeline ticketId={ticket.id} />
            </div>
          )}
        </QueryBoundary>
      )}
    </>
  );
}
