import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.router import router as api_router

import os

# Configure robust dual-target logging (Console + app.log)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
handlers = [logging.StreamHandler()]

# Safely handle read-only environments like Vercel
log_file = "/tmp/app.log" if os.environ.get("VERCEL") else "app.log"
handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=handlers,
    force=True
)

logger = logging.getLogger("email_service")

app = FastAPI(
    title="PointNest Generic Email Service",
    description="A highly reliable, generic microservice for templates and email dispatching.",
    version="1.0.0"
)

# Configure CORS for flexible local development and microservice usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include core email router
app.include_router(api_router)

@app.get("/", include_in_schema=False)
def root():
    """Redirect home requests to Interactive Swagger UI."""
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    """Verify application operational health."""
    return {"status": "healthy", "service": "generic-email-service"}

if __name__ == "__main__":
    logger.info("Initializing PointNest Generic Email Service...")
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        reload_dirs=["app", "templates"],
        reload_excludes=["*.log", "app.log"]
    )
