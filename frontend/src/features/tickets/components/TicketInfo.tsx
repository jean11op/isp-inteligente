import { formatDate } from "@/utils/formatDate";
import type { Ticket } from "@/types/ticket";
import PriorityBadge from "./PriorityBadge";
import StatusTrack from "./StatusTrack";

export default function TicketInfo({ ticket }: { ticket: Ticket }) {
  return (
    <article className="detail">
      <header className="detail-head">
        <p className="eyebrow">Ticket #{ticket.id}</p>
        <h2>{ticket.titulo}</h2>
      </header>

      <StatusTrack status={ticket.estado} />

      <dl className="detail-grid">
        <dt>Prioridad</dt>
        <dd>
          <PriorityBadge priority={ticket.prioridad} />
        </dd>
        <dt>Creado</dt>
        <dd>
          <time dateTime={ticket.fecha_creacion}>{formatDate(ticket.fecha_creacion)}</time>
        </dd>
        <dt>Actualizado</dt>
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
