import { createContext, useCallback, useContext, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Check, CircleAlert } from 'lucide-react'

const ToastCtx = createContext(null)
export const useToast = () => useContext(ToastCtx)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const toast = useCallback((text, kind = 'ok') => {
    const id = Math.random().toString(36).slice(2)
    setToasts((t) => [...t, { id, text, kind }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3600)
  }, [])

  return (
    <ToastCtx.Provider value={toast}>
      {children}
      <div className="pointer-events-none fixed inset-x-0 bottom-5 z-[80] flex flex-col items-center gap-2 px-4" role="status" aria-live="polite">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 16, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 8 }}
              transition={{ type: 'spring', stiffness: 420, damping: 30 }}
              className={`pointer-events-auto flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-semibold shadow-lg ${
                t.kind === 'error' ? 'bg-gulal text-white' : 'bg-midnight text-white'
              }`}
            >
              {t.kind === 'error' ? <CircleAlert size={16} /> : <Check size={16} className="text-pistachio" />}
              {t.text}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastCtx.Provider>
  )
}
