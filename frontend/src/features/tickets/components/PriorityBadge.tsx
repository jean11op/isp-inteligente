import type { TicketPriority } from "@/types/ticket";
import { PRIORITY_LABEL, PRIORITY_TONE } from "../labels";

export default function PriorityBadge({ priority }: { priority: TicketPriority }) {
  return (
    <span className="badge badge-flat" data-tone={PRIORITY_TONE[priority]}>
      {PRIORITY_LABEL[priority]}
    </span>
  );
}
