import { useState, type FormEvent } from "react";
import Alert from "@/components/ui/Alert";
import Button from "@/components/ui/Button";
import DataTable from "@/components/ui/DataTable";
import EmptyState from "@/components/ui/EmptyState";
import PageHeader from "@/components/ui/PageHeader";
import QueryBoundary from "@/components/ui/QueryBoundary";
import TextField from "@/components/ui/TextField";
import { useCreateInventoryItem, useInventory } from "@/features/inventory/hooks/useInventory";
import { getErrorMessage } from "@/utils/getErrorMessage";

export default function AdminInventoryPage() {
  const query = useInventory();
  const create = useCreateInventoryItem();
  const [nombre, setNombre] = useState("");
  const [cantidad, setCantidad] = useState("1");
  const [unidad, setUnidad] = useState("unidad");

  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate(
      { nombre: nombre.trim(), descripcion: "", cantidad: Number(cantidad), unidad: unidad.trim() },
      { onSuccess: () => { setNombre(""); setCantidad("1"); } },
    );
  }

  return (
    <>
      <PageHeader eyebrow="Administrador" title="Inventario" />
      <div className="stack">
        <section className="panel">
          <h3>Agregar material</h3>
          <form className="form form-inline" onSubmit={submit}>
            <TextField label="Nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
            <TextField label="Cantidad" type="number" min={0} value={cantidad} onChange={(e) => setCantidad(e.target.value)} required />
            <TextField label="Unidad" value={unidad} onChange={(e) => setUnidad(e.target.value)} required />
            <Button type="submit" loading={create.isPending} disabled={!nombre.trim()}>
              Agregar
            </Button>
          </form>
          {create.isError && (
            <Alert tone="error" title="No se pudo agregar el material">
              {getErrorMessage(create.error)}
            </Alert>
          )}
        </section>
        <QueryBoundary query={query} title="No pudimos cargar el inventario">
          {(items) =>
            items.length === 0 ? (
              <EmptyState title="Inventario vacío" description="Agrega el primer material con el formulario." />
            ) : (
              <DataTable
                caption="Inventario"
                rows={items}
                rowKey={(i) => i.id}
                columns={[
                  { header: "Material", cell: (i) => i.nombre },
                  { header: "Stock", cell: (i) => `${i.cantidad} ${i.unidad}`, align: "end" },
                  {
                    header: "Estado",
                    cell: (i) => (
                      <span className="badge badge-flat" data-tone={i.cantidad === 0 ? "danger" : i.cantidad < 5 ? "warn" : "done"}>
                        {i.cantidad === 0 ? "Agotado" : i.cantidad < 5 ? "Stock bajo" : "Disponible"}
                      </span>
                    ),
                  },
                ]}
              />
            )
          }
        </QueryBoundary>
      </div>
    </>
  );
}
