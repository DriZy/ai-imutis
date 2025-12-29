# AI-IMUTIS Backend (FastAPI)

Scaffolded FastAPI service that mirrors the backend/server requirements described in the project prompts. The code includes API routers, demo data, device IP tracking middleware, and simple in-memory rate limiting. Replace the stubbed logic with production integrations (Firebase Admin, PostgreSQL/PostGIS, Redis) as you harden the service.

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

- app/main.py — FastAPI app factory, middleware, CORS, router wiring
- app/config.py — environment-driven settings (CORS, rate limits)
- app/middleware.py — request id + device IP extraction
- app/rate_limit.py — in-memory sliding window limiter (swap with Redis for prod)
- app/dependencies.py — auth stub + shared dependencies
- app/data.py — demo data used by the routers
- app/routers/* — modular endpoint groups (travel, tourism, user, AI, notifications, health)
- app/schemas/* — Pydantic models for requests/responses

## Next Steps (recommended)

1. **Production Database:** Update DATABASE_URL in .env with your Supabase/cloud PostgreSQL credentials and enable PostGIS extension.
2. **Firebase Auth:** Replace `verify_firebase_token` stub with Firebase Admin SDK verification and custom claims for RBAC.
3. **SQLAlchemy Models:** Define database models, then generate migrations with `alembic revision --autogenerate`.
4. **Redis Rate Limiting:** Swap in-memory `rate_limiter` with Redis-backed implementation per SECURITY_GUIDE.md.
5. **AI Models:** Connect real AI inference (TensorFlow Lite, embeddings, Gemini API) behind the AI endpoints.
6. **CI/CD:** Add GitHub Actions workflow for testing and deployment.
7. **Security Hardening:** Implement CSP/HSTS headers, IP rotation detection, request validation, and audit logging.
