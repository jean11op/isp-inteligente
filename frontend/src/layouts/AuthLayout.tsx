import { Outlet } from "react-router";
import LogoMark from "@/components/ui/LogoMark";

const STEPS = [
  "Reportas el problema en minutos",
  "Un especialista lo diagnostica",
  "Si hace falta, un técnico te visita",
  "Sigues cada paso hasta que se resuelve",
];

const PREVIEW_BAR = ["done", "done", "done", "done", "done", "done", "current", "todo", "todo", "todo", "todo"];

export default function AuthLayout() {
  return (
    <div className="auth-layout">
      <aside className="auth-aside">
        <div className="auth-brand">
          <LogoMark />
          <span>ISP Inteligente</span>
        </div>

        <div>
          <p className="auth-aside-title">Cada incidencia, de principio a fin.</p>
          <p className="auth-aside-sub">Reporta una falla de tu conexión y mira en tiempo real quién la atiende.</p>
          <ol className="auth-aside-steps">
            {STEPS.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>

        {/* Ejemplo ilustrativo de cómo se ve el seguimiento */}
        <div className="auth-preview" aria-hidden="true">
          <div className="auth-preview-head">
            <span>Ejemplo · #128</span>
            <span className="badge" data-tone="field">En camino</span>
          </div>
          <p className="auth-preview-title">Sin internet desde la mañana</p>
          <div className="track-bar">
            {PREVIEW_BAR.map((state, index) => (
              <span key={index} data-state={state} />
            ))}
          </div>
          <p className="auth-preview-foot">Siguiente: el técnico llega a tu domicilio</p>
        </div>
      </aside>

      <main className="auth-main">
        <div className="auth-panel">
          <div className="auth-brand auth-brand-mobile">
            <LogoMark />
            <span>ISP Inteligente</span>
          </div>
          <div className="form">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
