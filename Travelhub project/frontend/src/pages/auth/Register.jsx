import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import FormInput from '../../components/common/FormInput'
import { registerUser } from '../../api/endpoints'

export default function Register() {
  const [form, setForm] = useState({
    username: '', email: '', phone: '', password: '', password2: '', role: 'customer',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await registerUser(form)
      navigate('/verify-otp', { state: { email: form.email } })
    } catch (err) {
      const data = err.response?.data
      setError(data ? Object.values(data).flat().join(' ') : 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Create your account" subtitle="Join TravelHub and start planning your next trip">
      <form onSubmit={handleSubmit}>
        <FormInput label="Username" name="username" value={form.username} onChange={handleChange} required />
        <FormInput label="Email" type="email" name="email" value={form.email} onChange={handleChange} required />
        <FormInput label="Phone" name="phone" value={form.phone} onChange={handleChange} />

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1.5">I am a</label>
          <select
            name="role"
            value={form.role}
            onChange={handleChange}
            className="w-full px-4 py-2.5 rounded-xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#0f2422] outline-none text-sm"
          >
            <option value="customer">Customer</option>
            <option value="hotel_owner">Hotel Owner</option>
            <option value="tour_operator">Tour Operator</option>
          </select>
        </div>

        <FormInput label="Password" type="password" name="password" value={form.password} onChange={handleChange} required />
        <FormInput label="Confirm Password" type="password" name="password2" value={form.password2} onChange={handleChange} required />

        {error && <p className="text-sm text-red-500 mb-4">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] text-white font-medium py-2.5 rounded-xl transition disabled:opacity-60"
        >
          {loading ? 'Creating account...' : 'Sign Up'}
        </button>
      </form>

      <p className="text-sm text-center mt-6 text-black/60 dark:text-white/60">
        Already have an account? <Link to="/login" className="text-[var(--color-primary)] font-medium">Login</Link>
      </p>
    </AuthLayout>
  )
}
