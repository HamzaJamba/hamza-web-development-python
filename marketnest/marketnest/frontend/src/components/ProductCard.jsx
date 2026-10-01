import { Link } from 'react-router-dom'
import { useRef } from 'react'
import { Plus } from 'lucide-react'
import ProductPlate from './ProductPlate'
import Stars from './Stars'
import { StallDot } from './Awning'
import { useCart } from '../context/CartContext'
import { useToast } from '../context/ToastContext'
import { pkr, discount } from '../lib/format'

export default function ProductCard({ product }) {
  const { add } = useCart()
  const toast = useToast()
  const plateRef = useRef(null)
  const off = discount(product.price, product.compare_at_price)
  const soldOut = product.stock === 0

  const onAdd = () => {
    if (!add(product, 1, plateRef.current)) toast(soldOut ? 'This one is sold out.' : 'You have all the stock in your cart.', 'error')
  }

  return (
    <article className="group flex flex-col">
      <div className="relative">
        <Link to={`/product/${product.slug}`} className="block overflow-hidden rounded-[20px]" aria-label={product.name}>
          <div ref={plateRef} className="aspect-[5/6] transition-transform duration-500 group-hover:scale-[1.03]">
            <ProductPlate product={product} iconSize={52} />
          </div>
        </Link>
        {off > 0 && (
          <span className="absolute left-3 top-3 rounded-full bg-gulal px-2.5 py-1 text-xs font-bold text-white">{off}% off</span>
        )}
        {!soldOut && product.stock <= 5 && (
          <span className="absolute right-3 top-3 rounded-full bg-white/90 px-2.5 py-1 text-xs font-semibold text-midnight">Only {product.stock} left</span>
        )}
        {soldOut && (
          <span className="absolute right-3 top-3 rounded-full bg-midnight px-2.5 py-1 text-xs font-semibold text-white">Sold out</span>
        )}
        <span className="price-tag absolute -bottom-3 left-3 bg-midnight py-1.5 pl-5 pr-3.5 font-display text-[13px] font-semibold text-white">
          {pkr(product.price)}
        </span>
      </div>

      <div className="mt-6 flex flex-1 flex-col gap-1.5">
        <Link to={`/stall/${product.vendor.slug}`} className="inline-flex w-fit items-center gap-1.5 text-xs font-semibold text-muted hover:text-midnight">
          <StallDot primary={product.vendor.awning_primary} secondary={product.vendor.awning_secondary} />
          {product.vendor.shop_name}
        </Link>
        <Link to={`/product/${product.slug}`} className="line-clamp-2 text-[15px] font-semibold leading-snug hover:text-lapis">
          {product.name}
        </Link>
        <div className="flex items-center gap-2">
          <Stars value={product.rating_avg} showNumber count={product.rating_count || undefined} />
          {product.compare_at_price && <span className="text-xs text-muted line-through">{pkr(product.compare_at_price)}</span>}
        </div>
        <button
          onClick={onAdd}
          disabled={soldOut}
          className="mt-2 inline-flex w-full items-center justify-center gap-1.5 rounded-full border-2 border-midnight px-4 py-2 text-sm font-bold transition-colors hover:bg-midnight hover:text-white disabled:cursor-not-allowed disabled:border-line disabled:text-muted disabled:hover:bg-transparent disabled:hover:text-muted"
        >
          <Plus size={16} strokeWidth={2.6} /> {soldOut ? 'Sold out' : 'Add to cart'}
        </button>
      </div>
    </article>
  )
}

export function ProductCardSkeleton() {
  return (
    <div className="animate-pulse" aria-hidden="true">
      <div className="aspect-[5/6] rounded-[20px] bg-mist" />
      <div className="mt-6 space-y-2">
        <div className="h-3 w-1/3 rounded bg-mist" />
        <div className="h-4 w-4/5 rounded bg-mist" />
        <div className="h-3 w-1/2 rounded bg-mist" />
        <div className="mt-3 h-9 rounded-full bg-mist" />
      </div>
    </div>
  )
}
