import ResourcePage from "../components/ResourcePage";
import { Badge } from "../components/ui";
import { useAuth } from "../lib/auth";
import { date } from "../lib/format";
import { EQUIP_CATEGORIES, EQUIP_STATUS, opts, plantOption, PRIORITIES } from "../lib/options";

export default function EquipmentList() {
  const { can } = useAuth();
  const write = can("PLANT_MANAGER", "ENGINEER");
  return (
    <ResourcePage title="Equipment" subtitle="Every pump, compressor, valve, generator, turbine and sensor with its service and warranty status."
      noun="equipment" endpoint="/equipment/" canWrite={write} canDelete={write} rowLink={(r) => `/equipment/${r.id}`}
      filters={[{ name: "category", label: "Category", options: opts(EQUIP_CATEGORIES) }, { name: "status", label: "Status", options: opts(EQUIP_STATUS) }]}
      columns={[
        { key: "name", label: "Name" }, { key: "serial_number", label: "Serial no." }, { key: "category_display", label: "Category" }, { key: "plant_name", label: "Plant" },
        { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> },
        { key: "health_score", label: "Health", render: (r) => <span className={r.health_score < 50 ? "font-semibold text-crit" : r.health_score < 80 ? "text-warn" : ""}>{r.health_score}</span> },
        { key: "next_maintenance_date", label: "Next maintenance", render: (r) => <span className={r.maintenance_overdue ? "font-medium text-crit" : ""}>{date(r.next_maintenance_date)}{r.maintenance_overdue && " (overdue)"}</span> },
        { key: "warranty_expiry", label: "Warranty", render: (r) => r.warranty_expiry ? <Badge value={r.warranty_active ? "ACTIVE" : "EXPIRED"} tone={r.warranty_active ? "ok" : "neutral"} label={r.warranty_active ? `Until ${date(r.warranty_expiry)}` : "Expired"} /> : "—" },
      ]}
      fields={[
        { name: "name", label: "Name", required: true }, { name: "serial_number", label: "Serial number", required: true },
        { name: "plant", label: "Plant", type: "select", optionsFrom: plantOption, required: true },
        { name: "category", label: "Category", type: "select", options: opts(EQUIP_CATEGORIES), required: true },
        { name: "status", label: "Status", type: "select", options: opts(EQUIP_STATUS), required: true },
        { name: "criticality", label: "Criticality", type: "select", options: opts(PRIORITIES), required: true },
        { name: "manufacturer", label: "Manufacturer" }, { name: "model_number", label: "Model number" },
        { name: "purchase_date", label: "Purchase date", type: "date" }, { name: "purchase_cost", label: "Purchase cost", type: "number", step: "0.01" },
        { name: "warranty_expiry", label: "Warranty expiry", type: "date" }, { name: "last_service_date", label: "Last service", type: "date" },
        { name: "next_maintenance_date", label: "Next maintenance", type: "date" }, { name: "location_note", label: "Location in plant" },
      ]}
      defaults={{ status: "OPERATIONAL", criticality: "MEDIUM", purchase_cost: 0 }} />
  );
}
