import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";

import Home from "./pages/customer/Home";
import RestaurantDetail from "./pages/customer/RestaurantDetail";
import Cart from "./pages/customer/Cart";
import Checkout from "./pages/customer/Checkout";
import Orders from "./pages/customer/Orders";
import OrderDetail from "./pages/customer/OrderDetail";
import Wishlist from "./pages/customer/Wishlist";
import Profile from "./pages/customer/Profile";
import Notifications from "./pages/customer/Notifications";

import RestaurantDashboard from "./pages/restaurant/RestaurantDashboard";
import MenuManager from "./pages/restaurant/MenuManager";
import RestaurantOrders from "./pages/restaurant/RestaurantOrders";

import RiderDashboard from "./pages/rider/RiderDashboard";

import AdminDashboard from "./pages/admin/AdminDashboard";
import Approvals from "./pages/admin/Approvals";
import AdminRiders from "./pages/admin/AdminRiders";
import Coupons from "./pages/admin/Coupons";
import Settings from "./pages/admin/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/verify-email" element={<ProtectedRoute><VerifyEmail /></ProtectedRoute>} />

          <Route path="/" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><Home /></ProtectedRoute>} />
          <Route path="/restaurants/:id" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><RestaurantDetail /></ProtectedRoute>} />
          <Route path="/cart" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><Cart /></ProtectedRoute>} />
          <Route path="/checkout" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><Checkout /></ProtectedRoute>} />
          <Route path="/orders" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><Orders /></ProtectedRoute>} />
          <Route path="/orders/:id" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><OrderDetail /></ProtectedRoute>} />
          <Route path="/wishlist" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><Wishlist /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><Profile /></ProtectedRoute>} />
          <Route path="/notifications" element={<ProtectedRoute allowedRoles={["CUSTOMER"]}><Notifications /></ProtectedRoute>} />

          <Route path="/restaurant" element={<ProtectedRoute allowedRoles={["RESTAURANT_OWNER"]}><RestaurantDashboard /></ProtectedRoute>} />
          <Route path="/restaurant/menu" element={<ProtectedRoute allowedRoles={["RESTAURANT_OWNER"]}><MenuManager /></ProtectedRoute>} />
          <Route path="/restaurant/orders" element={<ProtectedRoute allowedRoles={["RESTAURANT_OWNER"]}><RestaurantOrders /></ProtectedRoute>} />

          <Route path="/rider" element={<ProtectedRoute allowedRoles={["RIDER"]}><RiderDashboard /></ProtectedRoute>} />

          <Route path="/admin" element={<ProtectedRoute allowedRoles={["ADMIN"]}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/approvals" element={<ProtectedRoute allowedRoles={["ADMIN"]}><Approvals /></ProtectedRoute>} />
          <Route path="/admin/riders" element={<ProtectedRoute allowedRoles={["ADMIN"]}><AdminRiders /></ProtectedRoute>} />
          <Route path="/admin/coupons" element={<ProtectedRoute allowedRoles={["ADMIN"]}><Coupons /></ProtectedRoute>} />
          <Route path="/admin/settings" element={<ProtectedRoute allowedRoles={["ADMIN"]}><Settings /></ProtectedRoute>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
