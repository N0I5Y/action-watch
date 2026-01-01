from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import github_webhook, health, workflows, github_sync, debug, dashboard, auth, billing, settings, analytics, alerts
from app.core.db import Base, engine
from app.services.scheduling import start_scheduler, shutdown_scheduler
from app.core.config import settings as config_settings







def create_app() -> FastAPI:
    app = FastAPI(title="GitHub Actions Cron Monitor", version="0.1.0")

    frontend_url = config_settings.FRONTEND_URL.rstrip("/")
    origins = [
        frontend_url,
        f"{frontend_url}/",
        "http://localhost:5173",
        "http://localhost:5173/",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5173/",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/health", tags=["health"])
    app.include_router(github_webhook.router, prefix="/api/github", tags=["github"])
    app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
    app.include_router(github_sync.router, prefix="/api/github", tags=["github-sync"])
    app.include_router(debug.router, prefix="/api/debug", tags=["debug"])
    app.include_router(dashboard.router, prefix="/api", tags=["dashboard"]) 
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) 
    app.include_router(billing.router, prefix="/api/billing", tags=["billing"]) 
    app.include_router(settings.router, prefix="/api/settings", tags=["settings"]) 
    app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"]) 
    app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"]) 

    @app.on_event("startup")
    async def _startup():
        Base.metadata.create_all(bind=engine)
        start_scheduler()

    @app.on_event("shutdown")
    async def _shutdown():
        shutdown_scheduler()

    return app


app = create_app()
