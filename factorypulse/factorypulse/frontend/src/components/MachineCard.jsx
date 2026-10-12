import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Gauge, Thermometer, Activity } from 'lucide-react'
import { MachineStatusBadge } from './StatusBadge'

const TYPE_ICON = { motor: '⚙️', compressor: '🌀', conveyor: '📦', pump: '💧', turbine: '🌪️', cnc: '🔧' }

export default function MachineCard({ machine, index = 0 }) {
  const critical = machine.criticality === 'critical'
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04, duration: 0.35 }}>
      <Link to={`/machines/${machine.id}`}
        className="group block overflow-hidden rounded-2xl border border-steel-700 bg-steel-900 p-5 transition-all hover:-translate-y-1 hover:border-steel-500 hover:shadow-xl hover:shadow-cyan/5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-steel-800 text-xl">{TYPE_ICON[machine.machine_type] || '⚙️'}</span>
            <div>
              <p className="font-display font-bold leading-tight">{machine.name}</p>
              <p className="font-mono text-xs text-mist">{machine.machine_code}</p>
            </div>
          </div>
          {critical && <span className="rounded-full bg-rose-dim/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-rose">Critical</span>}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <MachineStatusBadge status={machine.status} />
          <span className="text-xs text-mist">{machine.plant_section}</span>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-2 border-t border-steel-800 pt-3 text-xs text-mist">
          <span className="flex items-center gap-1"><Activity size={12} /> Vib</span>
          <span className="flex items-center gap-1"><Thermometer size={12} /> Temp</span>
          <span className="flex items-center gap-1"><Gauge size={12} /> Press</span>
        </div>
        <div className="mt-1 grid grid-cols-3 gap-2 font-mono text-sm font-semibold text-chalk">
          <span>≤{Number(machine.normal_vibration_max).toFixed(1)}</span>
          <span>≤{Number(machine.normal_temperature_max).toFixed(0)}°</span>
          <span>≤{Number(machine.normal_pressure_max).toFixed(1)}</span>
        </div>
      </Link>
    </motion.div>
  )
}
