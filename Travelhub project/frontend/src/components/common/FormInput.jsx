export default function FormInput({ label, error, ...props }) {
  return (
    <div className="mb-4">
      {label && <label className="block text-sm font-medium mb-1.5">{label}</label>}
      <input
        {...props}
        className="w-full px-4 py-2.5 rounded-xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#0f2422] outline-none focus:ring-2 focus:ring-[var(--color-primary)]/40 text-sm"
      />
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  )
}
