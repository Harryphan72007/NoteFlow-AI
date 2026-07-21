# Known Issues

| ID | Layer | Issue | Impact | Status | Next action |
|---|---|---|---|---|---|
| KI001 | Repository | `D:\NoteFlow AI` is not a usable git repository | Cannot produce git diff/status evidence | OPEN | Continue carefully; do not rely on git rollback |
| KI002 | Backend | No backend existed at baseline | Initial backend has been scaffolded and tested for focused flows | MITIGATED | Continue broad endpoint/test coverage |
| KI003 | Frontend | Frontend uses embedded sample data and no API client | Visible actions are not backed by persistence/API | OPEN | Add API adapter and state wiring with no visual redesign |
| KI004 | Tests | No automated tests present at baseline | Focused backend tests and local workflow checks now exist | MITIGATED | Keep regression suite current |
| KI005 | Models | ASR/PaddleOCR/Ollama availability unknown | Real-model E2E is not verified locally | OPEN | Install/configure real models and rerun real ASR/OCR/Ollama tests |
| KI007 | Frontend integration | Approved frontend still uses embedded sample data | Backend exists but visible UI actions are not wired to API yet | OPEN | Add nonvisual API client/state wiring |
| KI008 | Frontend dependency install | `pnpm` required config fix and network approval | Build now passes, but package manager warns package.json `pnpm` field is ignored | OPEN | Move pnpm overrides to supported workspace config if needed |
| KI006 | Encoding | Pasted prompts and some frontend text show mojibake characters | May affect documentation readability and UI text if edited | OPEN | Avoid visual text changes; use ASCII in new files |

## Resume Notes

- Known issues initialized from baseline inspection.
