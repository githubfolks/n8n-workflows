from fastapi import FastAPI
from app.api.endpoints import router
from app.core.config import settings
import structlog

# Setup structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
