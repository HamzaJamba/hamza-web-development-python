import api from './axios'

// Auth
export const registerUser = (data) => api.post('/auth/register/', data)
export const verifyOtp = (data) => api.post('/auth/verify-otp/', data)
export const loginUser = (data) => api.post('/auth/login/', data)
export const forgotPassword = (data) => api.post('/auth/forgot-password/', data)
export const resetPassword = (data) => api.post('/auth/reset-password/', data)
export const getMe = () => api.get('/auth/me/')

// Hotels
export const listHotels = (params) => api.get('/hotels/', { params })
export const getHotel = (id) => api.get(`/hotels/${id}/`)

// Rooms
export const listRooms = (params) => api.get('/rooms/', { params })

// Tours
export const listTours = (params) => api.get('/tours/', { params })
export const getTour = (id) => api.get(`/tours/${id}/`)

// Bookings
export const createBooking = (data) => api.post('/bookings/', data)
export const listMyBookings = () => api.get('/bookings/')

// Payments
export const createPayment = (data) => api.post('/payments/', data)

// Reviews
export const listReviews = (params) => api.get('/reviews/', { params })
export const createReview = (data) => api.post('/reviews/', data)

// Wishlist
export const listWishlist = () => api.get('/wishlist/')
export const addToWishlist = (data) => api.post('/wishlist/', data)

// Notifications
export const listNotifications = () => api.get('/notifications/')

// Dashboard
export const getAdminDashboard = () => api.get('/dashboard/admin/')
export const getHotelOwnerDashboard = () => api.get('/dashboard/hotel-owner/')
export const getTourOperatorDashboard = () => api.get('/dashboard/tour-operator/')
export const getCustomerDashboard = () => api.get('/dashboard/customer/')
