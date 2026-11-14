
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";

export interface MapStation {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  distance_km?: number | null;
  source: string;
  last_updated?: string | null;
  measurements: {
    parameter: string;
    value: number;
    unit?: string | null;
    timestamp: string;
    source: string;
  }[];
}

interface PollutionMapProps {
  latitude: number;
  longitude: number;
  stations: MapStation[];
}

export default function PollutionMap({
  latitude,
  longitude,
  stations,
}: PollutionMapProps) {
  return (
    <div>
      <div
        style={{
          height: 360,
          width: "100%",
          borderRadius: 12,
          overflow: "hidden",
        }}
      >
        <MapContainer
          center={[latitude, longitude]}
          zoom={11}
          scrollWheelZoom={false}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <CircleMarker
            center={[latitude, longitude]}
            radius={9}
            pathOptions={{
              color: "#2563eb",
              fillColor: "#3b82f6",
              fillOpacity: 0.9,
            }}
          >
            <Popup>
              <strong>Your selected location</strong>
              <p>
                {latitude.toFixed(5)}, {longitude.toFixed(5)}
              </p>
            </Popup>
          </CircleMarker>

          {stations
            .filter(
              (station) =>
                Number.isFinite(station.latitude) &&
                Number.isFinite(station.longitude)
            )
            .map((station) => (
              <CircleMarker
                key={station.id}
                center={[station.latitude, station.longitude]}
                radius={7}
                pathOptions={{
                  color: "#dc2626",
                  fillColor: "#ef4444",
                  fillOpacity: 0.85,
                }}
              >
                <Popup>
                  <strong>{station.name}</strong>

                  <p>Source: {station.source}</p>

                  {station.distance_km != null && (
                    <p>
                      Distance: {station.distance_km.toFixed(2)} km
                    </p>
                  )}

                  {station.last_updated && (
                    <p>
                      Updated:{" "}
                      {new Date(station.last_updated).toLocaleString()}
                    </p>
                  )}

                  {station.measurements.length > 0 ? (
                    <ul>
                      {station.measurements.map((measurement, index) => (
                        <li key={`${measurement.parameter}-${index}`}>
                          {measurement.parameter.toUpperCase()}:{" "}
                          {measurement.value} {measurement.unit ?? ""}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>No pollutant measurements available.</p>
                  )}
                </Popup>
              </CircleMarker>
            ))}
        </MapContainer>
      </div>

      <p className="placeholder">
        Blue marker: your location. Red markers: nearby air-quality
        monitoring stations.
      </p>
    </div>
  );
}
