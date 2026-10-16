import { useMutation } from "@tanstack/react-query";
import { Download, Eye, FileSpreadsheet, FileText } from "lucide-react";
import { useState } from "react";

import { Button, Card, ErrorNote, Field, Input, PageHeader, Select } from "../components/ui";
import { api, download, errorMessage, getList, Row } from "../lib/api";
import { useQuery } from "@tanstack/react-query";

const REPORTS = [
  { id: "maintenance", title: "Maintenance report", desc: "Work orders in a date range with type, status, downtime and cost.", range: true },
  { id: "incidents", title: "Incident report", desc: "Incidents with severity, injuries, downtime and estimated loss.", range: true },
  { id: "equipment", title: "Equipment report", desc: "Asset register with health, service dates and warranty status.", range: false },
  { id: "monthly-performance", title: "Monthly performance", desc: "KPI summary for one month: throughput of work, cost, downtime, incidents.", range: false, month: true },
];

export default function Reports() {
  const [p, setP] = useState<Row>({ date_from: "", date_to: "", month: new Date().toISOString().slice(0, 7), plant: "" });
  const [preview, setPreview] = useState<Row | null>(null);
  const [name, setName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const plants = useQuery({ queryKey: ["plants-all"], queryFn: () => getList("/plants/") });
  const params = (id: string) => {
    const x: Row = {};
    const r = REPORTS.find((r) => r.id === id)!;
    if (p.plant) x.plant = p.plant;
    if (r.range) { if (p.date_from) x.date_from = p.date_from; if (p.date_to) x.date_to = p.date_to; }
    if (r.month) x.month = p.month;
    return x;
  };
  const view = useMutation({ mutationFn: async (id: string) => { setName(id); return (await api.get(`/reports/${id}/`, { params: params(id) })).data as Row; }, onSuccess: (d) => { setPreview(d); setErr(null); }, onError: (e) => setErr(errorMessage(e)) });
  const save = useMutation({ mutationFn: ({ id, fmt }: { id: string; fmt: string }) => download(`/reports/${id}/`, { ...params(id), export: fmt }, `${id}.${fmt}`), onError: (e) => setErr(errorMessage(e)) });

  return (
    <div className="space-y-5">
      <PageHeader title="Reports" subtitle="Preview on screen or export to PDF and Excel. Every export is recorded in the audit log." />
      <Card title="Filters">
        <div className="grid gap-4 sm:grid-cols-4">
          <Field label="From"><Input type="date" value={p.date_from} onChange={(e) => setP({ ...p, date_from: e.target.value })} /></Field>
          <Field label="To"><Input type="date" value={p.date_to} onChange={(e) => setP({ ...p, date_to: e.target.value })} /></Field>
          <Field label="Month (performance)"><Input type="month" value={p.month} onChange={(e) => setP({ ...p, month: e.target.value })} /></Field>
          <Field label="Plant"><Select value={p.plant} onChange={(e) => setP({ ...p, plant: e.target.value })}><option value="">All plants</option>{plants.data?.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</Select></Field>
        </div>
        <p className="mt-2 text-xs text-slate-500">Date range defaults to the last 90 days. The plant filter applies to maintenance, incident and equipment reports.</p>
      </Card>
      <div className="grid gap-4 md:grid-cols-2">
        {REPORTS.map((r) => (
          <Card key={r.id} title={r.title}>
            <p className="mb-4 text-sm text-slate-600">{r.desc}</p>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => view.mutate(r.id)} loading={view.isPending && name === r.id}><Eye className="h-4 w-4" />Preview</Button>
              <Button onClick={() => save.mutate({ id: r.id, fmt: "pdf" })}><FileText className="h-4 w-4" />PDF</Button>
              <Button onClick={() => save.mutate({ id: r.id, fmt: "xlsx" })}><FileSpreadsheet className="h-4 w-4" />Excel</Button>
            </div>
          </Card>
        ))}
      </div>
      <ErrorNote message={err} />
      {preview && (
        <Card title={`${preview.title} — ${preview.subtitle}`} action={<Button onClick={() => save.mutate({ id: name, fmt: "xlsx" })}><Download className="h-4 w-4" />Excel</Button>} pad={false}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-line bg-paper text-left text-slate-600"><tr>{preview.columns.map((c: string) => <th key={c} className="whitespace-nowrap px-4 py-2 font-medium">{c}</th>)}</tr></thead>
              <tbody>{preview.rows.map((row: unknown[], i: number) => <tr key={i} className="border-b border-line last:border-0">{row.map((v, j) => <td key={j} className="whitespace-nowrap px-4 py-2">{String(v)}</td>)}</tr>)}</tbody>
            </table>
            {preview.rows.length === 0 && <p className="p-6 text-center text-sm text-slate-500">No data for the selected filters.</p>}
          </div>
          {Object.keys(preview.summary).length > 0 && <div className="flex flex-wrap gap-6 border-t border-line px-4 py-3 text-sm">{Object.entries(preview.summary).map(([k, v]) => <span key={k}><span className="text-slate-500">{k}:</span> <b>{String(v)}</b></span>)}</div>}
        </Card>
      )}
    </div>
  );
}
