import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import api, { readError } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  const loadProfile = useCallback(async () => {
    const token = localStorage.getItem('fp_access')
    if (!token) { setReady(true); return }
    try {
      const res = await api.get('/auth/profile/')
      setUser(res.data)
    } catch {
      localStorage.removeItem('fp_access')
      localStorage.removeItem('fp_refresh')
    } finally {
      setReady(true)
    }
  }, [])

  useEffect(() => { loadProfile() }, [loadProfile])

  const login = async (email, password) => {
    const res = await api.post('/auth/login/', { email, password })
    localStorage.setItem('fp_access', res.data.access)
    localStorage.setItem('fp_refresh', res.data.refresh)
    setUser(res.data.user)
    return res.data.user
  }

  const register = async (payload) => {
    await api.post('/auth/register/', payload)
    return login(payload.email, payload.password)
  }

  const logout = () => {
    localStorage.removeItem('fp_access')
    localStorage.removeItem('fp_refresh')
    setUser(null)
  }

  const role = user?.role
  const isAdmin = role === 'admin'
  const isManager = role === 'plant_manager' || isAdmin
  const isEngineer = role === 'maintenance_engineer' || isManager

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout, isAdmin, isManager, isEngineer }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

export { readError }
