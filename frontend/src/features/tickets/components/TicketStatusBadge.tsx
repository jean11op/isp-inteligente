import type { TicketStatus } from "../../../types/ticket";
import { STATUS_LABEL } from "../labels";

export default function TicketStatusBadge({ status }: { status: TicketStatus }) {
  return <span className={`badge badge-${status.toLowerCase()}`}>{STATUS_LABEL[status]}</span>;
}