export default function Skeleton({ lines = 1 }: { lines?: number }) {
  return (
    <div className="skeleton-group" role="status">
      <span className="visually-hidden">Cargando…</span>
      {Array.from({ length: lines }, (_, index) => (
        <span key={index} className="skeleton" />
      ))}
    </div>
  );
}