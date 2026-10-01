import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

const tokens = {
  get access() { return localStorage.getItem('mn_access') },
  get refresh() { return localStorage.getItem('mn_refresh') },
  set({ access, refresh }) {
    if (access) localStorage.setItem('mn_access', access)
    if (refresh) localStorage.setItem('mn_refresh', refresh)
  },
  clear() {
    localStorage.removeItem('mn_access')
    localStorage.removeItem('mn_refresh')
  },
}
export { tokens }

api.interceptors.request.use((config) => {
  if (tokens.access) config.headers.Authorization = `Bearer ${tokens.access}`
  return config
})

// One silent refresh on 401, then give up and tell the app to sign the user out.
let refreshing = null
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    const isAuthCall = original?.url?.includes('/auth/')
    if (error.response?.status === 401 && !original._retried && !isAuthCall && tokens.refresh) {
      original._retried = true
      try {
        refreshing = refreshing || axios.post('/api/auth/token/refresh/', { refresh: tokens.refresh })
        const { data } = await refreshing
        tokens.set(data)
        return api(original)
      } catch {
        tokens.clear()
        window.dispatchEvent(new Event('auth:expired'))
      } finally {
        refreshing = null
      }
    }
    return Promise.reject(error)
  },
)

/** Turns a DRF error response into { fields: {name: text}, message } for forms. */
export function readError(err, fallback = 'Something went wrong. Please try again.') {
  const data = err?.response?.data
  if (!data) return { fields: {}, message: err?.code === 'ERR_NETWORK' ? 'Cannot reach the server. Is the backend running?' : fallback }
  if (typeof data === 'string') return { fields: {}, message: fallback }
  const fields = {}
  let message = data.detail || ''
  for (const [k, v] of Object.entries(data)) {
    if (k === 'detail' || k === 'code') continue
    const text = Array.isArray(v) ? v.join(' ') : typeof v === 'string' ? v : JSON.stringify(v)
    fields[k] = text
    if (!message) message = text
  }
  return { fields, message: message || fallback }
}

export default api
