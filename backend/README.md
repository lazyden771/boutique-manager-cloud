# Boutique Manager - Cloud API

FastAPI + PostgreSQL backend for the multi-shop, multi-device version of
Boutique Manager. Each shop signs up with its own account; a JWT auth token
scopes every request to that shop's data only. Ported directly from the
desktop app's business logic (sale_repository.py, product_repository.py) -
same rules for atomic sales, proportional partial refunds, double-refund
protection, and duplicate detection.

## Run locally

```
python -m venv venv
venv\Scripts\activate          (Windows)   or   source venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
copy .env.example .env         (Windows)   or   cp .env.example .env       (Mac/Linux)
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API docs (auto-generated
by FastAPI) - you can try every endpoint from the browser without writing
any frontend code yet.

With no `DATABASE_URL` set in `.env`, it uses a local SQLite file
(`boutique_cloud.db`) automatically - good enough to develop against before
you have Postgres set up.

## Run the tests

```
pip install pytest
pytest -v
```

34 tests covering auth, product CRUD + duplicate detection, atomic sale
recording, proportional refunds with double-refund protection, dashboard
totals, customers, suppliers, and image upload (Cloudinary is mocked in
tests - no real account or network needed to run the suite).

## Deploying to Railway (step by step)

1. **Push this folder to GitHub.**
   ```
   git init
   git add .
   git commit -m "Boutique Manager cloud API"
   ```
   Create a new repo on github.com, then:
   ```
   git remote add origin https://github.com/yourusername/boutique-cloud-api.git
   git branch -M main
   git push -u origin main
   ```

2. **Create a Railway account** at railway.app (sign in with GitHub - easiest).

3. **New Project → Deploy from GitHub repo** → pick this repo. Railway
   detects it's a Python app automatically via `railway.json`.

4. **Add a Postgres database**: in your Railway project, click **+ New →
   Database → PostgreSQL**. Railway automatically creates a `DATABASE_URL`
   variable and makes it available to your API service - you don't type
   this in yourself.

5. **Set the remaining environment variables** on your API service
   (Settings → Variables):
   - `SECRET_KEY` - generate one with:
     ```
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
     - free account at cloudinary.com, these three values are on your
       Cloudinary dashboard home page after signup.

6. **Deploy.** Railway builds and starts the service automatically on
   every push to `main`. You'll get a public URL like
   `https://boutique-cloud-api-production.up.railway.app` - that's the
   address the frontend (web app / phone app) will talk to.

7. **Verify it's alive**: visit `https://your-url/docs` in a browser - you
   should see the same interactive API docs you saw locally, now live on
   the internet.

## API overview

All endpoints except `/auth/signup` and `/auth/login` require a Bearer
token (returned by signup/login) in the `Authorization` header.

- `POST /auth/signup`, `POST /auth/login`
- `GET/POST /products`, `PUT/DELETE /products/{id}`, `POST /products/{id}/image`
- `GET /products/low-stock`
- `POST /sales`, `GET /sales`
- `POST /refunds`, `GET /refunds`
- `GET/POST /customers`, `GET /customers/{id}/total-spent`
- `GET/POST /suppliers`
- `GET /dashboard/today`, `/dashboard/month-profit`, `/dashboard/range`,
  `/dashboard/inventory-value`, `/dashboard/best-selling-products`

## Known simplification

Dashboard "today" and "this month" use UTC calendar boundaries rather than
a shop's local time (the desktop app converted to local time, since it
only ever ran on one PC in one timezone - a cloud account might be checked
from anywhere). If day-boundary timing ever looks off near midnight, add a
`timezone` field to `Account` and convert using it.

## What's not built yet

- Frontend (web app + phone app) - this API is ready for one to be built
  against it
- Staff/multi-user logins per shop (currently one login per shop)
- Barcode label generation and PDF receipts (existed in the desktop app,
  not yet ported to the API)

## Security audit (before deploying live)

A pass was done specifically checking for cross-tenant data leaks and
deployment gotchas. Fixed:

- **`DATABASE_URL` scheme**: Railway hands out `postgres://...`, but
  SQLAlchemy 1.4+ requires `postgresql://...` - unfixed, the app would
  have crashed the moment a real Postgres DB was attached. Now normalized
  automatically in `config.py`.
- **Cross-tenant reference leaks**: a shop could previously link a product
  to another shop's `supplier_id`, or a sale to another shop's
  `customer_id`, if they knew/guessed the ID. Both are now validated to
  belong to the requesting shop before being accepted.
- **Input validation floors**: passwords now require 8+ characters; prices
  and quantities can no longer be negative; shop/brand/product names can't
  be empty strings.
- **Refund lookup defense-in-depth**: the product row fetched during a
  refund is now explicitly re-scoped to the requesting shop's account,
  even though the existing sale-ownership check already made this safe in
  practice.

Every query in every router was manually checked to confirm it filters by
`account_id` - the multi-tenant isolation tests (`test_multi_tenant_isolation`,
`test_sale_on_another_shops_product_is_rejected`, etc.) exist specifically
to catch a regression here if a future change forgets that filter.

**Known gaps, not yet addressed** (worth knowing before a real public launch,
not blocking for you + friends testing it):
- No email verification on signup - anyone can sign up with any email
  address without proving they own it.
- `SECRET_KEY` now auto-generates and persists locally if you forget to
  set one (see below) - safe for a single server, but on Railway you
  should still set a real one explicitly, since the auto-generated file
  lives in storage that doesn't survive every kind of restart/redeploy.

**Fixed since the last audit pass:**
- **Login brute-force protection**: an email gets locked out for 15
  minutes after 5 failed login attempts in a 15-minute window (in-memory,
  resets on server restart - fine for one server instance, would need a
  shared store like Redis if this ever runs on multiple instances at once).
- **`SECRET_KEY` zero-setup fix**: previously fell back to a fixed,
  publicly-known default if you forgot to set one - now generates and
  caches a real random key automatically instead, removing the "same key
  as every other install" risk without requiring a manual step.
