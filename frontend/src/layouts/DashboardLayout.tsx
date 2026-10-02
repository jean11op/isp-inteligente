import { Outlet, useNavigate } from "react-router";
import { useAuth } from "../features/auth/useAuth";
import { PATHS } from "../routes/paths";

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate(PATHS.login, { replace: true });
  }

  return (
    <div>
      <header className="dashboard-header">
        <strong>ISP Inteligente</strong>
        <div className="dashboard-user">
          <span>
            {user?.username} · {user?.role}
          </span>
          <button className="btn" type="button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </header>
      <main className="dashboard-content">
        <Outlet />
      </main>
    </div>
  );
}