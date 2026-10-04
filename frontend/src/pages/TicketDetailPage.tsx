import { ChevronLeft } from "lucide-react";
import { Link } from "react-router";
import TicketDetail from "@/features/tickets/components/TicketDetail";
import { PATHS } from "@/routes/paths";

export default function TicketDetailPage() {
  return (
    <>
      <h1 className="visually-hidden">Detalle del ticket</h1>
      <Link className="back-link" to={PATHS.clientTickets}>
        <ChevronLeft size={18} aria-hidden="true" />
        Mis tickets
      </Link>
      <TicketDetail />
    </>
  );
}