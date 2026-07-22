# NoteFlow AI — LLM Project Context Prompt

Copy the prompt below into an LLM system/developer message when asking it to understand, review, modify, or extend this repository.

```text
You are working on NoteFlow AI, a local-first clinical documentation-support prototype. Your job is to make careful, evidence-based changes inside the existing repository. Read the relevant source files and tests before changing behavior. Do not invent APIs, models, routes, or dependencies when the repository already provides an established pattern.

PRODUCT PURPOSE
NoteFlow AI turns manual notes, audio recordings, and scanned documents into normalized, reviewable, auditable documentation. It supports customer management, ingestion, ASR, OCR, correction, comparison, deterministic documentation review, tasks, audit logging, and exports.

SAFETY BOUNDARY
This is documentation support, not a medical diagnosis or treatment system. Do not describe generated text or review findings as clinical truth. Do not add autonomous diagnosis, treatment recommendations, or hidden clinical decisions. Model output must remain reviewable, explainable where possible, and clearly separated from human-approved content.

ARCHITECTURE
The repository is split into:
- Frontend/: React + TypeScript + Vite single-page application.
- backend/app/: FastAPI application, routes, services, database models, schemas, and serializers.
- backend/tests/: backend, API, security, persistence, and regression tests.
- data/: local uploads, processed files, and exports.
- docs/: project documentation, API contracts, test matrices, decisions, and deployment notes.
- verification/: verification scripts and evidence.
- repair/: unfinished-work reports, repair plans, regression results, and implementation tracking.

The backend is the system of record. It uses FastAPI, SQLAlchemy, Pydantic, Alembic, SQLite by default, and optional PostgreSQL. The frontend communicates through the REST API. Local model adapters support ASR, OCR, and Ollama utilities.

END-TO-END PIPELINE
1. A user creates or selects a customer.
2. The user supplies a manual note, audio file/recording, or scanned image/document.
3. The backend validates extension, size, empty-file, safe-path, user-session, and customer context.
4. The original source is stored locally.
5. Manual text is accepted directly; audio is normalized and passed to ASR; images/documents are preprocessed and passed to OCR.
6. A normalized Document is persisted with source text, corrected text when available, language, confidence, status, metadata, and warnings.
7. ASR segments or OCR pages/blocks are persisted with timing/coordinates/confidence where available.
8. A reviewer inspects and corrects the result. Full-text and OCR-block corrections must be auditable.
9. Documents can be compared using WER, CER, token differences, and numeric/unit mismatch checks.
10. Deterministic documentation review can create Analysis and AnalysisIssue records for missing, contradictory, low-confidence, or follow-up-related documentation.
11. Reviewers accept/reject/resolve issues and create or update follow-up Tasks.
12. Important actions create AuditLog records.
13. Final documents and customer reports can be exported as TXT, JSON, PDF, SRT, or VTT where supported.

IMPORTANT DATA ENTITIES
- Customer: identity/profile and owner of related records.
- Document: normalized source, corrected content, status, language, confidence, and metadata.
- ASRSegment: transcript text, timing, and confidence.
- OCRPage/OCRBlock: page structure, extracted text, coordinates, and confidence.
- Analysis: comparison or documentation-review result.
- AnalysisIssue: severity, evidence, recommendation, and reviewer decision.
- Task: follow-up work linked to a customer, document, or analysis.
- Export: generated file metadata and format.
- AuditLog: important mutations, corrections, decisions, exports, and task events.

ROUTE GROUPS
- /api/auth: session/authentication routes.
- /api/customers: customer CRUD, archive/restore, related records, activity, and reports.
- /api/documents: manual notes, documents, correction, finalization, combination, OCR blocks, and exports.
- /api/transcribe and /api/ocr: processing ingestion capabilities exposed through processing routes.
- /api/compare: comparison metrics and mismatch detection.
- /api/clinical-review: deterministic documentation review.
- /api/issues: reviewer decisions on analysis issues where exposed.
- /api/tasks: task lifecycle.
- /api/ai: summarize, translate, key points, task extraction, and formatting utilities.
- /api/meta: supported options and metadata.
- /health: database, ASR, OCR, and Ollama service status. This endpoint is not the browser UI.

BACKEND IMPLEMENTATION RULES
- Put request/response validation in Pydantic schemas.
- Put reusable business logic in services, not duplicated in routes.
- Use SQLAlchemy sessions consistently and commit related records atomically where practical.
- Check authentication and active-user status for protected API requests.
- Check customer/resource ownership before scoped reads or writes.
- Use safe storage helpers; never concatenate untrusted paths.
- Preserve source material when creating corrected or finalized content.
- Record audit events for important mutations and reviewer decisions.
- Return useful processing warnings and fallback indicators.
- Keep database migrations synchronized with model changes.

FRONTEND IMPLEMENTATION RULES
- Follow existing component, styling, and API-client patterns.
- Keep temporary form/input state local, but use backend responses for persisted entities.
- Show processing, confidence, warnings, review state, and errors clearly.
- Do not claim that a locally generated result is clinically validated.
- Keep upload/recording previews separate from saved documents until the user submits them.
- After mutations, refresh or update the relevant customer/document/task state consistently.

MODEL AND FALLBACK RULES
- ASR is designed for Qwen3-ASR-0.6B CPU-oriented operation; larger Mega-ASR configuration is optional.
- OCR is designed around PaddleOCR local checkpoints.
- Structured generation is designed around local Ollama, commonly qwen3:4b.
- Model runtimes are not bundled with the repository.
- Text fallback modes exist for deterministic development/testing and must not be presented as real model quality.
- Never silently replace a real processing failure with fabricated clinical content.

CURRENT STATUS AND LIMITATIONS
- The core customer/document/task workflow has been verified.
- Real ASR, OCR, Ollama, persistence, security regression, API, workflow, and frontend build checks have been performed.
- Some secondary frontend screens still use local/sample state and need complete backend wiring.
- Authentication/authorization are not production-grade.
- Upload validation should be strengthened beyond extension checks with MIME/content validation.
- Full 1.7B Mega-ASR, multi-page PDF OCR, and PostgreSQL deployment are not fully validated.
- This prototype is not approved for real clinical use without qualified review, privacy controls, validated model behavior, and production hardening.

EXPECTED ENGINEERING WORKFLOW
1. Inspect the relevant files, API contracts, models, and tests.
2. State the smallest safe change that satisfies the request.
3. Preserve existing behavior outside the requested scope.
4. Implement using established repository patterns.
5. Add or update tests for changed backend behavior.
6. Run focused tests, then the broader relevant verification/build checks.
7. Report changed files, verification performed, and any remaining limitations.

When uncertain, prefer a transparent, reviewable, deterministic behavior over hidden automation. Ask for clarification only when a reasonable repository-grounded assumption would risk changing product scope, data semantics, or safety boundaries.
```
