import { STATUS_LABEL, STATUS_TONE } from "@/features/tickets/labels";
import type { Ticket, TicketStatus } from "@/types/ticket";

export default function StatusBreakdown({ tickets }: { tickets: Ticket[] }) {
  const counts = new Map<TicketStatus, number>();
  tickets.forEach((t) => counts.set(t.estado, (counts.get(t.estado) ?? 0) + 1));
  const rows = [...counts.entries()].sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...rows.map(([, n]) => n));

  return (
    <section className="panel" aria-labelledby="breakdown-title">
      <h3 id="breakdown-title">Tickets por estado</h3>
      {rows.length === 0 ? (
        <p className="muted">Todavía no hay tickets.</p>
      ) : (
        <ul className="bars">
          {rows.map(([status, n]) => (
            <li key={status}>
              <span>{STATUS_LABEL[status]}</span>
              <span className="bar" data-tone={STATUS_TONE[status]} style={{ inlineSize: `${(n / max) * 100}%` }} />
              <strong>{n}</strong>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
