import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Banknote, CreditCard, Lock } from 'lucide-react'
import api, { readError } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import Field, { inputCls } from '../components/Field'
import ProductPlate from '../components/ProductPlate'
import { StallDot } from '../components/Awning'
import { pkr } from '../lib/format'

export default function Checkout() {
  const { user } = useAuth()
  const { items, groups, subtotal, shipping, total, clear, setOpen } = useCart()
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: user?.full_name || '', phone: user?.phone || '', address: '', city: '', payment_method: 'cod', card_number: '' })
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-xl px-4 py-24 text-center">
        <h1 className="font-display text-2xl font-bold">Your cart is empty</h1>
        <p className="mt-3 text-muted">Add something from any stall, then come back here to check out.</p>
        <Link to="/shop" className="mt-6 inline-block rounded-full bg-lapis px-6 py-3 text-sm font-bold text-white">Browse the shop</Link>
      </div>
    )
  }

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErrors({}); setMessage('')
    try {
      const { data } = await api.post('/orders/checkout/', {
        ...form,
        card_number: form.payment_method === 'card' ? form.card_number : undefined,
        items: items.map((i) => ({ product: i.id, quantity: i.qty })),
      })
      clear()
      navigate(`/orders/${data.id}?placed=1`, { replace: true })
    } catch (err) {
      const { fields, message } = readError(err)
      setErrors(fields)
      setMessage(err?.response?.status === 402 ? `Payment failed. ${message}` : fields.items || message)
    } finally { setBusy(false) }
  }

  const method = (value, Icon, title, text) => (
    <label className={`flex cursor-pointer items-start gap-3 rounded-2xl border-2 p-4 transition-colors ${form.payment_method === value ? 'border-lapis bg-lapis/5' : 'border-line bg-white hover:border-midnight/40'}`}>
      <input type="radio" name="pay" className="mt-1 accent-lapis" checked={form.payment_method === value} onChange={() => setForm({ ...form, payment_method: value })} />
      <span><span className="flex items-center gap-2 font-bold"><Icon size={17} /> {title}</span><span className="mt-0.5 block text-sm text-muted">{text}</span></span>
    </label>
  )

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-2xl font-bold md:text-3xl">Checkout</h1>
      <form onSubmit={submit} className="mt-8 grid gap-10 lg:grid-cols-[1fr_400px]" noValidate>
        <div className="space-y-9">
          <section>
            <h2 className="font-display text-base font-semibold">Where should the parcels go?</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label="Full name" error={errors.full_name}><input className={inputCls} value={form.full_name} onChange={set('full_name')} autoComplete="name" required /></Field>
              <Field label="Phone" error={errors.phone}><input className={inputCls} value={form.phone} onChange={set('phone')} autoComplete="tel" placeholder="0300 1234567" required /></Field>
              <Field label="Street address" error={errors.address} className="sm:col-span-2"><input className={inputCls} value={form.address} onChange={set('address')} autoComplete="street-address" placeholder="House, street, area" required /></Field>
              <Field label="City" error={errors.city}><input className={inputCls} value={form.city} onChange={set('city')} autoComplete="address-level2" required /></Field>
            </div>
          </section>

          <section>
            <h2 className="font-display text-base font-semibold">How would you like to pay?</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {method('cod', Banknote, 'Cash on delivery', 'Pay the rider when each parcel arrives.')}
              {method('card', CreditCard, 'Card', 'Charged once, when you place the order.')}
            </div>
            {form.payment_method === 'card' && (
              <div className="mt-4 rounded-2xl border border-line bg-white p-5">
                <Field label="Card number" error={errors.card_number} hint="Test cards: 4242 4242 4242 4242 succeeds, 4000 0000 0000 0002 is declined.">
                  <input className={inputCls} inputMode="numeric" value={form.card_number} onChange={set('card_number')} placeholder="4242 4242 4242 4242" autoComplete="cc-number" />
                </Field>
                <p className="mt-3 flex items-center gap-1.5 text-xs text-muted"><Lock size={12} /> This is a demo. No real payment is taken and the number is not stored.</p>
              </div>
            )}
          </section>
        </div>

        <aside className="h-fit rounded-3xl border border-line bg-white p-6 lg:sticky lg:top-24" aria-label="Order summary">
          <h2 className="font-display text-base font-semibold">Your order</h2>
          <div className="mt-4 space-y-5">
            {groups.map(({ vendor, items: lines }) => (
              <div key={vendor.slug}>
                <p className="flex items-center gap-2 text-xs font-bold text-muted"><StallDot primary={vendor.awning_primary} secondary={vendor.awning_secondary} /> Parcel from {vendor.shop_name}</p>
                <ul className="mt-2 space-y-2.5">
                  {lines.map((l) => (
                    <li key={l.id} className="flex items-center gap-3">
                      <div className="h-12 w-12 shrink-0 overflow-hidden rounded-lg"><ProductPlate product={l} iconSize={20} /></div>
                      <p className="min-w-0 flex-1 truncate text-sm font-semibold">{l.name} <span className="text-muted">× {l.qty}</span></p>
                      <p className="text-sm font-bold">{pkr(l.price * l.qty)}</p>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <dl className="mt-6 space-y-1.5 border-t border-line pt-4 text-sm">
            <div className="flex justify-between"><dt className="text-muted">Subtotal</dt><dd className="font-semibold">{pkr(subtotal)}</dd></div>
            <div className="flex justify-between"><dt className="text-muted">Shipping</dt><dd className="font-semibold">{shipping ? pkr(shipping) : 'Free'}</dd></div>
            <div className="flex justify-between pt-2 text-base"><dt className="font-bold">Total</dt><dd className="font-display font-bold">{pkr(total)}</dd></div>
          </dl>
          {message && <p className="mt-4 rounded-xl bg-gulal/10 px-4 py-3 text-sm font-semibold text-gulal" role="alert">{message}</p>}
          <button disabled={busy} className="mt-5 w-full rounded-full bg-lapis py-3.5 text-[15px] font-bold text-white hover:bg-lapis-dark disabled:opacity-60">
            {busy ? 'Placing your order…' : `Place order for ${pkr(total)}`}
          </button>
          <button type="button" onClick={() => setOpen(true)} className="mt-3 w-full text-center text-sm font-bold text-lapis hover:underline">Edit cart</button>
        </aside>
      </form>
    </div>
  )
}
