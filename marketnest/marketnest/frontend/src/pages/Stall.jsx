import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { MapPin } from 'lucide-react'
import { motion } from 'framer-motion'
import useFetch from '../lib/useFetch'
import Awning from '../components/Awning'
import Stars from '../components/Stars'
import ProductCard, { ProductCardSkeleton } from '../components/ProductCard'
import Pagination from '../components/Pagination'

export default function Stall() {
  const { slug } = useParams()
  const [page, setPage] = useState(1)
  const stall = useFetch(`/vendors/${slug}/`)
  const products = useFetch('/catalog/products/', { vendor: slug, page, page_size: 12, ordering: '-sold_count' })

  if (stall.error) {
    return (
      <div className="mx-auto max-w-xl px-4 py-24 text-center">
        <h1 className="font-display text-2xl font-bold">That stall is not open</h1>
        <Link to="/shop" className="mt-6 inline-block rounded-full bg-lapis px-6 py-3 text-sm font-bold text-white">Browse the shop</Link>
      </div>
    )
  }
  const s = stall.data
  return (
    <div>
      {s && (
        <motion.div style={{ originY: 0 }} initial={{ scaleY: 0.4, opacity: 0.6 }} animate={{ scaleY: 1, opacity: 1 }} transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}>
          <Awning primary={s.awning_primary} secondary={s.awning_secondary} stripes={22} />
        </motion.div>
      )}
      <div className="mx-auto max-w-7xl px-4 pb-8 pt-8 sm:px-6">
        {s && (
          <header className="max-w-3xl">
            <h1 className="font-display text-3xl font-bold md:text-4xl">{s.shop_name}</h1>
            <p className="mt-3 text-lg text-muted">{s.tagline}</p>
            <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm font-semibold text-muted">
              <span className="inline-flex items-center gap-1.5"><MapPin size={15} /> {s.city}</span>
              <span>{s.product_count} products</span>
              {s.rating_avg > 0 && <Stars value={s.rating_avg} showNumber />}
            </div>
            {s.description && <p className="mt-5 max-w-[62ch] leading-relaxed">{s.description}</p>}
          </header>
        )}
        <div className="mt-12 grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-3 xl:grid-cols-4">
          {products.loading
            ? Array.from({ length: 4 }, (_, i) => <ProductCardSkeleton key={i} />)
            : (products.data?.results || []).map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
        {products.data && <Pagination page={page} count={products.data.count} pageSize={12} onPage={(n) => { setPage(n); window.scrollTo({ top: 0, behavior: 'smooth' }) }} />}
      </div>
    </div>
  )
}
