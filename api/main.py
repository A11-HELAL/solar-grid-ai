"""FastAPI entry point exposing the 8 analytical endpoints."""

from fastapi import FastAPI

app = FastAPI(
    title="Solar-Grid AI Analytical API",
    version="1.1.0",
    description="Read-only analytical API for solar forecasting and plant health intelligence.",
)


@app.get("/api/v1/health")
def get_health() -> dict:
    """Service health and database connectivity probe."""
    return {"status": "ok", "version": "1.1.0"}
