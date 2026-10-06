import { useState } from "react";
import EmptyState from "@/components/ui/EmptyState";
import { SelectField } from "@/components/ui/FormFields";
import PageHeader from "@/components/ui/PageHeader";
import QueryBoundary from "@/components/ui/QueryBoundary";
import TicketQueue from "@/features/tickets/components/TicketQueue";
import { useTickets } from "@/features/tickets/hooks/useTickets";
import { STATUS_LABEL } from "@/features/tickets/labels";
import { adminTicketPath } from "@/routes/paths";
import type { TicketStatus } from "@/types/ticket";

export default function AdminTicketsPage() {
  const query = useTickets();
  const [filter, setFilter] = useState("");

  return (
    <>
      <PageHeader eyebrow="Administrador" title="Tickets" />
      <div className="stack">
        <SelectField label="Filtrar por estado" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="">Todos</option>
          {Object.entries(STATUS_LABEL).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </SelectField>
        <QueryBoundary query={query} title="No pudimos cargar los tickets">
          {(tickets) => {
            const shown = filter ? tickets.filter((t) => t.estado === (filter as TicketStatus)) : tickets;
            return shown.length === 0 ? (
              <EmptyState title="Sin resultados" description="No hay tickets con ese estado." />
            ) : (
              <TicketQueue tickets={shown} pathFor={adminTicketPath} />
            );
          }}
        </QueryBoundary>
      </div>
    </>
  );
}
