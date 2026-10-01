import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import api, { tokens } from '../lib/api'

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [stall, setStall] = useState(null) // the signed-in person's own stall, if they have one
  const [ready, setReady] = useState(false)

  const loadStall = useCallback(async () => {
    try {
      const { data } = await api.get('/vendors/me/')
      setStall(data)
      return data
    } catch {
      setStall(null)
      return null
    }
  }, [])

  const loadUser = useCallback(async () => {
    try {
      const { data } = await api.get('/auth/profile/')
      setUser({ ...data, full_name: `${data.first_name} ${data.last_name}`.trim() || data.email })
      await loadStall()
    } catch {
      tokens.clear()
      setUser(null)
    }
  }, [loadStall])

  useEffect(() => {
    (tokens.access ? loadUser() : Promise.resolve()).finally(() => setReady(true))
    const expired = () => { setUser(null); setStall(null) }
    window.addEventListener('auth:expired', expired)
    return () => window.removeEventListener('auth:expired', expired)
  }, [loadUser])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login/', { email, password })
    tokens.set(data)
    await loadUser()
    return data.user
  }

  const register = async (form) => {
    await api.post('/auth/register/', form)
    return login(form.email, form.password)
  }

  const logout = async () => {
    try { await api.post('/auth/logout/', { refresh: tokens.refresh }) } catch { /* token may already be expired */ }
    tokens.clear()
    setUser(null)
    setStall(null)
  }

  const isAdmin = user?.role === 'admin' || user?.is_superuser
  return (
    <AuthCtx.Provider value={{ user, stall, ready, login, register, logout, loadStall, isAdmin }}>
      {children}
    </AuthCtx.Provider>
  )
}
