import ResourcePage from "../components/ResourcePage";
import { Badge } from "../components/ui";
import { dateTime, pretty } from "../lib/format";
import { opts, ROLES } from "../lib/options";

export default function UsersPage() {
  return (
    <ResourcePage title="User accounts" subtitle="Create accounts and assign roles. Role-based access is enforced by the API on every request." noun="user" endpoint="/auth/users/" canWrite canDelete
      filters={[{ name: "role", label: "Role", options: opts(ROLES) }, { name: "is_active", label: "Active", options: [{ value: "true", label: "Active" }, { value: "false", label: "Disabled" }] }]}
      columns={[{ key: "full_name", label: "Name" }, { key: "email", label: "Email" }, { key: "role", label: "Role", render: (r) => pretty(r.role) },
        { key: "is_active", label: "State", render: (r) => <Badge value={r.is_active ? "ACTIVE" : "OFFLINE"} label={r.is_active ? "Active" : "Disabled"} /> }, { key: "last_login", label: "Last login", render: (r) => dateTime(r.last_login) }]}
      fields={[{ name: "email", label: "Email", type: "email", required: true }, { name: "role", label: "Role", type: "select", options: opts(ROLES), required: true },
        { name: "first_name", label: "First name", required: true }, { name: "last_name", label: "Last name" }, { name: "phone", label: "Phone" },
        { name: "password", label: "Password", type: "password", hint: "At least 10 characters. Leave empty to keep the current password.", createOnly: false }, { name: "is_active", label: "Active", type: "checkbox" }]}
      defaults={{ role: "VIEWER", is_active: true }} />
  );
}
