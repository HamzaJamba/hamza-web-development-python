export default function Field({ label, error, hint, children, className = '' }) {
  return (
    <label className={`block ${className}`}>
      <span className="mb-1.5 block text-sm font-semibold">{label}</span>
      {children}
      {hint && !error && <span className="mt-1 block text-xs text-muted">{hint}</span>}
      {error && <span className="mt-1 block text-xs font-semibold text-gulal" role="alert">{error}</span>}
    </label>
  )
}

export const inputCls =
  'w-full rounded-xl border-2 border-line bg-white px-3.5 py-2.5 text-[15px] placeholder:text-muted/60 focus:border-lapis focus:outline-none'
