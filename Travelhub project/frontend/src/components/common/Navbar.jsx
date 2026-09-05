import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Menu, X, Sun, Moon, User, Heart, Bell } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()
  const { dark, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const dashboardPath = {
    admin: '/admin/dashboard',
    hotel_owner: '/hotel-owner/dashboard',
    tour_operator: '/tour-operator/dashboard',
    customer: '/customer/dashboard',
  }[user?.role] || '/'

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/70 dark:bg-[#0d1b1a]/80 border-b border-black/5 dark:border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl text-[var(--color-primary)]">
          🌍 TravelHub
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link to="/hotels" className="hover:text-[var(--color-primary)] transition">Hotels</Link>
          <Link to="/tours" className="hover:text-[var(--color-primary)] transition">Tours</Link>
          <Link to="/about" className="hover:text-[var(--color-primary)] transition">About</Link>
          <Link to="/contact" className="hover:text-[var(--color-primary)] transition">Contact</Link>
        </nav>

        <div className="hidden md:flex items-center gap-4">
          <button onClick={toggleTheme} className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10" aria-label="Toggle theme">
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <Link to="/wishlist" className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10"><Heart size={18} /></Link>
              <Link to="/notifications" className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10"><Bell size={18} /></Link>
              <Link to={dashboardPath} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--color-primary)] text-white text-sm">
                <User size={16} /> {user.username}
              </Link>
              <button onClick={() => { logout(); navigate('/') }} className="text-sm text-red-500 hover:underline">
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link to="/login" className="text-sm font-medium hover:text-[var(--color-primary)]">Login</Link>
              <Link to="/register" className="px-4 py-2 rounded-full bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-dark)] transition">
                Sign Up
              </Link>
            </div>
          )}
        </div>

        <button className="md:hidden p-2" onClick={() => setOpen(!open)}>
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {open && (
        <div className="md:hidden px-4 pb-4 flex flex-col gap-3 border-t border-black/5 dark:border-white/10 bg-white dark:bg-[#0d1b1a]">
          <Link to="/hotels" onClick={() => setOpen(false)}>Hotels</Link>
          <Link to="/tours" onClick={() => setOpen(false)}>Tours</Link>
          <Link to="/about" onClick={() => setOpen(false)}>About</Link>
          <Link to="/contact" onClick={() => setOpen(false)}>Contact</Link>
          {isAuthenticated ? (
            <>
              <Link to={dashboardPath} onClick={() => setOpen(false)}>Dashboard</Link>
              <button onClick={() => { logout(); setOpen(false); navigate('/') }} className="text-left text-red-500">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setOpen(false)}>Login</Link>
              <Link to="/register" onClick={() => setOpen(false)}>Sign Up</Link>
            </>
          )}
        </div>
      )}
    </header>
  )
}
