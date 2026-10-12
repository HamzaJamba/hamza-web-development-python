import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fp_access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing = null
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('fp_refresh')
      if (!refresh) return Promise.reject(error)
      try {
        refreshing = refreshing || axios.post('/api/auth/token/refresh/', { refresh })
        const { data } = await refreshing
        refreshing = null
        localStorage.setItem('fp_access', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        localStorage.removeItem('fp_access')
        localStorage.removeItem('fp_refresh')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export function readError(err) {
  const data = err?.response?.data
  if (!data) return { fields: {}, message: 'Something went wrong. Please try again.' }
  if (typeof data === 'string') return { fields: {}, message: data }
  if (data.detail) return { fields: {}, message: data.detail }
  const fields = {}
  let message = ''
  for (const [k, v] of Object.entries(data)) {
    const text = Array.isArray(v) ? v.join(' ') : String(v)
    fields[k] = text
    message = message || text
  }
  return { fields, message: message || 'Please check the form and try again.' }
}

export default api
