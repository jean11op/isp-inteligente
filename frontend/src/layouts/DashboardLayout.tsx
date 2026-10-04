import { LogOut } from "lucide-react";
import { Link, Outlet, useNavigate } from "react-router";
import LogoMark from "@/components/ui/LogoMark";
import { useAuth } from "@/features/auth/useAuth";
import { ROLE_HOME } from "@/routes/paths";
import { ROLE_LABEL, type Role } from "@/types/roles";
import Nav from "./Nav";
import { NAV_BY_ROLE } from "./navigation";

const FIELD_ROLES: Role[] = ["CLIENTE", "TECNICO"];

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const shell = FIELD_ROLES.includes(user.role) ? "field" : "console";

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="shell" data-shell={shell}>
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>

      <header className="shell-header">
        <Link className="shell-brand" to={ROLE_HOME[user.role]} aria-label="ISP Inteligente, ir al inicio">
          <LogoMark />
          <span>ISP Inteligente</span>
        </Link>
        <div className="shell-user">
          <div className="shell-user-info">
            <span className="shell-user-name">{user.username}</span>
            <span className="shell-user-role">{ROLE_LABEL[user.role]}</span>
          </div>
          <button className="icon-btn" type="button" onClick={handleLogout} aria-label="Cerrar sesión">
            <LogOut size={20} aria-hidden="true" />
          </button>
        </div>
      </header>

      <Nav items={NAV_BY_ROLE[user.role]} />

      <main id="contenido" className="shell-main" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
}