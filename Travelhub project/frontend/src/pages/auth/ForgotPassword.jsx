import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import FormInput from '../../components/common/FormInput'
import { forgotPassword } from '../../api/endpoints'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await forgotPassword({ email })
      navigate('/reset-password', { state: { email } })
    } catch (err) {
      setError(err.response?.data?.email?.[0] || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Forgot password?" subtitle="We'll send an OTP code to reset your password">
      <form onSubmit={handleSubmit}>
        <FormInput label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        {error && <p className="text-sm text-red-500 mb-4">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] text-white font-medium py-2.5 rounded-xl transition disabled:opacity-60"
        >
          {loading ? 'Sending...' : 'Send OTP'}
        </button>
      </form>
      <p className="text-sm text-center mt-6 text-black/60 dark:text-white/60">
        Back to <Link to="/login" className="text-[var(--color-primary)] font-medium">Login</Link>
      </p>
    </AuthLayout>
  )
}
