import ResourcePage from "../components/ResourcePage";
import { Badge } from "../components/ui";
import { useAuth } from "../lib/auth";
import { dateTime } from "../lib/format";
import { equipmentOption, opts, PRIORITIES, userOption, WO_STATUS, WO_TYPES } from "../lib/options";

export default function WorkOrders() {
  const { can } = useAuth();
  const write = can("PLANT_MANAGER", "ENGINEER");
  return (
    <ResourcePage title="Work orders" subtitle="Preventive, corrective and emergency jobs from request to completion." noun="work order" endpoint="/work-orders/"
      canWrite={write} rowLink={(r) => `/work-orders/${r.id}`} refetchMs={30_000}
      filters={[{ name: "status", label: "Status", options: opts(WO_STATUS) }, { name: "priority", label: "Priority", options: opts(PRIORITIES) }, { name: "wo_type", label: "Type", options: opts(WO_TYPES) },
        { name: "overdue", label: "Overdue", options: [{ value: "true", label: "Overdue only" }] }, { name: "assigned_to_me", label: "Mine", options: [{ value: "true", label: "Assigned to me" }] }]}
      columns={[
        { key: "number", label: "Number" }, { key: "title", label: "Title" }, { key: "equipment_name", label: "Equipment" },
        { key: "wo_type", label: "Type", render: (r) => <Badge value={r.wo_type} /> }, { key: "priority", label: "Priority", render: (r) => <Badge value={r.priority} /> },
        { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> },
        { key: "deadline", label: "Deadline", render: (r) => <span className={r.is_overdue ? "font-medium text-crit" : ""}>{dateTime(r.deadline)}{r.is_overdue && " ⚠"}</span> },
        { key: "engineer_name", label: "Engineer", render: (r) => r.engineer_name || "—" }]}
      fields={[
        { name: "title", label: "Title", required: true, full: true }, { name: "equipment", label: "Equipment", type: "select", optionsFrom: equipmentOption, required: true },
        { name: "wo_type", label: "Type", type: "select", options: opts(WO_TYPES), required: true }, { name: "priority", label: "Priority", type: "select", options: opts(PRIORITIES), required: true },
        { name: "deadline", label: "Deadline", type: "datetime-local" }, { name: "estimated_hours", label: "Estimated hours", type: "number", step: "0.5" },
        { name: "engineer", label: "Engineer", type: "select", optionsFrom: userOption("ENGINEER,PLANT_MANAGER") },
        { name: "technicians", label: "Technicians", type: "multiselect", optionsFrom: userOption("TECHNICIAN,ENGINEER"), hint: "Hold Ctrl / Cmd to select several." },
        { name: "description", label: "Description", type: "textarea" }]}
      defaults={{ wo_type: "CORRECTIVE", priority: "MEDIUM", technicians: [], estimated_hours: 0 }} />
  );
}
