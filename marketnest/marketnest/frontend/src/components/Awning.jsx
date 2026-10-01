/**
 * The stall awning: striped canvas with a scalloped edge.
 * Every stall carries its own two colours, and they follow that stall across the whole site.
 */
export default function Awning({ primary = '#2C3BE6', secondary = '#FFFFFF', stripes = 12, className = '' }) {
  const w = 60
  const h = 44
  const r = w / 2
  return (
    <svg
      viewBox={`0 0 ${stripes * w} ${h + r}`}
      className={`block w-full h-auto ${className}`}
      aria-hidden="true"
      focusable="false"
    >
      {Array.from({ length: stripes }, (_, i) => {
        const x = i * w
        return <path key={i} d={`M${x} 0H${x + w}V${h}A${r} ${r} 0 0 1 ${x} ${h}Z`} fill={i % 2 === 0 ? primary : secondary} />
      })}
      <rect width={stripes * w} height="7" fill="#000" opacity="0.08" />
    </svg>
  )
}

/** Two-colour dot that stands for a stall wherever there's no room for a full awning. */
export function StallDot({ primary, secondary, size = 14 }) {
  return (
    <span
      aria-hidden="true"
      className="inline-block shrink-0 rounded-full ring-1 ring-black/10"
      style={{ width: size, height: size, background: `linear-gradient(90deg, ${primary} 50%, ${secondary} 50%)` }}
    />
  )
}
