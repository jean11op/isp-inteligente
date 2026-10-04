import { Outlet } from "react-router";
import LogoMark from "@/components/ui/LogoMark";

const STEPS = [
  "Reportas el problema en minutos",
  "Un especialista lo diagnostica",
  "Si hace falta, un técnico te visita",
  "Sigues cada paso hasta que se resuelve",
];

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
          <ol className="auth-aside-steps">
            {STEPS.map((step, index) => (
              <li key={step}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                {step}
              </li>
            ))}
          </ol>
        </div>
        <span />
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