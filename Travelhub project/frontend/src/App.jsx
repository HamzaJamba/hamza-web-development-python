import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import DashboardLayout from './layouts/DashboardLayout'
import ProtectedRoute from './routes/ProtectedRoute'

import Home from './pages/Home'
import Hotels from './pages/Hotels'
import HotelDetails from './pages/HotelDetails'
import Tours from './pages/Tours'
import TourDetails from './pages/TourDetails'
import About from './pages/About'
import Contact from './pages/Contact'
import NotFound from './pages/NotFound'

import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import VerifyOtp from './pages/auth/VerifyOtp'
import ForgotPassword from './pages/auth/ForgotPassword'
import ResetPassword from './pages/auth/ResetPassword'

import Booking from './pages/customer/Booking'
import CustomerDashboard from './pages/customer/CustomerDashboard'
import Wishlist from './pages/customer/Wishlist'
import Notifications from './pages/customer/Notifications'

import AdminDashboard from './pages/admin/AdminDashboard'
import HotelOwnerDashboard from './pages/hotelOwner/HotelOwnerDashboard'
import TourOperatorDashboard from './pages/tourOperator/TourOperatorDashboard'

export default function App() {
  return (
    <Routes>
      {/* Public site */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/hotels" element={<Hotels />} />
        <Route path="/hotels/:id" element={<HotelDetails />} />
        <Route path="/tours" element={<Tours />} />
        <Route path="/tours/:id" element={<TourDetails />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<VerifyOtp />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        <Route path="/booking/:type/:hotelId?/room/:roomId" element={<ProtectedRoute><Booking /></ProtectedRoute>} />
        <Route path="/booking/:type/:tourId" element={<ProtectedRoute><Booking /></ProtectedRoute>} />

        <Route path="/wishlist" element={<ProtectedRoute><Wishlist /></ProtectedRoute>} />
        <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
      </Route>

      {/* Customer dashboard */}
      <Route element={<ProtectedRoute allowedRoles={['customer']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="/customer/dashboard" element={<CustomerDashboard />} />
      </Route>

      {/* Hotel owner dashboard */}
      <Route element={<ProtectedRoute allowedRoles={['hotel_owner']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="/hotel-owner/dashboard" element={<HotelOwnerDashboard />} />
      </Route>

      {/* Tour operator dashboard */}
      <Route element={<ProtectedRoute allowedRoles={['tour_operator']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="/tour-operator/dashboard" element={<TourOperatorDashboard />} />
      </Route>

      {/* Admin dashboard */}
      <Route element={<ProtectedRoute allowedRoles={['admin']}><DashboardLayout /></ProtectedRoute>}>
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
