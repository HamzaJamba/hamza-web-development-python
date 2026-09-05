import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-6xl font-bold text-[var(--color-primary)]">404</h1>
      <p className="text-black/50 dark:text-white/50 mt-2 mb-6">Page not found.</p>
      <Link to="/" className="bg-[var(--color-primary)] text-white px-6 py-2.5 rounded-xl font-medium">Back to Home</Link>
    </div>
  )
}
