import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Pause, Play, CheckCircle2, XCircle, UserPlus, PackagePlus } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Badge, Button, Card, ErrorNote, Field, Input, Modal, Select, Spinner, Textarea } from "../components/ui";
import { api, errorMessage, getList, Row } from "../lib/api";
import { useAuth } from "../lib/auth";
import { dateTime, money, num } from "../lib/format";

type Dlg = null | "complete" | "assign" | "part" | "hold" | "cancel";

export default function WorkOrderDetail() {
  const { id } = useParams();
  const { can } = useAuth();
  const qc = useQueryClient();
  const [dlg, setDlg] = useState<Dlg>(null);
  const [err, setErr] = useState<string | null>(null);
  const [f, setF] = useState<Row>({});
  const q = useQuery({ queryKey: ["wo", id], queryFn: async () => (await api.get(`/work-orders/${id}/`)).data as Row });
  const items = useQuery({ queryKey: ["items-all"], enabled: dlg === "part", queryFn: () => getList("/inventory/", { is_active: true }) });
  const users = useQuery({ queryKey: ["users-assign"], enabled: dlg === "assign", queryFn: () => getList("/auth/users/directory/", { role: "ENGINEER,PLANT_MANAGER,TECHNICIAN" }) });

  const run = useMutation({
    mutationFn: async ({ path, body }: { path: string; body?: Row }) => (await api.post(`/work-orders/${id}/${path}/`, body)).data,
    onSuccess: () => { setDlg(null); setF({}); setErr(null); qc.invalidateQueries({ queryKey: ["wo", id] }); qc.invalidateQueries({ queryKey: ["res", "/work-orders/"] }); },
    onError: (e) => setErr(errorMessage(e)),
  });
  if (q.isLoading) return <Spinner />;
  const w = q.data!;
  const open = ["OPEN", "ASSIGNED", "IN_PROGRESS", "ON_HOLD"].includes(w.status);
  const mgmt = can("PLANT_MANAGER", "ENGINEER");
  const field = can("PLANT_MANAGER", "ENGINEER", "TECHNICIAN");
  const go = (path: string, body?: Row) => { setErr(null); run.mutate({ path, body }); };
  const submit = (path: string, body: Row) => (e: FormEvent) => { e.preventDefault(); go(path, body); };

  return (
    <div className="space-y-5">
      <Link to="/work-orders" className="inline-flex items-center gap-1.5 text-sm text-gauge hover:underline"><ArrowLeft className="h-4 w-4" />All work orders</Link>
      <div className="rounded-lg border border-line bg-white p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm text-slate-500">{w.number}</p>
            <h1 className="text-3xl font-semibold text-ink-900">{w.title}</h1>
            <div className="mt-2 flex flex-wrap gap-2"><Badge value={w.status} /><Badge value={w.priority} /><Badge value={w.wo_type} />{w.is_overdue && <Badge value="OVERDUE" tone="crit" label="Overdue" />}</div>
          </div>
          <div className="flex flex-wrap gap-2">
            {field && ["OPEN", "ASSIGNED", "ON_HOLD"].includes(w.status) && <Button variant="primary" onClick={() => go("start")} loading={run.isPending}><Play className="h-4 w-4" />Start work</Button>}
            {field && w.status === "IN_PROGRESS" && <Button variant="primary" onClick={() => { setErr(null); setDlg("complete"); }}><CheckCircle2 className="h-4 w-4" />Complete</Button>}
            {field && w.status === "IN_PROGRESS" && <Button onClick={() => { setErr(null); setDlg("hold"); }}><Pause className="h-4 w-4" />Put on hold</Button>}
            {mgmt && open && <Button onClick={() => { setErr(null); setF({ engineer: w.engineer ?? "", technicians: w.technicians }); setDlg("assign"); }}><UserPlus className="h-4 w-4" />Assign</Button>}
            {mgmt && open && <Button variant="danger" onClick={() => { setErr(null); setDlg("cancel"); }}><XCircle className="h-4 w-4" />Cancel</Button>}
          </div>
        </div>
        {!dlg && <div className="mt-3"><ErrorNote message={err} /></div>}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Job details" className="lg:col-span-2">
          <p className="whitespace-pre-wrap text-sm text-slate-700">{w.description || "No description."}</p>
          <dl className="mt-4 grid gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
            {([["Equipment", <Link key="e" className="text-gauge hover:underline" to={`/equipment/${w.equipment}`}>{w.equipment_name} ({w.equipment_serial})</Link>], ["Plant", w.plant_name],
              ["Engineer", w.engineer_name || "—"], ["Technicians", w.technician_names?.join(", ") || "—"], ["Deadline", dateTime(w.deadline)], ["Started", dateTime(w.started_at)],
              ["Completed", dateTime(w.completed_at)], ["Downtime", `${num(w.downtime_hours, 1)} h`]] as [string, React.ReactNode][]).map(([k, v]) => (
              <div key={k}><dt className="text-slate-500">{k}</dt><dd className="font-medium">{v}</dd></div>))}
          </dl>
          {w.completion_notes && <div className="mt-4 rounded-md bg-paper p-3 text-sm"><p className="mb-1 font-medium">Notes</p><p className="whitespace-pre-wrap">{w.completion_notes}</p></div>}
        </Card>
        <Card title="Cost">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-slate-500">Spare parts</dt><dd>{money(w.parts_cost)}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Labour ({num(w.labor_hours, 1)} h)</dt><dd>{money(w.labor_cost)}</dd></div>
            <div className="flex justify-between border-t border-line pt-2 text-base font-semibold"><dt>Total</dt><dd>{money(w.total_cost)}</dd></div>
          </dl>
        </Card>
      </div>

      <Card title="Spare parts used" action={field && open && <Button onClick={() => { setErr(null); setF({ quantity: 1 }); setDlg("part"); }}><PackagePlus className="h-4 w-4" />Add part</Button>} pad={false}>
        {w.parts.length === 0 ? <p className="p-6 text-center text-sm text-slate-500">No parts recorded. Parts added here are deducted from inventory automatically.</p> :
          <table className="w-full text-sm"><thead className="border-b border-line bg-paper text-left text-slate-600"><tr><th className="px-4 py-2 font-medium">SKU</th><th className="px-4 py-2 font-medium">Item</th><th className="px-4 py-2 font-medium">Qty</th><th className="px-4 py-2 font-medium">Unit cost</th><th className="px-4 py-2 font-medium">Total</th></tr></thead>
            <tbody>{w.parts.map((p: Row) => <tr key={p.id} className="border-b border-line last:border-0"><td className="px-4 py-2">{p.item_sku}</td><td className="px-4 py-2">{p.item_name}</td><td className="px-4 py-2">{p.quantity}</td><td className="px-4 py-2">{money(p.unit_cost)}</td><td className="px-4 py-2">{money(p.total_cost)}</td></tr>)}</tbody></table>}
      </Card>

      {dlg === "complete" && (
        <Modal title="Complete work order" onClose={() => setDlg(null)}>
          <form className="space-y-4" onSubmit={submit("complete", { completion_notes: f.notes, labor_hours: f.labor || undefined, downtime_hours: f.down || undefined })}>
            <Field label="Completion notes *"><Textarea required value={f.notes ?? ""} onChange={(e) => setF({ ...f, notes: e.target.value })} placeholder="What was done, findings, follow-up needed" /></Field>
            <div className="grid grid-cols-2 gap-4"><Field label="Labour hours"><Input type="number" step="0.5" min="0" value={f.labor ?? ""} onChange={(e) => setF({ ...f, labor: e.target.value })} /></Field>
              <Field label="Downtime hours"><Input type="number" step="0.5" min="0" value={f.down ?? ""} onChange={(e) => setF({ ...f, down: e.target.value })} /></Field></div>
            <ErrorNote message={err} /><div className="flex justify-end gap-2"><Button type="button" onClick={() => setDlg(null)}>Cancel</Button><Button type="submit" variant="primary" loading={run.isPending}>Mark completed</Button></div>
          </form>
        </Modal>)}
      {(dlg === "hold" || dlg === "cancel") && (
        <Modal title={dlg === "hold" ? "Put on hold" : "Cancel work order"} onClose={() => setDlg(null)}>
          <form className="space-y-4" onSubmit={submit(dlg, { reason: f.reason })}>
            <Field label="Reason"><Textarea value={f.reason ?? ""} onChange={(e) => setF({ ...f, reason: e.target.value })} /></Field>
            <ErrorNote message={err} /><div className="flex justify-end gap-2"><Button type="button" onClick={() => setDlg(null)}>Back</Button><Button type="submit" variant={dlg === "cancel" ? "danger" : "primary"} loading={run.isPending}>{dlg === "hold" ? "Put on hold" : "Cancel work order"}</Button></div>
          </form>
        </Modal>)}
      {dlg === "assign" && (
        <Modal title="Assign crew" onClose={() => setDlg(null)}>
          <form className="space-y-4" onSubmit={submit("assign", { engineer: f.engineer || undefined, technicians: f.technicians })}>
            <Field label="Engineer"><Select value={f.engineer ?? ""} onChange={(e) => setF({ ...f, engineer: e.target.value ? +e.target.value : "" })}><option value="">— none —</option>{users.data?.filter((u) => ["ENGINEER", "PLANT_MANAGER"].includes(u.role)).map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}</Select></Field>
            <Field label="Technicians" hint="Hold Ctrl / Cmd to select several."><select multiple className="h-32 w-full rounded-md border border-line px-2 py-1 text-sm" value={(f.technicians ?? []).map(String)} onChange={(e) => setF({ ...f, technicians: Array.from(e.target.selectedOptions).map((o) => +o.value) })}>{users.data?.filter((u) => ["TECHNICIAN", "ENGINEER"].includes(u.role)).map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}</select></Field>
            <ErrorNote message={err} /><div className="flex justify-end gap-2"><Button type="button" onClick={() => setDlg(null)}>Cancel</Button><Button type="submit" variant="primary" loading={run.isPending}>Save assignment</Button></div>
          </form>
        </Modal>)}
      {dlg === "part" && (
        <Modal title="Add spare part" onClose={() => setDlg(null)}>
          <form className="space-y-4" onSubmit={submit("parts", { item: f.item, quantity: f.quantity })}>
            <Field label="Item *"><Select required value={f.item ?? ""} onChange={(e) => setF({ ...f, item: +e.target.value })}><option value="">Select…</option>{items.data?.map((i) => <option key={i.id} value={i.id}>{i.name} — {i.quantity} {i.unit} in stock</option>)}</Select></Field>
            <Field label="Quantity *"><Input type="number" step="0.01" min="0.01" required value={f.quantity ?? ""} onChange={(e) => setF({ ...f, quantity: e.target.value })} /></Field>
            <ErrorNote message={err} /><div className="flex justify-end gap-2"><Button type="button" onClick={() => setDlg(null)}>Cancel</Button><Button type="submit" variant="primary" loading={run.isPending}>Issue from stock</Button></div>
          </form>
        </Modal>)}
    </div>
  );
}
