# Railway Deployment Plan
https://github.com/yashpawar87/newspaper-ai.git
## Summary
Deploy this as a Railway monorepo with 3 Railway resources: existing `Postgres`, new `backend` FastAPI service, and new `frontend` Next.js service. Railway’s monorepo docs recommend separate services with separate root directories, so use `/backend` and `/frontend`.

Docs refs: [Railway monorepo](https://docs.railway.com/deployments/monorepo), [FastAPI](https://docs.railway.com/guides/fastapi), [Next.js](https://docs.railway.com/guides/nextjs), [PostgreSQL](https://docs.railway.com/databases/postgresql).

## Key Changes / Deployment Steps
- Create a GitHub repo from `/Users/yashpawar/rss-newspaper` and push the full project.
- In Railway, create/import two services from the same GitHub repo:
  - `backend`: Root Directory `/backend`
  - `frontend`: Root Directory `/frontend`
- Backend service settings:
  - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Healthcheck path: `/health`
  - Variables:
    - `DATABASE_URL=${{Postgres.DATABASE_URL}}` using the actual Railway Postgres service name if not `Postgres`
    - `FETCH_INTERVAL_MINUTES=15`
    - `SEED_ON_STARTUP=true`
    - `ADMIN_TOKEN=<strong-random-secret>`
    - `ALLOWED_ORIGINS=https://<frontend-domain>`
- Frontend service settings:
  - Build command: `npm run build`
  - Start command: `npm run start -- -p $PORT`
  - Variables:
    - `NEXT_PUBLIC_API_URL=https://<backend-domain>`
- Deployment order:
  1. Deploy backend first.
  2. Generate backend public domain.
  3. Deploy frontend with `NEXT_PUBLIC_API_URL` set to backend domain.
  4. Generate frontend public domain.
  5. Update backend `ALLOWED_ORIGINS` to frontend domain and redeploy backend.
  6. Trigger initial feed population with:
     `POST https://<backend-domain>/admin/fetch` using `X-Admin-Token`.

## Interfaces / URLs
- Backend public API:
  - `GET /health`
  - `GET /categories`
  - `GET /articles?category=tech&page=1&limit=15`
  - `GET /trending?limit=10`
  - `POST /admin/fetch`
- Frontend public pages:
  - `/`
  - `/top-stories`
  - `/latest-stories`
  - `/tech`
  - `/business`
  - `/entertainment`
  - `/sports`
  - `/lifestyle-fashion`
  - `/cricket`

## Test Plan
- Backend deployment:
  - Visit `https://<backend-domain>/health`.
  - Confirm `status` is `ok`, `source_count` is `8`, and feed `last_error` values are empty after fetch.
- Database population:
  - Run `POST /admin/fetch`.
  - Confirm `/health` article count increases.
  - Confirm `/articles?category=sports` returns articles.
- Frontend deployment:
  - Visit frontend homepage and each category page.
  - Confirm category pages no longer show “No ranked stories” after fetch.
  - Click an article and confirm no CORS error in browser console.
- Railway logs:
  - Backend logs should show no Postgres connection errors.
  - Frontend logs should show successful Next.js start on Railway `$PORT`.

## Assumptions
- Deployment method is GitHub monorepo.
- Railway Postgres already exists in the same Railway project.
- If the Postgres service is not named `Postgres`, use that exact service namespace in the variable reference.
- The backend scheduler remains inside the backend service for v1; no separate worker service is needed yet.
