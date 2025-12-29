"""FastAPI entrypoint for the AI-IMUTIS backend."""
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .config import get_settings
from .middleware import DeviceIPMiddleware, RequestContextMiddleware
from .routers import ai, health, notifications, tourism, travels, users

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("ai-imutis")

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)

# Middleware
app.add_middleware(RequestContextMiddleware)
app.add_middleware(DeviceIPMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Routers
app.include_router(health.router)
app.include_router(travels.router)
app.include_router(tourism.router)
app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    """Simple welcome endpoint."""

    return {"message": "AI-IMUTIS backend is running"}


def custom_openapi() -> dict:
    """Attach security schemes and tags to the generated OpenAPI schema."""

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {}).update(
        {
            "FirebaseAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Firebase ID Token",
            },
            "DeviceFingerprint": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Device-Fingerprint",
                "description": "Unique device identifier for session tracking",
            },
        }
    )

    openapi_schema["tags"] = [
        {"name": "Travel", "description": "Inter-urban travel route management"},
        {"name": "Tourism", "description": "City and attraction information"},
        {"name": "User", "description": "User profile and preferences"},
        {"name": "Notifications", "description": "Alerts and WebSocket streams"},
        {"name": "AI", "description": "AI predictions and recommendations"},
        {"name": "Health", "description": "Service readiness"},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


    app.openapi = custom_openapi


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting %s v%s", settings.app_name, settings.version)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Shutting down %s", settings.app_name)
