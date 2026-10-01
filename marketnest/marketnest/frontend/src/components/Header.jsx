import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, useNavigate, useSearchParams } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { ShoppingBag, Search, User, LogOut, Package, LayoutDashboard, Store, ShieldCheck } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2.5" aria-label="MarketNest home">
      <svg viewBox="0 0 64 64" className="h-9 w-9" aria-hidden="true">
        <rect width="64" height="64" rx="16" fill="#2C3BE6" />
        <path d="M10 14h44v14a7 7 0 0 1-11 0 7 7 0 0 1-11 0 7 7 0 0 1-11 0 7 7 0 0 1-11 0z" fill="#fff" />
        <path d="M10 14h11v14a7 7 0 0 1-11 0zM32 14h11v14a7 7 0 0 1-11 0z" fill="#FF5A8A" />
        <rect x="14" y="36" width="36" height="16" rx="4" fill="#C4EA6B" />
      </svg>
      <span className="font-display text-[17px] font-bold tracking-tight">MarketNest</span>
    </Link>
  )
}

export default function Header() {
  const { user, stall, logout, isAdmin } = useAuth()
  const { count, bump, setOpen } = useCart()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [q, setQ] = useState(params.get('q') || '')
  const [menu, setMenu] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    const close = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenu(false) }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [])

  const submit = (e) => {
    e.preventDefault()
    navigate(q.trim() ? `/shop?q=${encodeURIComponent(q.trim())}` : '/shop')
  }

  const link = ({ isActive }) => `text-sm font-semibold transition-colors hover:text-lapis ${isActive ? 'text-lapis' : ''}`
  const item = 'flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm font-semibold hover:bg-mist'

  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-chalk/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-3 px-4 py-3 sm:px-6">
        <Logo />
        <nav className="hidden items-center gap-6 md:flex" aria-label="Main">
          <NavLink to="/shop" className={link}>Shop</NavLink>
          {stall?.is_approved
            ? <NavLink to="/vendor" className={link}>Your stall</NavLink>
            : <NavLink to="/vendor/apply" className={link}>Open a stall</NavLink>}
        </nav>

        <form onSubmit={submit} className="order-last flex w-full items-center rounded-full border-2 border-line bg-white px-4 focus-within:border-lapis md:order-none md:w-auto md:flex-1 md:max-w-md" role="search">
          <Search size={17} className="text-muted" aria-hidden="true" />
          <input
            value={q} onChange={(e) => setQ(e.target.value)}
            placeholder="Search kurtas, earbuds, tea…"
            aria-label="Search products"
            className="w-full bg-transparent px-3 py-2.5 text-sm focus:outline-none"
          />
        </form>

        <div className="ml-auto flex items-center gap-2">
          <div className="relative" ref={menuRef}>
            {user ? (
              <button onClick={() => setMenu((m) => !m)} className="flex items-center gap-2 rounded-full border-2 border-line bg-white py-1.5 pl-1.5 pr-3.5 text-sm font-semibold hover:border-midnight" aria-expanded={menu} aria-haspopup="menu">
                <span className="grid h-7 w-7 place-items-center rounded-full bg-lapis text-xs font-bold text-white">{(user.full_name || 'U')[0].toUpperCase()}</span>
                <span className="hidden max-w-[110px] truncate sm:block">{user.first_name || user.full_name}</span>
              </button>
            ) : (
              <Link to="/login" className="inline-flex items-center gap-2 rounded-full border-2 border-line bg-white px-4 py-2 text-sm font-bold hover:border-midnight">
                <User size={16} /> Log in
              </Link>
            )}
            <AnimatePresence>
              {menu && user && (
                <motion.div
                  initial={{ opacity: 0, y: -6, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.14 }} role="menu"
                  className="absolute right-0 top-[calc(100%+8px)] z-50 w-56 origin-top-right rounded-2xl border border-line bg-white p-1.5 shadow-xl"
                  onClick={() => setMenu(false)}
                >
                  <div className="px-3 py-2 text-xs text-muted">Signed in as<br /><span className="font-semibold text-midnight">{user.email}</span></div>
                  <Link to="/orders" className={item} role="menuitem"><Package size={16} /> My orders</Link>
                  {stall?.is_approved
                    ? <Link to="/vendor" className={item} role="menuitem"><LayoutDashboard size={16} /> Stall dashboard</Link>
                    : <Link to="/vendor/apply" className={item} role="menuitem"><Store size={16} /> {stall ? 'Stall application' : 'Open a stall'}</Link>}
                  {isAdmin && <Link to="/admin-console" className={item} role="menuitem"><ShieldCheck size={16} /> Admin console</Link>}
                  <button onClick={() => { logout(); navigate('/') }} className={`${item} text-gulal`} role="menuitem"><LogOut size={16} /> Log out</button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button id="cart-button" onClick={() => setOpen(true)} className="relative grid h-11 w-11 place-items-center rounded-full bg-midnight text-white hover:bg-lapis" aria-label={`Open cart, ${count} items`}>
            <ShoppingBag size={19} />
            <AnimatePresence>
              {count > 0 && (
                <motion.span
                  key={bump}
                  initial={{ scale: 0.5 }} animate={{ scale: [1.5, 1] }} transition={{ type: 'spring', stiffness: 500, damping: 14 }}
                  className="absolute -right-1 -top-1 grid h-5 min-w-5 place-items-center rounded-full bg-gulal px-1 text-[11px] font-bold"
                >{count}</motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </div>
    </header>
  )
}
