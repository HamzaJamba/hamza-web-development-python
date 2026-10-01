import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { readError } from '../lib/api'
import Awning from '../components/Awning'
import Field, { inputCls } from '../components/Field'

const DEMOS = [
  ['Customer', 'customer1@marketnest.pk'],
  ['Vendor', 'anarkali@marketnest.pk'],
  ['Admin', 'admin@marketnest.pk'],
]

export default function Auth() {
  const { pathname } = useLocation()
  const mode = pathname === '/register' ? 'register' : 'login'
  const { user, login, register } = useAuth()
  const navigate = useNavigate()
  const [sp] = useSearchParams()
  const next = sp.get('next') || '/'
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', password: '', password2: '' })
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  if (user) return <Navigate to={next} replace />

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErrors({}); setMessage('')
    try {
      if (mode === 'login') await login(form.email, form.password)
      else await register(form)
      navigate(next, { replace: true })
    } catch (err) {
      const { fields, message } = readError(err)
      const status = err?.response?.status
      setErrors(fields)
      setMessage(status === 401 ? 'That email and password do not match.' : status === 429 ? 'Too many attempts. Wait a minute and try again.' : message)
    } finally { setBusy(false) }
  }

  return (
    <div className="mx-auto grid min-h-[calc(100vh-140px)] max-w-6xl gap-0 px-4 py-10 sm:px-6 lg:grid-cols-2">
      <div className="relative hidden overflow-hidden rounded-l-[28px] bg-midnight text-white lg:block">
        <Awning primary="#FF5A8A" secondary="#1D1B54" stripes={12} />
        <div className="px-10 pt-8">
          <h2 className="font-display text-3xl font-bold leading-tight">{mode === 'login' ? 'Welcome back to the bazaar' : 'Your cart, every stall'}</h2>
          <p className="mt-4 max-w-sm leading-relaxed text-white/70">
            {mode === 'login' ? 'Your orders and saved details are waiting.' : 'Create an account to check out, track each stall’s parcel and leave reviews.'}
          </p>
        </div>
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }} className="rounded-[28px] border border-line bg-white p-7 sm:p-10 lg:rounded-l-none">
        <h1 className="font-display text-2xl font-bold">{mode === 'login' ? 'Log in' : 'Create your account'}</h1>
        <p className="mt-2 text-sm text-muted">
          {mode === 'login' ? 'New here? ' : 'Already have an account? '}
          <Link to={`${mode === 'login' ? '/register' : '/login'}${sp.get('next') ? `?next=${encodeURIComponent(next)}` : ''}`} className="font-bold text-lapis hover:underline">
            {mode === 'login' ? 'Create an account' : 'Log in'}
          </Link>
        </p>

        <form onSubmit={submit} className="mt-7 space-y-4" noValidate>
          {mode === 'register' && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="First name" error={errors.first_name}><input className={inputCls} value={form.first_name} onChange={set('first_name')} autoComplete="given-name" required /></Field>
              <Field label="Last name" error={errors.last_name}><input className={inputCls} value={form.last_name} onChange={set('last_name')} autoComplete="family-name" /></Field>
            </div>
          )}
          <Field label="Email" error={errors.email}><input type="email" className={inputCls} value={form.email} onChange={set('email')} autoComplete="email" required /></Field>
          {mode === 'register' && <Field label="Phone" error={errors.phone} hint="For delivery updates."><input className={inputCls} value={form.phone} onChange={set('phone')} autoComplete="tel" /></Field>}
          <Field label="Password" error={errors.password} hint={mode === 'register' ? 'At least 8 characters.' : undefined}><input type="password" className={inputCls} value={form.password} onChange={set('password')} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} required /></Field>
          {mode === 'register' && <Field label="Confirm password" error={errors.password2}><input type="password" className={inputCls} value={form.password2} onChange={set('password2')} autoComplete="new-password" required /></Field>}

          {message && <p className="rounded-xl bg-gulal/10 px-4 py-3 text-sm font-semibold text-gulal" role="alert">{message}</p>}
          <button disabled={busy} className="w-full rounded-full bg-lapis py-3.5 text-[15px] font-bold text-white hover:bg-lapis-dark disabled:opacity-60">
            {busy ? 'One moment…' : mode === 'login' ? 'Log in' : 'Create account'}
          </button>
        </form>

        {mode === 'login' && (
          <div className="mt-8 border-t border-line pt-5">
            <p className="text-xs font-semibold text-muted">Demo accounts (password Demo@12345)</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {DEMOS.map(([label, email]) => (
                <button key={email} type="button" onClick={() => setForm({ ...form, email, password: 'Demo@12345' })} className="rounded-full border-2 border-line px-4 py-1.5 text-sm font-bold hover:border-midnight">{label}</button>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
