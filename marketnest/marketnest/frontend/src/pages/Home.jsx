import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Truck, Banknote, ShieldCheck, Shirt, Smartphone, Home as HomeIcon, Coffee, Sparkles, Dumbbell, BookOpen, Watch, Package } from 'lucide-react'
import useFetch from '../lib/useFetch'
import Awning from '../components/Awning'
import ProductPlate from '../components/ProductPlate'
import ProductCard, { ProductCardSkeleton } from '../components/ProductCard'
import StallCard from '../components/StallCard'
import { pkr } from '../lib/format'

const ICONS = { Shirt, Smartphone, Home: HomeIcon, Coffee, Sparkles, Dumbbell, BookOpen, Watch, Package }
const ease = [0.22, 1, 0.36, 1]
const HEADLINE = ['Shop', 'the', 'whole', 'bazaar,', 'pay', 'once.']

export default function Home() {
  const top = useFetch('/catalog/products/', { ordering: '-sold_count', page_size: 3 })
  const cats = useFetch('/catalog/categories/')
  const fresh = useFetch('/catalog/products/', { ordering: '-created_at', page_size: 8 })
  const sale = useFetch('/catalog/products/', { on_sale: true, page_size: 4 })
  const stalls = useFetch('/vendors/')

  return (
    <>
      {/* The one orchestrated moment on the site: the awning unrolls, then the headline lands. */}
      <section className="relative overflow-hidden">
        <motion.div style={{ originY: 0 }} initial={{ scaleY: 0 }} animate={{ scaleY: 1 }} transition={{ duration: 1, ease }}>
          <Awning primary="#2C3BE6" secondary="#FFFFFF" stripes={26} />
        </motion.div>

        <div className="mx-auto grid max-w-7xl gap-10 px-4 pb-16 pt-8 sm:px-6 lg:grid-cols-[1.15fr_1fr] lg:pt-14">
          <div>
            <h1 className="font-display text-[clamp(2.1rem,5.2vw,4rem)] font-bold leading-[1.08] tracking-tight">
              {HEADLINE.map((w, i) => (
                <span key={i} className="mr-[0.28em] inline-block overflow-hidden align-bottom">
                  <motion.span className="inline-block" initial={{ y: '110%' }} animate={{ y: 0 }}
                    transition={{ duration: 0.7, ease, delay: 0.85 + i * 0.07 }}>{w}</motion.span>
                </span>
              ))}
            </h1>
            <motion.p className="mt-6 max-w-[52ch] text-lg leading-relaxed text-muted"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.45, duration: 0.6 }}>
              Independent stalls from across Pakistan sell here. Fill one cart from any of them, check out once, and each stall packs and ships its own parcel.
            </motion.p>
            <motion.div className="mt-8 flex flex-wrap gap-3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.6, duration: 0.6 }}>
              <Link to="/shop" className="rounded-full bg-lapis px-7 py-3.5 text-[15px] font-bold text-white transition-colors hover:bg-lapis-dark">Start shopping</Link>
              <Link to="/vendor/apply" className="rounded-full border-2 border-midnight px-7 py-3 text-[15px] font-bold transition-colors hover:bg-midnight hover:text-white">Open your stall</Link>
            </motion.div>
            <motion.ul className="mt-10 grid gap-3 text-sm font-semibold sm:grid-cols-3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.8, duration: 0.6 }}>
              {[[Truck, 'Every stall ships its own parcel'], [Banknote, 'Cash on delivery or card'], [ShieldCheck, 'Free shipping over Rs 5,000']].map(([Icon, text]) => (
                <li key={text} className="flex items-start gap-2.5"><Icon size={18} className="mt-0.5 shrink-0 text-lapis" />{text}</li>
              ))}
            </motion.ul>
          </div>

          <Collage products={top.data?.results} loading={top.loading} />
        </div>
      </section>

      <div className="mx-auto max-w-7xl space-y-24 px-4 sm:px-6">
        {/* categories */}
        <section aria-label="Categories">
          <div className="no-scrollbar -mx-4 flex gap-3 overflow-x-auto px-4 pb-2 sm:mx-0 sm:px-0">
            {(cats.data || []).map((c) => {
              const Icon = ICONS[c.icon] || Package
              return (
                <Link key={c.slug} to={`/shop?category=${c.slug}`}
                  className="group flex shrink-0 items-center gap-3 rounded-full py-2 pl-2 pr-5 transition-transform hover:-translate-y-0.5"
                  style={{ background: `hsl(${c.hue} 72% 91%)` }}>
                  <span className="grid h-10 w-10 place-items-center rounded-full bg-white/80" style={{ color: `hsl(${c.hue} 55% 22%)` }}><Icon size={19} /></span>
                  <span className="text-sm font-bold" style={{ color: `hsl(${c.hue} 55% 18%)` }}>{c.name}</span>
                  <span className="text-xs font-semibold opacity-60">{c.product_count}</span>
                </Link>
              )
            })}
          </div>
        </section>

        <ProductSection title="Fresh on the stalls" more="/shop" state={fresh} count={8} />

        {(sale.loading || sale.data?.results?.length > 0) && (
          <ProductSection title="On sale now" more="/shop?on_sale=true" state={sale} count={4} />
        )}

        <section>
          <SectionHead title="Stalls to visit" />
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {(stalls.data || []).slice(0, 6).map((s) => <StallCard key={s.slug} stall={s} />)}
          </div>
        </section>

        <section className="overflow-hidden rounded-[28px] bg-midnight text-white">
          <Awning primary="#FFC533" secondary="#1D1B54" stripes={28} className="opacity-95" />
          <div className="grid gap-8 px-8 pb-12 pt-6 md:grid-cols-[1.4fr_1fr] md:px-14">
            <div>
              <h2 className="font-display text-2xl font-bold leading-tight md:text-3xl">Sell on MarketNest</h2>
              <p className="mt-4 max-w-[55ch] leading-relaxed text-white/75">
                Open a stall, list your products, and pack the orders that come in. The marketplace keeps a small commission on each sale (10% by default) and you see every rupee in your dashboard.
              </p>
            </div>
            <div className="flex items-end md:justify-end">
              <Link to="/vendor/apply" className="rounded-full bg-sun px-7 py-3.5 text-[15px] font-bold text-midnight transition-transform hover:-translate-y-0.5">Open your stall</Link>
            </div>
          </div>
        </section>
      </div>
    </>
  )
}

