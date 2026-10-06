import { useState } from "react";
import DataTable, { type Column } from "@/components/ui/DataTable";
import EmptyState from "@/components/ui/EmptyState";
import PageHeader from "@/components/ui/PageHeader";
import QueryBoundary from "@/components/ui/QueryBoundary";
import { useClients, useSpecialists, useTechnicians, useUsers } from "@/features/admin/hooks/usePeople";
import type { AppUser, ClientProfile, StaffProfile } from "@/types/domain";
import { ROLE_LABEL } from "@/types/roles";

type Tab = "clients" | "technicians" | "specialists" | "users";
const TABS: { id: Tab; label: string }[] = [
  { id: "clients", label: "Clientes" },
  { id: "technicians", label: "Técnicos" },
  { id: "specialists", label: "Especialistas" },
  { id: "users", label: "Usuarios" },
];

const yesNo = (v: boolean) => (
  <span className="badge badge-flat" data-tone={v ? "done" : "closed"}>
    {v ? "Sí" : "No"}
  </span>
);

const clientCols: Column<ClientProfile>[] = [
  { header: "Cliente", cell: (c) => `${c.nombres} ${c.apellidos}` },
  { header: "Documento", cell: (c) => c.documento },
  { header: "Teléfono", cell: (c) => c.telefono },
  { header: "Servicio activo", cell: (c) => yesNo(c.servicio_activo) },
];

const staffCols: Column<StaffProfile>[] = [
  { header: "ID", cell: (s) => `#${s.id}` },
  { header: "Especialidad", cell: (s) => s.especialidad || "—" },
  { header: "Disponible", cell: (s) => yesNo(s.disponible) },
  { header: "Activo", cell: (s) => yesNo(s.activo) },
  { header: "Carga", cell: (s) => s.carga_trabajo ?? "—", align: "end" },
];

const userCols: Column<AppUser>[] = [
  { header: "Usuario", cell: (u) => u.username },
  { header: "Correo", cell: (u) => u.email || "—" },
  { header: "Rol", cell: (u) => ROLE_LABEL[u.role] },
];

function Table<T extends { id: number }>({ rows, columns, caption }: { rows: T[]; columns: Column<T>[]; caption: string }) {
  if (rows.length === 0) return <EmptyState title="Sin registros" description="Todavía no hay datos en esta sección." />;
  return <DataTable rows={rows} columns={columns} rowKey={(r) => r.id} caption={caption} />;
}

export default function AdminPeoplePage() {
  const [tab, setTab] = useState<Tab>("clients");
  const clients = useClients();
  const technicians = useTechnicians();
  const specialists = useSpecialists();
  const users = useUsers();

  return (
    <>
      <PageHeader eyebrow="Administrador" title="Personas y accesos" />
      <div className="stack">
        <div className="segmented" role="tablist" aria-label="Sección">
          {TABS.map((t) => (
            <button key={t.id} type="button" role="tab" aria-selected={tab === t.id} onClick={() => setTab(t.id)}>
              {t.label}
            </button>
          ))}
        </div>
        {tab === "clients" && (
          <QueryBoundary query={clients} title="No pudimos cargar los clientes">
            {(rows) => <Table rows={rows} columns={clientCols} caption="Clientes" />}
          </QueryBoundary>
        )}
        {tab === "technicians" && (
          <QueryBoundary query={technicians} title="No pudimos cargar los técnicos">
            {(rows) => <Table rows={rows} columns={staffCols} caption="Técnicos" />}
          </QueryBoundary>
        )}
        {tab === "specialists" && (
          <QueryBoundary query={specialists} title="No pudimos cargar los especialistas">
            {(rows) => <Table rows={rows} columns={staffCols} caption="Especialistas" />}
          </QueryBoundary>
        )}
        {tab === "users" && (
          <QueryBoundary query={users} title="No pudimos cargar los usuarios">
            {(rows) => <Table rows={rows} columns={userCols} caption="Usuarios" />}
          </QueryBoundary>
        )}
      </div>
    </>
  );
}
