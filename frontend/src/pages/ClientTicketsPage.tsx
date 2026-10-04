import { Link } from "react-router";
import PageHeader from "@/components/ui/PageHeader";
import TicketList from "@/features/tickets/components/TicketList";
import { PATHS } from "@/routes/paths";

export default function ClientTicketsPage() {
  return (
    <>
      <PageHeader
        title="Mis tickets"
        actions={
          <Link className="btn" to={PATHS.clientNewTicket}>
            Reportar incidencia
          </Link>
        }
      />
      <TicketList />
    </>
  );
}