const MACHINE_STATUS = {
  running: { label: 'Running', dot: 'bg-emerald', text: 'text-emerald' },
  idle: { label: 'Idle', dot: 'bg-mist', text: 'text-mist' },
  maintenance: { label: 'Maintenance', dot: 'bg-amber', text: 'text-amber' },
  down: { label: 'Down', dot: 'bg-rose', text: 'text-rose' },
}

const WO_STATUS = {
  open: { label: 'Open', dot: 'bg-cyan', text: 'text-cyan' },
  in_progress: { label: 'In Progress', dot: 'bg-amber', text: 'text-amber' },
  completed: { label: 'Completed', dot: 'bg-emerald', text: 'text-emerald' },
  cancelled: { label: 'Cancelled', dot: 'bg-mist', text: 'text-mist' },
}

const PRIORITY = {
  low: 'text-mist border-steel-600',
  medium: 'text-cyan border-cyan-dim/50',
  high: 'text-amber border-amber-dim/50',
  critical: 'text-rose border-rose-dim/50',
}

export function MachineStatusBadge({ status }) {
  const s = MACHINE_STATUS[status] || MACHINE_STATUS.idle
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${s.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  )
}

export function WorkOrderStatusBadge({ status }) {
  const s = WO_STATUS[status] || WO_STATUS.open
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border border-steel-600 px-2.5 py-0.5 text-xs font-semibold ${s.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  )
}

export function PriorityBadge({ priority }) {
  return (
    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-bold uppercase tracking-wide ${PRIORITY[priority] || PRIORITY.medium}`}>
      {priority}
    </span>
  )
}
