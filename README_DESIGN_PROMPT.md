# README design prompt

Use this prompt with a writing or design model to create a polished GitHub README for **NoteFlow AI**:

```text
Design a clear, credible, developer-focused README for NoteFlow AI, a local clinical documentation-support prototype.

Audience: developers, technical reviewers, hackathon judges, and evaluators who need to understand the product quickly.
Tone: calm, precise, transparent about limitations, and technically confident without making medical claims.
Visual direction: modern healthcare software; deep navy, slate, white, teal/mint accents, and small amber status highlights. Use concise sections, badges, diagrams, and real screenshots. Avoid marketing fluff and avoid implying diagnosis or treatment.

Explain the product in one sentence: NoteFlow AI turns local audio, scanned documents, and text into structured documentation workflows with review, comparison, persistence, and export features.

Required README structure:
1. Hero: project name, one-line value proposition, safety disclaimer, and the generated workflow illustration at `docs/assets/noteflow-workflow-hero.png`.
2. “What it does”: explain audio transcription, OCR, structured analysis, review queues, customer/document management, comparisons, tasks, audit history, and exports.
3. “Product tour”: show the real dashboard screenshot at `verification/evidence/screenshots/frontend_dashboard.png` and briefly explain the queue, pending reviews, service health, and processing activity.
4. “Architecture”: include `docs/assets/noteflow-architecture.svg` and describe the React/Vite frontend, FastAPI backend, SQLAlchemy/Alembic persistence, local ASR/OCR/model services, and export routes.
5. “Workflow”: include `docs/assets/noteflow-workflow.svg` and show input → processing → review → export.
6. “Quick start”: preserve the repository’s actual PowerShell setup commands for backend, migrations, frontend, and tests. Do not invent Docker instructions; Docker support was removed.
7. “Model notes”: accurately mention Qwen3-ASR-0.6B as the normal CPU configuration, optional Mega-ASR 1.7B configuration, local PP-OCRv6 checkpoints, and Ollama with local qwen3:4b.
8. “Safety and scope”: clearly state that this is documentation support, not medical diagnosis or treatment, and that human review remains necessary.
9. “Project status”: link to the verification and audit reports already present in the repository.

Writing constraints: use Markdown that renders cleanly on GitHub; keep paragraphs short; prefer tables for capabilities and commands; include alt text for every image; do not claim production readiness; do not fabricate benchmark numbers, supported file types, or cloud deployment features.
``` 

