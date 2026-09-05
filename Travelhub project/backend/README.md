# 🌍 TravelHub — Backend (Django REST Framework)

TravelHub is a full-stack **AI-inspired Travel & Tour Booking Platform** where users can explore flights, hotels, and tour packages, make bookings, complete payments, and manage their entire trip from one platform — inspired by Airbnb, Booking.com, Expedia, Agoda, and MakeMyTrip.

This repository contains the **backend API**, built with Django REST Framework and PostgreSQL, powering role-based dashboards for Admin, Hotel Owners, Tour Operators, and Customers.

---

## 📸 Screenshots

> _Add screenshots here (Admin dashboard, API docs / Swagger, DB schema, Postman tests, etc.)_

| Admin Dashboard | Hotel Owner Panel | API (Swagger/Postman) |
|---|---|---|
| ![admin](screenshots/admin-dashboard.png) | ![hotel](screenshots/hotel-owner.png) | ![api](screenshots/api-docs.png) |

---

## 👥 User Roles

| Role | Capabilities |
|---|---|
| 👑 **Admin** | Full system control — manage hotels, tour operators, customers, packages, bookings, payments, reviews, coupons, notifications, CMS pages, and analytics |
| 🏨 **Hotel Owner** | Registers → gets admin-approved → manages rooms, pricing, availability, bookings & revenue |
| 🧳 **Tour Operator** | Manages tour packages, schedules, bookings & revenue |
| 👤 **Customer** | Browses, books, pays, reviews, and manages trips/wishlist |

---

## 🛠 Tech Stack

- **Framework:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Auth:** JWT Authentication (role-based access control)
- **Payments:** Stripe / PayPal (planned) + Demo (Cash / Fake Card)
- **Other:** Django Filters (search/filtering), Django Signals (notifications), Celery (future async tasks)

---

## 📂 App Structure

```
backend/
├── accounts/         # Users, roles, JWT auth, OTP, password reset
├── hotels/            # Hotel owner profiles, hotel CRUD, approval flow
├── rooms/              # Room CRUD, pricing, facilities, availability calendar
├── tours/              # Tour operator profiles, tour packages, schedules
├── bookings/          # Booking lifecycle (hotel + tour), status management
├── payments/          # Payment records, gateway integration, demo payments
├── reviews/            # Ratings, comments, review images
├── notifications/     # Booking/payment/system notifications
├── wishlist/           # Saved hotels & tours
├── dashboard/         # Analytics: revenue, occupancy, sales charts
└── common/             # Shared utils, permissions, pagination, mixins
```

---

## 🗄 Core Database Models

`Users` · `Hotels` · `Rooms` · `RoomImages` · `TourOperators` · `TourPackages` · `Bookings` · `Payments` · `Reviews` · `Wishlist` · `Notifications` · `Coupons`

---

## 🔐 Authentication Flow

- Register → OTP Verification → Login (JWT access/refresh tokens)
- Forgot Password → OTP → Reset Password
- Role-based permissions enforced on every endpoint (Admin / Hotel Owner / Tour Operator / Customer)

---

## 🔎 Key Features

- Instant search & filtering (destination, budget, dates, guests, rating)
- Hotel & room management with availability calendar
- Tour package management with itinerary/schedule
- 6-step booking flow: Hotel → Room → Date → Guest Details → Payment → Confirmation
- Coupons & discounts
- Wishlist (hotels + tours)
- Review & rating system with images
- Real-time-style notifications (booking, payment, cancellation)
- Admin approval workflow for Hotel Owners & Tour Operators
- Dashboard analytics: revenue, monthly sales, top destinations, occupancy rate

---

## ⚙️ Setup Instructions

```bash
# 1. Clone the repo
git clone <repo-url>
cd travelhub-backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Set: SECRET_KEY, DEBUG, DATABASE_URL, JWT settings, EMAIL settings

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

---

## 🔑 Environment Variables (`.env`)

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/travelhub
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

---

## 📊 API Overview (planned: 70–100 endpoints across 12+ apps)

| Module | Sample Endpoints |
|---|---|
| Auth | `/api/auth/register/`, `/api/auth/login/`, `/api/auth/verify-otp/` |
| Hotels | `/api/hotels/`, `/api/hotels/<id>/rooms/` |
| Tours | `/api/tours/`, `/api/tours/<id>/schedule/` |
| Bookings | `/api/bookings/`, `/api/bookings/<id>/confirm/` |
| Payments | `/api/payments/`, `/api/payments/<id>/status/` |
| Reviews | `/api/reviews/` |
| Dashboard | `/api/dashboard/admin/`, `/api/dashboard/hotel-owner/` |

---

## 🚀 Development Roadmap

1. Project Setup (Django + PostgreSQL)
2. Authentication (JWT + Roles)
3. Hotel Module
4. Room Module
5. Tour Package Module
6. Search & Filters
7. Booking System
8. Payment Module
9. Reviews & Wishlist
10. Dashboards & Analytics
11. Notifications
12. Deployment

---

## 👨‍💻 Author

**Hamza** — Final Year BS Software Engineering, COMSATS University Islamabad (Vehari Campus)
Backend-focused Full Stack Developer (Django REST + React)
