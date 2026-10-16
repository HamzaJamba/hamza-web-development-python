import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Wand2 } from "lucide-react";

import ResourcePage from "../components/ResourcePage";
import { Badge, Button } from "../components/ui";
import { api, errorMessage } from "../lib/api";
import { useAuth } from "../lib/auth";
import { date } from "../lib/format";
import { equipmentOption, userOption } from "../lib/options";

export default function Maintenance() {
  const { can } = useAuth();
  const qc = useQueryClient();
  const write = can("PLANT_MANAGER", "ENGINEER");
  const gen = useMutation({ mutationFn: async () => (await api.post("/maintenance/schedules/generate-work-orders/")).data,
    onSuccess: (d) => { alert(`${d.created} preventive work order(s) created.`); qc.invalidateQueries({ queryKey: ["res"] }); }, onError: (e) => alert(errorMessage(e)) });
  return (
    <ResourcePage title="Maintenance plans" subtitle="Recurring preventive maintenance. Work orders are generated automatically ahead of each due date." noun="plan" endpoint="/maintenance/schedules/"
      canWrite={write} canDelete={write}
      headerActions={write && <Button onClick={() => gen.mutate()} loading={gen.isPending}><Wand2 className="h-4 w-4" />Generate due work orders</Button>}
      filters={[{ name: "is_active", label: "State", options: [{ value: "true", label: "Active" }, { value: "false", label: "Paused" }] }]}
      columns={[{ key: "title", label: "Plan" }, { key: "equipment_name", label: "Equipment" }, { key: "interval_days", label: "Every", render: (r) => `${r.interval_days} days` },
        { key: "last_performed", label: "Last done", render: (r) => date(r.last_performed) },
        { key: "next_due", label: "Next due", render: (r) => <span className={r.is_overdue ? "font-medium text-crit" : ""}>{date(r.next_due)}{r.is_overdue && " (overdue)"}</span> },
        { key: "auto_create_work_order", label: "Auto work order", render: (r) => <Badge value={r.auto_create_work_order ? "ACTIVE" : "IDLE"} label={r.auto_create_work_order ? "On" : "Off"} /> }]}
      fields={[{ name: "equipment", label: "Equipment", type: "select", optionsFrom: equipmentOption, required: true }, { name: "title", label: "Plan title", required: true },
        { name: "interval_days", label: "Interval (days)", type: "number", required: true }, { name: "estimated_hours", label: "Estimated hours", type: "number", step: "0.5" },
        { name: "last_performed", label: "Last performed", type: "date" }, { name: "next_due", label: "Next due", type: "date", hint: "Leave empty to calculate from the interval." },
        { name: "assigned_engineer", label: "Engineer", type: "select", optionsFrom: userOption("ENGINEER,PLANT_MANAGER") },
        { name: "auto_create_work_order", label: "Create work orders automatically", type: "checkbox" }, { name: "is_active", label: "Active", type: "checkbox" },
        { name: "description", label: "Task checklist / notes", type: "textarea" }]}
      defaults={{ interval_days: 90, auto_create_work_order: true, is_active: true, estimated_hours: 0 }} />
  );
}
