import { Link, matchPath, useLocation } from "react-router";
import type { NavItem } from "./navigation";

export default function Nav({ items }: { items: NavItem[] }) {
  const { pathname } = useLocation();

  return (
    <nav className="shell-nav" aria-label="Principal">
      <ul>
        {items.map(({ to, label, icon: Icon, end, primary, isActive }) => {
          const active = isActive
            ? isActive(pathname)
            : matchPath({ path: to, end: end ?? false }, pathname) !== null;

          return (
            <li key={to}>
              <Link
                className="nav-link"
                to={to}
                aria-current={active ? "page" : undefined}
                data-primary={primary || undefined}
              >
                <Icon size={20} aria-hidden="true" />
                <span>{label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}