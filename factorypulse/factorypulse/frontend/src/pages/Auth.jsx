import { useState } from 'react'
import { useNavigate, useLocation, Link, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Activity, Mail, Lock, User as UserIcon } from 'lucide-react'
import { useAuth, readError } from '../context/AuthContext'
import Field, { inputCls } from '../components/Field'

const DEMOS = [
  { email: 'admin@factorypulse.io', role: 'Admin' },
  { email: 'manager@factorypulse.io', role: 'Plant Manager' },
  { email: 'engineer@factorypulse.io', role: 'Maintenance Engineer' },
  { email: 'operator@factorypulse.io', role: 'Operator' },
]

export default function Auth() {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [params] = useSearchParams()
  const isRegister = params.get('mode') === 'register' || location.pathname === '/register'

  const [form, setForm] = useState({ email: '', password: '', password2: '', first_name: '', last_name: '' })
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErrors({}); setMessage('')
    try {
      if (isRegister) await register(form)
      else await login(form.email, form.password)
      navigate(location.state?.from?.pathname || '/')
    } catch (err) {
      const { fields, message } = readError(err)
      setErrors(fields); setMessage(message)
    } finally { setBusy(false) }
  }

  return (
    <div className="relative flex min-h-[calc(100vh-64px)] items-center justify-center overflow-hidden px-4 py-12">
      <div className="pointer-events-none absolute inset-0 opacity-30"
        style={{ backgroundImage: 'radial-gradient(circle at 20% 20%, rgba(34,211,238,0.15), transparent 40%), radial-gradient(circle at 80% 80%, rgba(245,158,11,0.1), transparent 40%)' }} />

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        className="relative w-full max-w-md rounded-2xl border border-steel-700 bg-steel-900/80 p-8 backdrop-blur-sm">
        <div className="flex items-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan to-cyan-dim text-steel-950">
            <Activity size={20} strokeWidth={2.5} />
          </span>
          <span className="font-display text-xl font-bold">FactoryPulse</span>
        </div>

        <h1 className="mt-6 font-display text-2xl font-bold">{isRegister ? 'Create your account' : 'Sign in to the plant'}</h1>
        <p className="mt-1 text-sm text-mist">{isRegister ? 'Monitor equipment and manage maintenance.' : 'Real-time monitoring, AI insights, predictive maintenance.'}</p>

        {message && <p className="mt-4 rounded-lg bg-rose-dim/15 px-4 py-2.5 text-sm font-medium text-rose">{message}</p>}

        <form onSubmit={submit} className="mt-6 space-y-4">
          {isRegister && (
            <div className="grid grid-cols-2 gap-3">
              <Field label="First name" error={errors.first_name}>
                <input className={inputCls} value={form.first_name} onChange={set('first_name')} />
              </Field>
              <Field label="Last name" error={errors.last_name}>
                <input className={inputCls} value={form.last_name} onChange={set('last_name')} />
              </Field>
            </div>
          )}
          <Field label="Email" error={errors.email}>
            <div className="relative">
              <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-steel-500" />
              <input required type="email" className={`${inputCls} pl-9`} value={form.email} onChange={set('email')} placeholder="you@factorypulse.io" />
            </div>
          </Field>
          <Field label="Password" error={errors.password}>
            <div className="relative">
              <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-steel-500" />
              <input required type="password" className={`${inputCls} pl-9`} value={form.password} onChange={set('password')} />
            </div>
          </Field>
          {isRegister && (
            <Field label="Confirm password" error={errors.password2}>
              <input required type="password" className={inputCls} value={form.password2} onChange={set('password2')} />
            </Field>
          )}

          <button disabled={busy} className="w-full rounded-lg bg-cyan py-3 text-sm font-bold text-steel-950 transition-colors hover:bg-cyan/90 disabled:opacity-60">
            {busy ? 'Please wait…' : isRegister ? 'Create account' : 'Sign in'}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-mist">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <Link to={isRegister ? '/login' : '/register'} className="font-semibold text-cyan hover:underline">
            {isRegister ? 'Sign in' : 'Register'}
          </Link>
        </p>

        {!isRegister && (
          <div className="mt-6 rounded-xl border border-steel-700 bg-steel-800/50 p-4">
            <p className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-mist"><UserIcon size={12} /> Demo logins (password: Demo@12345)</p>
            <div className="grid grid-cols-2 gap-1.5 text-xs">
              {DEMOS.map((d) => (
                <button key={d.email} type="button" onClick={() => setForm({ ...form, email: d.email, password: 'Demo@12345' })}
                  className="rounded-md border border-steel-600 px-2 py-1.5 text-left text-mist hover:border-cyan hover:text-cyan">
                  {d.role}
                </button>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