function SectionHead({ title, more }) {
  return (
    <div className="flex items-end justify-between gap-4">
      <h2 className="font-display text-2xl font-bold tracking-tight md:text-[28px]">{title}</h2>
      {more && <Link to={more} className="shrink-0 text-sm font-bold text-lapis hover:underline">See all</Link>}
    </div>
  )
}

function ProductSection({ title, more, state, count }) {
  return (
    <section>
      <SectionHead title={title} more={more} />
      <div className="mt-8 grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-3 lg:grid-cols-4">
        {state.loading
          ? Array.from({ length: count }, (_, i) => <ProductCardSkeleton key={i} />)
          : (state.data?.results || []).map((p) => <ProductCard key={p.id} product={p} />)}
      </div>
    </section>
  )
}

/** Three best-sellers laid out like goods on a stall counter. */
function Collage({ products, loading }) {
  const slots = [
    { cls: 'left-0 top-8 w-[54%]', rot: -3 },
    { cls: 'right-0 top-0 w-[42%]', rot: 4 },
    { cls: 'right-[8%] bottom-0 w-[46%]', rot: -2 },
  ]
  return (
    <div className="relative mx-auto hidden h-[440px] w-full max-w-[520px] lg:block" aria-label="Best sellers">
      {slots.map((s, i) => {
        const p = products?.[i]
        return (
          <motion.div key={i} className={`absolute ${s.cls}`} style={{ rotate: s.rot }}
            initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease, delay: 1.3 + i * 0.12 }}>
            <div className="relative aspect-[4/5] overflow-hidden rounded-[22px] bg-mist shadow-[0_18px_40px_-18px_rgba(29,27,84,0.45)]">
              {p && <Link to={`/product/${p.slug}`} className="block h-full" aria-label={p.name}><ProductPlate product={p} iconSize={46} /></Link>}
            </div>
            {p && <span className="price-tag absolute -bottom-3 left-4 bg-midnight py-1.5 pl-5 pr-3.5 font-display text-xs font-semibold text-white">{pkr(p.price)}</span>}
          </motion.div>
        )
      })}
      {loading && <span className="sr-only">Loading best sellers</span>}
    </div>
  )
}
