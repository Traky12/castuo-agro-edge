"""FastAPI entrypoint for CASTUO Agro Edge gateway."""

from fastapi import FastAPI

from gateway.health.routes import router as health_router
from gateway.telemetry.routes import router as telemetry_router

app = FastAPI(
    title="CASTUO Agro Edge",
    description="Offline-first rural edge computing stack for agritech",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(telemetry_router)
