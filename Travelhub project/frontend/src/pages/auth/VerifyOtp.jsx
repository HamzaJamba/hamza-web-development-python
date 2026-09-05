import { useState } from 'react'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import FormInput from '../../components/common/FormInput'
import { verifyOtp } from '../../api/endpoints'

export default function VerifyOtp() {
  const location = useLocation()
  const navigate = useNavigate()
  const [email, setEmail] = useState(location.state?.email || '')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await verifyOtp({ email, code })
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.non_field_errors?.[0] || 'Invalid or expired OTP.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Verify your email" subtitle="Enter the 6-digit code we sent to your email">
      <form onSubmit={handleSubmit}>
        <FormInput label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <FormInput label="OTP Code" value={code} onChange={(e) => setCode(e.target.value)} maxLength={6} required />
        {error && <p className="text-sm text-red-500 mb-4">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] text-white font-medium py-2.5 rounded-xl transition disabled:opacity-60"
        >
          {loading ? 'Verifying...' : 'Verify Account'}
        </button>
      </form>
      <p className="text-sm text-center mt-6 text-black/60 dark:text-white/60">
        Back to <Link to="/login" className="text-[var(--color-primary)] font-medium">Login</Link>
      </p>
    </AuthLayout>
  )
}
