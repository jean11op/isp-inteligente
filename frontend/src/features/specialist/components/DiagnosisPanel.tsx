import { useState } from "react";
import { ClipboardCheck, Truck, Wrench } from "lucide-react";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import { TextAreaField } from "@/components/ui/FormFields";
import { useUpdateTicket } from "@/features/tickets/hooks/useTickets";
import type { Ticket } from "@/types/ticket";
import { getErrorMessage } from "@/utils/getErrorMessage";

/** CU-15 diagnóstico · CU-16 resolución remota · CU-17 solicitar visita · CU-18 información para el técnico. */
export default function DiagnosisPanel({ ticket }: { ticket: Ticket }) {
  const update = useUpdateTicket(ticket.id);
  const [diagnostico, setDiagnostico] = useState(ticket.diagnostico);
  const { estado } = ticket;
  const canDiagnose = estado === "EN_REVISION" || estado === "ESPERANDO_ESPECIALISTA";
  const hasText = diagnostico.trim().length >= 10;

  return (
    <section className="panel" aria-labelledby="dx-title">
      <h3 id="dx-title">Atención del especialista</h3>

      {estado === "NUEVO" && (
        <>
          <p className="muted">El ticket aún no fue tomado. Inicia la revisión para poder diagnosticarlo.</p>
          <Button loading={update.isPending} onClick={() => update.mutate({ estado: "EN_REVISION" })}>
            <ClipboardCheck size={18} aria-hidden="true" /> Iniciar revisión
          </Button>
        </>
      )}

      {estado === "EN_REVISION" && (
        <Button variant="secondary" loading={update.isPending} onClick={() => update.mutate({ estado: "ESPERANDO_ESPECIALISTA" })}>
          Pausar: esperar datos del cliente
        </Button>
      )}

      {(canDiagnose || estado === "DIAGNOSTICADO") && (
        <TextAreaField
          label="Diagnóstico y notas para el técnico"
          hint="Mínimo 10 caracteres. El técnico verá este texto antes de la visita."
          value={diagnostico}
          rows={5}
          maxLength={2000}
          onChange={(e) => setDiagnostico(e.target.value)}
        />
      )}

      {canDiagnose && (
        <Button
          loading={update.isPending}
          disabled={!hasText}
          onClick={() => update.mutate({ estado: "DIAGNOSTICADO", diagnostico: diagnostico.trim() })}
        >
          Guardar diagnóstico
        </Button>
      )}

      {estado === "DIAGNOSTICADO" && (
        <div className="action-row">
          <Button
            loading={update.isPending}
            disabled={!hasText}
            onClick={() => update.mutate({ estado: "REQUIERE_VISITA", diagnostico: diagnostico.trim() })}
          >
            <Truck size={18} aria-hidden="true" /> Solicitar visita técnica
          </Button>
          <Button
            variant="secondary"
            loading={update.isPending}
            disabled={!hasText}
            onClick={() => update.mutate({ estado: "RESUELTO", diagnostico: diagnostico.trim() })}
          >
            <Wrench size={18} aria-hidden="true" /> Resolver de forma remota
          </Button>
        </div>
      )}

      {!["NUEVO", "EN_REVISION", "ESPERANDO_ESPECIALISTA", "DIAGNOSTICADO"].includes(estado) && (
        <p className="muted">Este ticket ya salió de la etapa de diagnóstico. No necesita acciones tuyas.</p>
      )}

      {update.isError && (
        <Alert tone="error" title="No se pudo actualizar el ticket">
          {getErrorMessage(update.error)}
        </Alert>
      )}
    </section>
  );
}
