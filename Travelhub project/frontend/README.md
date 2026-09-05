# 🌍 TravelHub — Frontend (React)

TravelHub is a full-stack **AI-inspired Travel & Tour Booking Platform** where users can explore flights, hotels, and tour packages, make bookings, complete payments, and manage their entire trip from one platform — inspired by Airbnb, Booking.com, Expedia, Agoda, and MakeMyTrip.

This repository contains the **frontend web app**, built with React, delivering a premium, animated, commercial-grade travel booking experience for Admin, Hotel Owner, Tour Operator, and Customer roles.

---

## 📸 Screenshots

> _Add screenshots here (Home page hero, Hotel details, Booking flow, Dashboards, etc.)_

| Home Page | Hotel Details | Booking Flow | Admin Dashboard |
|---|---|---|---|
| ![home](screenshots/home.png) | ![hotel](screenshots/hotel-details.png) | ![booking](screenshots/booking-flow.png) | ![dashboard](screenshots/admin-dashboard.png) |

---

## 👥 User Roles & Dashboards

| Role | Dashboard Highlights |
|---|---|
| 👑 **Admin** | Total users/hotels/operators/bookings/revenue, sales charts, top destinations, pending approvals, full CRUD management |
| 🏨 **Hotel Owner** | Rooms, bookings, monthly revenue, occupancy rate, reviews, availability calendar |
| 🧳 **Tour Operator** | Packages, bookings, revenue, upcoming tours |
| 👤 **Customer** | Upcoming trips, booking history, wishlist, saved hotels/tours, notifications |

---

## 🛠 Tech Stack

- **Library:** React (Vite)
- **Styling:** Tailwind CSS
- **Animations:** Framer Motion
- **Design:** Glassmorphism, gradient backgrounds, smooth page transitions
- **UX:** Dark/Light mode, responsive design, skeleton loaders, toast notifications, interactive maps
- **State/Data:** Context API / hooks, Axios (API layer)
- **Auth:** JWT (access/refresh tokens)

---

## 📂 Folder Structure

```
frontend/
├── src/
│   ├── api/            # Axios instances, endpoint definitions
│   ├── assets/          # Images, videos, icons
│   ├── components/     # Reusable UI components (cards, navbar, footer, modals)
│   ├── context/         # Auth context, theme context, wishlist context
│   ├── hooks/            # Custom hooks (useAuth, useFetch, useDebounce, etc.)
│   ├── layouts/         # Role-based dashboard layouts
│   ├── pages/            # Route-level pages (Home, HotelDetails, Booking, Dashboards)
│   ├── routes/           # Protected/role-based routing
│   ├── services/        # Business logic wrappers over API calls
│   └── utils/            # Helpers, formatters, validators
```

---

## 🌍 Key Pages & Features

### Home Page
- Full-screen hero video (mountains, beaches, cities) + search box (destination, check-in, check-out, guests)
- Popular Destinations carousel (Paris, Dubai, Turkey, Italy, Switzerland, Bali)
- Trending Hotels (image slider, rating, price, Book Now)
- Tour Packages (animated cards, included services, reviews)
- Footer (Contact, About, Terms, Privacy, Social links)

### Authentication
- Login / Register / Forgot Password / OTP Verification / Reset Password (JWT-based)

### Search System
- Instant filtering by destination, budget, country, hotel, tour, date, guests

### Hotel Details Page
- Image gallery, facilities, map, available rooms, reviews, Book button

### Room Details
- Images, price, description, bed type, bathroom, balcony, WiFi, AC, TV, availability calendar

### Tour Details
- Package images/videos, itinerary timeline, included/excluded services, map, reviews

### Booking Flow (6 steps)
`Select Hotel → Select Room → Choose Date → Guest Details → Payment → Booking Confirmed`

### Wishlist
- Save favourite hotels and tours

### Dashboards
- Role-specific analytics with charts: revenue, sales, monthly bookings, popular cities

### Notifications
- Booking confirmed/cancelled, payment success, new tour available

### Reviews
- Rating, comment, image upload

---

## ⚙️ Setup Instructions

```bash
# 1. Clone the repo
git clone <repo-url>
cd travelhub-frontend

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.example .env
# Set: VITE_API_BASE_URL, VITE_STRIPE_KEY (optional)

# 4. Run development server
npm run dev

# 5. Build for production
npm run build
```

---

## 🔑 Environment Variables (`.env`)

```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_STRIPE_PUBLIC_KEY=your-stripe-public-key
```

---

## 🚀 Development Roadmap

1. Project Setup (React + Vite)
2. Authentication UI (JWT + Roles)
3. Home Page UI
4. Hotel Module UI
5. Room Module UI
6. Tour Package Module UI
7. Search & Filters UI
8. Booking Flow UI
9. Payment Module UI
10. Reviews & Wishlist UI
11. Role-based Dashboards & Charts
12. Deployment

---

## 🎯 Project Scale

- 35–45 React pages
- 70–100 Django REST APIs (backend)
- Role-based authentication (Admin / Hotel Owner / Tour Operator / Customer)
- Production-style architecture, portfolio & interview-ready

---

## 👨‍💻 Author

**Hamza** — Final Year BS Software Engineering, COMSATS University Islamabad (Vehari Campus)
Backend-focused Full Stack Developer (Django REST + React)
