import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Lines } from "../components/charts";
import { Badge, Card, Gauge, Select, Spinner } from "../components/ui";
import { api, Row } from "../lib/api";
import { date, dateTime, num, pretty } from "../lib/format";

export default function EquipmentDetail() {
  const { id } = useParams();
  const [metric, setMetric] = useState("TEMPERATURE");
  const [hours, setHours] = useState(24);
  const eq = useQuery({ queryKey: ["eq", id], queryFn: async () => (await api.get(`/equipment/${id}/`)).data as Row, refetchInterval: 20_000 });
  const latest = useQuery({ queryKey: ["latest", id], queryFn: async () => (await api.get("/monitoring/readings/latest/", { params: { equipment: id } })).data as Row[], refetchInterval: 10_000 });
  const series = useQuery({ queryKey: ["series", id, metric, hours], refetchInterval: 15_000,
    queryFn: async () => (await api.get("/monitoring/readings/series/", { params: { equipment: id, metric, hours } })).data as Row[] });
  const wos = useQuery({ queryKey: ["eq-wos", id], queryFn: async () => (await api.get(`/equipment/${id}/work-orders/`)).data as Row[] });
  const sch = useQuery({ queryKey: ["eq-sch", id], queryFn: async () => (await api.get("/maintenance/schedules/", { params: { equipment: id } })).data.results as Row[] });
  const alerts = useQuery({ queryKey: ["eq-alerts", id], refetchInterval: 15_000, queryFn: async () => (await api.get("/monitoring/alerts/", { params: { equipment: id, page_size: 8 } })).data.results as Row[] });

  if (eq.isLoading) return <Spinner />;
  const e = eq.data!;
  const info: [string, string][] = [
    ["Serial number", e.serial_number], ["Plant", e.plant_name], ["Category", e.category_display], ["Manufacturer", `${e.manufacturer || "—"} ${e.model_number || ""}`],
    ["Criticality", pretty(e.criticality)], ["Purchased", date(e.purchase_date)], ["Warranty", e.warranty_expiry ? `${date(e.warranty_expiry)} (${e.warranty_active ? "active" : "expired"})` : "—"],
    ["Last service", date(e.last_service_date)], ["Next maintenance", date(e.next_maintenance_date)],
  ];
  const unit = latest.data?.find((l) => l.metric === metric)?.unit ?? "";

  return (
    <div className="space-y-5">
      <Link to="/equipment" className="inline-flex items-center gap-1.5 text-sm text-gauge hover:underline"><ArrowLeft className="h-4 w-4" />All equipment</Link>
      <div className="flex flex-wrap items-center gap-5 rounded-lg border border-line bg-white p-5">
        <Gauge value={e.health_score} size={88} label="Health score" />
        <div className="min-w-0 flex-1">
          <h1 className="text-3xl font-semibold text-ink-900">{e.name}</h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-2"><Badge value={e.status} />{e.maintenance_overdue && <Badge value="OVERDUE" tone="crit" label="Maintenance overdue" />}{e.open_alerts > 0 && <Badge value="CRITICAL" tone="warn" label={`${e.open_alerts} open alert${e.open_alerts > 1 ? "s" : ""}`} />}</div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Details" className="lg:col-span-1">
          <dl className="space-y-2 text-sm">{info.map(([k, v]) => <div key={k} className="flex justify-between gap-4 border-b border-line pb-2 last:border-0"><dt className="text-slate-500">{k}</dt><dd className="text-right font-medium">{v}</dd></div>)}</dl>
        </Card>
        <Card title="Live readings" className="lg:col-span-2" action={<span className="text-xs text-slate-500">Updates every 10 s</span>}>
          {latest.data?.length === 0 && <p className="py-6 text-center text-sm text-slate-500">No telemetry received yet. Post readings to <code>/api/v1/monitoring/readings/</code> or run <code>simulate_iot</code>.</p>}
          <div className="grid gap-3 sm:grid-cols-3">
            {latest.data?.map((l) => (
              <button key={l.metric} onClick={() => setMetric(l.metric)} className={`rounded-md border p-3 text-left ${metric === l.metric ? "border-gauge ring-1 ring-gauge" : "border-line hover:bg-paper"}`}>
                <p className="text-xs text-slate-500">{pretty(l.metric)}</p>
                <p className="font-display text-2xl font-semibold">{num(l.value, 1)}<span className="ml-1 text-sm font-normal text-slate-500">{l.unit}</span></p>
                <Badge value={l.state} />
              </button>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between"><p className="text-sm font-medium">{pretty(metric)} trend {unit && `(${unit})`}</p>
            <Select aria-label="Time range" className="w-auto" value={hours} onChange={(ev) => setHours(+ev.target.value)}><option value={6}>Last 6 h</option><option value={24}>Last 24 h</option><option value={72}>Last 3 days</option><option value={168}>Last 7 days</option></Select></div>
          <Lines height={220} fill labels={(series.data ?? []).map((p) => dateTime(p.t))} series={[{ label: pretty(metric), data: (series.data ?? []).map((p) => p.v), color: "#1f7a8c" }]} />
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Recent alerts" pad={false}>
          {alerts.data?.length === 0 ? <p className="p-6 text-center text-sm text-slate-500">No alerts recorded.</p> :
            <ul className="divide-y divide-line">{alerts.data?.map((a) => <li key={a.id} className="flex items-center justify-between px-4 py-2.5 text-sm"><span>{pretty(a.metric)} {num(a.value, 1)}{a.unit} <span className="text-slate-500">· {dateTime(a.created_at)} · ×{a.occurrence_count}</span></span><span className="flex gap-1.5"><Badge value={a.severity} /><Badge value={a.status} /></span></li>)}</ul>}
        </Card>
        <Card title="Maintenance plans" pad={false}>
          {sch.data?.length === 0 ? <p className="p-6 text-center text-sm text-slate-500">No recurring plans.</p> :
            <ul className="divide-y divide-line">{sch.data?.map((s) => <li key={s.id} className="flex items-center justify-between px-4 py-2.5 text-sm"><span>{s.title}<span className="block text-xs text-slate-500">Every {s.interval_days} days</span></span><span className={s.is_overdue ? "font-medium text-crit" : ""}>Due {date(s.next_due)}</span></li>)}</ul>}
        </Card>
      </div>

      <Card title="Work order history" pad={false}>
        {wos.data?.length === 0 ? <p className="p-6 text-center text-sm text-slate-500">No work orders for this equipment.</p> :
          <table className="w-full text-sm"><tbody>{wos.data?.map((w) => <tr key={w.id} className="border-b border-line last:border-0"><td className="px-4 py-2.5"><Link className="font-medium text-gauge hover:underline" to={`/work-orders/${w.id}`}>{w.number}</Link></td><td className="px-4 py-2.5">{w.title}</td><td className="px-4 py-2.5"><Badge value={w.wo_type} /></td><td className="px-4 py-2.5"><Badge value={w.status} /></td><td className="px-4 py-2.5 text-slate-500">{date(w.created_at)}</td></tr>)}</tbody></table>}
      </Card>
    </div>
  );
}
