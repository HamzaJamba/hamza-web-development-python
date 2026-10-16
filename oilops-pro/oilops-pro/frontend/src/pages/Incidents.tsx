import ResourcePage from "../components/ResourcePage";
import { Badge } from "../components/ui";
import { useAuth } from "../lib/auth";
import { dateTime, money } from "../lib/format";
import { equipmentOption, INCIDENT_STATUS, INCIDENT_TYPES, opts, plantOption, SEVERITIES } from "../lib/options";

export default function Incidents() {
  const { can } = useAuth();
  const report = can("PLANT_MANAGER", "ENGINEER", "TECHNICIAN", "SAFETY_OFFICER", "STORE_KEEPER", "HR");
  return (
    <ResourcePage title="Incidents" subtitle="Gas leaks, fires, explosions, equipment failures, near misses and safety violations. Photos and documents attach on the incident page." noun="incident"
      endpoint="/incidents/" canWrite={report} rowLink={(r) => `/incidents/${r.id}`}
      filters={[{ name: "incident_type", label: "Type", options: opts(INCIDENT_TYPES) }, { name: "severity", label: "Severity", options: opts(SEVERITIES) }, { name: "status", label: "Status", options: opts(INCIDENT_STATUS) }]}
      columns={[{ key: "number", label: "Number" }, { key: "title", label: "Title" }, { key: "incident_type", label: "Type", render: (r) => <Badge value={r.incident_type} tone="neutral" /> },
        { key: "severity", label: "Severity", render: (r) => <Badge value={r.severity} /> }, { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> },
        { key: "plant_name", label: "Plant" }, { key: "occurred_at", label: "Occurred", render: (r) => dateTime(r.occurred_at) },
        { key: "estimated_loss", label: "Est. loss", render: (r) => money(r.estimated_loss) }]}
      fields={[{ name: "title", label: "Title", required: true, full: true }, { name: "incident_type", label: "Type", type: "select", options: opts(INCIDENT_TYPES), required: true },
        { name: "severity", label: "Severity", type: "select", options: opts(SEVERITIES), required: true }, { name: "plant", label: "Plant", type: "select", optionsFrom: plantOption, required: true },
        { name: "equipment", label: "Equipment involved", type: "select", optionsFrom: equipmentOption, hint: "Equipment failures raise a repair work order automatically." },
        { name: "occurred_at", label: "When it happened", type: "datetime-local" }, { name: "injuries", label: "Injuries", type: "number" },
        { name: "downtime_hours", label: "Downtime (hours)", type: "number", step: "0.5" }, { name: "estimated_loss", label: "Estimated loss", type: "number", step: "0.01" },
        { name: "description", label: "What happened", type: "textarea", required: true }]}
      defaults={{ severity: "MINOR", injuries: 0, downtime_hours: 0, estimated_loss: 0, incident_type: "NEAR_MISS" }} />
  );
}
