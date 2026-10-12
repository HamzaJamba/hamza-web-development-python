import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { AlertTriangle, Wrench, Radio, TrendingUp } from 'lucide-react'
import useFetch from '../lib/useFetch'
import OEEGauge from '../components/OEEGauge'
import { useAuth } from '../context/AuthContext'

function StatCard({ label, value, icon: Icon, accent = 'text-cyan', delay = 0 }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: 0.35 }}
      className="rounded-2xl border border-steel-700 bg-steel-900 p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wide text-mist">{label}</span>
        {Icon && <Icon size={16} className={accent} />}
      </div>
      <p className="mt-2 font-display text-3xl font-bold">{value}</p>
    </motion.div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const { data, loading } = useFetch('/dashboard/overview/')

  if (loading || !data) {
    return <div className="mx-auto max-w-7xl px-4 py-16 text-center text-sm text-mist sm:px-6">Loading plant status…</div>
  }

  const statusEntries = Object.entries(data.status_counts || {})
  const woPriority = Object.entries(data.work_orders_by_priority || {})

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-display text-2xl font-bold md:text-3xl">Plant Overview</h1>
        <p className="mt-1 text-sm text-mist">Welcome back, {user?.full_name || user?.email}. Here's what's happening on the floor right now.</p>
      </motion.div>

      <div className="mt-8 grid gap-5 lg:grid-cols-[auto_1fr]">
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
          className="flex items-center justify-center rounded-2xl border border-steel-700 bg-steel-900 p-8">
          <OEEGauge value={data.oee_percent} />
        </motion.div>

        <div className="grid grid-cols-2 gap-5 md:grid-cols-4">
          <StatCard label="Total Machines" value={data.total_machines} icon={Radio} delay={0.05} />
          <StatCard label="Availability" value={`${data.availability_percent}%`} icon={TrendingUp} accent="text-emerald" delay={0.1} />
          <StatCard label="Anomalies (24h)" value={data.anomalies_24h} icon={AlertTriangle} accent="text-rose" delay={0.15} />
          <StatCard label="Open Work Orders" value={data.open_work_orders} icon={Wrench} accent="text-amber" delay={0.2} />
        </div>
      </div>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="rounded-2xl border border-steel-700 bg-steel-900 p-6">
          <h3 className="font-display text-lg font-bold">Machine Status</h3>
          <div className="mt-4 space-y-3">
            {statusEntries.map(([status, count]) => {
              const pct = Math.round((count / data.total_machines) * 100)
              const colorMap = { running: 'bg-emerald', idle: 'bg-mist', maintenance: 'bg-amber', down: 'bg-rose' }
              return (
                <div key={status}>
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span className="capitalize font-semibold text-chalk">{status}</span>
                    <span className="text-mist">{count} machines</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-steel-800">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 0.8, delay: 0.3 }}
                      className={`h-full rounded-full ${colorMap[status] || 'bg-cyan'}`} />
                  </div>
                </div>
              )
            })}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="rounded-2xl border border-steel-700 bg-steel-900 p-6">
          <h3 className="font-display text-lg font-bold">Work Orders by Priority</h3>
          {woPriority.length === 0 ? (
            <p className="mt-4 text-sm text-mist">No open work orders — floor is clear.</p>
          ) : (
            <div className="mt-4 space-y-3">
              {woPriority.map(([priority, count]) => {
                const colorMap = { low: 'bg-steel-500', medium: 'bg-cyan', high: 'bg-amber', critical: 'bg-rose' }
                return (
                  <div key={priority} className="flex items-center justify-between rounded-lg border border-steel-700 px-3.5 py-2.5">
                    <span className="text-sm font-semibold capitalize">{priority}</span>
                    <span className={`flex h-6 min-w-6 items-center justify-center rounded-full px-2 text-xs font-bold text-steel-950 ${colorMap[priority]}`}>{count}</span>
                  </div>
                )
              })}
            </div>
          )}
          <Link to="/work-orders" className="mt-4 inline-block text-sm font-semibold text-cyan hover:underline">View all work orders →</Link>
        </motion.div>
      </div>

      {data.critical_machines_down > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
          className="mt-6 flex items-center gap-3 rounded-2xl border border-rose-dim/50 bg-rose-dim/10 p-5">
          <AlertTriangle className="shrink-0 text-rose animate-pulse-ring rounded-full" size={22} />
          <p className="text-sm font-semibold text-rose">
            {data.critical_machines_down} critical machine{data.critical_machines_down > 1 ? 's are' : ' is'} currently down — immediate attention needed.
          </p>
        </motion.div>
      )}
    </div>
  )
}
