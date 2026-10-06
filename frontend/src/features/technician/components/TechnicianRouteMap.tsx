import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, Polyline, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import Alert from "@/components/ui/Alert";
import type { Ticket } from "@/types/ticket";
import { useAuth } from "@/features/auth/useAuth";
import { useTechnicians } from "@/features/admin/hooks/usePeople";
import "leaflet/dist/leaflet.css";

interface RouteData {
  coordinates: [number, number][];
  distance: number;
  duration: number;
}

interface TechnicianRouteMapProps {
  ticket: Ticket;
}

function FitRoute({ coordinates }: { coordinates: [number, number][] }) {
  const map = useMap();

  useEffect(() => {
    if (coordinates.length < 2) return;

    const bounds = L.latLngBounds(coordinates);
    map.fitBounds(bounds, { padding: [40, 40] });
  }, [coordinates, map]);

  return null;
}

export default function TechnicianRouteMap({
  ticket,
}: TechnicianRouteMapProps) {
  const { user } = useAuth();
  const technicians = useTechnicians();
  const [route, setRoute] = useState<RouteData | null>(null);
  const [loadingRoute, setLoadingRoute] = useState(false);
  const [routeError, setRouteError] = useState<string | null>(null);

  const technician = useMemo(
    () => technicians.data?.find((item) => item.user === user?.id),
    [technicians.data, user?.id],
  );

  const address = useMemo(
    () =>
      ticket.client_info.addresses.find((item) => item.principal) ??
      ticket.client_info.addresses[0],
    [ticket.client_info.addresses],
  );

  const technicianPosition = useMemo(() => {
    if (!technician?.latitud || !technician?.longitud) return null;

    const lat = Number(technician.latitud);
    const lng = Number(technician.longitud);

    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;

    return [lat, lng] as [number, number];
  }, [technician]);

  const clientPosition = useMemo(() => {
    if (!address) return null;

    const lat = Number(address.latitud);
    const lng = Number(address.longitud);

    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;

    return [lat, lng] as [number, number];
  }, [address]);

  useEffect(() => {
    if (!technicianPosition || !clientPosition) return;

    const [originLat, originLng] = technicianPosition;
    const [destinationLat, destinationLng] = clientPosition;

    let cancelled = false;

    async function loadRoute() {
      setLoadingRoute(true);
      setRouteError(null);

      try {
        const url =
          `https://router.project-osrm.org/route/v1/driving/` +
          `${originLng},${originLat};${destinationLng},${destinationLat}` +
          `?overview=full&geometries=geojson`;

        const response = await fetch(url);

        if (!response.ok) {
          throw new Error("No se pudo calcular la ruta.");
        }

        const data = await response.json();

        const firstRoute = data.routes?.[0];

        if (!firstRoute) {
          throw new Error("No se encontró una ruta disponible.");
        }

        const coordinates = firstRoute.geometry.coordinates.map(
          ([lng, lat]: [number, number]) => [lat, lng] as [number, number],
        );

        if (!cancelled) {
          setRoute({
            coordinates,
            distance: firstRoute.distance,
            duration: firstRoute.duration,
          });
        }
      } catch (error) {
        if (!cancelled) {
          setRouteError(
            error instanceof Error
              ? error.message
              : "No se pudo calcular la ruta.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingRoute(false);
        }
      }
    }

    void loadRoute();

    return () => {
      cancelled = true;
    };
  }, [technicianPosition, clientPosition]);

  if (technicians.isPending) {
    return (
      <section className="panel">
        <h3>Ruta al domicilio</h3>
        <p className="muted">Cargando ubicación del técnico…</p>
      </section>
    );
  }

  if (!technician) {
    return (
      <Alert tone="warning" title="No se encontró tu ubicación">
        No existe un perfil de técnico asociado al usuario actual.
      </Alert>
    );
  }

  if (!technicianPosition) {
    return (
      <Alert tone="warning" title="Ubicación del técnico no disponible">
        El técnico todavía no tiene coordenadas registradas.
      </Alert>
    );
  }

  if (!address || !clientPosition) {
    return (
      <Alert tone="warning" title="Ubicación del cliente no disponible">
        El cliente no tiene un domicilio con coordenadas registradas.
      </Alert>
    );
  }

  const center = technicianPosition;

  const distanceKm = route ? route.distance / 1000 : null;
  const durationMinutes = route ? Math.round(route.duration / 60) : null;

  return (
    <section className="panel" aria-labelledby="route-title">
      <div className="stack">
        <div>
          <h3 id="route-title">Ruta al domicilio del cliente</h3>
          <p className="muted">{address.direccion}</p>
        </div>

        {loadingRoute && (
          <p className="muted">Calculando ruta de desplazamiento…</p>
        )}

        {routeError && (
          <Alert tone="error" title="No se pudo calcular la ruta">
            {routeError}
          </Alert>
        )}

        {route && (
          <div className="panel">
            <strong>
              {distanceKm?.toFixed(1)} km
            </strong>
            {" · "}
            <span>
              aproximadamente {durationMinutes} min
            </span>
          </div>
        )}

        <div style={{ height: 420, width: "100%", borderRadius: 12, overflow: "hidden" }}>
          <MapContainer
            center={center}
            zoom={14}
            scrollWheelZoom
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <Marker position={technicianPosition}>
              <Popup>
                <strong>Sede / punto de partida</strong>
                <br />
                Punto de salida del técnico
              </Popup>
            </Marker>

            <Marker position={clientPosition}>
              <Popup>
                <strong>Cliente</strong>
                <br />
                {address.direccion}
              </Popup>
            </Marker>

            {route && (
              <>
                <Polyline positions={route.coordinates} />
                <FitRoute coordinates={route.coordinates} />
              </>
            )}
          </MapContainer>
        </div>
      </div>
    </section>
  );
}