import { Link } from "react-router";
import { formatDate } from "@/utils/formatDate";
import type { Ticket } from "@/types/ticket";
import PriorityBadge from "./PriorityBadge";
import TicketStatusBadge from "./TicketStatusBadge";

interface TicketQueueProps {
  tickets: Ticket[];
  pathFor: (id: number) => string;
}

export default function TicketQueue({ tickets, pathFor }: TicketQueueProps) {
  return (
    <ul className="ticket-list">
      {tickets.map((ticket) => (
        <li key={ticket.id}>
          <Link className="ticket-item" to={pathFor(ticket.id)}>
            <div className="ticket-item-main">
              <span className="ticket-id">#{ticket.id}</span>
              <strong>{ticket.titulo}</strong>
              <time dateTime={ticket.fecha_creacion}>{formatDate(ticket.fecha_creacion)}</time>
            </div>
            <div className="ticket-item-badges">
              <PriorityBadge priority={ticket.prioridad} />
              <TicketStatusBadge status={ticket.estado} />
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}
