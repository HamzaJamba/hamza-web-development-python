import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, LayoutDashboard, Cpu, ClipboardList, LogOut, Menu, X, ShieldCheck } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const linkCls = ({ isActive }) =>
  `flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-semibold transition-colors ${
    isActive ? 'bg-steel-700 text-cyan' : 'text-mist hover:bg-steel-800 hover:text-chalk'
  }`

export default function Header() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  const links = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/machines', label: 'Machines', icon: Cpu },
    { to: '/work-orders', label: 'Work Orders', icon: ClipboardList },
  ]
  if (isAdmin) links.push({ to: '/audit', label: 'Audit', icon: ShieldCheck })

  return (
    <header className="sticky top-0 z-40 border-b border-steel-700 bg-steel-950/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-cyan to-cyan-dim text-steel-950"
          >
            <Activity size={18} strokeWidth={2.5} />
          </motion.div>
          <span className="font-display text-lg font-bold tracking-tight">FactoryPulse</span>
        </Link>

        {user && (
          <nav className="hidden items-center gap-1 md:flex">
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} className={linkCls} end={l.to === '/'}>
                <l.icon size={15} /> {l.label}
              </NavLink>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <div className="hidden text-right sm:block">
                <p className="text-sm font-semibold leading-none">{user.full_name || user.email}</p>
                <p className="mt-0.5 text-xs capitalize leading-none text-mist">{user.role?.replace('_', ' ')}</p>
              </div>
              <button onClick={() => { logout(); navigate('/login') }}
                className="flex items-center gap-1.5 rounded-lg border border-steel-600 px-3 py-2 text-xs font-semibold text-mist hover:border-rose-dim hover:text-rose transition-colors">
                <LogOut size={14} /> <span className="hidden sm:inline">Logout</span>
              </button>
              <button className="md:hidden" onClick={() => setOpen(!open)}>
                {open ? <X size={20} /> : <Menu size={20} />}
              </button>
            </>
          ) : (
            <Link to="/login" className="rounded-lg bg-cyan px-4 py-2 text-sm font-bold text-steel-950 hover:bg-cyan/90">
              Sign in
            </Link>
          )}
        </div>
      </div>

      <AnimatePresence>
        {open && user && (
          <motion.nav initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-steel-700 md:hidden">
            <div className="flex flex-col gap-1 p-3">
              {links.map((l) => (
                <NavLink key={l.to} to={l.to} className={linkCls} end={l.to === '/'} onClick={() => setOpen(false)}>
                  <l.icon size={15} /> {l.label}
                </NavLink>
              ))}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}
