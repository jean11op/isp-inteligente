import type { TicketStatus } from "@/types/ticket";
import { STATUS_LABEL, STATUS_TONE } from "../labels";

export default function TicketStatusBadge({ status }: { status: TicketStatus }) {
  return (
    <span className="badge" data-tone={STATUS_TONE[status]}>
      {STATUS_LABEL[status]}
    </span>
  );
}