import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Donut, HBars, Lines, StackedBars } from "../components/charts";
import { Badge, Card, Gauge, PageHeader, Spinner, Stat } from "../components/ui";
import { api, Row } from "../lib/api";
import { ago, money, num, pretty } from "../lib/format";

const get = <T = Row,>(url: string) => ({ queryKey: ["an", url], queryFn: async () => (await api.get(url)).data as T, refetchInterval: 60_000 });
const monthLabel = (m: string) => new Date(m + "-01").toLocaleDateString(undefined, { month: "short" });

export default function Dashboard() {
  const ov = useQuery(get("/analytics/overview/"));
  const health = useQuery(get("/analytics/equipment-health/"));
  const cost = useQuery(get("/analytics/maintenance-cost/"));
  const down = useQuery(get("/analytics/downtime/"));
  const inc = useQuery(get("/analytics/incidents/"));
  const usage = useQuery(get("/analytics/inventory-usage/"));
  const perf = useQuery(get<Row[]>("/analytics/employee-performance/"));
  const alerts = useQuery({ queryKey: ["alerts-open"], refetchInterval: 15_000, queryFn: async () => (await api.get("/monitoring/alerts/", { params: { status: "OPEN", page_size: 6 } })).data.results as Row[] });

  if (ov.isLoading) return <Spinner />;
  const o = ov.data ?? {};

  return (
    <div className="space-y-5">
      <PageHeader title="Operations overview" subtitle="Live position across all plants. Figures refresh automatically." />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Open work orders" value={o.open_work_orders} hint={`${o.overdue_work_orders} overdue · ${o.critical_work_orders} critical`} tone={o.overdue_work_orders ? "warn" : undefined} />
        <Stat label="Active sensor alerts" value={o.open_alerts} hint={`${o.critical_alerts} critical`} tone={o.critical_alerts ? "crit" : "ok"} />
        <Stat label="Open incidents" value={o.open_incidents} hint={`${o.incidents_30d} reported in the last 30 days`} tone={o.open_incidents ? "warn" : "ok"} />
        <Stat label="Low-stock items" value={o.low_stock_items} hint={`${o.maintenance_overdue} equipment overdue for maintenance`} tone={o.low_stock_items ? "warn" : "ok"} />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Fleet health" className="lg:col-span-1">
          <div className="flex items-center gap-6">
            <div className="text-center"><Gauge value={o.avg_health ?? 0} size={104} label="Average health" /><p className="mt-1 text-xs text-slate-500">Average health</p></div>
            <div className="text-center"><Gauge value={o.availability_pct ?? 0} size={104} label="Availability" /><p className="mt-1 text-xs text-slate-500">Availability</p></div>
          </div>
          <p className="mt-4 text-sm text-slate-600">{o.equipment_operational} of {o.equipment_total} assets operational.</p>
          {health.data && <div className="mt-3"><Donut labels={health.data.health_buckets.map((b: Row) => b.label)} data={health.data.health_buckets.map((b: Row) => b.count)} colors={["#2f855a", "#c98a12", "#c53030"]} height={150} /></div>}
        </Card>

        <Card title="Needs attention" className="lg:col-span-2" action={<Link to="/monitoring" className="text-sm font-medium text-gauge hover:underline">All alerts</Link>}>
          {alerts.data?.length === 0 && <p className="py-6 text-center text-sm text-slate-500">No open alerts. All monitored equipment is within limits.</p>}
          <ul className="divide-y divide-line">
            {alerts.data?.map((a) => (
              <li key={a.id} className="flex items-center justify-between gap-3 py-2.5">
                <div className="min-w-0">
                  <Link to={`/equipment/${a.equipment}`} className="block truncate font-medium text-ink-900 hover:underline">{a.equipment_name}</Link>
                  <p className="text-sm text-slate-600">{pretty(a.metric)} {num(a.value, 1)}{a.unit} · {a.plant_name} · {ago(a.last_seen_at)}</p>
                </div>
                <Badge value={a.severity} />
              </li>
            ))}
          </ul>
          {health.data && (
            <div className="mt-4 border-t border-line pt-3">
              <p className="mb-2 text-sm font-medium text-ink-800">Lowest health score</p>
              <div className="flex flex-wrap gap-2">
                {health.data.lowest.slice(0, 5).map((e: Row) => <Link key={e.id} to={`/equipment/${e.id}`} className="rounded border border-line px-2.5 py-1 text-sm hover:bg-paper">{e.name} <b className="ml-1">{e.health_score}</b></Link>)}
              </div>
            </div>
          )}
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Maintenance cost by type" action={<span className="text-sm text-slate-500">{money(cost.data?.total)} in 6 months</span>}>
          {cost.data ? <StackedBars labels={cost.data.monthly.map((m: Row) => monthLabel(m.month))} series={[
            { label: "Preventive", data: cost.data.monthly.map((m: Row) => m.PREVENTIVE), color: "#1f7a8c" },
            { label: "Corrective", data: cost.data.monthly.map((m: Row) => m.CORRECTIVE), color: "#c98a12" },
            { label: "Emergency", data: cost.data.monthly.map((m: Row) => m.EMERGENCY), color: "#e4572e" }]} /> : <Spinner />}
        </Card>
        <Card title="Downtime hours" action={<span className="text-sm text-slate-500">{num(down.data?.total_hours, 1)} h total</span>}>
          {down.data ? <Lines labels={down.data.monthly.map((m: Row) => monthLabel(m.month))} series={[
            { label: "Incidents", data: down.data.monthly.map((m: Row) => m.incident_hours), color: "#e4572e" },
            { label: "Work orders", data: down.data.monthly.map((m: Row) => m.work_order_hours), color: "#1f7a8c" }]} /> : <Spinner />}
        </Card>
        <Card title="Incidents by type" action={<span className="text-sm text-slate-500">{inc.data?.total ?? 0} incidents · {inc.data?.injuries ?? 0} injuries</span>}>
          {inc.data ? <StackedBars labels={inc.data.monthly.map((m: Row) => monthLabel(m.month))}
            series={["GAS_LEAK", "FIRE", "EXPLOSION", "EQUIPMENT_FAILURE", "NEAR_MISS", "SAFETY_VIOLATION"].map((t) => ({ label: pretty(t), data: inc.data.monthly.map((m: Row) => m[t]) }))} /> : <Spinner />}
        </Card>
        <Card title="Inventory consumption">
          {usage.data ? <StackedBars labels={usage.data.monthly.map((m: Row) => monthLabel(m.month))}
            series={["SPARE_PART", "CHEMICAL", "LUBRICANT", "SAFETY"].map((t) => ({ label: pretty(t), data: usage.data.monthly.map((m: Row) => m[t]) }))} /> : <Spinner />}
        </Card>
        <Card title="Most downtime by equipment (hours)">
          {down.data && <HBars labels={down.data.top_equipment.map((e: Row) => e.equipment)} data={down.data.top_equipment.map((e: Row) => e.hours)} color="#e4572e" />}
        </Card>
        <Card title="Team performance, last 90 days" pad={false}>
          <table className="w-full text-sm">
            <thead className="border-b border-line bg-paper text-left text-slate-600"><tr><th className="px-4 py-2 font-medium">Name</th><th className="px-4 py-2 font-medium">Completed</th><th className="px-4 py-2 font-medium">On time</th><th className="px-4 py-2 font-medium">Labour h</th></tr></thead>
            <tbody>
              {perf.data?.slice(0, 8).map((p) => (
                <tr key={p.user_id} className="border-b border-line last:border-0">
                  <td className="px-4 py-2">{p.name}<span className="ml-2 text-xs text-slate-500">{pretty(p.role)}</span></td>
                  <td className="px-4 py-2">{p.completed}</td>
                  <td className="px-4 py-2"><Badge value={p.on_time_pct >= 80 ? "OK" : "WARNING"} tone={p.on_time_pct >= 80 ? "ok" : "warn"} label={`${p.on_time_pct}%`} /></td>
                  <td className="px-4 py-2">{p.labor_hours}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {perf.data?.length === 0 && <p className="p-6 text-center text-sm text-slate-500">No completed work orders in this period.</p>}
        </Card>
      </div>
    </div>
  );
}
