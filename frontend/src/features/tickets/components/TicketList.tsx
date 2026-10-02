import { Link } from "react-router";
import { clientTicketPath } from "../../../routes/paths";
import { formatDate } from "../../../utils/formatDate";
import { getErrorMessage } from "../../../utils/getErrorMessage";
import { useMyTickets } from "../hooks/useTickets";
import TicketStatusBadge from "./TicketStatusBadge";

export default function TicketList() {
  const { data, isPending, isError, error, refetch } = useMyTickets();

  if (isPending) return <p>Cargando tickets...</p>;

  if (isError) {
    return (
      <div className="form">
        <p className="form-error">
          {getErrorMessage(error, "No se pudieron cargar los tickets")}
        </p>
        <button className="btn" type="button" onClick={() => refetch()}>
          Reintentar
        </button>
      </div>
    );
  }

  if (data.length === 0) return <p>Aún no has reportado ninguna incidencia.</p>;

  return (
    <ul className="ticket-list">
      {data.map((ticket) => (
        <li key={ticket.id}>
          <Link className="ticket-item" to={clientTicketPath(ticket.id)}>
            <div>
              <strong>
                #{ticket.id} · {ticket.titulo}
              </strong>
              <small>{formatDate(ticket.fecha_creacion)}</small>
            </div>
            <TicketStatusBadge status={ticket.estado} />
          </Link>
        </li>
      ))}
    </ul>
  );
}