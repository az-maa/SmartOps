from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Smart OPS API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ==================== INCLUDE ALL ROUTERS ====================
# Import all controllers
from app.controllers import (
    auth_controller,
    server_controller,
    metrics_controller,
    anomaly_controller,
    prediction_controller
)

# Register all routers (ONLY ONCE!)
app.include_router(auth_controller.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(server_controller.router, prefix="/api/servers", tags=["Servers"])
app.include_router(metrics_controller.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(anomaly_controller.router, prefix="/api/anomalies", tags=["Anomalies"])
app.include_router(prediction_controller.router, prefix="/api/predictions", tags=["Predictions"])