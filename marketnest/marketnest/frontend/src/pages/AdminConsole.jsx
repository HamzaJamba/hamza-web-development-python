import { useState } from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, Store, TrendingUp, Users, ScrollText, Check } from 'lucide-react'
import useFetch from '../lib/useFetch'
import api, { readError } from '../lib/api'
import { useToast } from '../context/ToastContext'
import { pkr, shortDate } from '../lib/format'

const TABS = [
  { id: 'overview', label: 'Overview', icon: TrendingUp },
  { id: 'vendors', label: 'Pending stalls', icon: Store },
  { id: 'audit', label: 'Audit log', icon: ScrollText },
]

export default function AdminConsole() {
  const [tab, setTab] = useState('overview')
  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="flex items-center gap-2.5">
        <ShieldCheck className="text-lapis" size={26} />
        <h1 className="font-display text-2xl font-bold md:text-3xl">Admin console</h1>
      </div>

      <div className="mt-6 flex gap-1.5 rounded-full border-2 border-line bg-white p-1.5">
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-full py-2.5 text-sm font-bold transition-colors ${tab === t.id ? 'bg-midnight text-white' : 'text-muted hover:text-midnight'}`}>
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </div>

      <div className="mt-8">
        {tab === 'overview' && <AdminOverview />}
        {tab === 'vendors' && <PendingVendors />}
        {tab === 'audit' && <AuditLog />}
      </div>
    </div>
  )
}

function StatCard({ label, value, icon: Icon }) {
  return (
    <div className="rounded-2xl border border-line bg-white p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wide text-muted">{label}</span>
        {Icon && <Icon size={16} className="text-lapis" />}
      </div>
      <p className="mt-2 font-display text-2xl font-bold">{value}</p>
    </div>
  )
}

function AdminOverview() {
  const { data, loading } = useFetch('/dashboard/admin/')
  if (loading) return <p className="text-sm text-muted">Loading…</p>
  if (!data) return null
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="GMV" value={pkr(data.gmv)} icon={TrendingUp} />
        <StatCard label="Commission earned" value={pkr(data.commission_earned)} />
        <StatCard label="Orders" value={data.orders} />
        <StatCard label="Active stalls" value={data.vendors} icon={Store} />
        <StatCard label="Pending stalls" value={data.pending_vendors} />
        <StatCard label="Customers" value={data.customers} icon={Users} />
      </div>
      <div className="rounded-2xl border border-line bg-white p-6">
        <h3 className="font-display text-lg font-bold">Top stalls by revenue</h3>
        <ul className="mt-4 space-y-3">
          {data.top_vendors.map((v) => (
            <li key={v.shop_name} className="flex items-center justify-between text-sm">
              <span className="font-semibold">{v.shop_name}</span>
              <span className="text-muted">{pkr(v.revenue)}</span>
            </li>
          ))}
          {data.top_vendors.length === 0 && <p className="text-sm text-muted">No sales yet.</p>}
        </ul>
      </div>
    </div>
  )
}

function PendingVendors() {
  const { data, loading, reload } = useFetch('/vendors/pending/')
  const toast = useToast()
  const vendors = data || []

  const approve = async (slug) => {
    try {
      await api.post(`/vendors/${slug}/approve/`)
      toast('Stall approved')
      reload()
    } catch (err) {
      toast(readError(err).message, 'error')
    }
  }

  if (loading) return <p className="text-sm text-muted">Loading…</p>
  if (vendors.length === 0) return <p className="text-sm text-muted">No pending applications.</p>

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {vendors.map((v) => (
        <motion.div key={v.id} layout className="rounded-2xl border border-line bg-white p-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-display text-lg font-bold">{v.shop_name}</p>
              <p className="text-sm text-muted">{v.city} · {v.tagline}</p>
            </div>
            <button onClick={() => approve(v.slug)} className="flex shrink-0 items-center gap-1.5 rounded-full bg-lapis px-4 py-2 text-xs font-bold text-white hover:bg-lapis-dark">
              <Check size={14} /> Approve
            </button>
          </div>
          <p className="mt-3 text-sm leading-relaxed text-muted">{v.description}</p>
        </motion.div>
      ))}
    </div>
  )
}

function AuditLog() {
  const { data, loading } = useFetch('/audit/logs/')
  const logs = data?.results || data || []
  if (loading) return <p className="text-sm text-muted">Loading…</p>
  return (
    <div className="overflow-x-auto rounded-2xl border border-line bg-white">
      <table className="w-full text-sm">
        <thead className="border-b border-line bg-mist text-left text-xs font-bold uppercase tracking-wide text-muted">
          <tr>
            <th className="px-4 py-3">When</th>
            <th className="px-4 py-3">Who</th>
            <th className="px-4 py-3">Action</th>
            <th className="px-4 py-3">Model</th>
            <th className="px-4 py-3">Details</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((l) => (
            <tr key={l.id} className="border-b border-line last:border-0">
              <td className="px-4 py-3 text-muted">{shortDate(l.timestamp)}</td>
              <td className="px-4 py-3">{l.user_email || 'system'}</td>
              <td className="px-4 py-3"><span className="rounded-full bg-mist px-2.5 py-0.5 text-xs font-bold uppercase">{l.action}</span></td>
              <td className="px-4 py-3">{l.model_name}</td>
              <td className="px-4 py-3 text-muted">{l.object_repr}</td>
            </tr>
          ))}
          {logs.length === 0 && (
            <tr><td colSpan={5} className="px-4 py-8 text-center text-muted">No activity logged yet.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
