import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { SlidersHorizontal, X } from 'lucide-react'
import useFetch from '../lib/useFetch'
import ProductCard, { ProductCardSkeleton } from '../components/ProductCard'
import Pagination from '../components/Pagination'
import { inputCls } from '../components/Field'

const SORTS = {
  newest: ['Newest', '-created_at'],
  popular: ['Best selling', '-sold_count'],
  rating: ['Top rated', '-rating_avg'],
  price_asc: ['Price, low to high', 'price'],
  price_desc: ['Price, high to low', '-price'],
}
const PAGE_SIZE = 12

export default function Shop() {
  const [sp, setSp] = useSearchParams()
  const [showFilters, setShowFilters] = useState(false)
  const q = sp.get('q') || ''
  const category = sp.get('category') || ''
  const sort = sp.get('sort') || 'newest'
  const page = Number(sp.get('page') || 1)
  const onSale = sp.get('on_sale') === 'true'
  const inStock = sp.get('in_stock') === 'true'
  const [min, setMin] = useState(sp.get('min') || '')
  const [max, setMax] = useState(sp.get('max') || '')

  const cats = useFetch('/catalog/categories/')
  const { data, loading, error } = useFetch('/catalog/products/', {
    search: q || undefined, category: category || undefined, ordering: SORTS[sort]?.[1],
    min_price: sp.get('min') || undefined, max_price: sp.get('max') || undefined,
    on_sale: onSale || undefined, in_stock: inStock || undefined, page, page_size: PAGE_SIZE,
  })

  const set = (patch) => {
    const next = new URLSearchParams(sp)
    Object.entries({ page: undefined, ...patch }).forEach(([k, v]) => (v === undefined || v === '' || v === false ? next.delete(k) : next.set(k, v)))
    setSp(next)
  }
  const clear = () => { setMin(''); setMax(''); setSp({}) }
  const activeCat = cats.data?.find((c) => c.slug === category)
  const anyFilter = q || category || onSale || inStock || sp.get('min') || sp.get('max')

  const filters = (
    <div className="space-y-7">
      <div>
        <h3 className="text-sm font-bold">Category</h3>
        <ul className="mt-3 space-y-1">
          <li><button onClick={() => set({ category: '' })} className={`w-full rounded-lg px-3 py-2 text-left text-sm font-semibold ${!category ? 'bg-midnight text-white' : 'hover:bg-mist'}`}>All products</button></li>
          {(cats.data || []).map((c) => (
            <li key={c.slug}>
              <button onClick={() => set({ category: c.slug })} className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm font-semibold ${category === c.slug ? 'bg-midnight text-white' : 'hover:bg-mist'}`}>
                {c.name}<span className="text-xs opacity-60">{c.product_count}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
      <form onSubmit={(e) => { e.preventDefault(); set({ min, max }) }}>
        <h3 className="text-sm font-bold">Price in rupees</h3>
        <div className="mt-3 flex items-center gap-2">
          <input className={inputCls} inputMode="numeric" placeholder="Min" value={min} onChange={(e) => setMin(e.target.value.replace(/\D/g, ''))} aria-label="Minimum price" />
          <input className={inputCls} inputMode="numeric" placeholder="Max" value={max} onChange={(e) => setMax(e.target.value.replace(/\D/g, ''))} aria-label="Maximum price" />
        </div>
        <button className="mt-2 w-full rounded-full border-2 border-midnight py-2 text-sm font-bold hover:bg-midnight hover:text-white">Apply price</button>
      </form>
      <div className="space-y-2.5">
        {[['On sale only', onSale, 'on_sale'], ['In stock only', inStock, 'in_stock']].map(([label, on, key]) => (
          <label key={key} className="flex cursor-pointer items-center gap-2.5 text-sm font-semibold">
            <input type="checkbox" checked={on} onChange={(e) => set({ [key]: e.target.checked ? 'true' : '' })} className="h-4 w-4 accent-lapis" />
            {label}
          </label>
        ))}
      </div>
    </div>
  )

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold md:text-3xl">{q ? `Results for “${q}”` : activeCat ? activeCat.name : onSale ? 'On sale' : 'All products'}</h1>
          <p className="mt-1 text-sm text-muted" aria-live="polite">{loading ? 'Searching…' : `${data?.count ?? 0} products`}</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowFilters(true)} className="inline-flex items-center gap-2 rounded-full border-2 border-line bg-white px-4 py-2 text-sm font-bold lg:hidden"><SlidersHorizontal size={16} /> Filters</button>
          <select value={sort} onChange={(e) => set({ sort: e.target.value })} className={`${inputCls} !w-auto !rounded-full !py-2 font-semibold`} aria-label="Sort products">
            {Object.entries(SORTS).map(([k, [label]]) => <option key={k} value={k}>{label}</option>)}
          </select>
        </div>
      </div>

      <div className="mt-8 grid gap-10 lg:grid-cols-[230px_1fr]">
        <aside className="hidden lg:block" aria-label="Filters">{filters}</aside>

        <div>
          {error ? (
            <div className="rounded-2xl border border-line bg-white p-8 text-center">
              <p className="font-semibold">We could not load products.</p>
              <p className="mt-1 text-sm text-muted">Check that the backend is running on port 8000, then reload.</p>
            </div>
          ) : loading ? (
            <Grid>{Array.from({ length: 8 }, (_, i) => <ProductCardSkeleton key={i} />)}</Grid>
          ) : data.results.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-line bg-white/60 p-12 text-center">
              <p className="font-display text-lg font-semibold">Nothing matches these filters</p>
              <p className="mt-2 text-sm text-muted">Try a broader search or remove a filter.</p>
              {anyFilter && <button onClick={clear} className="mt-5 rounded-full bg-lapis px-6 py-2.5 text-sm font-bold text-white">Clear all filters</button>}
            </div>
          ) : (
            <>
              <Grid>{data.results.map((p) => <ProductCard key={p.id} product={p} />)}</Grid>
              <Pagination page={page} count={data.count} pageSize={PAGE_SIZE} onPage={(n) => { set({ page: n > 1 ? n : '' }); window.scrollTo({ top: 0, behavior: 'smooth' }) }} />
            </>
          )}
        </div>
      </div>

      {showFilters && (
        <div className="fixed inset-0 z-[60] lg:hidden" role="dialog" aria-modal="true" aria-label="Filters">
          <div className="absolute inset-0 bg-midnight/40" onClick={() => setShowFilters(false)} />
          <div className="absolute inset-x-0 bottom-0 max-h-[85vh] overflow-y-auto rounded-t-3xl bg-chalk p-6">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="font-display text-base font-semibold">Filters</h2>
              <button onClick={() => setShowFilters(false)} className="grid h-9 w-9 place-items-center rounded-full hover:bg-mist" aria-label="Close filters"><X size={19} /></button>
            </div>
            {filters}
            <button onClick={() => setShowFilters(false)} className="mt-6 w-full rounded-full bg-lapis py-3 text-sm font-bold text-white">Show {data?.count ?? ''} products</button>
          </div>
        </div>
      )}
    </div>
  )
}

const Grid = ({ children }) => <div className="grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-3 xl:grid-cols-4">{children}</div>
