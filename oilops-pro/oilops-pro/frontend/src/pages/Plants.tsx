import { useQuery } from "@tanstack/react-query";
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer } from "react-leaflet";
import { useState } from "react";

import ResourcePage from "../components/ResourcePage";
import { Badge, Card, PageHeader, Spinner, Tabs } from "../components/ui";
import { getList, Row } from "../lib/api";
import { useAuth } from "../lib/auth";
import { num } from "../lib/format";
import { opts, PLANT_STATUS, PLANT_TYPES, plantOption, userOption } from "../lib/options";

const COLOR: Record<string, string> = { OPERATIONAL: "#2f855a", MAINTENANCE: "#c98a12", SHUTDOWN: "#c53030" };
type Tab = "map" | "plants" | "pipelines" | "tanks";

function MapView() {
  const plants = useQuery({ queryKey: ["map-plants"], queryFn: () => getList("/plants/") });
  const pipes = useQuery({ queryKey: ["map-pipes"], queryFn: () => getList("/plants/pipelines/") });
  if (plants.isLoading) return <Spinner />;
  const withGeo = (plants.data ?? []).filter((p) => p.latitude && p.longitude);
  const byId: Row = Object.fromEntries(withGeo.map((p) => [p.id, p]));
  return (
    <Card pad={false}>
      <MapContainer center={[29.5, 69.5]} zoom={5} style={{ height: 520 }} scrollWheelZoom>
        <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {pipes.data?.map((l) => byId[l.origin] && byId[l.destination] && (
          <Polyline key={l.id} positions={[[+byId[l.origin].latitude, +byId[l.origin].longitude], [+byId[l.destination].latitude, +byId[l.destination].longitude]]}
            pathOptions={{ color: "#1f7a8c", weight: 3, dashArray: l.status === "ACTIVE" ? undefined : "6 6" }}>
            <Popup><b>{l.name}</b><br />{num(l.length_km)} km · {l.product}</Popup>
          </Polyline>
        ))}
        {withGeo.map((p) => (
          <CircleMarker key={p.id} center={[+p.latitude, +p.longitude]} radius={p.plant_type === "GAS_STATION" ? 7 : 11}
            pathOptions={{ color: "#0f2a2e", weight: 2, fillColor: COLOR[p.status] ?? "#64748b", fillOpacity: 0.95 }}>
            <Popup>
              <b>{p.name}</b><br />{p.plant_type_display} · {p.city}<br />
              {p.equipment_count} equipment · {p.tank_count} tanks<br /><Badge value={p.status} />
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="flex flex-wrap gap-4 border-t border-line px-4 py-2.5 text-sm text-slate-600">
        {Object.entries(COLOR).map(([k, c]) => <span key={k} className="flex items-center gap-1.5"><span className="h-3 w-3 rounded-full" style={{ background: c }} />{k.charAt(0) + k.slice(1).toLowerCase()}</span>)}
        <span className="flex items-center gap-1.5"><span className="h-0.5 w-5 bg-gauge" />Pipeline</span>
      </div>
    </Card>
  );
}

export default function Plants() {
  const { can } = useAuth();
  const [tab, setTab] = useState<Tab>("map");
  const write = can("PLANT_MANAGER");
  const eng = can("PLANT_MANAGER", "ENGINEER");
  return (
    <div>
      <PageHeader title="Plants & assets" subtitle="Refineries, processing plants, terminals, fuel stations, pipelines and storage tanks." />
      <Tabs value={tab} onChange={setTab} tabs={[{ id: "map", label: "Map" }, { id: "plants", label: "Plants" }, { id: "pipelines", label: "Pipelines" }, { id: "tanks", label: "Storage tanks" }]} />
      {tab === "map" && <MapView />}
      {tab === "plants" && (
        <ResourcePage embedded noun="plant" endpoint="/plants/" canWrite={write} canDelete={write}
          filters={[{ name: "plant_type", label: "Type", options: opts(PLANT_TYPES) }, { name: "status", label: "Status", options: opts(PLANT_STATUS) }]}
          columns={[{ key: "code", label: "Code" }, { key: "name", label: "Name" }, { key: "plant_type_display", label: "Type" }, { key: "city", label: "City" },
            { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> }, { key: "equipment_count", label: "Equipment" }, { key: "capacity_bpd", label: "Capacity (bpd)", render: (r) => num(r.capacity_bpd) }]}
          fields={[{ name: "code", label: "Code", required: true }, { name: "name", label: "Name", required: true },
            { name: "plant_type", label: "Type", type: "select", options: opts(PLANT_TYPES), required: true }, { name: "status", label: "Status", type: "select", options: opts(PLANT_STATUS), required: true },
            { name: "city", label: "City" }, { name: "address", label: "Address" },
            { name: "latitude", label: "Latitude", type: "number", step: "0.000001" }, { name: "longitude", label: "Longitude", type: "number", step: "0.000001" },
            { name: "capacity_bpd", label: "Capacity (barrels/day)", type: "number" }, { name: "commissioned_on", label: "Commissioned on", type: "date" },
            { name: "manager", label: "Manager", type: "select", optionsFrom: userOption("PLANT_MANAGER,ENGINEER") }]}
          defaults={{ plant_type: "PLANT", status: "OPERATIONAL", capacity_bpd: 0 }} />
      )}
      {tab === "pipelines" && (
        <ResourcePage embedded noun="pipeline" endpoint="/plants/pipelines/" canWrite={eng} canDelete={eng}
          columns={[{ key: "code", label: "Code" }, { key: "name", label: "Name" }, { key: "origin_name", label: "From" }, { key: "destination_name", label: "To" },
            { key: "length_km", label: "Length (km)" }, { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> }]}
          fields={[{ name: "code", label: "Code", required: true }, { name: "name", label: "Name", required: true },
            { name: "origin", label: "Origin", type: "select", optionsFrom: plantOption, required: true }, { name: "destination", label: "Destination", type: "select", optionsFrom: plantOption, required: true },
            { name: "product", label: "Product" }, { name: "status", label: "Status", type: "select", options: opts(["ACTIVE", "IDLE", "MAINTENANCE", "DECOMMISSIONED"]), required: true },
            { name: "length_km", label: "Length (km)", type: "number", step: "0.01" }, { name: "diameter_inch", label: "Diameter (inch)", type: "number", step: "0.1" },
            { name: "max_pressure_bar", label: "Max pressure (bar)", type: "number", step: "0.01" }]}
          defaults={{ status: "ACTIVE", product: "Crude oil" }} />
      )}
      {tab === "tanks" && (
        <ResourcePage embedded noun="tank" endpoint="/plants/tanks/" canWrite={eng || can("TECHNICIAN")} canDelete={eng}
          columns={[{ key: "tag", label: "Tag" }, { key: "plant_name", label: "Plant" }, { key: "product", label: "Product" },
            { key: "fill_percent", label: "Fill level", render: (r) => <div className="flex items-center gap-2"><div className="h-2 w-24 overflow-hidden rounded bg-slate-200"><div className="h-full" style={{ width: `${r.fill_percent}%`, background: r.fill_percent > 90 || r.fill_percent < 15 ? "#c98a12" : "#1f7a8c" }} /></div>{r.fill_percent}%</div> },
            { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> }]}
          fields={[{ name: "plant", label: "Plant", type: "select", optionsFrom: plantOption, required: true }, { name: "tag", label: "Tag", required: true },
            { name: "product", label: "Product", type: "select", options: opts(["CRUDE", "DIESEL", "PETROL", "KEROSENE", "LPG", "NATURAL_GAS"]), required: true },
            { name: "status", label: "Status", type: "select", options: opts(["IN_SERVICE", "OUT_OF_SERVICE", "INSPECTION"]), required: true },
            { name: "capacity_litres", label: "Capacity (L)", type: "number", step: "0.01", required: true }, { name: "current_level_litres", label: "Current level (L)", type: "number", step: "0.01" },
            { name: "last_inspection", label: "Last inspection", type: "date" }]}
          defaults={{ product: "CRUDE", status: "IN_SERVICE", current_level_litres: 0 }} />
      )}
    </div>
  );
}
