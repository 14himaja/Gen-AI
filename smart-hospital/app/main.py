from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.api.auth import router as auth_router
from app.api.hospital import router as hospital_router
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown management."""
    print(f"[{settings.APP_NAME}] Server started successfully on http://{settings.HOST}:{settings.PORT}")
    print(f"[{settings.APP_NAME}] Web UI available at: http://{settings.HOST}:{settings.PORT}/")
    print(f"[{settings.APP_NAME}] API documentation at: http://{settings.HOST}:{settings.PORT}/docs")
    yield
    print(f"[{settings.APP_NAME}] Server shutting down...")


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Conversational Multi-Agent Healthcare Operations Assistant using Google ADK + FastAPI + MCP",
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount Static Files (HTML, CSS, JS)
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Register Routers
    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(hospital_router, prefix=settings.API_PREFIX)
    app.include_router(chat_router, prefix=settings.API_PREFIX)
    app.include_router(admin_router, prefix=settings.API_PREFIX)

    @app.get("/")
    async def root():
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "operational",
            "docs": "/docs",
            "active_model": settings.MODEL_NAME
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()
