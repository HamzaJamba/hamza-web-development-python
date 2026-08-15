import client from "./client";

// ---- Restaurants ----
export const listRestaurants = (params) => client.get("/restaurants/", { params }).then((r) => r.data);
export const getRestaurant = (id) => client.get(`/restaurants/${id}/`).then((r) => r.data);
export const createRestaurant = (payload) => client.post("/restaurants/", payload).then((r) => r.data);
export const updateRestaurant = (id, payload) => client.patch(`/restaurants/${id}/`, payload).then((r) => r.data);
export const myRestaurants = () => client.get("/restaurants/mine/").then((r) => r.data);
export const toggleRestaurantOpen = (id) => client.post(`/restaurants/${id}/toggle-open/`).then((r) => r.data);
export const approveRestaurant = (id, status) =>
  client.post(`/restaurants/${id}/approve/`, { status }).then((r) => r.data);

// ---- Menu ----
export const listCategories = () => client.get("/menu/categories/").then((r) => r.data);
export const createCategory = (payload) => client.post("/menu/categories/", payload).then((r) => r.data);
export const listFoodItems = (params) => client.get("/menu/food-items/", { params }).then((r) => r.data);
export const getFoodItem = (id) => client.get(`/menu/food-items/${id}/`).then((r) => r.data);
export const createFoodItem = (payload) => client.post("/menu/food-items/", payload).then((r) => r.data);
export const updateFoodItem = (id, payload) => client.patch(`/menu/food-items/${id}/`, payload).then((r) => r.data);
export const deleteFoodItem = (id) => client.delete(`/menu/food-items/${id}/`);

// ---- Wishlist ----
export const listWishlist = () => client.get("/menu/wishlist/").then((r) => r.data);
export const addWishlist = (food_item) => client.post("/menu/wishlist/", { food_item }).then((r) => r.data);
export const removeWishlist = (id) => client.delete(`/menu/wishlist/${id}/`);

// ---- Cart ----
export const getCart = () => client.get("/cart/").then((r) => r.data);
export const addCartItem = (payload) => client.post("/cart/items/", payload).then((r) => r.data);
export const updateCartItem = (id, quantity) => client.patch(`/cart/items/${id}/`, { quantity }).then((r) => r.data);
export const removeCartItem = (id) => client.delete(`/cart/items/${id}/`).then((r) => r.data);
export const clearCart = () => client.delete("/cart/");

// ---- Orders ----
export const checkout = (payload) => client.post("/orders/checkout/", payload).then((r) => r.data);
export const listOrders = (params) => client.get("/orders/", { params }).then((r) => r.data);
export const getOrder = (id) => client.get(`/orders/${id}/`).then((r) => r.data);
export const updateOrderStatus = (id, status) => client.post(`/orders/${id}/status/`, { status }).then((r) => r.data);
export const cancelOrder = (id, reason) => client.post(`/orders/${id}/cancel/`, { reason }).then((r) => r.data);
export const listCoupons = () => client.get("/orders/coupons/").then((r) => r.data);
export const createCoupon = (payload) => client.post("/orders/coupons/", payload).then((r) => r.data);

// ---- Payments ----
export const getPayment = (orderId) => client.get(`/payments/${orderId}/`).then((r) => r.data);
export const confirmPayment = (orderId, transaction_id) =>
  client.post(`/payments/${orderId}/confirm/`, { transaction_id }).then((r) => r.data);

// ---- Riders ----
export const getRiderProfile = () => client.get("/riders/me/").then((r) => r.data);
export const updateRiderProfile = (payload) => client.patch("/riders/me/", payload).then((r) => r.data);
export const toggleOnline = () => client.post("/riders/toggle-online/").then((r) => r.data);
export const updateLocation = (payload) => client.post("/riders/location/", payload).then((r) => r.data);
export const availableDeliveries = () => client.get("/riders/deliveries/available/").then((r) => r.data);
export const myDeliveries = () => client.get("/riders/deliveries/mine/").then((r) => r.data);
export const acceptDelivery = (id) => client.post(`/riders/deliveries/${id}/accept/`).then((r) => r.data);
export const updateDeliveryStatus = (id, status) =>
  client.post(`/riders/deliveries/${id}/status/`, { status }).then((r) => r.data);

// ---- Reviews ----
export const listReviews = (params) => client.get("/reviews/", { params }).then((r) => r.data);
export const createReview = (payload) => client.post("/reviews/", payload).then((r) => r.data);
export const flagReview = (id) => client.post(`/reviews/${id}/flag/`).then((r) => r.data);

// ---- Notifications ----
export const listNotifications = () => client.get("/notifications/").then((r) => r.data);
export const markNotificationRead = (id) => client.post(`/notifications/${id}/read/`).then((r) => r.data);
export const markAllNotificationsRead = () => client.post("/notifications/mark-all-read/");

// ---- Dashboard ----
export const adminDashboard = () => client.get("/dashboard/admin/").then((r) => r.data);
export const restaurantDashboard = (restaurant_id) =>
  client.get("/dashboard/restaurant/", { params: { restaurant_id } }).then((r) => r.data);
export const getPlatformSettings = () => client.get("/dashboard/settings/").then((r) => r.data);
export const updatePlatformSettings = (payload) => client.patch("/dashboard/settings/", payload).then((r) => r.data);

// ---- Admin user management ----
export const listUsers = (params) => client.get("/accounts/admin/users/", { params }).then((r) => r.data);
export const approveUser = (id) => client.post(`/accounts/admin/users/${id}/approve/`).then((r) => r.data);
export const suspendUser = (id) => client.post(`/accounts/admin/users/${id}/suspend/`).then((r) => r.data);
export const activateUser = (id) => client.post(`/accounts/admin/users/${id}/activate/`).then((r) => r.data);

// ---- Menu bulk import ----
export const bulkImportFoodItems = (restaurantId, file) => {
  const form = new FormData();
  form.append("restaurant", restaurantId);
  form.append("file", file);
  return client.post("/menu/food-items/bulk-import/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((r) => r.data);
};

// ---- Email verification ----
export const sendEmailVerification = () => client.post("/accounts/verify-email/").then((r) => r.data);
export const confirmEmailVerification = (payload) =>
  client.post("/accounts/verify-email/confirm/", payload).then((r) => r.data);

// ---- Rider CNIC admin review ----
export const adminListRiders = (params) => client.get("/riders/admin/list/", { params }).then((r) => r.data);
export const adminReviewCnic = (riderId, payload) =>
  client.post(`/riders/admin/${riderId}/review-cnic/`, payload).then((r) => r.data);
