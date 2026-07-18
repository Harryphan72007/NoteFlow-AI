from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routes import ai, clinical_review, compare, customers, documents, processing, tasks


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
    return app


app = create_app()
