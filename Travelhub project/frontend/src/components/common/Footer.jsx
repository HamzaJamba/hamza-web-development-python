import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="bg-[var(--color-dark)] text-white/80 mt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 grid grid-cols-1 md:grid-cols-4 gap-10">
        <div>
          <h3 className="text-white text-xl font-bold mb-3">🌍 TravelHub</h3>
          <p className="text-sm leading-relaxed">
            Explore the world with confidence — flights, hotels & tours, all in one place.
          </p>
          <div className="flex gap-4 mt-4 text-sm">
            <a href="#" className="hover:text-[var(--color-accent)]">Facebook</a>
            <a href="#" className="hover:text-[var(--color-accent)]">Instagram</a>
            <a href="#" className="hover:text-[var(--color-accent)]">Twitter</a>
            <a href="#" className="hover:text-[var(--color-accent)]">YouTube</a>
          </div>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3">Company</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/about" className="hover:text-white">About Us</Link></li>
            <li><Link to="/contact" className="hover:text-white">Contact</Link></li>
            <li><Link to="/careers" className="hover:text-white">Careers</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3">Explore</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/hotels" className="hover:text-white">Hotels</Link></li>
            <li><Link to="/tours" className="hover:text-white">Tour Packages</Link></li>
            <li><Link to="/wishlist" className="hover:text-white">Wishlist</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3">Legal</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/terms" className="hover:text-white">Terms of Service</Link></li>
            <li><Link to="/privacy" className="hover:text-white">Privacy Policy</Link></li>
          </ul>
        </div>
      </div>

      <div className="border-t border-white/10 py-5 text-center text-xs text-white/50">
        © {new Date().getFullYear()} TravelHub. All rights reserved.
      </div>
    </footer>
  )
}
