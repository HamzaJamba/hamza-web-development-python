import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import ProductPlate from '../components/ProductPlate'
import { FREE_SHIPPING_FROM, SHIPPING_FEE } from '../lib/format'

const CartCtx = createContext(null)
export const useCart = () => useContext(CartCtx)

const load = () => {
  try { return JSON.parse(localStorage.getItem('mn_cart')) || [] } catch { return [] }
}

export function CartProvider({ children }) {
  const [items, setItems] = useState(load)
  const [open, setOpen] = useState(false)
  const [flights, setFlights] = useState([])
  const [bump, setBump] = useState(0)
  const lastFlight = useRef(0)

  useEffect(() => { localStorage.setItem('mn_cart', JSON.stringify(items)) }, [items])

  const fly = useCallback((product, sourceEl) => {
    const target = document.getElementById('cart-button')
    if (!sourceEl || !target || window.matchMedia('(prefers-reduced-motion: reduce)').matches) { setBump((b) => b + 1); return }
    const from = sourceEl.getBoundingClientRect()
    const to = target.getBoundingClientRect()
    const id = ++lastFlight.current
    setFlights((f) => [...f, { id, product, from, to }])
  }, [])

  const add = useCallback((product, qty = 1, sourceEl = null) => {
    const have = items.find((i) => i.id === product.id)?.qty || 0
    const next = Math.min(have + qty, product.stock, 20)
    if (next <= have) return false // already holding all the stock there is
    const line = {
      id: product.id, slug: product.slug, name: product.name, price: Number(product.price), stock: product.stock,
      hue: product.hue, image_url: product.image_url, category_icon: product.category?.icon,
      vendor: { slug: product.vendor.slug, shop_name: product.vendor.shop_name, awning_primary: product.vendor.awning_primary, awning_secondary: product.vendor.awning_secondary },
      qty: next,
    }
    setItems((prev) => (prev.some((i) => i.id === product.id) ? prev.map((i) => (i.id === product.id ? line : i)) : [...prev, line]))
    fly(product, sourceEl)
    return true
  }, [fly, items])

  const setQty = (id, qty) =>
    setItems((prev) => prev.flatMap((i) => (i.id !== id ? [i] : qty <= 0 ? [] : [{ ...i, qty: Math.min(qty, i.stock, 20) }])))
  const remove = (id) => setItems((prev) => prev.filter((i) => i.id !== id))
  const clear = () => setItems([])

  const value = useMemo(() => {
    const subtotal = items.reduce((s, i) => s + i.price * i.qty, 0)
    const shipping = items.length === 0 || subtotal >= FREE_SHIPPING_FROM ? 0 : SHIPPING_FEE
    const groups = Object.values(
      items.reduce((acc, i) => {
        (acc[i.vendor.slug] ||= { vendor: i.vendor, items: [] }).items.push(i)
        return acc
      }, {}),
    )
    return {
      items, groups, subtotal, shipping, total: subtotal + shipping,
      count: items.reduce((s, i) => s + i.qty, 0), bump,
      open, setOpen, add, setQty, remove, clear,
    }
  }, [items, open, bump, add])

  return (
    <CartCtx.Provider value={value}>
      {children}
      <FlightLayer flights={flights} done={(id) => { setFlights((f) => f.filter((x) => x.id !== id)); setBump((b) => b + 1) }} />
    </CartCtx.Provider>
  )
}

/** The product plate lifts off the page and drops into the cart button. */
function FlightLayer({ flights, done }) {
  return (
    <div className="pointer-events-none fixed inset-0 z-[70]" aria-hidden="true">
      <AnimatePresence>
        {flights.map((f) => {
          const size = 64
          const startX = f.from.left + f.from.width / 2 - size / 2
          const startY = f.from.top + f.from.height / 2 - size / 2
          const endX = f.to.left + f.to.width / 2 - size / 2
          const endY = f.to.top + f.to.height / 2 - size / 2
          return (
            <motion.div
              key={f.id}
              className="absolute overflow-hidden rounded-2xl shadow-xl"
              style={{ left: 0, top: 0, width: size, height: size }}
              initial={{ x: startX, y: startY, scale: 1, opacity: 1 }}
              animate={{ x: endX, y: [startY, Math.min(startY, endY) - 70, endY], scale: 0.28, opacity: 0.9 }}
              transition={{ duration: 0.75, ease: [0.5, 0, 0.2, 1] }}
              onAnimationComplete={() => done(f.id)}
            >
              <ProductPlate product={{ ...f.product, category_icon: f.product.category?.icon }} iconSize={26} />
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
