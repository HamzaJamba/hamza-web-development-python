# City Care — Hospital Management System

A Django practice project covering: Project & App structure, Models, Views (class-based),
URLs, Templates, Forms (incl. formsets), CRUD, Authentication & role-based permissions,
Static files (CSS/JS), Media files (image/document uploads), MySQL/SQLite, and Bootstrap 5.

## Features
- **Doctor Management** — profiles with specialization, fee, availability, photo
- **Patient Records** — registration, search, photo, active/inactive status
- **Appointment Booking** — book/edit/cancel, clash detection (a doctor can't be double-booked)
- **Billing** — invoices with consultation fee + other charges, paid/partial/unpaid tracking
- **Medical History** — diagnosis notes per visit, with file attachments (X-rays, lab reports)
- **Prescriptions** — multi-medicine prescriptions using a Django inline formset
- **Role-based Dashboards** — different views for Admin / Doctor / Receptionist
- **Reports** — PDF & Excel exports (patients, appointments, billing, doctor-wise summary,
  full per-patient medical report)

## Roles
- **Admin** — full access, manages staff & doctors
- **Doctor** — sees own appointments, writes prescriptions, views patients
- **Receptionist** — registers patients, books appointments, manages billing

---

## Setup

### 1. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

By default `DB_ENGINE=sqlite` in `.env` — **no database setup needed**, just run it.

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Seed demo data (optional but recommended)
```bash
python manage.py seed_demo_data
```
This creates:
- Admin: `admin` / `admin123`
- Receptionist: `reception1` / `reception123`
- Doctors: `dr.ali`, `dr.sara`, `dr.usman` / `doctor123`
- 8 demo patients, appointments, invoices, prescriptions

### 6. Run the server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000**

---

## Using MySQL instead of SQLite

Open `.env` and change:
```env
DB_ENGINE=mysql
DB_NAME=hms_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

Create the database first (in MySQL Workbench, phpMyAdmin, or the `mysql` CLI):
```sql
CREATE DATABASE hms_db;
```

This project uses **PyMySQL** (a pure-Python MySQL driver) instead of `mysqlclient`,
so there's no need to install MySQL C connector / Visual C++ Build Tools on Windows —
`pip install -r requirements.txt` is enough.

Then run `python manage.py migrate` again against MySQL and re-seed if you like.

---

## Project structure
```
accounts/       custom User model (ADMIN/DOCTOR/RECEPTIONIST), login, staff CRUD
doctors/        Doctor profiles + CRUD
patients/       Patient records, Medical History (with file uploads)
appointments/   Booking, clash detection
billing/        Invoices
prescriptions/  Prescriptions with a Medicine inline formset
dashboard/      Role-based dashboard views
reports/        PDF (ReportLab) & Excel (openpyxl) exports
templates/      Bootstrap 5 templates, shared base.html + partials
static/css/     Custom theme (blue/teal, animated EKG line on login)
media/          Uploaded photos & attachments (gitignored)
```

## Notes
- `DEBUG=False` and a real `SECRET_KEY` before deploying anywhere public.
- Media files are served by Django's dev server only when `DEBUG=True`; use a proper
  web server (Nginx, etc.) to serve `/media/` in production.
- Admin site is available at `/admin/` using the same admin login.
