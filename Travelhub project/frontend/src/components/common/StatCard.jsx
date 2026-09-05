export default function StatCard({ label, value, icon: Icon }) {
  return (
    <div className="bg-white dark:bg-[#0f2422] rounded-2xl p-5 shadow-sm border border-black/5 dark:border-white/10 flex items-center gap-4">
      {Icon && (
        <div className="w-12 h-12 rounded-xl bg-[var(--color-primary)]/10 flex items-center justify-center text-[var(--color-primary)]">
          <Icon size={22} />
        </div>
      )}
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-sm text-black/50 dark:text-white/50">{label}</p>
      </div>
    </div>
  )
}
