import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";
import { PATHS, clientTicketPath } from "../../../routes/paths";
import type { TicketPriority } from "../../../types/ticket";
import { getErrorMessage } from "../../../utils/getErrorMessage";
import { useCreateTicket } from "../hooks/useTickets";
import { PRIORITY_LABEL } from "../labels";

type Step = "titulo" | "descripcion" | "prioridad" | "confirmar";

interface Message {
  from: "bot" | "user";
  text: string;
}

const MIN_TITULO = 5;
const MIN_DESCRIPCION = 20;
const PRIORITIES: TicketPriority[] = ["BAJA", "MEDIA", "ALTA", "CRITICA"];

const INITIAL_MESSAGES: Message[] = [
  {
    from: "bot",
    text: "Hola, soy el asistente de soporte. Cuéntame en pocas palabras: ¿cuál es el problema con tu servicio de internet?",
  },
];

export default function ChatbotReport() {
  const navigate = useNavigate();
  const createTicket = useCreateTicket();
  const [step, setStep] = useState<Step>("titulo");
  const [input, setInput] = useState("");
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [prioridad, setPrioridad] = useState<TicketPriority>("MEDIA");
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);

  function addMessages(...newMessages: Message[]) {
    setMessages((previous) => [...previous, ...newMessages]);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text) return;
    setInput("");

    if (step === "titulo") {
      if (text.length < MIN_TITULO) {
        addMessages(
          { from: "user", text },
          { from: "bot", text: "Necesito un poco más de información. ¿Puedes explicarlo con otras palabras?" },
        );
        return;
      }
      setTitulo(text);
      addMessages(
        { from: "user", text },
        { from: "bot", text: "Gracias. Ahora cuéntame con más detalle: ¿desde cuándo ocurre, qué luces ves en el router y afecta a todos tus dispositivos?" },
      );
      setStep("descripcion");
      return;
    }

    if (step === "descripcion") {
      if (text.length < MIN_DESCRIPCION) {
        addMessages(
          { from: "user", text },
          { from: "bot", text: "Necesito más datos para ayudarte. ¿Puedes ampliar la descripción?" },
        );
        return;
      }
      setDescripcion(text);
      addMessages(
        { from: "user", text },
        { from: "bot", text: "Entendido. ¿Qué tan urgente es para ti?" },
      );
      setStep("prioridad");
    }
  }

  function choosePriority(value: TicketPriority) {
    setPrioridad(value);
    addMessages(
      { from: "user", text: PRIORITY_LABEL[value] },
      { from: "bot", text: "Listo. Revisa el resumen y confirma para registrar tu incidencia." },
    );
    setStep("confirmar");
  }

  function handleConfirm() {
    createTicket.mutate(
      { titulo, descripcion, prioridad },
      { onSuccess: (ticket) => navigate(clientTicketPath(ticket.id)) },
    );
  }

  function handleRestart() {
    createTicket.reset();
    setStep("titulo");
    setInput("");
    setTitulo("");
    setDescripcion("");
    setPrioridad("MEDIA");
    setMessages(INITIAL_MESSAGES);
  }

  return (
    <section className="chat">
      <div className="chat-messages" aria-live="polite">
        {messages.map((message, index) => (
          <p key={index} className={`chat-msg chat-msg-${message.from}`}>
            {message.text}
          </p>
        ))}
      </div>

      {(step === "titulo" || step === "descripcion") && (
        <form className="chat-form" onSubmit={handleSubmit}>
          <textarea
            aria-label="Tu mensaje"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            rows={2}
            maxLength={step === "titulo" ? 150 : 2000}
            placeholder={step === "titulo" ? "Ej: No tengo conexión a internet" : "Describe el problema con detalle"}
          />
          <button className="btn" type="submit">
            Enviar
          </button>
        </form>
      )}

      {step === "prioridad" && (
        <div className="chat-options">
          {PRIORITIES.map((value) => (
            <button key={value} className="btn" type="button" onClick={() => choosePriority(value)}>
              {PRIORITY_LABEL[value]}
            </button>
          ))}
        </div>
      )}

      {step === "confirmar" && (
        <div className="chat-summary">
          <h3>Resumen de tu reporte</h3>
          <dl className="detail-grid">
            <dt>Problema</dt>
            <dd>{titulo}</dd>
            <dt>Detalle</dt>
            <dd>{descripcion}</dd>
            <dt>Prioridad</dt>
            <dd>{PRIORITY_LABEL[prioridad]}</dd>
          </dl>
          {createTicket.isError && (
            <p className="form-error">
              {getErrorMessage(createTicket.error, "No se pudo registrar la incidencia")}
            </p>
          )}
          <div className="chat-options">
            <button className="btn" type="button" onClick={handleConfirm} disabled={createTicket.isPending}>
              {createTicket.isPending ? "Registrando..." : "Registrar incidencia"}
            </button>
            <button className="btn btn-secondary" type="button" onClick={handleRestart}>
              Empezar de nuevo
            </button>
          </div>
        </div>
      )}

      <p>
        <Link to={PATHS.client}>← Cancelar</Link>
      </p>
    </section>
  );
}