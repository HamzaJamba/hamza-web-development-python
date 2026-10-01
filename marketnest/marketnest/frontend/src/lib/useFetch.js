import { useEffect, useState, useCallback } from 'react'
import api from './api'

/** Small data hook: { data, loading, error, reload }. Re-fetches when `url` (incl. params) changes. */
export default function useFetch(url, params) {
  const [state, setState] = useState({ data: null, loading: true, error: null })
  const key = url ? url + JSON.stringify(params || {}) : null

  const run = useCallback(() => {
    if (!url) return () => {}
    let cancelled = false
    setState((s) => ({ ...s, loading: true, error: null }))
    api.get(url, { params })
      .then((r) => !cancelled && setState({ data: r.data, loading: false, error: null }))
      .catch((e) => !cancelled && setState({ data: null, loading: false, error: e }))
    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  useEffect(() => run(), [run])
  return { ...state, reload: run }
}
