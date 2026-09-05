import { useEffect, useState } from 'react'
import { Map, CalendarCheck, DollarSign, Plane } from 'lucide-react'
import StatCard from '../../components/common/StatCard'
import Skeleton from '../../components/common/Skeleton'
import { getTourOperatorDashboard } from '../../api/endpoints'

export default function TourOperatorDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getTourOperatorDashboard().then((res) => setData(res.data)).catch(() => setData({}))
  }, [])

  if (!data) return <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{Array.from({length:4}).map((_,i)=><Skeleton key={i} className="h-24"/>)}</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Tour Operator Overview</h1>
      <p className="text-black/50 dark:text-white/50 mb-8">Your packages performance</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Packages" value={data.total_packages ?? 0} icon={Map} />
        <StatCard label="Total Bookings" value={data.total_bookings ?? 0} icon={CalendarCheck} />
        <StatCard label="Revenue" value={`$${data.revenue ?? 0}`} icon={DollarSign} />
        <StatCard label="Upcoming Tours" value={data.upcoming_tours ?? 0} icon={Plane} />
      </div>
    </div>
  )
}
