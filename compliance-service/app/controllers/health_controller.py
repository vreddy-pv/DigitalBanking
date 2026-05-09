from fastapi import APIRouter
from app.database import engine

health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "UP"
    except Exception:
        db_status = "DOWN"

    return {
        "status": "healthy" if db_status == "UP" else "degraded",
        "service": "compliance-service",
        "version": "1.0.0",
        "database": db_status,
    }
