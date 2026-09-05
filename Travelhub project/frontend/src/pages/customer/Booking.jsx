import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import FormInput from '../../components/common/FormInput'
import { useAuth } from '../../context/AuthContext'
import { createBooking, createPayment } from '../../api/endpoints'

const STEPS = ['Date', 'Guest Details', 'Payment', 'Confirmed']

export default function Booking() {
  const { type, hotelId, roomId, tourId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [booking, setBooking] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const [form, setForm] = useState({
    check_in: '', check_out: '', tour_date: '', guests: 1,
    guest_name: user?.username || '', guest_email: user?.email || '', guest_phone: user?.phone || '',
    total_price: 0, coupon_code: '', method: 'cash',
  })

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1))
  const back = () => setStep((s) => Math.max(s - 1, 0))

  const handleConfirmBooking = async () => {
    setError('')
    setLoading(true)
    try {
      const payload = {
        booking_type: type,
        room: type === 'hotel' ? roomId : undefined,
        tour_package: type === 'tour' ? tourId : undefined,
        check_in: form.check_in || undefined,
        check_out: form.check_out || undefined,
        tour_date: form.tour_date || undefined,
        guests: form.guests,
        guest_name: form.guest_name,
        guest_email: form.guest_email,
        guest_phone: form.guest_phone,
        total_price: form.total_price || 100,
        coupon_code: form.coupon_code,
      }
      const { data } = await createBooking(payload)
      setBooking(data)
      await createPayment({ booking: data.id, amount: data.total_price, method: form.method })
      next()
    } catch (err) {
      setError('Booking failed. Please check your details and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Stepper */}
      <div className="flex items-center justify-between mb-10">
        {STEPS.map((label, i) => (
          <div key={label} className="flex-1 flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
              i <= step ? 'bg-[var(--color-primary)] text-white' : 'bg-black/10 dark:bg-white/10 text-black/40'
            }`}>
              {i < step ? <Check size={14} /> : i + 1}
            </div>
            {i < STEPS.length - 1 && <div className={`flex-1 h-0.5 mx-2 ${i < step ? 'bg-[var(--color-primary)]' : 'bg-black/10 dark:bg-white/10'}`} />}
          </div>
        ))}
      </div>

      <motion.div key={step} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="bg-white dark:bg-[#0f2422] rounded-2xl p-8 border border-black/5 dark:border-white/10">
        {step === 0 && (
          <>
            <h2 className="text-xl font-bold mb-6">Choose Date</h2>
            {type === 'hotel' ? (
              <>
                <FormInput label="Check-in" type="date" value={form.check_in} onChange={(e) => setForm({ ...form, check_in: e.target.value })} />
                <FormInput label="Check-out" type="date" value={form.check_out} onChange={(e) => setForm({ ...form, check_out: e.target.value })} />
              </>
            ) : (
              <FormInput label="Tour Date" type="date" value={form.tour_date} onChange={(e) => setForm({ ...form, tour_date: e.target.value })} />
            )}
            <FormInput label="Guests" type="number" min="1" value={form.guests} onChange={(e) => setForm({ ...form, guests: e.target.value })} />
            <button onClick={next} className="w-full bg-[var(--color-primary)] text-white font-medium py-2.5 rounded-xl mt-2">Continue</button>
          </>
        )}

        {step === 1 && (
          <>
            <h2 className="text-xl font-bold mb-6">Guest Details</h2>
            <FormInput label="Full Name" value={form.guest_name} onChange={(e) => setForm({ ...form, guest_name: e.target.value })} required />
            <FormInput label="Email" type="email" value={form.guest_email} onChange={(e) => setForm({ ...form, guest_email: e.target.value })} required />
            <FormInput label="Phone" value={form.guest_phone} onChange={(e) => setForm({ ...form, guest_phone: e.target.value })} required />
            <FormInput label="Total Price ($)" type="number" value={form.total_price} onChange={(e) => setForm({ ...form, total_price: e.target.value })} />
            <FormInput label="Coupon Code (optional)" value={form.coupon_code} onChange={(e) => setForm({ ...form, coupon_code: e.target.value })} />
            <div className="flex gap-3">
              <button onClick={back} className="flex-1 border border-black/10 dark:border-white/15 py-2.5 rounded-xl">Back</button>
              <button onClick={next} className="flex-1 bg-[var(--color-primary)] text-white font-medium py-2.5 rounded-xl">Continue</button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="text-xl font-bold mb-6">Payment</h2>
            <div className="space-y-2 mb-6">
              {[['cash', 'Cash Payment (Demo)'], ['fake_card', 'Fake Card Payment (Demo)']].map(([val, label]) => (
                <label key={val} className="flex items-center gap-3 border border-black/10 dark:border-white/15 rounded-xl px-4 py-3 cursor-pointer">
                  <input type="radio" name="method" checked={form.method === val} onChange={() => setForm({ ...form, method: val })} />
                  {label}
                </label>
              ))}
            </div>
            {error && <p className="text-sm text-red-500 mb-4">{error}</p>}
            <div className="flex gap-3">
              <button onClick={back} className="flex-1 border border-black/10 dark:border-white/15 py-2.5 rounded-xl">Back</button>
              <button onClick={handleConfirmBooking} disabled={loading} className="flex-1 bg-[var(--color-primary)] text-white font-medium py-2.5 rounded-xl disabled:opacity-60">
                {loading ? 'Processing...' : 'Pay & Confirm'}
              </button>
            </div>
          </>
        )}

        {step === 3 && (
          <div className="text-center py-6">
            <div className="w-16 h-16 rounded-full bg-green-500/10 text-green-600 flex items-center justify-center mx-auto mb-4">
              <Check size={32} />
            </div>
            <h2 className="text-xl font-bold mb-2">Booking Confirmed!</h2>
            <p className="text-sm text-black/50 dark:text-white/50 mb-6">
              Booking #{booking?.id} — a confirmation has been sent to your dashboard.
            </p>
            <button onClick={() => navigate('/customer/dashboard')} className="bg-[var(--color-primary)] text-white font-medium px-6 py-2.5 rounded-xl">
              Go to Dashboard
            </button>
          </div>
        )}
      </motion.div>
    </div>
  )
}
