import { Link } from "react-router";
import TicketDetail from "../features/tickets/components/TicketDetail";
import { PATHS } from "../routes/paths";

export default function TicketDetailPage() {
  return (
    <>
      <h2>Detalle del ticket</h2>
      <TicketDetail />
      <p>
        <Link to={PATHS.clientTickets}>← Volver a mis tickets</Link>
      </p>
    </>
  );
}