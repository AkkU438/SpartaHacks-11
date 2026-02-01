from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.mongo import close_db, connect_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    await connect_db()
    try:
        yield
    finally:
        await close_db()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    allowed_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    if allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.api_v1_str)

    @app.get("/")
    def root() -> dict:
        return {"name": settings.app_name, "env": settings.env}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()

