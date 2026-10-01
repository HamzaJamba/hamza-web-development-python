# MarketNest — Multi-Vendor E-Commerce Marketplace

A Daraz/Amazon-style marketplace: independent "stalls" (vendors) list products, customers
fill one cart from any of them, checkout once, and each stall packs/ships its own parcel.

Django + DRF backend, React + Vite + Tailwind v4 + Framer Motion frontend with a distinctive
"bazaar" visual identity (striped awnings, flying-to-cart animation, hand-drawn product plates).

## Stack
- **Backend**: Django, DRF, SimpleJWT, django-filter, drf-spectacular (Swagger/ReDoc)
- **Frontend**: React 19, Vite, Tailwind CSS v4, Framer Motion, React Router, Axios, lucide-react

## Backend apps
- **accounts / authentication** — custom email-based User, JWT login/register/refresh/logout, profile
- **roles** — Role & Permission system (Customer, Vendor, Admin)
- **vendors** — stall applications, approval workflow, commission rate
- **catalog** — categories + products (vendor-owned, `mine` endpoint for a vendor's own listings)
- **orders** — cart→checkout, multi-vendor order splitting into per-vendor `OrderItem`s with their
  own status lifecycle (pending → packed → shipped → delivered), cancel/refund logic
- **payments** — simulated payment gateway (no real charges)
- **reviews** — product ratings/reviews
- **dashboard** — vendor dashboard (revenue, commission, top products, low stock, 14-day chart)
  and admin dashboard (GMV, commission earned, top vendors, pending approvals)
- **audit** — who changed what, when (products, vendor approvals, etc.)

## Frontend pages
Home, Shop (search/filter/category), Product detail, Stall (vendor storefront), Cart (drawer),
Checkout, Orders + Order detail, Login/Register, Vendor application, Vendor dashboard
(overview/products/orders tabs), Admin console (overview/pending stalls/audit log).

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo       # creates demo stalls, products, and login accounts
python manage.py runserver 8000
```

Demo logins (password `Demo@12345`):
- Admin: `admin@marketnest.pk`
- Customer: `customer1@marketnest.pk`
- Vendor: `anarkali@marketnest.pk` (also gadgets@, karkhano@, spice@, pottery@, margalla@)

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Opens on `http://localhost:5173` — the Vite dev server proxies `/api/*` to `http://127.0.0.1:8000`,
so no CORS setup is needed in development.

### API docs
`http://127.0.0.1:8000/api/docs/` (Swagger) or `/api/redoc/`

## Notes
Payments are simulated — no real card processing or charges happen anywhere in this project.
