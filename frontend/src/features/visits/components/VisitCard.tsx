import { CalendarClock } from "lucide-react";
import { VISIT_LABEL } from "@/features/tickets/labels";
import { formatDate } from "@/utils/formatDate";
import { useTicketVisit } from "../hooks/useVisits";

/** Información de la visita técnica del ticket (CU-06 / CU-20). */
export default function VisitCard({ ticketId }: { ticketId: number }) {
  const { visit, isPending } = useTicketVisit(ticketId);
  if (isPending || !visit) return null;

  return (
    <section className="panel" aria-labelledby={`visit-${ticketId}`}>
      <h3 id={`visit-${ticketId}`}>Visita técnica</h3>
      <dl className="detail-grid">
        <dt>Estado</dt>
        <dd>
          <span className="badge" data-tone="field">
            {VISIT_LABEL[visit.estado]}
          </span>
        </dd>
        <dt>
          <CalendarClock size={14} aria-hidden="true" /> Programada
        </dt>
        <dd>{formatDate(visit.fecha_programada)}</dd>
        {visit.resultado && (
          <>
            <dt>Resultado</dt>
            <dd>{visit.resultado}</dd>
          </>
        )}
      </dl>
    </section>
  );
}
