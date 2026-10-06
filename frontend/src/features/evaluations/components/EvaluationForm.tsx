import { useState, type FormEvent } from "react";
import { Star } from "lucide-react";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import { TextAreaField } from "@/components/ui/FormFields";
import { getErrorMessage } from "@/utils/getErrorMessage";
import { useCreateEvaluation, useTicketEvaluation } from "../hooks/useEvaluations";

export default function EvaluationForm({ ticketId }: { ticketId: number }) {
  const existing = useTicketEvaluation(ticketId);
  const create = useCreateEvaluation(ticketId);
  const [score, setScore] = useState(0);
  const [comment, setComment] = useState("");

  if (existing.isPending) return null;

  if (existing.data) {
    return (
      <section className="panel">
        <h3>Tu evaluación</h3>
        <Stars value={existing.data.puntuacion} />
        {existing.data.comentario && <p className="muted">{existing.data.comentario}</p>}
      </section>
    );
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (score === 0) return;
    create.mutate({ puntuacion: score, comentario: comment.trim() });
  }

  return (
    <section className="panel" aria-labelledby="eval-title">
      <h3 id="eval-title">¿Cómo fue tu atención?</h3>
      <form className="form" onSubmit={handleSubmit}>
        <div className="rating" role="radiogroup" aria-label="Puntuación">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              role="radio"
              aria-checked={score === n}
              aria-label={`${n} de 5`}
              data-on={n <= score || undefined}
              onClick={() => setScore(n)}
            >
              <Star size={26} aria-hidden="true" />
            </button>
          ))}
        </div>
        <TextAreaField
          label="Comentario (opcional)"
          value={comment}
          maxLength={500}
          rows={3}
          onChange={(e) => setComment(e.target.value)}
        />
        {create.isError && (
          <Alert tone="error" title="No se pudo enviar tu evaluación">
            {getErrorMessage(create.error)}
          </Alert>
        )}
        <Button type="submit" loading={create.isPending} disabled={score === 0}>
          Enviar evaluación
        </Button>
      </form>
    </section>
  );
}

function Stars({ value }: { value: number }) {
  return (
    <div className="rating" role="img" aria-label={`${value} de 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} data-on={n <= value || undefined}>
          <Star size={22} aria-hidden="true" />
        </span>
      ))}
    </div>
  );
}
