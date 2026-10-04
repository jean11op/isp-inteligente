import { useParams } from "react-router";
import Alert from "@/components/ui/Alert";
import Skeleton from "@/components/ui/Skeleton";
import { formatDate } from "@/utils/formatDate";
import { getErrorMessage } from "@/utils/getErrorMessage";
import { useTicket } from "../hooks/useTickets";
import { PRIORITY_LABEL } from "../labels";
import StatusTrack from "./StatusTrack";

export default function TicketDetail() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const { data: ticket, isPending, isError, error } = useTicket(id);

  if (!Number.isFinite(id)) {
    return (
      <Alert tone="error" title="Ticket no encontrado">
        Ticket inexistente o no autorizado.
      </Alert>
    );
  }
  if (isPending) return <Skeleton lines={5} />;
  if (isError) {
    return (
      <Alert tone="error" title="No se pudo cargar el ticket">
        {getErrorMessage(error, "Inténtalo de nuevo en unos segundos.")}
      </Alert>
    );
  }

  return (
    <article className="detail">
      <header className="detail-head">
        <p className="eyebrow">Ticket #{ticket.id}</p>
        <h2>{ticket.titulo}</h2>
      </header>

      <StatusTrack status={ticket.estado} />

      <dl className="detail-grid">
        <dt>Prioridad</dt>
        <dd>{PRIORITY_LABEL[ticket.prioridad]}</dd>
        <dt>Creado</dt>
        <dd>
          <time dateTime={ticket.fecha_creacion}>{formatDate(ticket.fecha_creacion)}</time>
        </dd>
        <dt>Última actualización</dt>
        <dd>
          <time dateTime={ticket.fecha_actualizacion}>{formatDate(ticket.fecha_actualizacion)}</time>
        </dd>
        <dt>Descripción</dt>
        <dd>{ticket.descripcion}</dd>
        {ticket.diagnostico && (
          <>
            <dt>Diagnóstico</dt>
            <dd>{ticket.diagnostico}</dd>
          </>
        )}
        {ticket.solucion && (
          <>
            <dt>Solución</dt>
            <dd>{ticket.solucion}</dd>
          </>
        )}
      </dl>
    </article>
  );
}