import { useParams } from "react-router";
import { formatDate } from "../../../utils/formatDate";
import { getErrorMessage } from "../../../utils/getErrorMessage";
import { useTicket } from "../hooks/useTickets";
import { PRIORITY_LABEL } from "../labels";
import TicketStatusBadge from "./TicketStatusBadge";

export default function TicketDetail() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const { data: ticket, isPending, isError, error } = useTicket(id);

  if (!Number.isFinite(id)) {
    return <p className="form-error">Ticket inexistente o no autorizado</p>;
  }
  if (isPending) return <p>Cargando ticket...</p>;
  if (isError) {
    return (
      <p className="form-error">
        {getErrorMessage(error, "No se pudo cargar el ticket")}
      </p>
    );
  }

  return (
    <article className="detail">
      <h3>
        #{ticket.id} · {ticket.titulo}
      </h3>
      <p>
        <TicketStatusBadge status={ticket.estado} />
      </p>
      <dl className="detail-grid">
        <dt>Prioridad</dt>
        <dd>{PRIORITY_LABEL[ticket.prioridad]}</dd>
        <dt>Creado</dt>
        <dd>{formatDate(ticket.fecha_creacion)}</dd>
        <dt>Última actualización</dt>
        <dd>{formatDate(ticket.fecha_actualizacion)}</dd>
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