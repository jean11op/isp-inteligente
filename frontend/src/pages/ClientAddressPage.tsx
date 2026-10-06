import { useEffect, useState } from "react";
import { AlertCircle, LocateFixed, Loader2, Save } from "lucide-react";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import Button from "@/components/ui/Button";
import PageHeader from "@/components/ui/PageHeader";
import QueryBoundary from "@/components/ui/QueryBoundary";
import TextField from "@/components/ui/TextField";
import {
  useAddresses,
  useSaveAddress,
} from "@/features/clients/hooks/useAddresses";
import type { AddressInput } from "@/types/domain";
import "leaflet/dist/leaflet.css";

const DEFAULT_POSITION: [number, number] = [-8.1116, -79.0287];

const markerIcon = L.icon({
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface ReverseGeocodeResponse {
  display_name?: string;
}

async function reverseGeocode(
  latitude: number,
  longitude: number,
): Promise<string | null> {
  try {
    const url = new URL(
      "https://nominatim.openstreetmap.org/reverse",
    );

    url.searchParams.set("format", "jsonv2");
    url.searchParams.set("lat", latitude.toString());
    url.searchParams.set("lon", longitude.toString());
    url.searchParams.set("zoom", "18");
    url.searchParams.set("addressdetails", "1");

    const response = await fetch(url.toString(), {
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      return null;
    }

    const data = (await response.json()) as ReverseGeocodeResponse;

    return data.display_name ?? null;
  } catch {
    return null;
  }
}

export default function ClientAddressPage() {
  const query = useAddresses();
  const saveAddress = useSaveAddress();

  return (
    <QueryBoundary query={query} title="Domicilio">
      {(addresses) => (
        <AddressForm
          address={addresses?.[0]}
          saveAddress={saveAddress}
        />
      )}
    </QueryBoundary>
  );
}

function AddressForm({
  address,
  saveAddress,
}: {
  address?: {
    id: number;
    direccion: string;
    referencia: string;
    latitud: string;
    longitud: string;
    principal: boolean;
  };
  saveAddress: ReturnType<typeof useSaveAddress>;
}) {
  const [form, setForm] = useState<AddressInput>({
    direccion: "",
    referencia: "",
    latitud: "",
    longitud: "",
    principal: true,
  });

  const [isLocating, setIsLocating] = useState(false);
  const [isResolvingAddress, setIsResolvingAddress] = useState(false);

  useEffect(() => {
    if (!address) return;

    setForm({
      direccion: address.direccion,
      referencia: address.referencia,
      latitud: address.latitud,
      longitud: address.longitud,
      principal: address.principal,
    });
  }, [address]);

  const updateField = (
    field: keyof AddressInput,
    value: string | boolean,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const updatePosition = async (
    latitude: number,
    longitude: number,
    resolveAddress = true,
  ) => {
    setForm((current) => ({
      ...current,
      latitud: latitude.toFixed(6),
      longitud: longitude.toFixed(6),
    }));

    if (!resolveAddress) return;

    setIsResolvingAddress(true);

    const addressText = await reverseGeocode(latitude, longitude);

    if (addressText) {
      setForm((current) => ({
        ...current,
        direccion: addressText,
        latitud: latitude.toFixed(6),
        longitud: longitude.toFixed(6),
      }));
    }

    setIsResolvingAddress(false);
  };

  const useCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert("Tu navegador no permite obtener la ubicación.");
      return;
    }

    setIsLocating(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        await updatePosition(
          position.coords.latitude,
          position.coords.longitude,
          true,
        );

        setIsLocating(false);
      },
      () => {
        setIsLocating(false);

        alert(
          "No se pudo obtener tu ubicación. Verifica los permisos del navegador.",
        );
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
      },
    );
  };

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    const latitude = Number.parseFloat(form.latitud);
    const longitude = Number.parseFloat(form.longitud);

    if (!form.direccion.trim()) {
      alert("Ingresa una dirección.");
      return;
    }

    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      alert("Ingresa una latitud y longitud válidas.");
      return;
    }

    if (
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      alert("La latitud o longitud están fuera de rango.");
      return;
    }

    const payload = {
      id: address?.id,
      direccion: form.direccion.trim(),
      referencia: form.referencia.trim(),
      latitud: latitude.toFixed(6),
      longitud: longitude.toFixed(6),
      principal: form.principal,
    };

    console.log("DATOS DOMICILIO:", payload);

    try {
      await saveAddress.mutateAsync(payload);
    } catch (error) {
      console.error("ERROR AL GUARDAR DOMICILIO:", error);
    }
  };

  const latitude = Number.parseFloat(form.latitud);
  const longitude = Number.parseFloat(form.longitud);

  const position: [number, number] =
    Number.isFinite(latitude) && Number.isFinite(longitude)
      ? [latitude, longitude]
      : DEFAULT_POSITION;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mi domicilio"
        eyebrow="Datos de atención"
      />

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-start gap-3 rounded-lg bg-slate-50 p-4">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-slate-600" />

          <div>
            <p className="font-medium text-slate-900">
              Domicilio de atención
            </p>

            <p className="mt-1 text-sm text-slate-600">
              Indica dónde debe realizarse la visita técnica. Puedes
              usar tu ubicación actual o mover el marcador directamente
              en el mapa.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >
          <TextField
            label="Dirección"
            value={form.direccion}
            onChange={(event) =>
              updateField("direccion", event.target.value)
            }
            placeholder="Ej. Av. España 123, Trujillo"
            required
          />

          {isResolvingAddress && (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              Buscando la dirección de la ubicación seleccionada...
            </div>
          )}

          <TextField
            label="Referencia"
            value={form.referencia}
            onChange={(event) =>
              updateField("referencia", event.target.value)
            }
            placeholder="Ej. Frente al parque"
          />

          <div>
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm font-medium text-slate-700">
                Ubicación en el mapa
              </p>

              <span className="text-xs text-slate-500">
                Arrastra el marcador para ajustarlo
              </span>
            </div>

            <div className="overflow-hidden rounded-xl border border-slate-200">
              <MapContainer
                center={position}
                zoom={15}
                scrollWheelZoom
                style={{
                  height: "380px",
                  width: "100%",
                }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapCenter position={position} />

                <LocationMarker
                  position={position}
                  onPositionChange={updatePosition}
                />
              </MapContainer>
            </div>

            <p className="mt-2 text-xs text-slate-500">
              También puedes hacer clic directamente sobre el mapa
              para cambiar la ubicación.
            </p>
          </div>

          <button
            type="button"
            onClick={useCurrentLocation}
            disabled={isLocating}
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
          >
            {isLocating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <LocateFixed className="h-4 w-4" />
            )}

            {isLocating
              ? "Obteniendo ubicación..."
              : "Usar mi ubicación actual"}
          </button>

          <div className="grid gap-5 md:grid-cols-2">
            <TextField
              label="Latitud"
              value={form.latitud}
              onChange={(event) =>
                updateField("latitud", event.target.value)
              }
              placeholder="-8.1116"
              required
            />

            <TextField
              label="Longitud"
              value={form.longitud}
              onChange={(event) =>
                updateField("longitud", event.target.value)
              }
              placeholder="-79.0287"
              required
            />
          </div>

          <div className="flex flex-col gap-4 border-t border-slate-200 pt-5 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-slate-500">
              {address
                ? "Puedes modificar tu domicilio cuando lo necesites."
                : "Aún no tienes un domicilio registrado."}
            </p>

            <Button
              type="submit"
              disabled={saveAddress.isPending}
            >
              <Save className="mr-2 h-4 w-4" />

              {saveAddress.isPending
                ? "Guardando..."
                : address
                  ? "Actualizar domicilio"
                  : "Guardar domicilio"}
            </Button>
          </div>

          {saveAddress.isError && (
            <p className="text-sm text-red-600">
              No se pudo guardar el domicilio. Verifica los datos e
              inténtalo nuevamente.
            </p>
          )}

          {saveAddress.isSuccess && (
            <p className="text-sm text-green-600">
              Domicilio guardado correctamente.
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

function LocationMarker({
  position,
  onPositionChange,
}: {
  position: [number, number];
  onPositionChange: (
    latitude: number,
    longitude: number,
  ) => void;
}) {
  useMapEvents({
    click(event) {
      void onPositionChange(
        event.latlng.lat,
        event.latlng.lng,
      );
    },
  });

  return (
    <Marker
      position={position}
      icon={markerIcon}
      draggable
      eventHandlers={{
        dragend(event) {
          const marker = event.target as L.Marker;
          const { lat, lng } = marker.getLatLng();

          void onPositionChange(lat, lng);
        },
      }}
    >
      <Popup>
        <strong>Ubicación del domicilio</strong>
        <br />
        Arrastra este marcador para ajustar la ubicación.
      </Popup>
    </Marker>
  );
}

function MapCenter({
  position,
}: {
  position: [number, number];
}) {
  const map = useMap();

  useEffect(() => {
    map.setView(position, map.getZoom());
  }, [map, position]);

  return null;
}