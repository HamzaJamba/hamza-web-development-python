import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { LayoutDashboard, Package, ListOrdered, Plus, Pencil, X, TrendingUp, TriangleAlert } from 'lucide-react'
import useFetch from '../lib/useFetch'
import api, { readError } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { pkr, shortDate } from '../lib/format'
import ProductPlate from '../components/ProductPlate'
import Field, { inputCls } from '../components/Field'

const TABS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'products', label: 'Products', icon: Package },
  { id: 'orders', label: 'Orders', icon: ListOrdered },
]

export default function VendorDashboard() {
  const { stall } = useAuth()
  const [tab, setTab] = useState('overview')

  if (stall && !stall.is_approved) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6">
        <TriangleAlert className="mx-auto text-sun" size={44} />
        <h1 className="mt-4 font-display text-2xl font-bold">Application under review</h1>
        <p className="mt-3 text-muted">An admin needs to approve {stall.shop_name} before you can start selling. This usually doesn't take long.</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold md:text-3xl">{stall?.shop_name}</h1>
          <p className="mt-1 text-sm text-muted">{stall?.city} · {stall?.commission_rate}% commission</p>
        </div>
      </div>

      <div className="mt-6 flex gap-1.5 rounded-full border-2 border-line bg-white p-1.5">
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-full py-2.5 text-sm font-bold transition-colors ${tab === t.id ? 'bg-midnight text-white' : 'text-muted hover:text-midnight'}`}>
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </div>

      <div className="mt-8">
        {tab === 'overview' && <Overview />}
        {tab === 'products' && <Products />}
        {tab === 'orders' && <VendorOrders />}
      </div>
    </div>
  )
}

function StatCard({ label, value, icon: Icon, accent = 'text-midnight' }) {
  return (
    <div className="rounded-2xl border border-line bg-white p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wide text-muted">{label}</span>
        {Icon && <Icon size={16} className={accent} />}
      </div>
      <p className="mt-2 font-display text-2xl font-bold">{value}</p>
    </div>
  )
}

function Overview() {
  const { data, loading } = useFetch('/dashboard/vendor/')
  if (loading) return <p className="text-sm text-muted">Loading…</p>
  if (!data) return null
  const maxRev = Math.max(1, ...data.daily.map((d) => d.revenue))

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Revenue" value={pkr(data.revenue)} icon={TrendingUp} accent="text-lapis" />
        <StatCard label="Net (after commission)" value={pkr(data.net)} />
        <StatCard label="Orders" value={data.orders} />
        <StatCard label="Waiting to pack" value={data.waiting} accent="text-gulal" />
      </div>

      <div className="rounded-2xl border border-line bg-white p-6">
        <h3 className="font-display text-lg font-bold">Last 14 days</h3>
        <div className="mt-6 flex h-40 items-end gap-1.5">
          {data.daily.map((d, i) => (
            <motion.div key={d.date} initial={{ height: 0 }} animate={{ height: `${Math.max(4, (d.revenue / maxRev) * 100)}%` }}
              transition={{ delay: i * 0.02, duration: 0.4 }}
              className="group relative flex-1 rounded-t-md bg-lapis/80 hover:bg-lapis" title={`${d.date}: ${pkr(d.revenue)}`} />
          ))}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-line bg-white p-6">
          <h3 className="font-display text-lg font-bold">Top products</h3>
          <ul className="mt-4 space-y-3">
            {data.top_products.length === 0 && <p className="text-sm text-muted">No sales yet.</p>}
            {data.top_products.map((p) => (
              <li key={p.slug} className="flex items-center justify-between text-sm">
                <span className="font-semibold">{p.name}</span>
                <span className="text-muted">{p.sold_count} sold</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-2xl border border-line bg-white p-6">
          <h3 className="font-display text-lg font-bold">Low stock</h3>
          <ul className="mt-4 space-y-3">
            {data.low_stock.length === 0 && <p className="text-sm text-muted">Everything is well stocked.</p>}
            {data.low_stock.map((p) => (
              <li key={p.slug} className="flex items-center justify-between text-sm">
                <span className="font-semibold">{p.name}</span>
                <span className="font-bold text-gulal">{p.stock} left</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

function Products() {
  const { data, loading, reload } = useFetch('/catalog/products/mine/')
  const { data: cats } = useFetch('/catalog/categories/')
  const toast = useToast()
  const [editing, setEditing] = useState(null) // null = closed, {} = new, {...} = edit
  const products = data?.results || data || []

  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-bold">Your products ({products.length})</h3>
        <button onClick={() => setEditing({})} className="flex items-center gap-2 rounded-full bg-lapis px-5 py-2.5 text-sm font-bold text-white hover:bg-lapis-dark">
          <Plus size={16} /> Add product
        </button>
      </div>

      {loading ? <p className="mt-6 text-sm text-muted">Loading…</p> : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((p) => (
            <div key={p.id} className="overflow-hidden rounded-2xl border border-line bg-white">
              <div className="aspect-[4/3]"><ProductPlate product={p} /></div>
              <div className="p-4">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-bold leading-snug">{p.name}</p>
                  <button onClick={() => setEditing(p)} className="shrink-0 text-muted hover:text-lapis"><Pencil size={15} /></button>
                </div>
                <p className="mt-1 text-sm text-muted">{pkr(p.price)} · {p.stock} in stock</p>
                <span className={`mt-2 inline-block rounded-full px-2.5 py-0.5 text-xs font-bold ${p.is_active ? 'bg-pistachio/60 text-midnight' : 'bg-mist text-muted'}`}>
                  {p.is_active ? 'Active' : 'Hidden'}
                </span>
              </div>
            </div>
          ))}
          {products.length === 0 && <p className="col-span-full text-sm text-muted">No products yet — add your first one.</p>}
        </div>
      )}

      <AnimatePresence>
        {editing !== null && (
          <ProductForm product={editing} categories={cats || []} onClose={() => setEditing(null)}
            onSaved={() => { setEditing(null); reload(); toast('Product saved') }} />
        )}
      </AnimatePresence>
    </div>
  )
}

function ProductForm({ product, categories, onClose, onSaved }) {
  const isNew = !product.id
  const [form, setForm] = useState({
    name: product.name || '', description: product.description || '',
    price: product.price || '', compare_at_price: product.compare_at_price || '',
    stock: product.stock ?? 10, category_id: product.category?.id || categories[0]?.id || '',
    image_url: product.image_url || '', is_active: product.is_active ?? true,
  })
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErrors({})
    try {
      if (isNew) await api.post('/catalog/products/', form)
      else await api.patch(`/catalog/products/${product.slug}/`, form)
      onSaved()
    } catch (err) {
      setErrors(readError(err).fields)
    } finally { setBusy(false) }
  }

  return (
    <motion.div className="fixed inset-0 z-50 grid place-items-center bg-midnight/40 p-4"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
      <motion.form onSubmit={submit} onClick={(e) => e.stopPropagation()}
        initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
        className="max-h-[90vh] w-full max-w-lg space-y-4 overflow-y-auto rounded-2xl bg-white p-6">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-lg font-bold">{isNew ? 'Add product' : 'Edit product'}</h3>
          <button type="button" onClick={onClose}><X size={20} /></button>
        </div>
        <Field label="Name" error={errors.name}><input required className={inputCls} value={form.name} onChange={set('name')} /></Field>
        <Field label="Description" error={errors.description}><textarea rows={3} className={inputCls} value={form.description} onChange={set('description')} /></Field>
        <Field label="Photo URL" error={errors.image_url} hint="Paste a link to a product photo (optional — a placeholder graphic is used if left blank)">
          <input className={inputCls} value={form.image_url} onChange={set('image_url')} placeholder="https://..." />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Price (Rs)" error={errors.price}><input required type="number" step="0.01" className={inputCls} value={form.price} onChange={set('price')} /></Field>
          <Field label="Compare-at price" error={errors.compare_at_price} hint="Optional, for sale pricing"><input type="number" step="0.01" className={inputCls} value={form.compare_at_price} onChange={set('compare_at_price')} /></Field>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Stock" error={errors.stock}><input required type="number" className={inputCls} value={form.stock} onChange={set('stock')} /></Field>
          <Field label="Category" error={errors.category_id}>
            <select className={inputCls} value={form.category_id} onChange={set('category_id')}>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </Field>
        </div>
        <label className="flex items-center gap-2 text-sm font-semibold">
          <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
          Visible in shop
        </label>
        <button disabled={busy} className="w-full rounded-full bg-lapis py-3 text-sm font-bold text-white hover:bg-lapis-dark disabled:opacity-60">
          {busy ? 'Saving…' : 'Save product'}
        </button>
      </motion.form>
    </motion.div>
  )
}

function VendorOrders() {
  const { data, loading, reload } = useFetch('/orders/vendor-items/')
  const toast = useToast()
  const items = data?.results || data || []

  const advance = async (id, status) => {
    try {
      await api.post(`/orders/items/${id}/status/`, { status })
      toast('Order updated')
      reload()
    } catch (err) {
      toast(readError(err).message, 'error')
    }
  }

  if (loading) return <p className="text-sm text-muted">Loading…</p>
  if (items.length === 0) return <p className="text-sm text-muted">No orders yet.</p>

  return (
    <div className="space-y-3">
      {items.map((i) => (
        <div key={i.id} className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-white p-4">
          <div>
            <p className="font-bold">{i.product_name} × {i.quantity}</p>
            <p className="text-sm text-muted">{i.customer_name} · {i.city} · {shortDate(i.order_date)}</p>
            <p className="text-sm text-muted">Order #{i.order_number} · {pkr(i.line_total)}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-mist px-3 py-1 text-xs font-bold">{i.status_label}</span>
            {(i.next_statuses || []).map((s) => (
              <button key={s} onClick={() => advance(i.id, s)} className="rounded-full border-2 border-line px-3.5 py-1.5 text-xs font-bold hover:border-midnight">
                Mark {s}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
