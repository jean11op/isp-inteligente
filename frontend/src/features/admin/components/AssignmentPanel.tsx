import { useState, type FormEvent } from "react";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import { SelectField } from "@/components/ui/FormFields";
import TextField from "@/components/ui/TextField";
import { NEXT_STATUSES, STATUS_LABEL } from "@/features/tickets/labels";
import { useUpdateTicket } from "@/features/tickets/hooks/useTickets";
import { useCreateVisit, useTicketVisit } from "@/features/visits/hooks/useVisits";
import type { Ticket, TicketStatus } from "@/types/ticket";
import { getErrorMessage } from "@/utils/getErrorMessage";
import { staffLabel } from "../staffLabel";
import { useSpecialists, useTechnicians, useUsers } from "../hooks/usePeople";

/** CU-34 gestionar tickets · CU-41 asignación de técnico · programación de visitas. */
export default function AssignmentPanel({ ticket }: { ticket: Ticket }) {
  const update = useUpdateTicket(ticket.id);
  const specialists = useSpecialists();
  const technicians = useTechnicians();
  const users = useUsers();
  const { visit } = useTicketVisit(ticket.id);
  const createVisit = useCreateVisit();

  const [specialist, setSpecialist] = useState(String(ticket.specialist ?? ""));
  const [technician, setTechnician] = useState(String(ticket.technician ?? ""));
  const [nextStatus, setNextStatus] = useState("");
  const [when, setWhen] = useState("");

  const nextOptions = (NEXT_STATUSES[ticket.estado] ?? []).filter((s) => s !== "TECNICO_ASIGNADO");
  const needsTechnician = ticket.estado === "REQUIERE_VISITA" || ticket.estado === "SEGUNDA_VISITA";

  function saveSpecialist(event: FormEvent) {
    event.preventDefault();
    update.mutate({ specialist: Number(specialist) });
  }

  function saveTechnician(event: FormEvent) {
    event.preventDefault();
    update.mutate(
      needsTechnician
        ? { technician: Number(technician), estado: "TECNICO_ASIGNADO" }
        : { technician: Number(technician) },
    );
  }

  function saveStatus(event: FormEvent) {
    event.preventDefault();
    update.mutate({ estado: nextStatus as TicketStatus }, { onSuccess: () => setNextStatus("") });
  }

  function saveVisit(event: FormEvent) {
    event.preventDefault();
    if (!ticket.technician) return;
    createVisit.mutate(
      { ticket: ticket.id, technician: ticket.technician, fecha_programada: new Date(when).toISOString() },
      { onSuccess: () => setWhen("") },
    );
  }

  const error = update.error ?? createVisit.error;

  return (
    <section className="panel" aria-labelledby="assign-title">
      <h3 id="assign-title">Gestión del ticket</h3>

      <form className="form form-inline" onSubmit={saveSpecialist}>
        <SelectField label="Especialista" value={specialist} onChange={(e) => setSpecialist(e.target.value)}>
          <option value="">Sin asignar</option>
          {specialists.data?.filter((s) => s.activo).map((s) => (
            <option key={s.id} value={s.id}>
              {staffLabel(s, users.data)}
            </option>
          ))}
        </SelectField>
        <Button type="submit" variant="secondary" loading={update.isPending} disabled={!specialist}>
          Asignar
        </Button>
      </form>

      <form className="form form-inline" onSubmit={saveTechnician}>
        <SelectField
          label="Técnico"
          hint={needsTechnician ? "Al asignar, el ticket pasa a «Técnico asignado»." : undefined}
          value={technician}
          onChange={(e) => setTechnician(e.target.value)}
        >
          <option value="">Sin asignar</option>
          {technicians.data?.filter((t) => t.activo && t.disponible).map((t) => (
            <option key={t.id} value={t.id}>
              {staffLabel(t, users.data)}
            </option>
          ))}
        </SelectField>
        <Button type="submit" variant="secondary" loading={update.isPending} disabled={!technician}>
          Asignar
        </Button>
      </form>

      {nextOptions.length > 0 && (
        <form className="form form-inline" onSubmit={saveStatus}>
          <SelectField label="Cambiar estado" value={nextStatus} onChange={(e) => setNextStatus(e.target.value)}>
            <option value="">Selecciona…</option>
            {nextOptions.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABEL[s]}
              </option>
            ))}
          </SelectField>
          <Button type="submit" variant="secondary" loading={update.isPending} disabled={!nextStatus}>
            Aplicar
          </Button>
        </form>
      )}

      {ticket.estado === "TECNICO_ASIGNADO" && !visit && (
        <form className="form form-inline" onSubmit={saveVisit}>
          <TextField
            label="Programar visita"
            type="datetime-local"
            value={when}
            onChange={(e) => setWhen(e.target.value)}
            required
          />
          <Button type="submit" loading={createVisit.isPending} disabled={!when}>
            Crear visita
          </Button>
        </form>
      )}

      {error && (
        <Alert tone="error" title="No se pudo guardar el cambio">
          {getErrorMessage(error)}
        </Alert>
      )}
    </section>
  );
}
