import { Plus } from "lucide-react";
import { Link } from "react-router";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import Skeleton from "@/components/ui/Skeleton";
import { useAuth } from "@/features/auth/useAuth";
import StatusTrack from "@/features/tickets/components/StatusTrack";
import { useMyTickets } from "@/features/tickets/hooks/useTickets";
import { PATHS, clientTicketPath } from "@/routes/paths";
import { getErrorMessage } from "@/utils/getErrorMessage";

export default function ClientDashboardPage() {
  const { user } = useAuth();
  const { data, isPending, isError, error, refetch } = useMyTickets();
  const active = data?.find((ticket) => ticket.estado !== "CERRADO");

  return (
    <div className="home">
      <header className="home-greeting">
        <p className="eyebrow">Panel del cliente</p>
        <h1>Hola, {user?.fullName?.split(" ")[0] ?? user?.username}</h1>
      </header>

      {isPending && <Skeleton lines={3} />}

      {isError && (
        <Alert
          tone="error"
          title="No pudimos cargar tus tickets"
          action={
            <Button variant="secondary" onClick={() => refetch()}>
              Reintentar
            </Button>
          }
        >
          {getErrorMessage(error, "Inténtalo de nuevo en unos segundos.")}
        </Alert>
      )}

      {data &&
        (active ? (
          <section className="home-block" aria-labelledby="active-title">
            <p className="eyebrow">Incidencia activa · #{active.id}</p>
            <h2 id="active-title">{active.titulo}</h2>
            <StatusTrack status={active.estado} />
            <Link className="btn btn-secondary" to={clientTicketPath(active.id)}>
              Ver detalle
            </Link>
          </section>
        ) : (
          <section className="home-block">
            <h2>Todo en orden</h2>
            <p>No tienes incidencias abiertas.</p>
          </section>
        ))}

      <div className="home-actions">
        <Link className="btn" to={PATHS.clientNewTicket}>
          <Plus size={20} aria-hidden="true" />
          Reportar incidencia
        </Link>
        <Link className="btn btn-secondary" to={PATHS.clientTickets}>
          Ver todos mis tickets
        </Link>
      </div>
    </div>
  );
}