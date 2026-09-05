import { useEffect, useState } from 'react'
import { Plane, History, DollarSign } from 'lucide-react'
import StatCard from '../../components/common/StatCard'
import Skeleton from '../../components/common/Skeleton'
import { getCustomerDashboard } from '../../api/endpoints'

export default function CustomerDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getCustomerDashboard().then((res) => setData(res.data)).catch(() => setData({}))
  }, [])

  if (!data) return <div className="grid grid-cols-2 md:grid-cols-3 gap-4">{Array.from({length:3}).map((_,i)=><Skeleton key={i} className="h-24"/>)}</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Welcome back 👋</h1>
      <p className="text-black/50 dark:text-white/50 mb-8">Here's a summary of your trips</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard label="Upcoming Trips" value={data.upcoming_trips ?? 0} icon={Plane} />
        <StatCard label="Booking History" value={data.booking_history ?? 0} icon={History} />
        <StatCard label="Total Spent" value={`$${data.total_spent ?? 0}`} icon={DollarSign} />
      </div>
    </div>
  )
}
