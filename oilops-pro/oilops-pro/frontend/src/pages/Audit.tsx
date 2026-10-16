import ResourcePage from "../components/ResourcePage";
import { Badge } from "../components/ui";
import { dateTime } from "../lib/format";

export default function Audit() {
  return (
    <ResourcePage title="Audit log" subtitle="Who created, changed, deleted, exported or signed in, with before/after values. Read-only." noun="entry" endpoint="/audit/logs/"
      filters={[{ name: "action", label: "Action", options: ["CREATE", "UPDATE", "DELETE", "LOGIN", "LOGIN_FAILED", "LOGOUT", "EXPORT", "UPLOAD", "START", "COMPLETE", "ASSIGN", "CANCEL", "HOLD", "PASSWORD_CHANGE"].map((v) => ({ value: v, label: v })) }]}
      columns={[{ key: "timestamp", label: "Time", render: (r) => dateTime(r.timestamp) }, { key: "user_name", label: "User", render: (r) => r.user_name || "—" },
        { key: "action", label: "Action", render: (r) => <Badge value={r.action} /> }, { key: "model", label: "Record", render: (r) => `${r.model} ${r.object_repr ? "· " + r.object_repr : ""}` },
        { key: "changes", label: "Changes", render: (r) => <code className="block max-w-md truncate text-xs text-slate-600" title={JSON.stringify(r.changes)}>{Object.keys(r.changes ?? {}).slice(0, 4).join(", ") || "—"}</code> },
        { key: "ip_address", label: "IP", render: (r) => r.ip_address ?? "—" }]} />
  );
}
