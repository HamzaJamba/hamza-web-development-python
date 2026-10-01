import { useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import api, { readError } from '../lib/api'
import useFetch from '../lib/useFetch'
import { useToast } from '../context/ToastContext'
import Awning from '../components/Awning'
import ProductPlate from '../components/ProductPlate'
import { STATUS_STYLE } from './Orders'
import { pkr, shortDate, ORDER_STEPS, STEP_LABEL } from '../lib/format'

export default function OrderDetail() {
  const { id } = useParams()
  const [sp] = useSearchParams()
  const { data: o, loading, error, reload } = useFetch(`/orders/${id}/`)
  const toast = useToast()
  const [busy, setBusy] = useState(false)

  if (error) return <div className="mx-auto max-w-xl px-4 py-24 text-center"><h1 className="font-display text-2xl font-bold">Order not found</h1><Link to="/orders" className="mt-6 inline-block font-bold text-lapis">Back to my orders</Link></div>
  if (loading || !o) return <p className="p-16 text-center text-sm text-muted">Loading…</p>

  const parcels = Object.values(o.items.reduce((acc, i) => { (acc[i.vendor_slug] ||= { name: i.vendor_name, p: i.awning_primary, s: i.awning_secondary, items: [] }).items.push(i); return acc }, {}))
  const canCancel = o.items.every((i) => i.status === 'pending') && o.status !== 'cancelled'

  const cancel = async () => {
    if (!window.confirm('Cancel this whole order? Any payment will be refunded.')) return
    setBusy(true)
    try { await api.post(`/orders/${o.id}/cancel/`); toast('Order cancelled'); reload() } catch (e) { toast(readError(e).message, 'error') } finally { setBusy(false) }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      {sp.get('placed') && (
        <div className="mb-10 flex items-center gap-5 rounded-3xl bg-midnight p-6 text-white sm:p-8">
          <motion.svg viewBox="0 0 52 52" className="h-16 w-16 shrink-0" aria-hidden="true">
            <motion.circle cx="26" cy="26" r="24" fill="none" stroke="#C4EA6B" strokeWidth="3" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.6 }} />
            <motion.path d="M15 27l8 8 15-17" fill="none" stroke="#C4EA6B" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.45, delay: 0.5 }} />
          </motion.svg>
          <div>
            <h2 className="font-display text-xl font-bold">Order placed</h2>
            <p className="mt-1 text-white/70">Each stall has been told to pack its parcel. You can follow them below.</p>
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold">{o.number}</h1>
          <p className="mt-1 text-sm text-muted">Placed on {shortDate(o.created_at)}</p>
        </div>
        <span className={`rounded-full px-4 py-1.5 text-sm font-bold ${STATUS_STYLE[o.status]}`}>{o.status_label}</span>
      </div>

      <div className="mt-8 space-y-6">
        {parcels.map((p) => {
          const live = p.items.filter((i) => i.status !== 'cancelled')
          const stage = live.length ? Math.min(...live.map((i) => ORDER_STEPS.indexOf(i.status))) : -1
          return (
            <section key={p.name} className="overflow-hidden rounded-3xl border border-line bg-white">
              <Awning primary={p.p} secondary={p.s} stripes={20} className="-mb-4" />
              <div className="px-6 pb-6 pt-6">
                <h2 className="font-display text-base font-semibold">Parcel from {p.name}</h2>
                {stage >= 0 ? (
                  <ol className="mt-5 grid grid-cols-4 gap-2" aria-label="Parcel progress">
                    {ORDER_STEPS.map((s, i) => (
                      <li key={s} className="text-center">
                        <span className={`mx-auto grid h-8 w-8 place-items-center rounded-full text-xs font-bold ${i <= stage ? 'bg-lapis text-white' : 'bg-mist text-muted'}`}>{i <= stage ? <Check size={15} /> : i + 1}</span>
                        <span className={`mt-1.5 block text-xs font-semibold ${i <= stage ? '' : 'text-muted'}`}>{STEP_LABEL[s]}</span>
                      </li>
                    ))}
                  </ol>
                ) : <p className="mt-3 text-sm font-semibold text-muted">This parcel was cancelled.</p>}
                <ul className="mt-6 divide-y divide-line">
                  {p.items.map((i) => (
                    <li key={i.id} className="flex items-center gap-4 py-3">
                      <div className="h-14 w-14 shrink-0 overflow-hidden rounded-xl"><ProductPlate product={{ ...i, id: i.product, name: i.product_name }} iconSize={22} /></div>
                      <div className="min-w-0 flex-1">
                        {i.product_slug ? <Link to={`/product/${i.product_slug}`} className="font-semibold hover:text-lapis">{i.product_name}</Link> : <span className="font-semibold">{i.product_name}</span>}
                        <p className="text-sm text-muted">{pkr(i.unit_price)} × {i.quantity}</p>
                      </div>
                      <p className="font-bold">{pkr(i.line_total)}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </section>
          )
        })}
      </div>

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        <section className="rounded-3xl border border-line bg-white p-6">
          <h2 className="font-display text-base font-semibold">Delivery</h2>
          <p className="mt-3 text-sm leading-relaxed">{o.full_name}<br />{o.address}<br />{o.city}<br />{o.phone}</p>
        </section>
        <section className="rounded-3xl border border-line bg-white p-6">
          <h2 className="font-display text-base font-semibold">Payment</h2>
          <p className="mt-3 text-sm text-muted">{o.payment_method === 'card' ? 'Card' : 'Cash on delivery'}, {o.payment_status}</p>
          <dl className="mt-3 space-y-1.5 text-sm">
            <div className="flex justify-between"><dt className="text-muted">Subtotal</dt><dd className="font-semibold">{pkr(o.subtotal)}</dd></div>
            <div className="flex justify-between"><dt className="text-muted">Shipping</dt><dd className="font-semibold">{Number(o.shipping_fee) ? pkr(o.shipping_fee) : 'Free'}</dd></div>
            <div className="flex justify-between border-t border-line pt-2 text-base"><dt className="font-bold">Total</dt><dd className="font-display font-bold">{pkr(o.total)}</dd></div>
          </dl>
        </section>
      </div>

      {canCancel && <button onClick={cancel} disabled={busy} className="mt-8 rounded-full border-2 border-gulal px-6 py-2.5 text-sm font-bold text-gulal hover:bg-gulal hover:text-white disabled:opacity-50">Cancel order</button>}
    </div>
  )
}
