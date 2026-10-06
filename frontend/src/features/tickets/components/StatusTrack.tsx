import type { TicketStatus } from "@/types/ticket";
import { OFF_FLOW_STATUSES, STATUS_LABEL, TICKET_FLOW } from "../labels";

type StepState = "done" | "current" | "todo";

const STEP_STATE_TEXT: Record<StepState, string> = {
  done: "completado",
  current: "paso actual",
  todo: "pendiente",
};

const LAST_REGULAR_STEP: TicketStatus = "EN_ATENCION";

export default function StatusTrack({ status }: { status: TicketStatus }) {
  const offFlow = OFF_FLOW_STATUSES.includes(status);
  const currentIndex = TICKET_FLOW.indexOf(offFlow ? LAST_REGULAR_STEP : status);
  const nextStep = offFlow ? undefined : TICKET_FLOW[currentIndex + 1];

  function stateOf(index: number): StepState {
    if (index < currentIndex) return "done";
    if (index === currentIndex) return offFlow ? "done" : "current";
    return "todo";
  }

  let nextText = "Proceso completado.";
  if (offFlow) nextText = "Este caso salió del flujo habitual y requiere atención adicional del equipo.";
  else if (nextStep) nextText = `Siguiente: ${STATUS_LABEL[nextStep]}`;

  return (
    <div className="track">
      <div className="track-head">
        <p className="track-current">{STATUS_LABEL[status]}</p>
        {!offFlow && (
          <p className="track-count">
            Paso {currentIndex + 1} de {TICKET_FLOW.length}
          </p>
        )}
      </div>

      <div className="track-bar" aria-hidden="true">
        {TICKET_FLOW.map((step, index) => (
          <span key={step} data-state={stateOf(index)} />
        ))}
      </div>

      <p className="track-next">{nextText}</p>

      <details className="track-steps">
        <summary>Ver todos los pasos</summary>
        <ol className="track-list">
          {TICKET_FLOW.map((step, index) => {
            const state = stateOf(index);
            return (
              <li key={step} data-state={state} aria-current={state === "current" ? "step" : undefined}>
                {STATUS_LABEL[step]}
                <span className="visually-hidden"> ({STEP_STATE_TEXT[state]})</span>
              </li>
            );
          })}
        </ol>
      </details>
    </div>
  );
}