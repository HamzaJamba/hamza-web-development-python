import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RequireAuth({ children }) {
  const { user, ready } = useAuth()
  const loc = useLocation()
  if (!ready) return <div className="grid min-h-[50vh] place-items-center text-sm text-muted">Loading…</div>
  if (!user) return <Navigate to={`/login?next=${encodeURIComponent(loc.pathname + loc.search)}`} replace />
  return children
}
