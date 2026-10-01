import { Shirt, Smartphone, Home, Coffee, Sparkles, Dumbbell, BookOpen, Watch, Package } from 'lucide-react'

const ICONS = { Shirt, Smartphone, Home, Coffee, Sparkles, Dumbbell, BookOpen, Watch, Package }

/**
 * Stand-in artwork for products that have no photo: a flat colour plate built from the
 * product's hue, with the category icon on top. If image_url is set, the photo is used instead.
 */
export default function ProductPlate({ product, className = '', iconSize = 56 }) {
  const { hue = 200, image_url: image, id = 0 } = product
  const Icon = ICONS[product.category?.icon || product.category_icon] || Package
  const v = Number(id) % 3

  if (image) {
    return <img src={image} alt={product.name} loading="lazy" className={`h-full w-full object-cover ${className}`} />
  }

  const bg = `hsl(${hue} 72% 91%)`
  const big = `hsl(${hue} 78% 80%)`
  const mid = `hsl(${hue} 68% 64%)`
  const light = `hsl(${hue} 85% 97%)`
  const ink = `hsl(${hue} 55% 20%)`
  const circle = [[150, 55], [55, 60], [140, 150]][v]
  const block = [[26, 108, -12], [112, 30, 10], [30, 40, -8]][v]

  return (
    <div className={`relative h-full w-full overflow-hidden ${className}`} style={{ background: bg }} role="img" aria-label={product.name || 'Product'}>
      <svg viewBox="0 0 200 200" className="absolute inset-0 h-full w-full" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <circle cx={circle[0]} cy={circle[1]} r="74" fill={big} />
        <rect x={block[0]} y={block[1]} width="96" height="74" rx="20" fill={mid} transform={`rotate(${block[2]} ${block[0] + 48} ${block[1] + 37})`} />
        <circle cx={200 - circle[0] * 0.5} cy={200 - circle[1] * 0.6} r="14" fill={light} />
        <circle cx="24" cy="176" r="6" fill={light} />
        <circle cx="176" cy="24" r="4" fill={light} />
      </svg>
      <div className="absolute inset-0 grid place-items-center">
        <span className="grid place-items-center rounded-[22px] bg-white/75 p-5 backdrop-blur-[1px]" style={{ color: ink }}>
          <Icon size={iconSize} strokeWidth={1.6} />
        </span>
      </div>
    </div>
  )
}
