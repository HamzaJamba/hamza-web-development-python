import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Store, CheckCircle2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { readError } from '../lib/api'
import api from '../lib/api'
import Awning from '../components/Awning'
import Field, { inputCls } from '../components/Field'

const SWATCHES = ['#2C3BE6', '#FF5A8A', '#FFC533', '#1D1B54', '#C4EA6B', '#00A896']

export default function VendorApply() {
  const { stall, loadStall } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    shop_name: '', tagline: '', description: '', city: '', awning_primary: SWATCHES[0],
  })
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  if (stall) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6">
        <CheckCircle2 className="mx-auto text-lapis" size={48} />
        <h1 className="mt-4 font-display text-2xl font-bold">
          {stall.is_approved ? 'Your stall is live' : 'Application submitted'}
        </h1>
        <p className="mt-3 text-muted">
          {stall.is_approved
            ? `${stall.shop_name} is open for business.`
            : `Thanks for applying with ${stall.shop_name}. An admin will review it shortly.`}
        </p>
        {stall.is_approved && (
          <button onClick={() => navigate('/vendor')} className="mt-6 rounded-full bg-lapis px-7 py-3 text-sm font-bold text-white hover:bg-lapis-dark">
            Go to your dashboard
          </button>
        )}
      </div>
    )
  }

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErrors({}); setMessage('')
    try {
      await api.post('/vendors/apply/', form)
      await loadStall()
    } catch (err) {
      const { fields, message } = readError(err)
      setErrors(fields); setMessage(message)
    } finally { setBusy(false) }
  }

  return (
    <div className="mx-auto grid min-h-[calc(100vh-140px)] max-w-6xl gap-0 px-4 py-10 sm:px-6 lg:grid-cols-2">
      <div className="relative hidden overflow-hidden rounded-l-[28px] text-white lg:block" style={{ background: form.awning_primary }}>
        <Awning primary="#FFFFFF" secondary={form.awning_primary} stripes={12} />
        <div className="px-10 pt-8">
          <Store size={32} />
          <h2 className="mt-4 font-display text-3xl font-bold leading-tight">Open your own stall</h2>
          <p className="mt-4 max-w-sm leading-relaxed text-white/85">
            List your products, get orders from every corner of Pakistan, and keep 90% of every sale.
          </p>
        </div>
      </div>

      <motion.form onSubmit={submit} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}
        className="space-y-5 rounded-[28px] border border-line bg-white p-7 sm:p-10 lg:rounded-l-none">
        <h1 className="font-display text-2xl font-bold">Apply to sell</h1>
        {message && <p className="rounded-xl bg-gulal/10 px-4 py-3 text-sm font-semibold text-gulal">{message}</p>}

        <Field label="Shop name" error={errors.shop_name}>
          <input required className={inputCls} value={form.shop_name} onChange={set('shop_name')} placeholder="e.g. Anarkali Crafts" />
        </Field>
        <Field label="Tagline" error={errors.tagline} hint="One line describing what you sell">
          <input className={inputCls} value={form.tagline} onChange={set('tagline')} maxLength={160} />
        </Field>
        <Field label="City" error={errors.city}>
          <input required className={inputCls} value={form.city} onChange={set('city')} placeholder="e.g. Lahore" />
        </Field>
        <Field label="Description" error={errors.description}>
          <textarea rows={4} className={inputCls} value={form.description} onChange={set('description')} />
        </Field>
        <Field label="Stall colour">
          <div className="flex gap-2.5">
            {SWATCHES.map((c) => (
              <button type="button" key={c} onClick={() => setForm({ ...form, awning_primary: c })}
                className="h-9 w-9 rounded-full ring-offset-2 transition-transform hover:-translate-y-0.5"
                style={{ background: c, boxShadow: form.awning_primary === c ? `0 0 0 2px ${c}` : 'none', outline: form.awning_primary === c ? '2px solid #1D1B54' : 'none', outlineOffset: 2 }}
                aria-label={`Choose ${c}`} />
            ))}
          </div>
        </Field>

        <button disabled={busy} className="w-full rounded-full bg-lapis py-3.5 text-[15px] font-bold text-white transition-colors hover:bg-lapis-dark disabled:opacity-60">
          {busy ? 'Submitting…' : 'Submit application'}
        </button>
        <p className="text-xs text-muted">MarketNest keeps a 10% commission on each sale. You can update your stall details anytime from your dashboard.</p>
      </motion.form>
    </div>
  )
}
