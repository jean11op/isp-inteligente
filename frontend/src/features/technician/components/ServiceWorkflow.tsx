import { useState, type FormEvent } from "react";
import { CheckCircle2, MapPin, Navigation, Wrench } from "lucide-react";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import { SelectField, TextAreaField } from "@/components/ui/FormFields";
import TextField from "@/components/ui/TextField";
import { useInventory, useRegisterUsage, useVisitUsage } from "@/features/inventory/hooks/useInventory";
import { useUpdateTicket } from "@/features/tickets/hooks/useTickets";
import { useTicketVisit, useUpdateVisit } from "@/features/visits/hooks/useVisits";
import type { Ticket, TicketStatus } from "@/types/ticket";
import type { VisitStatus } from "@/types/domain";
import { getErrorMessage } from "@/utils/getErrorMessage";

interface Step {
  from: TicketStatus;
  label: string;
  visit: VisitStatus;
  ticket: TicketStatus;
  icon: typeof Navigation;
}

const STEPS: Step[] = [
  { from: "TECNICO_ASIGNADO", label: "Iniciar desplazamiento", visit: "EN_CAMINO", ticket: "EN_CAMINO", icon: Navigation },
  { from: "EN_CAMINO", label: "Registrar llegada", visit: "EN_DOMICILIO", ticket: "EN_DOMICILIO", icon: MapPin },
  { from: "EN_DOMICILIO", label: "Iniciar atención", visit: "EN_ATENCION", ticket: "EN_ATENCION", icon: Wrench },
];

/** CU-23 desplazamiento · CU-25 llegada · CU-26 resultado · CU-27 materiales · CU-28 no resuelto. */
export default function ServiceWorkflow({ ticket }: { ticket: Ticket }) {
  const { visit, isPending } = useTicketVisit(ticket.id);
  const updateVisit = useUpdateVisit();
  const updateTicket = useUpdateTicket(ticket.id);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (isPending) return null;
  if (!visit) {
    return (
      <Alert tone="warning" title="Aún no hay una visita programada">
        El administrador debe crear la visita para este ticket antes de que puedas iniciarla.
      </Alert>
    );
  }
  const currentVisit = visit;

  async function run(action: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (e) {
      setError(getErrorMessage(e, "No se pudo completar la acción"));
    } finally {
      setBusy(false);
    }
  }

  const step = STEPS.find((s) => s.from === ticket.estado);

  async function advance(s: Step) {
    await updateVisit.mutateAsync({ id: currentVisit.id, patch: { estado: s.visit } });
    await updateTicket.mutateAsync({ estado: s.ticket });
  }

  async function finish(resolved: boolean, text: string) {
    await updateVisit.mutateAsync({ id: currentVisit.id, patch: { estado: "COMPLETADA", resultado: text } });
    await updateTicket.mutateAsync(
      resolved ? { estado: "RESUELTO", solucion: text } : { estado: "NO_RESUELTO", solucion: text },
    );
  }

  return (
    <div className="stack">
      {step && (
        <section className="panel">
          <h3>Siguiente paso</h3>
          <Button loading={busy} onClick={() => void run(() => advance(step))}>
            <step.icon size={18} aria-hidden="true" /> {step.label}
          </Button>
        </section>
      )}

      {ticket.estado === "EN_ATENCION" && (
        <>
          <Materials visitId={currentVisit.id} />
          <ResultForm busy={busy} onSubmit={(resolved, text) => void run(() => finish(resolved, text))} />
        </>
      )}

      {ticket.estado === "TECNICO_ASIGNADO" || step ? null : (
        <p className="muted">
          {ticket.estado === "NO_RESUELTO"
            ? "Reportaste esta incidencia como no resuelta. El administrador coordinará la segunda intervención."
            : "No hay acciones pendientes para este servicio."}
        </p>
      )}

      {error && (
        <Alert tone="error" title="No se pudo completar la acción">
          {error}
        </Alert>
      )}
    </div>
  );
}

function Materials({ visitId }: { visitId: number }) {
  const items = useInventory();
  const usage = useVisitUsage(visitId);
  const register = useRegisterUsage();
  const [item, setItem] = useState("");
  const [qty, setQty] = useState("1");

  function submit(event: FormEvent) {
    event.preventDefault();
    register.mutate(
      { visit: visitId, item: Number(item), cantidad: Number(qty) },
      { onSuccess: () => { setItem(""); setQty("1"); void usage.refetch(); } },
    );
  }

  const nameOf = (id: number) => items.data?.find((i) => i.id === id)?.nombre ?? `Material #${id}`;

  return (
    <section className="panel" aria-labelledby="mat-title">
      <h3 id="mat-title">Materiales utilizados</h3>
      {usage.data && usage.data.length > 0 && (
        <ul className="plain-list">
          {usage.data.map((u) => (
            <li key={u.id}>
              <span>{nameOf(u.item)}</span>
              <strong>× {u.cantidad}</strong>
            </li>
          ))}
        </ul>
      )}
      <form className="form form-inline" onSubmit={submit}>
        <SelectField label="Material" value={item} onChange={(e) => setItem(e.target.value)} required>
          <option value="">Selecciona…</option>
          {items.data?.map((i) => (
            <option key={i.id} value={i.id}>
              {i.nombre} ({i.cantidad} {i.unidad})
            </option>
          ))}
        </SelectField>
        <TextField label="Cantidad" type="number" min={1} value={qty} onChange={(e) => setQty(e.target.value)} required />
        <Button type="submit" variant="secondary" loading={register.isPending} disabled={!item}>
          Registrar
        </Button>
      </form>
      {register.isError && (
        <Alert tone="error" title="No se pudo registrar el material">
          {getErrorMessage(register.error)}
        </Alert>
      )}
    </section>
  );
}

function ResultForm({ busy, onSubmit }: { busy: boolean; onSubmit: (resolved: boolean, text: string) => void }) {
  const [resolved, setResolved] = useState(true);
  const [text, setText] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    onSubmit(resolved, text.trim());
  }

  return (
    <section className="panel" aria-labelledby="res-title">
      <h3 id="res-title">Resultado de la atención</h3>
      <form className="form" onSubmit={submit}>
        <div className="segmented" role="radiogroup" aria-label="Resultado">
          <button type="button" role="radio" aria-checked={resolved} onClick={() => setResolved(true)}>
            <CheckCircle2 size={16} aria-hidden="true" /> Resuelto
          </button>
          <button type="button" role="radio" aria-checked={!resolved} onClick={() => setResolved(false)}>
            No resuelto
          </button>
        </div>
        <TextAreaField
          label={resolved ? "¿Qué se hizo para resolverlo?" : "¿Por qué no se pudo resolver?"}
          value={text}
          rows={4}
          maxLength={2000}
          onChange={(e) => setText(e.target.value)}
        />
        <Button type="submit" loading={busy} disabled={text.trim().length < 10} variant={resolved ? "primary" : "danger"}>
          {resolved ? "Cerrar servicio como resuelto" : "Reportar como no resuelto"}
        </Button>
      </form>
    </section>
  );
}
