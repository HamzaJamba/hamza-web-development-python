import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import FormInput from '../../components/common/FormInput'
import { useAuth } from '../../context/AuthContext'

const DASHBOARD_BY_ROLE = {
  admin: '/admin/dashboard',
  hotel_owner: '/hotel-owner/dashboard',
  tour_operator: '/tour-operator/dashboard',
  customer: '/customer/dashboard',
}

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(form.username, form.password)
      navigate(DASHBOARD_BY_ROLE[user.role] || '/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials or account not verified.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Welcome back" subtitle="Login to manage your bookings and trips">
      <form onSubmit={handleSubmit}>
        <FormInput
          label="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          required
        />
        <FormInput
          label="Password"
          type="password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />
        <div className="text-right mb-4">
          <Link to="/forgot-password" className="text-xs text-[var(--color-primary)]">Forgot password?</Link>
        </div>
        {error && <p className="text-sm text-red-500 mb-4">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] text-white font-medium py-2.5 rounded-xl transition disabled:opacity-60"
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p className="text-sm text-center mt-6 text-black/60 dark:text-white/60">
        Don't have an account? <Link to="/register" className="text-[var(--color-primary)] font-medium">Sign up</Link>
      </p>
    </AuthLayout>
  )
}
