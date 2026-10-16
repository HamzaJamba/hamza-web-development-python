import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, FileText, Image as ImageIcon, Trash2, Upload } from "lucide-react";
import { FormEvent, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Badge, Button, Card, ErrorNote, Field, Select, Spinner, Textarea } from "../components/ui";
import { api, errorMessage, Row } from "../lib/api";
import { useAuth } from "../lib/auth";
import { dateTime, money } from "../lib/format";
import { INCIDENT_STATUS, opts } from "../lib/options";

export default function IncidentDetail() {
  const { id } = useParams();
  const { can } = useAuth();
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [form, setForm] = useState<Row | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const q = useQuery({ queryKey: ["inc", id], queryFn: async () => (await api.get(`/incidents/${id}/`)).data as Row });
  const refresh = () => qc.invalidateQueries({ queryKey: ["inc", id] });
  const investigate = can("PLANT_MANAGER", "ENGINEER", "SAFETY_OFFICER");
  const save = useMutation({ mutationFn: (b: Row) => api.patch(`/incidents/${id}/`, b), onSuccess: () => { setForm(null); setErr(null); refresh(); }, onError: (e) => setErr(errorMessage(e)) });
  const upload = useMutation({ mutationFn: (file: File) => { const fd = new FormData(); fd.append("file", file); return api.post(`/incidents/${id}/attachments/`, fd); },
    onSuccess: refresh, onError: (e) => setErr(errorMessage(e)) });
  const remove = useMutation({ mutationFn: (aid: number) => api.delete(`/incidents/attachments/${aid}/`), onSuccess: refresh });

  if (q.isLoading) return <Spinner />;
  const i = q.data!;
  const edit = form ?? { status: i.status, root_cause: i.root_cause, corrective_action: i.corrective_action };
  const onSave = (e: FormEvent) => { e.preventDefault(); setErr(null); save.mutate(edit); };

  return (
    <div className="space-y-5">
      <Link to="/incidents" className="inline-flex items-center gap-1.5 text-sm text-gauge hover:underline"><ArrowLeft className="h-4 w-4" />All incidents</Link>
      <div className="rounded-lg border border-line bg-white p-5">
        <p className="text-sm text-slate-500">{i.number}</p>
        <h1 className="text-3xl font-semibold text-ink-900">{i.title}</h1>
        <div className="mt-2 flex flex-wrap gap-2"><Badge value={i.incident_type} tone="neutral" /><Badge value={i.severity} /><Badge value={i.status} /></div>
        <p className="mt-4 whitespace-pre-wrap text-sm text-slate-700">{i.description}</p>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
          {[["Plant", i.plant_name], ["Equipment", i.equipment_name || "—"], ["Occurred", dateTime(i.occurred_at)], ["Reported by", i.reporter_name || "—"],
            ["Injuries", i.injuries], ["Downtime", `${i.downtime_hours} h`], ["Estimated loss", money(i.estimated_loss)], ["Closed", dateTime(i.closed_at)]].map(([k, v]) => <div key={k as string}><dt className="text-slate-500">{k}</dt><dd className="font-medium">{v}</dd></div>)}
        </dl>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Investigation">
          {investigate ? (
            <form onSubmit={onSave} className="space-y-3">
              <Field label="Status"><Select value={edit.status} onChange={(e) => setForm({ ...edit, status: e.target.value })}>{opts(INCIDENT_STATUS).map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</Select></Field>
              <Field label="Root cause" hint="Required before resolving or closing."><Textarea value={edit.root_cause ?? ""} onChange={(e) => setForm({ ...edit, root_cause: e.target.value })} /></Field>
              <Field label="Corrective action"><Textarea value={edit.corrective_action ?? ""} onChange={(e) => setForm({ ...edit, corrective_action: e.target.value })} /></Field>
              <ErrorNote message={err} /><Button type="submit" variant="primary" loading={save.isPending}>Save investigation</Button>
            </form>
          ) : <div className="space-y-2 text-sm"><p><b>Root cause:</b> {i.root_cause || "Not yet determined."}</p><p><b>Corrective action:</b> {i.corrective_action || "Not yet defined."}</p></div>}
        </Card>

        <Card title="Photos & documents" action={<><input ref={fileRef} type="file" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) upload.mutate(f); e.target.value = ""; }} />
          <Button onClick={() => fileRef.current?.click()} loading={upload.isPending}><Upload className="h-4 w-4" />Upload</Button></>}>
          {!investigate && <ErrorNote message={err} />}
          {i.attachments.length === 0 ? <p className="py-6 text-center text-sm text-slate-500">No files yet. Images, PDF, Word, Excel and text files up to 10 MB are accepted.</p> :
            <ul className="grid gap-3 sm:grid-cols-2">{i.attachments.map((a: Row) => (
              <li key={a.id} className="overflow-hidden rounded-md border border-line">
                {a.kind === "PHOTO" ? <a href={a.file} target="_blank" rel="noreferrer"><img src={a.file} alt={a.file_name} className="h-32 w-full object-cover" /></a> : <a href={a.file} target="_blank" rel="noreferrer" className="flex h-32 items-center justify-center bg-paper"><FileText className="h-10 w-10 text-slate-400" /></a>}
                <div className="flex items-center justify-between gap-2 px-3 py-2 text-xs"><span className="flex min-w-0 items-center gap-1.5">{a.kind === "PHOTO" ? <ImageIcon className="h-3.5 w-3.5 shrink-0" /> : <FileText className="h-3.5 w-3.5 shrink-0" />}<span className="truncate">{a.file_name}</span></span>
                  {investigate && <button aria-label="Delete file" onClick={() => confirm("Delete this file?") && remove.mutate(a.id)} className="text-crit"><Trash2 className="h-4 w-4" /></button>}</div>
              </li>))}</ul>}
        </Card>
      </div>
    </div>
  );
}
