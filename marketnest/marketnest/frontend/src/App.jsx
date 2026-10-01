import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import { ToastProvider } from './context/ToastContext'
import Header from './components/Header'
import Footer from './components/Footer'
import CartDrawer from './components/CartDrawer'
import RequireAuth from './components/RequireAuth'

import Home from './pages/Home'
import Shop from './pages/Shop'
import Product from './pages/Product'
import Stall from './pages/Stall'
import Auth from './pages/Auth'
import Checkout from './pages/Checkout'
import Orders from './pages/Orders'
import OrderDetail from './pages/OrderDetail'
import VendorApply from './pages/VendorApply'
import VendorDashboard from './pages/VendorDashboard'
import AdminConsole from './pages/AdminConsole'

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <CartProvider>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/shop" element={<Shop />} />
                <Route path="/product/:slug" element={<Product />} />
                <Route path="/stall/:slug" element={<Stall />} />
                <Route path="/login" element={<Auth />} />
                <Route path="/register" element={<Auth />} />
                <Route path="/vendor/apply" element={<RequireAuth><VendorApply /></RequireAuth>} />
                <Route path="/vendor" element={<RequireAuth><VendorDashboard /></RequireAuth>} />
                <Route path="/admin-console" element={<RequireAuth><AdminConsole /></RequireAuth>} />
                <Route path="/checkout" element={<RequireAuth><Checkout /></RequireAuth>} />
                <Route path="/orders" element={<RequireAuth><Orders /></RequireAuth>} />
                <Route path="/orders/:id" element={<RequireAuth><OrderDetail /></RequireAuth>} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            <Footer />
            <CartDrawer />
          </div>
        </CartProvider>
      </AuthProvider>
    </ToastProvider>
  )
}

function NotFound() {
  return (
    <div className="mx-auto grid min-h-[50vh] max-w-3xl place-items-center px-4 text-center">
      <div>
        <h1 className="font-display text-3xl font-bold">This stall doesn't exist</h1>
        <p className="mt-3 text-muted">The page you're looking for has moved or never existed.</p>
      </div>
    </div>
  )
}
