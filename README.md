# Lux Gems — Django + DRF Jewelry Showroom

Production-style e-commerce showroom with a dark emerald and gold UI, PostgreSQL, Docker, Django REST Framework, and JWT authentication. The published reference site was used only for visual and content inspiration; this codebase is an independent implementation.

## Features

- **Stack:** Django 5, Django REST Framework, PostgreSQL, WhiteNoise, Gunicorn, Docker Compose  
- **Auth:** Registration, login/logout, password reset email flow, session-based web auth  
- **Roles:** `Profile.role` (`admin` / `customer`) plus Django superuser; admin dashboard and product/order admin UIs are restricted to admin role  
- **Customer area:** Account dashboard and order history for signed-in customers  
- **Catalog:** Showroom with search, category/material filters, price range, sort, pagination; product detail with related pieces  
- **Admin product CRUD:** Web UI under `/dashboard/admin/products/` (image upload supported)  
- **Cart & checkout:** Server-side cart per user, checkout creates `Order` + `OrderItem`, adjusts stock atomically  
- **Order management:** Customers see their orders; admins list/filter orders and update status  
- **REST API:** Versioned under `/api/v1/` with filters, search, ordering, pagination; JWT obtain/refresh endpoints  
- **Permissions:** Read-only catalog for anonymous users; writes (products, categories, order status, user listing) require admin role; cart and orders scoped to the authenticated user (admins see all orders via API and admin UI)

## Secrets: `.env` (not in Git)

1. Copy the template: `copy .env.example .env` (PowerShell) or `cp .env.example .env` (macOS/Linux).  
2. Set **`DJANGO_SECRET_KEY`** to a long random string (never reuse across environments). Quick generate:

   `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

3. For **production**: set `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS` to your domain(s), `DJANGO_CSRF_TRUSTED_ORIGINS` to your full HTTPS origins (comma-separated), `DATABASE_URL` if you use PostgreSQL, and `SECURE_SSL_REDIRECT=1` when the app is served only over HTTPS.

The app loads `.env` automatically via `python-dotenv` in `luxgems/settings.py`. **`.env` is listed in `.gitignore`** so it is not pushed to GitHub.

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django signing; required unique value per deploy |
| `DJANGO_DEBUG` | `1` local, `0` production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | HTTPS origins for CSRF (needed when `DEBUG=0` and using a real domain) |
| `SECURE_SSL_REDIRECT` | `1` to redirect HTTP→HTTPS when `DEBUG=0` |
| `DATABASE_URL` | Empty = SQLite; else `postgresql://...` |
| `EMAIL_*` / `DEFAULT_FROM_EMAIL` | Set `EMAIL_HOST` (+ user/password) to use SMTP; otherwise use `EMAIL_BACKEND` (e.g. console) |

## Quick start (local, SQLite)

Without PostgreSQL, the project falls back to SQLite for fast local demos.

```powershell
cd c:\Users\HUMMAS\Desktop\web
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

`seed_demo` creates categories/products and assigns **HTTPS image URLs** (Unsplash / Pexels) on each demo slug; it also clears any uploaded file on those products so the storefront uses web images only. Pass `--skip-images` to leave `image_url` / files unchanged.

Open http://127.0.0.1:8000/ — log into `/admin/` with the superuser, open **Accounts → Profiles**, and set your profile **role** to **Admin** to unlock the Lux Gems admin dashboard and product tools (superusers are treated as admins automatically).

## PostgreSQL (local)

1. Create database and user matching your URL.  
2. Set `DATABASE_URL` in `.env`, for example:

`DATABASE_URL=postgresql://luxgems:luxgems@127.0.0.1:5432/luxgems`

3. Run migrations and seed as above.

## Docker Compose

```powershell
cd c:\Users\HUMMAS\Desktop\web
copy .env.example .env
docker compose up --build
```

Application: http://localhost:8000/  
PostgreSQL is exposed on port **5432** with user/password/database `luxgems` (change for real deployments).

Ensure `.env` contains at least:

- `DJANGO_SECRET_KEY` — long random string  
- `DJANGO_DEBUG=0` for production-like runs  
- `DJANGO_ALLOWED_HOSTS` — comma-separated hosts  

## REST API & JWT

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/token/` | Obtain access + refresh (body: `username`, `password`) |
| `POST /api/v1/auth/token/refresh/` | Refresh access token |
| `GET /api/v1/me/` | Current user (Bearer JWT or session) |
| `GET/POST /api/v1/categories/` | Categories (writes: admin) |
| `GET/POST/PUT/PATCH/DELETE /api/v1/products/` | Products (writes: admin) |
| `GET /api/v1/cart/` | Current user cart |
| `POST /api/v1/cart/add/` | JSON `{"product_id": <id>, "quantity": 1}` |
| `POST /api/v1/cart/items/<id>/update/` | JSON `{"quantity": n}` |
| `POST /api/v1/cart/items/<id>/remove/` | Remove line |
| `GET /api/v1/orders/` | Customer: own orders; Admin: all |
| `PATCH /api/v1/orders/<id>/status/` | Admin only — body `{"status": "shipped"}` etc. |
| `GET /api/v1/users/` | Admin only — user directory |

Statuses: `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`.

Example token request:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ -H "Content-Type: application/json" -d "{\"username\":\"you@example.com\",\"password\":\"yourpass\"}"
```

(`username` in the JSON is the Django **username** field; for email-registered storefront users this is the same as their **email**.)

## Project layout

- `luxgems/` — settings, root URLs  
- `accounts/` — profiles, auth views, middleware ensuring profiles, DRF `IsAdminRole`  
- `catalog/` — categories, products, showroom, admin product CRUD  
- `cart/` — cart models and views  
- `orders/` — checkout, orders, admin status updates  
- `api/` — DRF routers, serializers, JWT wiring  
- `templates/`, `static/` — Lux Gems UI  

## Security notes

- Configure real email (`EMAIL_HOST` + SMTP fields in `.env`, or `EMAIL_BACKEND`) for password reset in production.  
- Turn on `SECURE_SSL_REDIRECT` and HTTPS when behind TLS termination.  
- Replace default `SECRET_KEY` and database credentials.  
- Add rate limiting / throttling for public APIs if exposing to the internet.

## GitHub (first push)

From the project folder (adjust remote URL to your empty repo):

```powershell
cd c:\Users\HUMMAS\Desktop\web
git init
git add .
git status
git commit -m "Initial commit: Lux Gems Django storefront"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Do **not** commit `.env`, `db.sqlite3`, `media/`, or `staticfiles/` — they are ignored by `.gitignore`. On the server or PaaS, create `.env` again or use the host’s “environment variables” UI with the same names as in `.env.example`.

## Export a zip (Windows)

Creates **`luxgems-web.zip` on your Desktop**, excluding `.git`, virtualenvs, caches, database, secrets, and build artefacts:

```powershell
cd c:\Users\HUMMAS\Desktop\web
tar -caf "$env:USERPROFILE\Desktop\luxgems-web.zip" `
  --exclude=.git --exclude=.venv --exclude=venv `
  --exclude=__pycache__ --exclude=staticfiles --exclude=media `
  --exclude=.env --exclude=db.sqlite3 .
```

To include your **local** `.env` or database in a **private backup** zip only, remove the corresponding `--exclude` flags (never upload that zip to a public place).

## License

Demo / portfolio use. Adapt as needed for your own projects.
