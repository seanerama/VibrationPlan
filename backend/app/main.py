"""VME Compatibility Analyzer — FastAPI application entry point."""

import logging

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VME Compatibility Analyzer",
    description="Classifies VMs against the HPE VM Essentials compatibility matrix.",
    version="1.0.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
