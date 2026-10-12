import { useState, useEffect, useCallback, useRef } from 'react'
import api from './api'

export default function useFetch(url, params) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const paramsRef = useRef(params)
  paramsRef.current = params

  const load = useCallback(async () => {
    if (!url) return
    setLoading(true)
    try {
      const res = await api.get(url, { params: paramsRef.current })
      setData(res.data)
      setError(null)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [url, JSON.stringify(params)])

  useEffect(() => { load() }, [load])

  return { data, loading, error, reload: load }
}
