import { useEffect, useState } from 'react'
import { Users, Building2, Map, CalendarCheck, DollarSign, Clock } from 'lucide-react'
import StatCard from '../../components/common/StatCard'
import Skeleton from '../../components/common/Skeleton'
import { getAdminDashboard } from '../../api/endpoints'

export default function AdminDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getAdminDashboard().then((res) => setData(res.data)).catch(() => setData({}))
  }, [])

  if (!data) return <div className="grid grid-cols-2 md:grid-cols-3 gap-4">{Array.from({length:6}).map((_,i)=><Skeleton key={i} className="h-24"/>)}</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Admin Overview</h1>
      <p className="text-black/50 dark:text-white/50 mb-8">System-wide stats at a glance</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
        <StatCard label="Total Users" value={data.total_users ?? 0} icon={Users} />
        <StatCard label="Total Hotels" value={data.total_hotels ?? 0} icon={Building2} />
        <StatCard label="Tour Operators" value={data.total_tour_operators ?? 0} icon={Map} />
        <StatCard label="Total Bookings" value={data.total_bookings ?? 0} icon={CalendarCheck} />
        <StatCard label="Total Revenue" value={`$${data.total_revenue ?? 0}`} icon={DollarSign} />
        <StatCard label="Pending Approvals" value={data.pending_approvals ?? 0} icon={Clock} />
      </div>

      <div className="bg-white dark:bg-[#0f2422] rounded-2xl p-6 border border-black/5 dark:border-white/10">
        <h3 className="font-semibold mb-4">Top Destinations</h3>
        {data.top_destinations?.length > 0 ? (
          <ul className="space-y-2 text-sm">
            {data.top_destinations.map((d) => (
              <li key={d.destination} className="flex justify-between border-b border-black/5 dark:border-white/10 pb-2">
                <span>{d.destination}</span>
                <span className="text-black/50 dark:text-white/50">{d.count} packages</span>
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-black/40">No data yet.</p>}
      </div>
    </div>
  )
}
