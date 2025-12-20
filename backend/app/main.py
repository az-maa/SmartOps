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


# Include routers
from app.controllers import auth_controller

app.include_router(auth_controller.router, prefix="/api/auth", tags=["auth"])
# Include routers
from app.controllers import auth_controller, server_controller

app.include_router(auth_controller.router, prefix="/api/auth", tags=["auth"])
app.include_router(server_controller.router, prefix="/api/servers", tags=["servers"])

# TODO: Add more routers as you build them
# from app.controllers import server_controller
# app.include_router(server_controller.router, prefix="/api/servers", tags=["servers"])