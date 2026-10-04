import { Link } from "react-router";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import EmptyState from "@/components/ui/EmptyState";
import Skeleton from "@/components/ui/Skeleton";
import { PATHS, clientTicketPath } from "@/routes/paths";
import { formatDate } from "@/utils/formatDate";
import { getErrorMessage } from "@/utils/getErrorMessage";
import { useMyTickets } from "../hooks/useTickets";
import TicketStatusBadge from "./TicketStatusBadge";

export default function TicketList() {
  const { data, isPending, isError, error, refetch } = useMyTickets();

  if (isPending) return <Skeleton lines={4} />;

  if (isError) {
    return (
      <Alert
        tone="error"
        title="No se pudieron cargar tus tickets"
        action={
          <Button variant="secondary" onClick={() => refetch()}>
            Reintentar
          </Button>
        }
      >
        {getErrorMessage(error, "Inténtalo de nuevo en unos segundos.")}
      </Alert>
    );
  }

  if (data.length === 0) {
    return (
      <EmptyState
        title="Aún no has reportado incidencias"
        description="Cuando tengas un problema con tu servicio, repórtalo aquí y podrás seguirlo paso a paso."
        action={
          <Link className="btn" to={PATHS.clientNewTicket}>
            Reportar incidencia
          </Link>
        }
      />
    );
  }

  return (
    <ul className="ticket-list">
      {data.map((ticket) => (
        <li key={ticket.id}>
          <Link className="ticket-item" to={clientTicketPath(ticket.id)}>
            <div className="ticket-item-main">
              <span className="ticket-id">#{ticket.id}</span>
              <strong>{ticket.titulo}</strong>
              <time dateTime={ticket.fecha_creacion}>{formatDate(ticket.fecha_creacion)}</time>
            </div>
            <TicketStatusBadge status={ticket.estado} />
          </Link>
        </li>
      ))}
    </ul>
  );
}