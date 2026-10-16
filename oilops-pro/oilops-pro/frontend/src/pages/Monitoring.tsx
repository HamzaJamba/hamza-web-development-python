import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, CheckCheck } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import ResourcePage from "../components/ResourcePage";
import { Badge, Button, PageHeader, Tabs } from "../components/ui";
import { api, errorMessage } from "../lib/api";
import { useAuth } from "../lib/auth";
import { dateTime, num, pretty } from "../lib/format";
import { equipmentOption, METRICS, opts } from "../lib/options";

export default function Monitoring() {
  const { can } = useAuth();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"alerts" | "thresholds">("alerts");
  const act = useMutation({ mutationFn: ({ id, a }: { id: number; a: string }) => api.post(`/monitoring/alerts/${id}/${a}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["res", "/monitoring/alerts/"] }), onError: (e) => alert(errorMessage(e)) });
  const field = can("TECHNICIAN", "ENGINEER", "PLANT_MANAGER");

  return (
    <div>
      <PageHeader title="Live monitoring" subtitle="Threshold breaches from temperature, pressure, voltage, vibration and oil-level sensors. Critical alerts open an emergency work order automatically." />
      <Tabs value={tab} onChange={setTab} tabs={[{ id: "alerts", label: "Alerts" }, { id: "thresholds", label: "Thresholds" }]} />
      {tab === "alerts" ? (
        <ResourcePage embedded noun="alert" endpoint="/monitoring/alerts/" refetchMs={10_000} searchable={false}
          filters={[{ name: "status", label: "Status", options: opts(["OPEN", "ACKNOWLEDGED", "RESOLVED"]) }, { name: "severity", label: "Severity", options: opts(["WARNING", "CRITICAL"]) }, { name: "metric", label: "Metric", options: opts(METRICS) }]}
          columns={[
            { key: "severity", label: "Severity", render: (r) => <Badge value={r.severity} /> },
            { key: "equipment_name", label: "Equipment", render: (r) => <Link className="font-medium text-gauge hover:underline" to={`/equipment/${r.equipment}`}>{r.equipment_name}</Link> },
            { key: "plant_name", label: "Plant" }, { key: "metric", label: "Metric", render: (r) => `${pretty(r.metric)} ${num(r.value, 1)} ${r.unit}` },
            { key: "occurrence_count", label: "Count" }, { key: "created_at", label: "First seen", render: (r) => dateTime(r.created_at) },
            { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> }]}
          rowActions={(r) => field && r.status !== "RESOLVED" ? (
            <>{r.status === "OPEN" && <Button variant="ghost" onClick={() => act.mutate({ id: r.id, a: "acknowledge" })}><Check className="h-4 w-4" />Acknowledge</Button>}
              <Button variant="ghost" onClick={() => act.mutate({ id: r.id, a: "resolve" })}><CheckCheck className="h-4 w-4" />Resolve</Button></>) : null} />
      ) : (
        <ResourcePage embedded noun="threshold" endpoint="/monitoring/thresholds/" canWrite={can("ENGINEER", "PLANT_MANAGER")} canDelete={can("ENGINEER", "PLANT_MANAGER")} searchable={false}
          filters={[{ name: "metric", label: "Metric", options: opts(METRICS) }, { name: "severity", label: "Severity", options: opts(["WARNING", "CRITICAL"]) }]}
          columns={[{ key: "metric", label: "Metric", render: (r) => pretty(r.metric) }, { key: "scope", label: "Applies to", render: (r) => r.equipment_name || (r.category ? pretty(r.category) : "All equipment") },
            { key: "min_value", label: "Min", render: (r) => r.min_value ?? "—" }, { key: "max_value", label: "Max", render: (r) => r.max_value ?? "—" },
            { key: "severity", label: "Severity", render: (r) => <Badge value={r.severity} /> }, { key: "is_active", label: "Active", render: (r) => (r.is_active ? "Yes" : "No") }]}
          fields={[{ name: "metric", label: "Metric", type: "select", options: opts(METRICS), required: true }, { name: "severity", label: "Severity", type: "select", options: opts(["WARNING", "CRITICAL"]), required: true },
            { name: "equipment", label: "Specific equipment (optional)", type: "select", optionsFrom: equipmentOption, hint: "Overrides category-wide limits for this asset." },
            { name: "category", label: "Equipment category (optional)", type: "select", options: opts(["PUMP", "COMPRESSOR", "VALVE", "GENERATOR", "TURBINE", "SENSOR"]) },
            { name: "min_value", label: "Minimum allowed", type: "number", step: "any" }, { name: "max_value", label: "Maximum allowed", type: "number", step: "any" },
            { name: "is_active", label: "Active", type: "checkbox" }]}
          defaults={{ severity: "WARNING", is_active: true }} />
      )}
    </div>
  );
}
