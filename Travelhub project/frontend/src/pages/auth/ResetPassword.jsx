import { useState } from 'react'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import FormInput from '../../components/common/FormInput'
import { resetPassword } from '../../api/endpoints'

export default function ResetPassword() {
  const location = useLocation()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: location.state?.email || '', code: '', new_password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await resetPassword(form)
      navigate('/login')
    } catch (err) {
      const data = err.response?.data
      setError(data ? Object.values(data).flat().join(' ') : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Reset password" subtitle="Enter the OTP and your new password">
      <form onSubmit={handleSubmit}>
        <FormInput label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <FormInput label="OTP Code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} maxLength={6} required />
        <FormInput label="New Password" type="password" value={form.new_password} onChange={(e) => setForm({ ...form, new_password: e.target.value })} required />
        {error && <p className="text-sm text-red-500 mb-4">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] text-white font-medium py-2.5 rounded-xl transition disabled:opacity-60"
        >
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
      <p className="text-sm text-center mt-6 text-black/60 dark:text-white/60">
        Back to <Link to="/login" className="text-[var(--color-primary)] font-medium">Login</Link>
      </p>
    </AuthLayout>
  )
}
