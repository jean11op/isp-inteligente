import { formatDate } from "@/utils/formatDate";
import type { Ticket } from "@/types/ticket";
import PriorityBadge from "./PriorityBadge";
import StatusTrack from "./StatusTrack";
import Button from "@/components/ui/Button";
import { useAuth } from "@/features/auth/useAuth";
import { useRequestSpecialist, useUpdateTicket } from "../hooks/useTickets";

export default function TicketInfo({ ticket }: { ticket: Ticket }) {
  const { user } = useAuth();
  const updateTicket = useUpdateTicket(ticket.id);
  const requestSpecialist = useRequestSpecialist(ticket.id);
  const canRequestSpecialist =
    user?.role === "CLIENTE" && ["NUEVO", "EN_REVISION"].includes(ticket.estado);
  const canCloseTicket = user?.role === "CLIENTE" && ticket.estado === "RESUELTO";

  return (
    <article className="detail">
      <header className="detail-head">
        <p className="eyebrow">Ticket #{ticket.id}</p>
        <h2>{ticket.titulo}</h2>
      </header>

      <StatusTrack status={ticket.estado} />
      {(canRequestSpecialist || canCloseTicket) && (
        <div className="actions">
          {canRequestSpecialist && (
            <Button
              type="button"
              onClick={() => requestSpecialist.mutate()}
              disabled={requestSpecialist.isPending}
            >
              {requestSpecialist.isPending ? "Solicitando..." : "Solicitar especialista"}
            </Button>
          )}
          {canCloseTicket && (
            <Button
              type="button"
              onClick={() => updateTicket.mutate({ estado: "CERRADO" })}
              disabled={updateTicket.isPending}
            >
              {updateTicket.isPending ? "Cerrando..." : "Confirmar solución"}
            </Button>
          )}
        </div>
      )}

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
        <dt>Cliente</dt>
        <dd>
          {ticket.client_info.nombres} {ticket.client_info.apellidos} · {ticket.client_info.telefono}
        </dd>
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
