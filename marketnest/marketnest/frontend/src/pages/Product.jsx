import { useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Minus, Plus, Truck, Star } from 'lucide-react'
import api, { readError } from '../lib/api'
import useFetch from '../lib/useFetch'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import ProductPlate from '../components/ProductPlate'
import ProductCard from '../components/ProductCard'
import Awning from '../components/Awning'
import Stars from '../components/Stars'
import { inputCls } from '../components/Field'
import { pkr, discount, shortDate } from '../lib/format'

export default function Product() {
  const { slug } = useParams()
  const { data: p, loading, error, reload } = useFetch(`/catalog/products/${slug}/`)
  const reviews = useFetch(p ? '/reviews/' : null, p ? { product: p.id } : undefined)
  const more = useFetch(p ? '/catalog/products/' : null, p ? { vendor: p.vendor.slug, page_size: 5 } : undefined)
  const { add, setOpen } = useCart()
  const toast = useToast()
  const [qty, setQty] = useState(1)
  const plate = useRef(null)

  if (error) return <Missing />
  if (loading || !p) return <div className="mx-auto grid min-h-[60vh] max-w-7xl place-items-center text-sm text-muted">Loading…</div>

  const off = discount(p.price, p.compare_at_price)
  const soldOut = p.stock === 0
  const others = (more.data?.results || []).filter((x) => x.id !== p.id).slice(0, 4)

  const onAdd = () => {
    if (add(p, qty, plate.current)) toast(`${qty} added to your cart`)
    else toast('You already have all the stock in your cart.', 'error')
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <nav className="mb-6 text-sm text-muted" aria-label="Breadcrumb">
        <Link className="hover:text-lapis" to="/shop">Shop</Link> / <Link className="hover:text-lapis" to={`/shop?category=${p.category.slug}`}>{p.category.name}</Link>
      </nav>

      <div className="grid gap-10 lg:grid-cols-2 lg:gap-16">
        <div ref={plate} className="aspect-square overflow-hidden rounded-[28px]">
          <ProductPlate product={p} iconSize={110} />
        </div>

        <div>
          <Link to={`/stall/${p.vendor.slug}`} className="block w-48 overflow-hidden rounded-xl">
            <Awning primary={p.vendor.awning_primary} secondary={p.vendor.awning_secondary} stripes={8} className="-mb-2" />
            <span className="block rounded-b-xl border border-t-0 border-line bg-white px-3 pb-2 pt-3 text-sm font-bold hover:text-lapis">{p.vendor.shop_name}</span>
          </Link>

          <h1 className="mt-5 font-display text-2xl font-bold leading-tight md:text-[32px]">{p.name}</h1>
          <a href="#reviews" className="mt-3 inline-block"><Stars value={p.rating_avg} size={17} showNumber count={p.rating_count} /></a>

          <div className="mt-6 flex flex-wrap items-baseline gap-3">
            <span className="font-display text-3xl font-bold">{pkr(p.price)}</span>
            {p.compare_at_price && <span className="text-lg text-muted line-through">{pkr(p.compare_at_price)}</span>}
            {off > 0 && <span className="rounded-full bg-gulal px-3 py-1 text-sm font-bold text-white">Save {off}%</span>}
          </div>

          <p className="mt-6 max-w-[60ch] leading-relaxed text-muted">{p.description}</p>

          <p className={`mt-6 text-sm font-bold ${soldOut ? 'text-gulal' : p.stock <= 5 ? 'text-gulal' : 'text-midnight'}`}>
            {soldOut ? 'Sold out' : p.stock <= 5 ? `Only ${p.stock} left` : 'In stock'}
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <div className="inline-flex items-center rounded-full border-2 border-line bg-white">
              <button onClick={() => setQty((q) => Math.max(1, q - 1))} className="grid h-11 w-11 place-items-center rounded-full hover:bg-mist" aria-label="Decrease quantity"><Minus size={16} /></button>
              <span className="w-9 text-center font-bold" aria-live="polite">{qty}</span>
              <button onClick={() => setQty((q) => Math.min(p.stock, 20, q + 1))} className="grid h-11 w-11 place-items-center rounded-full hover:bg-mist" aria-label="Increase quantity"><Plus size={16} /></button>
            </div>
            <button onClick={onAdd} disabled={soldOut} className="rounded-full bg-lapis px-8 py-3 text-[15px] font-bold text-white transition-colors hover:bg-lapis-dark disabled:cursor-not-allowed disabled:bg-line disabled:text-muted">
              {soldOut ? 'Sold out' : 'Add to cart'}
            </button>
            <button onClick={() => setOpen(true)} className="text-sm font-bold text-lapis hover:underline">View cart</button>
          </div>

          <p className="mt-7 flex items-center gap-2.5 text-sm text-muted"><Truck size={18} className="text-lapis" /> Ships from {p.vendor.shop_name}. Free shipping over Rs 5,000.</p>
        </div>
      </div>

      <Reviews product={p} state={reviews} onPosted={() => { reviews.reload(); reload() }} />

      {others.length > 0 && (
        <section className="mt-20">
          <h2 className="font-display text-2xl font-bold">More from {p.vendor.shop_name}</h2>
          <div className="mt-8 grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-4">{others.map((o) => <ProductCard key={o.id} product={o} />)}</div>
        </section>
      )}
    </div>
  )
}

