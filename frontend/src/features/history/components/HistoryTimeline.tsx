import { STATUS_LABEL } from "@/features/tickets/labels";
import QueryBoundary from "@/components/ui/QueryBoundary";
import type { TicketStatus } from "@/types/ticket";
import { formatDate } from "@/utils/formatDate";
import { useTicketHistory } from "../hooks/useTicketHistory";

const label = (s: string) => STATUS_LABEL[s as TicketStatus] ?? s;

export default function HistoryTimeline({ ticketId }: { ticketId: number }) {
  const query = useTicketHistory(ticketId);
  return (
    <section className="panel" aria-labelledby={`hist-${ticketId}`}>
      <h3 id={`hist-${ticketId}`}>Historial</h3>
      <QueryBoundary query={query} title="No se pudo cargar el historial" lines={3}>
        {(entries) =>
          entries.length === 0 ? (
            <p className="muted">Aún no hay cambios de estado registrados.</p>
          ) : (
            <ol className="timeline">
              {entries.map((e) => (
                <li key={e.id}>
                  <p>
                    {e.estado_anterior ? `${label(e.estado_anterior)} → ` : ""}
                    <strong>{label(e.estado_nuevo)}</strong>
                  </p>
                  <time dateTime={e.fecha}>{formatDate(e.fecha)}</time>
                  {e.comentario && <p className="muted">{e.comentario}</p>}
                </li>
              ))}
            </ol>
          )
        }
      </QueryBoundary>
    </section>
  );
}
