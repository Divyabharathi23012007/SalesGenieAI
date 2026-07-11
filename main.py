"""Main entry point for the SalesGenie AI FastAPI application."""

from fastapi import FastAPI

from database import models  # Registers all SQLAlchemy models
from database.connection import Base, engine
from modules.module1_leads import router as leads_router
from modules.module2_intelligence import router as intelligence_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="SalesGenie AI",
    version="1.0.0",
    description="AI Sales Intelligence Platform",
)

# Register API routers
app.include_router(leads_router)
app.include_router(intelligence_router)


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Root endpoint.
    """
    return {
        "message": "SalesGenie AI API is running successfully"
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    """
    return {
        "status": "healthy"
    }
