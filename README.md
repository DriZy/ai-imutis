# AI-IMUTIS Backend (FastAPI)

FastAPI service with PostgreSQL/PostGIS, Redis-backed rate limiting, Firebase authentication, seeded travel/tourism data, and modular routers. Includes device IP tracking, security headers, and Sentry wiring.

## Quickstart

### Option 1: Docker (Recommended)

```bash
cd backend
docker-compose up --build
```

This starts PostgreSQL with PostGIS and the FastAPI backend. The backend will automatically run migrations on startup.

**Access:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
- PostgreSQL: localhost:5432 (user: postgres, password: postgres, db: ai_imutis)

### Option 2: Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set up your database connection in .env
# DATABASE_URL=postgresql://user:password@localhost:5432/ai_imutis

alembic upgrade head    # apply migrations
uvicorn app.main:app --reload
```

### Migrations (Alembic)

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration (after defining SQLAlchemy models)
alembic revision -m "your message" --autogenerate

# Rollback one migration
alembic downgrade -1
```

## Layout

- app/main.py — FastAPI app factory, middleware, CORS, router wiring, Sentry init, startup seeding
- app/config.py — environment-driven settings (CORS, rate limits, DB/Redis/Firebase/Sentry)
- app/middleware.py — request id, device IP extraction, security headers
- app/rate_limit.py — Redis sliding-window rate limiter
- app/dependencies.py — Firebase Admin auth + rate limit identifiers
- app/db.py — async SQLAlchemy engine/session
- app/models.py — SQLAlchemy models (users, sessions, cities, attractions, travel routes, bookings, notifications, subscriptions)
- app/seed.py — idempotent seeding from app/data.py into Postgres
- app/routers/* — modular endpoint groups (travel, tourism, user, AI, notifications, health)
- app/schemas/* — Pydantic models for requests/responses
- alembic/ — migrations (includes PostGIS enablement)
- .github/workflows/ci.yml — basic CI compile check

## Frontend Integration Guide

- Base URLs: API `http://localhost:8000`; Swagger `http://localhost:8000/docs`; OpenAPI JSON `http://localhost:8000/openapi.json`.
- Auth: Firebase ID token in `Authorization: Bearer <ID_TOKEN>`. WebSockets: `?token=<ID_TOKEN>` or `Authorization: Bearer <ID_TOKEN>`.
- Headers: always `Content-Type: application/json`; optional `X-Device-Fingerprint` for session tracking.
- Rate limits: Redis-backed sliding window; on `429`, honor `Retry-After`.

Key endpoints
- Travel: list `GET /api/travels`; search `POST /api/travels/search`; detail `GET /api/travels/{route_id}`; book (auth) `POST /api/travels/book`; estimate `POST /api/travels/estimate`.
- Tourism: cities `GET /api/cities`; city attractions `GET /api/cities/{city_id}/attractions`; attraction detail `GET /api/attractions/{attraction_id}`; search `POST /api/attractions/search`.
- AI: departure windows `POST /api/ai/estimate-departure`; traffic `GET /api/ai/traffic-prediction/{route_id}`; recommend attractions `POST /api/ai/recommend-attractions`; guides `POST /api/ai/tourist-guide/{attraction_id}`; city suggestions `GET /api/ai/tourism-suggestions/{city_id}`; travel patterns `POST /api/ai/analyze-travel-pattern`.
- Users (auth): verify token `POST /api/auth/verify-token`; profile `GET/PUT /api/users/profile`; preferences `POST /api/users/preferences`; sessions `GET /api/users/sessions`, `DELETE /api/users/sessions/{session_id}`; track location `POST /api/users/locations/track`.
- Notifications (auth): list `GET /api/notifications`; subscribe `POST /api/notifications/subscribe` `{ token, channels }`; dismiss `DELETE /api/notifications/{id}`.

WebSockets
- Notifications: `ws://localhost:8000/api/ws/user/{user_id}/notifications?token=<ID_TOKEN>` (requires matching user_id + valid token; closes with 4401/4403 if unauthorized/forbidden).
- Traffic: `ws://localhost:8000/api/ai/ws/route/{route_id}/traffic` (demo feed).

Example fetch (JS)
```js
const token = await firebase.auth().currentUser.getIdToken();
const res = await fetch(`${API_BASE}/api/travels/search`, {
	method: 'POST',
	headers: {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${token}`,
		'X-Device-Fingerprint': deviceId,
	},
	body: JSON.stringify({ origin: 'douala', destination: 'yaounde', departure_date: new Date().toISOString(), passengers: 2 }),
});
if (!res.ok) throw new Error(await res.text());
const data = await res.json();
```

Example WebSocket (JS)
```js
const token = await firebase.auth().currentUser.getIdToken();
const ws = new WebSocket(`${WS_BASE}/api/ws/user/${userId}/notifications?token=${token}`);
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.onclose = (e) => console.warn('ws closed', e.code);
```

Error handling
- Parse JSON `detail` on non-2xx.
- On 401/403, refresh Firebase token and retry once.
- On 429, respect `Retry-After` header before retrying.

## Next Steps

- Add broader test coverage (unit + integration with Postgres/Redis/Firebase).
- Expand CI to run tests, lint, and apply migrations in a containerized DB.
- Tune AI endpoints with real inference or external APIs if available.
