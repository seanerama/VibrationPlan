"""VME Compatibility Analyzer — FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models.database import SessionLocal, init_db
from app.models.seed import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize database tables and seed data on startup."""
    logger.info("Starting up — initializing database.")
    init_db()
    with SessionLocal() as db:
        seed_database(db)
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="VME Compatibility Analyzer",
    description="Classifies VMs against the HPE VM Essentials compatibility matrix.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
