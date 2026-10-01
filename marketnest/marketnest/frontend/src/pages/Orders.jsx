import { Link } from 'react-router-dom'
import useFetch from '../lib/useFetch'
import ProductPlate from '../components/ProductPlate'
import { pkr, shortDate } from '../lib/format'

export const STATUS_STYLE = {
  placed: 'bg-sun text-midnight', processing: 'bg-sun text-midnight', shipped: 'bg-lapis text-white',
  delivered: 'bg-pistachio text-midnight', cancelled: 'bg-mist text-muted',
}

export default function Orders() {
  const { data, loading } = useFetch('/orders/')
  const orders = data?.results || []
  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-2xl font-bold md:text-3xl">My orders</h1>
      {loading ? (
        <p className="mt-8 text-sm text-muted">Loading…</p>
      ) : orders.length === 0 ? (
        <div className="mt-8 rounded-2xl border border-dashed border-line bg-white/60 p-12 text-center">
          <p className="font-display text-lg font-semibold">No orders yet</p>
          <p className="mt-2 text-sm text-muted">When you place an order, you can follow each stall’s parcel here.</p>
          <Link to="/shop" className="mt-5 inline-block rounded-full bg-lapis px-6 py-2.5 text-sm font-bold text-white">Start shopping</Link>
        </div>
      ) : (
        <ul className="mt-8 space-y-4">
          {orders.map((o) => (
            <li key={o.id}>
              <Link to={`/orders/${o.id}`} className="flex flex-wrap items-center gap-x-6 gap-y-3 rounded-2xl border border-line bg-white p-5 transition-colors hover:border-midnight">
                <div className="flex -space-x-3">
                  {o.items.slice(0, 3).map((i) => <div key={i.id} className="h-12 w-12 overflow-hidden rounded-xl ring-2 ring-white"><ProductPlate product={{ ...i, id: i.product, name: i.product_name }} iconSize={20} /></div>)}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-display text-sm font-semibold">{o.number}</p>
                  <p className="text-sm text-muted">{shortDate(o.created_at)}, {o.items.length} {o.items.length === 1 ? 'item' : 'items'}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-bold ${STATUS_STYLE[o.status]}`}>{o.status_label}</span>
                <p className="font-display text-sm font-bold">{pkr(o.total)}</p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
