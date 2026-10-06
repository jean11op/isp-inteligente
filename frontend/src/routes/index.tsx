import type { ReactElement } from "react";
import { Navigate, createBrowserRouter, type RouteObject } from "react-router";
import AuthLayout from "../layouts/AuthLayout";
import DashboardLayout from "../layouts/DashboardLayout";
import AdminDashboardPage from "../pages/AdminDashboardPage";
import AdminInventoryPage from "../pages/AdminInventoryPage";
import AdminPeoplePage from "../pages/AdminPeoplePage";
import AdminTicketPage from "../pages/AdminTicketPage";
import AdminTicketsPage from "../pages/AdminTicketsPage";
import ClientDashboardPage from "../pages/ClientDashboardPage";
import ClientAddressPage from "../pages/ClientAddressPage";
import ClientTicketsPage from "../pages/ClientTicketsPage";
import HomePage from "../pages/HomePage";
import LoginPage from "../pages/LoginPage";
import NewTicketPage from "../pages/NewTicketPage";
import RegisterPage from "../pages/RegisterPage";
import SpecialistDashboardPage from "../pages/SpecialistDashboardPage";
import SpecialistTicketPage from "../pages/SpecialistTicketPage";
import TechnicianDashboardPage from "../pages/TechnicianDashboardPage";
import TechnicianServicePage from "../pages/TechnicianServicePage";
import TicketDetailPage from "../pages/TicketDetailPage";
import type { Role } from "../types/roles";
import { PATHS } from "./paths";
import RoleRoute from "./RoleRoute";

// Cada rol tiene su prefijo (/cliente, /tecnico...) y solo ese rol puede entrar.
// "pages" son las rutas hijas de ese rol, relativas a su prefijo.
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
    { path: "domicilio", element: <ClientAddressPage /> },
  ]),
  dashboardRoute(PATHS.specialist, "ESPECIALISTA", <SpecialistDashboardPage />, [
    { path: "tickets/:ticketId", element: <SpecialistTicketPage /> },
  ]),
  dashboardRoute(PATHS.technician, "TECNICO", <TechnicianDashboardPage />, [
    { path: "servicios/:ticketId", element: <TechnicianServicePage /> },
  ]),
  dashboardRoute(PATHS.admin, "ADMINISTRADOR", <AdminDashboardPage />, [
    { path: "tickets", element: <AdminTicketsPage /> },
    { path: "tickets/:ticketId", element: <AdminTicketPage /> },
    { path: "personas", element: <AdminPeoplePage /> },
    { path: "inventario", element: <AdminInventoryPage /> },
  ]),
  { path: "*", element: <Navigate to={PATHS.home} replace /> },
]);