import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { X, Minus, Plus, Trash2, ShoppingBag } from 'lucide-react'
import { useCart } from '../context/CartContext'
import Awning from './Awning'
import ProductPlate from './ProductPlate'
import { pkr, FREE_SHIPPING_FROM } from '../lib/format'

export default function CartDrawer() {
  const { open, setOpen, groups, items, subtotal, shipping, total, setQty, remove } = useCart()
  const navigate = useNavigate()
  const panel = useRef(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('keydown', onKey)
    panel.current?.focus()
    return () => document.removeEventListener('keydown', onKey)
  }, [open, setOpen])

  const toFree = Math.max(0, FREE_SHIPPING_FROM - subtotal)
  const progress = Math.min(100, (subtotal / FREE_SHIPPING_FROM) * 100)

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-[60] bg-midnight/40" onClick={() => setOpen(false)}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          />
          <motion.aside
            ref={panel} tabIndex={-1} role="dialog" aria-modal="true" aria-label="Your cart"
            className="fixed inset-y-0 right-0 z-[65] flex w-full max-w-md flex-col bg-chalk shadow-2xl outline-none"
            initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 380, damping: 40 }}
          >
            <div className="flex items-center justify-between border-b border-line px-5 py-4">
              <h2 className="font-display text-base font-semibold">Your cart</h2>
              <button onClick={() => setOpen(false)} className="grid h-9 w-9 place-items-center rounded-full hover:bg-mist" aria-label="Close cart"><X size={19} /></button>
            </div>

            {items.length === 0 ? (
              <div className="grid flex-1 place-items-center px-8 text-center">
                <div>
                  <span className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-mist"><ShoppingBag size={26} className="text-muted" /></span>
                  <p className="mt-4 font-semibold">Your cart is empty</p>
                  <p className="mt-1 text-sm text-muted">Add something from any stall. They all check out together.</p>
                  <button onClick={() => { setOpen(false); navigate('/shop') }} className="mt-5 rounded-full bg-lapis px-6 py-2.5 text-sm font-bold text-white hover:bg-lapis-dark">Browse the shop</button>
                </div>
              </div>
            ) : (
              <>
                <div className="flex-1 space-y-6 overflow-y-auto px-5 py-5">
                  {groups.map(({ vendor, items: lines }) => (
                    <section key={vendor.slug} aria-label={`Parcel from ${vendor.shop_name}`}>
                      <div className="overflow-hidden rounded-t-xl">
                        <Awning primary={vendor.awning_primary} secondary={vendor.awning_secondary} stripes={14} className="-mb-3" />
                      </div>
                      <div className="rounded-b-2xl border border-t-0 border-line bg-white px-4 pb-2 pt-4">
                        <p className="text-xs font-semibold text-muted">One parcel from</p>
                        <p className="font-display text-sm font-semibold">{vendor.shop_name}</p>
                        <ul className="mt-2 divide-y divide-line">
                          {lines.map((l) => (
                            <li key={l.id} className="flex gap-3 py-3">
                              <div className="h-16 w-16 shrink-0 overflow-hidden rounded-xl"><ProductPlate product={{ ...l, id: l.id }} iconSize={24} /></div>
                              <div className="min-w-0 flex-1">
                                <p className="line-clamp-2 text-sm font-semibold leading-snug">{l.name}</p>
                                <p className="mt-0.5 text-sm text-muted">{pkr(l.price)}</p>
                                <div className="mt-2 flex items-center justify-between">
                                  <div className="inline-flex items-center rounded-full border-2 border-line">
                                    <button onClick={() => setQty(l.id, l.qty - 1)} className="grid h-8 w-8 place-items-center rounded-full hover:bg-mist" aria-label={`Fewer ${l.name}`}><Minus size={14} /></button>
                                    <span className="w-7 text-center text-sm font-bold" aria-live="polite">{l.qty}</span>
                                    <button onClick={() => setQty(l.id, l.qty + 1)} disabled={l.qty >= l.stock} className="grid h-8 w-8 place-items-center rounded-full hover:bg-mist disabled:opacity-30" aria-label={`More ${l.name}`}><Plus size={14} /></button>
                                  </div>
                                  <button onClick={() => remove(l.id)} className="grid h-8 w-8 place-items-center rounded-full text-muted hover:bg-mist hover:text-gulal" aria-label={`Remove ${l.name}`}><Trash2 size={15} /></button>
                                </div>
                              </div>
                              <p className="text-sm font-bold">{pkr(l.price * l.qty)}</p>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </section>
                  ))}
                </div>

                <div className="border-t border-line bg-white px-5 py-4">
                  <p className="text-xs font-semibold text-muted">
                    {toFree > 0 ? `Add ${pkr(toFree)} more for free shipping.` : 'You have free shipping.'}
                  </p>
                  <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-mist">
                    <motion.div className="h-full rounded-full bg-pistachio" initial={false} animate={{ width: `${progress}%` }} transition={{ type: 'spring', stiffness: 200, damping: 30 }} />
                  </div>
                  <dl className="mt-3 space-y-1 text-sm">
                    <div className="flex justify-between"><dt className="text-muted">Subtotal</dt><dd className="font-semibold">{pkr(subtotal)}</dd></div>
                    <div className="flex justify-between"><dt className="text-muted">Shipping</dt><dd className="font-semibold">{shipping ? pkr(shipping) : 'Free'}</dd></div>
                    <div className="flex justify-between pt-1 text-base"><dt className="font-bold">Total</dt><dd className="font-display font-bold">{pkr(total)}</dd></div>
                  </dl>
                  <button onClick={() => { setOpen(false); navigate('/checkout') }} className="mt-4 w-full rounded-full bg-lapis py-3 text-sm font-bold text-white hover:bg-lapis-dark">
                    Go to checkout
                  </button>
                </div>
              </>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
