from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import settings
from .database import Base, SessionLocal, engine
from .routes import ai, auth, clinical_review, compare, customers, documents, meta, processing, tasks
from .services.auth import decode_token


def create_app() -> FastAPI:
    settings.ensure_directories()
    if settings.auto_create_db:
        Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="NoteFlow AI Backend",
        version="0.1.0",
        description="Local documentation-support prototype. Not a medical diagnosis or treatment system.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_api_session(request: Request, call_next):
        if request.url.path.startswith("/api") and not request.url.path.startswith("/api/auth"):
            header = request.headers.get("authorization", "")
            if not header.lower().startswith("bearer "):
                return JSONResponse({"detail": "Authentication required"}, status_code=401)
            try:
                payload = decode_token(header.split(" ", 1)[1].strip())
                with SessionLocal() as db:
                    user = db.get(__import__("backend.app.models", fromlist=["User"]).User, payload.get("sub"))
                    if not user or not user.is_active:
                        raise ValueError("unknown user")
                    request.state.user = user
            except Exception:
                return JSONResponse({"detail": "Invalid or expired session token"}, status_code=401)
        return await call_next(request)

    @app.get("/health")
    def health():
        from .services.ai_tools import ollama_status
        from .services.model_status import asr_status, ocr_status

        return {
            "status": "ok",
            "services": {
                "database": {"available": True, "url": settings.database_url},
                "asr": asr_status(),
                "ocr": ocr_status(),
                "ollama": ollama_status(),
            },
        }

    app.include_router(customers.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(processing.router, prefix="/api")
    app.include_router(compare.router, prefix="/api")
    app.include_router(clinical_review.router, prefix="/api")
    app.include_router(tasks.router, prefix="/api")
    app.include_router(ai.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(meta.router, prefix="/api")
    return app


app = create_app()