function Reviews({ product, state, onPosted }) {
  const { user } = useAuth()
  const toast = useToast()
  const list = state.data || []
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [busy, setBusy] = useState(false)
  const dist = [5, 4, 3, 2, 1].map((n) => ({ n, c: list.filter((r) => r.rating === n).length }))

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      await api.post('/reviews/', { product: product.id, rating, comment })
      toast('Review saved')
      setComment('')
      onPosted()
    } catch (err) { toast(readError(err).message, 'error') } finally { setBusy(false) }
  }

  return (
    <section id="reviews" className="mt-20 scroll-mt-24">
      <h2 className="font-display text-2xl font-bold">Reviews</h2>
      <div className="mt-8 grid gap-10 lg:grid-cols-[320px_1fr]">
        <div>
          <div className="flex items-end gap-3">
            <span className="font-display text-5xl font-bold">{product.rating_count ? Number(product.rating_avg).toFixed(1) : '–'}</span>
            <div className="pb-1.5"><Stars value={product.rating_avg} size={16} /><p className="mt-1 text-xs text-muted">{product.rating_count} {product.rating_count === 1 ? 'review' : 'reviews'}</p></div>
          </div>
          <ul className="mt-5 space-y-1.5">
            {dist.map(({ n, c }) => (
              <li key={n} className="flex items-center gap-2 text-xs font-semibold text-muted">
                <span className="w-3">{n}</span>
                <span className="h-2 flex-1 overflow-hidden rounded-full bg-mist"><span className="block h-full rounded-full bg-sun" style={{ width: list.length ? `${(c / list.length) * 100}%` : 0 }} /></span>
                <span className="w-4 text-right">{c}</span>
              </li>
            ))}
          </ul>

          <div className="mt-8">
            {user ? (
              <form onSubmit={submit} className="space-y-3">
                <p className="text-sm font-bold">Rate this product</p>
                <div className="flex gap-1" role="radiogroup" aria-label="Your rating">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button type="button" key={n} onClick={() => setRating(n)} role="radio" aria-checked={rating === n} aria-label={`${n} stars`} className="rounded p-0.5">
                      <Star size={26} className={n <= rating ? 'fill-sun text-sun' : 'text-line'} strokeWidth={n <= rating ? 0 : 2} />
                    </button>
                  ))}
                </div>
                <textarea className={inputCls} rows={3} placeholder="What did you think? (optional)" value={comment} onChange={(e) => setComment(e.target.value)} aria-label="Your review" />
                <button disabled={busy} className="rounded-full bg-midnight px-6 py-2.5 text-sm font-bold text-white hover:bg-lapis disabled:opacity-60">{busy ? 'Saving…' : 'Post review'}</button>
                <p className="text-xs text-muted">Posting again replaces your earlier review.</p>
              </form>
            ) : (
              <p className="text-sm text-muted"><Link to={`/login?next=${encodeURIComponent(location.pathname)}`} className="font-bold text-lapis hover:underline">Log in</Link> to review this product.</p>
            )}
          </div>
        </div>

        <div>
          {list.length === 0 ? (
            <p className="rounded-2xl border border-dashed border-line p-8 text-center text-sm text-muted">No reviews yet. Be the first to rate this product.</p>
          ) : (
            <ul className="divide-y divide-line">
              {list.map((r) => (
                <li key={r.id} className="py-5 first:pt-0">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                    <Stars value={r.rating} />
                    <span className="text-sm font-bold">{r.user_name}</span>
                    {r.verified_purchase && <span className="rounded-full bg-pistachio px-2.5 py-0.5 text-xs font-bold text-midnight">Bought here</span>}
                    <span className="text-xs text-muted">{shortDate(r.created_at)}</span>
                  </div>
                  {r.comment && <p className="mt-2 max-w-[65ch] leading-relaxed">{r.comment}</p>}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  )
}

function Missing() {
  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center">
      <h1 className="font-display text-2xl font-bold">We could not find that product</h1>
      <p className="mt-3 text-muted">It may have been removed by the stall.</p>
      <Link to="/shop" className="mt-6 inline-block rounded-full bg-lapis px-6 py-3 text-sm font-bold text-white">Back to the shop</Link>
    </div>
  )
}
