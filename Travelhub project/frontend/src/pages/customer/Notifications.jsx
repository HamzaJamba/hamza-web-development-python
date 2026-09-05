import { useEffect, useState } from 'react'
import { Bell } from 'lucide-react'
import { listNotifications } from '../../api/endpoints'
import Skeleton from '../../components/common/Skeleton'

export default function Notifications() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listNotifications().then((res) => setItems(res.data.results || res.data || [])).finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-2xl font-bold mb-1 flex items-center gap-2"><Bell /> Notifications</h1>
      <p className="text-black/50 dark:text-white/50 mb-8">Booking & payment updates</p>

      {loading ? (
        <div className="space-y-3">{Array.from({length:4}).map((_,i)=><Skeleton key={i} className="h-16"/>)}</div>
      ) : items.length > 0 ? (
        <div className="space-y-3">
          {items.map((n) => (
            <div key={n.id} className={`p-4 rounded-xl border ${n.is_read ? 'border-black/5 dark:border-white/10' : 'border-[var(--color-primary)]/40 bg-[var(--color-primary)]/5'}`}>
              <p className="font-medium text-sm">{n.title}</p>
              <p className="text-xs text-black/50 dark:text-white/50 mt-1">{n.message}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-black/40">No notifications yet.</p>
      )}
    </div>
  )
}
