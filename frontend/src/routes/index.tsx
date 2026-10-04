import type { ReactElement } from "react";
import { Navigate, createBrowserRouter, type RouteObject } from "react-router";
import AuthLayout from "../layouts/AuthLayout";
import DashboardLayout from "../layouts/DashboardLayout";
import AdminDashboardPage from "../pages/AdminDashboardPage";
import ClientDashboardPage from "../pages/ClientDashboardPage";
import ClientTicketsPage from "../pages/ClientTicketsPage";
import HomePage from "../pages/HomePage";
import LoginPage from "../pages/LoginPage";
import NewTicketPage from "../pages/NewTicketPage";
import RegisterPage from "../pages/RegisterPage";
import SpecialistDashboardPage from "../pages/SpecialistDashboardPage";
import TechnicianDashboardPage from "../pages/TechnicianDashboardPage";
import TicketDetailPage from "../pages/TicketDetailPage";
import type { Role } from "../types/roles";
import { PATHS } from "./paths";
import RoleRoute from "./RoleRoute";

function dashboardRoute(
  path: string,
  role: Role,
  home: ReactElement,
  pages: RouteObject[] = [],
): RouteObject {
  return {
    path,
    element: <RoleRoute role={role} />,
    children: [
      {
        element: <DashboardLayout />,
        children: [{ index: true, element: home }, ...pages],
      },
    ],
  };
}

export const router = createBrowserRouter([
  { path: PATHS.home, element: <HomePage /> },
  {
    element: <AuthLayout />,
    children: [
      { path: PATHS.login, element: <LoginPage /> },
      { path: PATHS.register, element: <RegisterPage /> },
    ],
  },
  dashboardRoute(PATHS.client, "CLIENTE", <ClientDashboardPage />, [
    { path: "tickets", element: <ClientTicketsPage /> },
    { path: "tickets/nuevo", element: <NewTicketPage /> },
    { path: "tickets/:ticketId", element: <TicketDetailPage /> },
  ]),
  dashboardRoute(PATHS.specialist, "ESPECIALISTA", <SpecialistDashboardPage />),
  dashboardRoute(PATHS.technician, "TECNICO", <TechnicianDashboardPage />),
  dashboardRoute(PATHS.admin, "ADMINISTRADOR", <AdminDashboardPage />),
  { path: "*", element: <Navigate to={PATHS.home} replace /> },
]);