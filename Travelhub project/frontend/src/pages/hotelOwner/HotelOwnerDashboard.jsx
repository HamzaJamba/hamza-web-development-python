import { useEffect, useState } from 'react'
import { BedDouble, CalendarCheck, DollarSign, Star } from 'lucide-react'
import StatCard from '../../components/common/StatCard'
import Skeleton from '../../components/common/Skeleton'
import { getHotelOwnerDashboard } from '../../api/endpoints'

export default function HotelOwnerDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getHotelOwnerDashboard().then((res) => setData(res.data)).catch(() => setData({}))
  }, [])

  if (!data) return <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{Array.from({length:4}).map((_,i)=><Skeleton key={i} className="h-24"/>)}</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Hotel Owner Overview</h1>
      <p className="text-black/50 dark:text-white/50 mb-8">Your property performance</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Rooms" value={data.total_rooms ?? 0} icon={BedDouble} />
        <StatCard label="Total Bookings" value={data.total_bookings ?? 0} icon={CalendarCheck} />
        <StatCard label="Monthly Revenue" value={`$${data.monthly_revenue ?? 0}`} icon={DollarSign} />
        <StatCard label="Average Rating" value={(data.average_rating ?? 0).toFixed?.(1) ?? data.average_rating} icon={Star} />
      </div>
    </div>
  )
}
