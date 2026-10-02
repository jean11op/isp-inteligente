import { Link } from "react-router";
import TicketList from "../features/tickets/components/TicketList";
import { PATHS } from "../routes/paths";

export default function ClientTicketsPage() {
  return (
    <>
      <div className="page-header">
        <h2>Mis tickets</h2>
        <Link className="btn" to={PATHS.clientNewTicket}>
          Reportar incidencia
        </Link>
      </div>
      <TicketList />
      <p>
        <Link to={PATHS.client}>← Volver al panel</Link>
      </p>
    </>
  );
}