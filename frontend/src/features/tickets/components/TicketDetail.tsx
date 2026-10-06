import { useParams } from "react-router";
import Alert from "@/components/ui/Alert";
import QueryBoundary from "@/components/ui/QueryBoundary";
import EvaluationForm from "@/features/evaluations/components/EvaluationForm";
import HistoryTimeline from "@/features/history/components/HistoryTimeline";
import VisitCard from "@/features/visits/components/VisitCard";
import { useTicket } from "../hooks/useTickets";
import TicketInfo from "./TicketInfo";

export default function TicketDetail() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const query = useTicket(id);

  if (!Number.isFinite(id)) {
    return (
      <Alert tone="error" title="Ticket no encontrado">
        Ticket inexistente o no autorizado.
      </Alert>
    );
  }

  return (
    <QueryBoundary query={query} title="No se pudo cargar el ticket" lines={5}>
      {(ticket) => (
        <div className="stack">
          <TicketInfo ticket={ticket} />
          <VisitCard ticketId={ticket.id} />
          {(ticket.estado === "RESUELTO" || ticket.estado === "CERRADO") && <EvaluationForm ticketId={ticket.id} />}
          <HistoryTimeline ticketId={ticket.id} />
        </div>
      )}
    </QueryBoundary>
  );
}
