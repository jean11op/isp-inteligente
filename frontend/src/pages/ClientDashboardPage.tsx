import { Link } from "react-router";
import { PATHS } from "../routes/paths";

export default function ClientDashboardPage() {
  return (
    <>
      <h2>Panel del cliente</h2>
      <div className="card-grid">
        <Link className="card" to={PATHS.clientNewTicket}>
          Reportar una incidencia
        </Link>
        <Link className="card" to={PATHS.clientTickets}>
          Mis tickets
        </Link>
      </div>
    </>
  );
}