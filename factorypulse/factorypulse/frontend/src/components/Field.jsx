export const inputCls =
  'w-full rounded-lg border border-steel-600 bg-steel-800 px-3.5 py-2.5 text-sm text-chalk placeholder:text-steel-500 outline-none transition-colors focus:border-cyan focus:ring-2 focus:ring-cyan/20'

export default function Field({ label, error, hint, children }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-mist">{label}</span>
      {children}
      {hint && !error && <span className="mt-1 block text-xs text-steel-500">{hint}</span>}
      {error && <span className="mt-1 block text-xs font-medium text-rose">{error}</span>}
    </label>
  )
}
