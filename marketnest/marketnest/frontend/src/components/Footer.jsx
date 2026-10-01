import { Link } from 'react-router-dom'
import { Logo } from './Header'

export default function Footer() {
  return (
    <footer className="mt-24 border-t border-line bg-white">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <Logo />
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted">
            A marketplace of independent stalls across Pakistan. Each stall packs and ships its own parcel, and you pay once.
          </p>
        </div>
        <div>
          <h4 className="text-sm font-bold">Shop</h4>
          <ul className="mt-3 space-y-2 text-sm text-muted">
            <li><Link className="hover:text-lapis" to="/shop">All products</Link></li>
            <li><Link className="hover:text-lapis" to="/shop?on_sale=true">On sale</Link></li>
            <li><Link className="hover:text-lapis" to="/orders">Track an order</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-bold">Sell</h4>
          <ul className="mt-3 space-y-2 text-sm text-muted">
            <li><Link className="hover:text-lapis" to="/vendor/apply">Open a stall</Link></li>
            <li><Link className="hover:text-lapis" to="/vendor">Stall dashboard</Link></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-line py-5 text-center text-xs text-muted">
        MarketNest is a portfolio project. Payments are simulated and no real charges are made.
      </div>
    </footer>
  )
}
