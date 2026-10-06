import type { ReactNode } from "react";
import type { UseQueryResult } from "@tanstack/react-query";
import { getErrorMessage } from "@/utils/getErrorMessage";
import Alert from "./Alert";
import Button from "./Button";
import Skeleton from "./Skeleton";

/** Estados de carga y error uniformes para cualquier consulta. */
export default function QueryBoundary<T>({
  query,
  title,
  children,
  lines = 4,
}: {
  query: UseQueryResult<T>;
  title: string;
  children: (data: T) => ReactNode;
  lines?: number;
}) {
  if (query.isPending) return <Skeleton lines={lines} />;
  if (query.isError) {
    return (
      <Alert
        tone="error"
        title={title}
        action={
          <Button variant="secondary" onClick={() => void query.refetch()}>
            Reintentar
          </Button>
        }
      >
        {getErrorMessage(query.error, "Inténtalo de nuevo en unos segundos.")}
      </Alert>
    );
  }
  return <>{children(query.data)}</>;
}
