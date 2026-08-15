# Food Delivery Platform — Backend Architecture

## App breakdown (9 apps, decoupled by domain)

| App            | Responsibility                                  | Key Models                        |
|----------------|--------------------------------------------------|------------------------------------|
| accounts       | Auth + role-based users, addresses               | User, Address                      |
| restaurants    | Restaurant profile, hours, approval status       | Restaurant, WorkingHour            |
| menu           | Categories + food catalog                        | Category, FoodItem, FoodImage      |
| cart           | Active customer cart                              | Cart, CartItem                     |
| orders         | Checkout, order lifecycle, coupons               | Coupon, Order, OrderItem           |
| payments       | Payment record per order (COD/Stripe/PayPal)     | Payment                            |
| riders         | Rider profile + delivery assignment              | Rider, Delivery                    |
| reviews        | Restaurant & food ratings, tied to an order       | Review, ReviewImage                |
| notifications  | In-app notification feed per user                | Notification                       |

## Design decisions

1. **Single custom `User` model with a `role` field** (`ADMIN`, `RESTAURANT_OWNER`, `RIDER`, `CUSTOMER`)
   instead of 4 separate auth tables. Simplifies JWT auth to one login endpoint; permissions
   branch on `request.user.role` in DRF permission classes.

2. **UUID primary keys** everywhere (not auto-increment ints) — safer to expose in URLs/APIs,
   avoids ID-enumeration, and plays well with a future multi-region/replicated DB.

3. **Snapshot fields on `OrderItem`** (`food_name_snapshot`, `unit_price_snapshot`) — order history
   must stay accurate even if a restaurant later edits or deletes a food item.

4. **`Cart` is one-per-customer and scoped to one restaurant** at a time (`cart.restaurant`),
   matching real food-delivery UX (you can't checkout from two restaurants in one order).

5. **Denormalized counters** (`Restaurant.avg_rating`, `FoodItem.total_orders`, etc.) — updated via
   signals/service functions on order-completion and review-creation, so dashboard analytics don't
   need expensive aggregate queries on every request.

6. **App dependency direction** (no circular imports):
   `accounts` ← `restaurants` ← `menu` ← `cart`/`orders` ← `payments`/`riders`/`reviews`/`notifications`

## Full endpoint map (all live-tested)

| App | Endpoint | Who | What |
|---|---|---|---|
| accounts | `POST /api/accounts/register/` | public | signup; RESTAURANT_OWNER/RIDER start `is_approved=False` |
| accounts | `POST /api/accounts/login/` `/login/refresh/` `/logout/` | public/auth | JWT with `role`+`is_approved` claims |
| accounts | `GET/PATCH /api/accounts/profile/` | auth | own profile |
| accounts | `POST /api/accounts/change-password/` | auth | change password |
| accounts | `POST /api/accounts/password-reset/` `/confirm/` | public | forgot-password flow (console email in dev) |
| accounts | `CRUD /api/accounts/addresses/` | customer | saved delivery addresses |
| accounts | `CRUD /api/accounts/admin/users/` + `/approve/` `/suspend/` `/activate/` | admin | manage all Riders/Owners/Customers |
| restaurants | `CRUD /api/restaurants/` + `/approve/` `/toggle-open/` `/mine/` | public read / owner / admin | restaurant lifecycle |
| restaurants | `CRUD /api/restaurants/{id}/hours/` | owner | working hours |
| menu | `CRUD /api/menu/categories/` | public read / admin write | global categories |
| menu | `CRUD /api/menu/food-items/` + nested `/images/` | public read / owner write | food catalog |
| menu | `GET/POST/DELETE /api/menu/wishlist/` | customer | saved favourite foods |
| cart | `GET/DELETE /api/cart/`, `POST /api/cart/items/`, `PATCH/DELETE /api/cart/items/{id}/` | customer | single active cart |
| orders | `POST /api/orders/checkout/` | customer | Cart → Order (+Payment), coupon validated live |
| orders | `GET /api/orders/` `/{id}/` | role-scoped | order history/detail |
| orders | `POST /api/orders/{id}/status/` | owner | kitchen status flow |
| orders | `POST /api/orders/{id}/cancel/` | customer | cancel while PENDING/ACCEPTED |
| orders | `CRUD /api/orders/coupons/` | admin | coupon catalog management |
| payments | `GET /api/payments/{order_id}/`, `POST .../confirm/` | scoped/auth | payment status + gateway confirm stub |
| riders | `GET/PATCH /api/riders/me/`, `/toggle-online/`, `/location/` | rider | rider profile |
| riders | `GET /api/riders/deliveries/available/` `/mine/`, `POST .../accept/` `/status/` | rider | delivery lifecycle |
| reviews | `CRUD /api/reviews/` + `/flag/` `/unflag/` | customer create / admin moderate | ratings, auto-updates avg_rating via signal |
| notifications | `GET /api/notifications/`, `POST .../read/` `/mark-all-read/` | auth | notification feed |
| dashboard | `GET /api/dashboard/admin/` | admin | platform-wide sales, popular foods, order breakdown |
| dashboard | `GET /api/dashboard/restaurant/?restaurant_id=` | owner | per-restaurant sales, best-selling food |
| dashboard | `GET/PATCH /api/dashboard/settings/` | admin | delivery charge, tax %, rider fee, commission % — **live-applied to every checkout** |

## Still not built (frontend + a few "nice to have" spec items)
- React frontend (all 4 dashboards) — spec structure ready in the original doc, not started
- Email verification flow (field exists, no send/confirm endpoints yet)
- Route info / Google Maps integration (advanced feature)
- Multi-language, dark mode (frontend-only concerns)

## Next steps (in order)
1. React frontend wired to these APIs (Axios services per app, matching this same folder split)
2. Email verification endpoints (mirrors the password-reset uid/token pattern already built)
3. Deployment: Render/Railway (backend) + Vercel (frontend) + PostgreSQL

## Run it
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
