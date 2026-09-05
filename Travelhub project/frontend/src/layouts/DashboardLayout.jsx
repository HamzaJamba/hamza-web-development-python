import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = {
  admin: [
    { label: 'Overview', to: '/admin/dashboard' },
    { label: 'Hotels', to: '/admin/hotels' },
    { label: 'Tour Operators', to: '/admin/tour-operators' },
    { label: 'Customers', to: '/admin/customers' },
    { label: 'Bookings', to: '/admin/bookings' },
    { label: 'Payments', to: '/admin/payments' },
    { label: 'Coupons', to: '/admin/coupons' },
    { label: 'Reviews', to: '/admin/reviews' },
  ],
  hotel_owner: [
    { label: 'Overview', to: '/hotel-owner/dashboard' },
    { label: 'My Hotels', to: '/hotel-owner/hotels' },
    { label: 'Rooms', to: '/hotel-owner/rooms' },
    { label: 'Bookings', to: '/hotel-owner/bookings' },
    { label: 'Reviews', to: '/hotel-owner/reviews' },
  ],
  tour_operator: [
    { label: 'Overview', to: '/tour-operator/dashboard' },
    { label: 'My Packages', to: '/tour-operator/packages' },
    { label: 'Bookings', to: '/tour-operator/bookings' },
    { label: 'Revenue', to: '/tour-operator/revenue' },
  ],
  customer: [
    { label: 'Overview', to: '/customer/dashboard' },
    { label: 'Upcoming Trips', to: '/customer/trips' },
    { label: 'Booking History', to: '/customer/history' },
    { label: 'Wishlist', to: '/customer/wishlist' },
    { label: 'Profile', to: '/customer/profile' },
  ],
}

export default function DashboardLayout() {
  const { user } = useAuth()
  const location = useLocation()
  const items = NAV_ITEMS[user?.role] || []

  return (
    <div className="min-h-screen flex bg-[var(--color-light)] dark:bg-[#0d1b1a]">
      <aside className="w-64 shrink-0 bg-white dark:bg-[#0f2422] border-r border-black/5 dark:border-white/10 p-6 hidden md:block">
        <Link to="/" className="text-xl font-bold text-[var(--color-primary)]">🌍 TravelHub</Link>
        <p className="text-xs text-black/50 dark:text-white/50 mt-1 mb-6 capitalize">{user?.role?.replace('_', ' ')} Panel</p>
        <nav className="flex flex-col gap-1">
          {items.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                location.pathname === item.to
                  ? 'bg-[var(--color-primary)] text-white'
                  : 'hover:bg-black/5 dark:hover:bg-white/10'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6 md:p-10">
        <Outlet />
      </main>
    </div>
  )
}
