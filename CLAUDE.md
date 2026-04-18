# MindMate

AI-powered mental health companion with journaling, mood tracking, CBT-based advice (RAG), therapy session support, chat sessions, weekly summaries, and crisis guardrails.

## Commands

```bash
uv run uvicorn app.main:app --reload --port 8000                       # Backend
cd frontend && npm run dev                                              # Frontend (port 3000)
uv run python -m app.scripts.index_pdfs                                 # Index PDFs into ChromaDB
uv run pytest tests/ -v                                                 # Tests
uv run ruff check app/ tests/                                           # Lint backend
cd frontend && npm run build                                            # Build frontend
```

## Architecture

- **Backend:** FastAPI + LangGraph + Groq (Llama 3.3 70B) + SQLite + ChromaDB
- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind CSS v4 + shadcn/ui (base-ui)
- **LLM:** Groq free tier by default, OpenAI as fallback via `LLM_PROVIDER` config
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2) — runs locally, no API cost
- **Database:** SQLite at `app/data/mindmate.db`, PostgreSQL-ready via `DATABASE_URL`
- **Vectors:** ChromaDB at `app/data/chroma/`, pgvector-ready for production

## Key Conventions — FOLLOW THESE

- All settings via `app.core.config.get_settings()` — NEVER use `os.getenv()` directly
- All DB modules import engine from `app.db.engine` — single source
- All LLM calls go through `app.core.llm.get_llm()` provider abstraction — never instantiate clients directly
- API endpoints under `/api/v1/`
- All DB operations and LLM calls are async
- All prompts live in `app/prompts/prompt_texts.py` — never inline prompt strings in logic files
- Crisis check runs before intent routing in LangGraph (non-negotiable safety requirement)
- Frontend uses `"use client"` on all pages — no server components for state management
- Frontend components use `@base-ui/react` primitives (NOT Radix) — no `asChild` prop, use `render` prop instead
- Frontend AGENTS.md warns about Next.js breaking changes — read `node_modules/next/dist/docs/` before using unfamiliar Next.js APIs

## LangGraph Flow

```
load_history -> detect_intent -> route
  -> crisis (if crisis detected) -> enrich_response -> save_messages -> END
  -> selfcare -> enrich_response -> save_messages -> END
  -> journal -> enrich_response -> save_messages -> END
  -> therapy -> enrich_response -> save_messages -> END
  -> general -> enrich_response -> save_messages -> END
```

`enrich_response` does passive mood detection + generates split feedback:
- "Based on your history" — synthesizes moods, journals, therapy sessions
- "What science says" — RAG from knowledge base with citations

## File Ownership Map (for parallel work)

Use this to avoid conflicts when multiple agents work simultaneously.

### Backend — independent modules (safe to parallelize)

| Area | Files | Owner |
|------|-------|-------|
| Chat & Messages | `app/db/message_store.py`, chat endpoints in `app/main.py` | chat-agent |
| Journal | `app/tools/journaling/journal_store.py`, `journal_analytics.py`, journal endpoints in `app/main.py` | journal-agent |
| Therapy | `app/tools/therapy/therapy_store.py`, `therapy_router.py`, therapy endpoints in `app/main.py` | therapy-agent |
| Mood | `app/tools/selfcare/mood_tracker.py`, `mood_analytics.py`, mood endpoints in `app/main.py` | mood-agent |
| RAG/Knowledge | `app/tools/selfcare/rag_tool.py`, `app/core/vectorstore.py`, knowledge endpoints in `app/main.py` | rag-agent |
| Insights | `app/tools/insights/cross_reference.py`, `weekly_summary.py` | insights-agent |
| Prompts | `app/prompts/prompt_texts.py` | SHARED — coordinate changes |

### Backend — shared files (coordinate before editing)

- `app/main.py` — add endpoints at the bottom of the relevant section, don't reorder existing ones
- `app/db/models.py` — add new tables/columns, never remove existing ones, add migrations in `setup_db.py`
- `app/langraph_runner.py` — the LangGraph flow; changes here affect all chat behavior
- `app/core/config.py` — settings; add new vars, don't change defaults of existing ones

### Frontend — independent pages (safe to parallelize)

| Page | Files |
|------|-------|
| Chat | `frontend/src/app/chat/page.tsx` |
| Dashboard | `frontend/src/app/dashboard/page.tsx` |
| Journal | `frontend/src/app/journal/page.tsx` |
| Therapy | `frontend/src/app/therapy/page.tsx` |
| Summary | `frontend/src/app/summary/page.tsx` |
| Knowledge | `frontend/src/app/knowledge/page.tsx` |
| Settings | `frontend/src/app/settings/page.tsx` |

### Frontend — shared files (coordinate before editing)

- `frontend/src/lib/api.ts` — add new functions at the bottom of the relevant section
- `frontend/src/lib/utils.ts` — shared utilities (getMoodColor, cn)
- `frontend/src/components/sidebar.tsx` — nav items array
- `frontend/src/app/globals.css` — theme variables
- `frontend/src/context/auth.tsx` — auth state

## Database Schema

Tables: `users`, `chat_sessions`, `messages` (has `session_id`), `journal_entries` (has `sentiment_score`, `summary`), `mood_logs`, `therapy_sessions`, `reminders`

Migrations go in `app/db/setup_db.py` `_migrate()` — use `PRAGMA table_info` to check if column exists before ALTER TABLE.

## Adding a New Feature — Checklist

1. **Backend model** — add table/columns in `app/db/models.py`, add migration in `setup_db.py`
2. **Backend logic** — create module in `app/tools/`, add prompts in `prompt_texts.py`
3. **Backend API** — add endpoint in `app/main.py` under the right section
4. **Frontend API** — add function in `frontend/src/lib/api.ts`
5. **Frontend page** — create page in `frontend/src/app/{name}/page.tsx`
6. **Sidebar** — add nav item in `frontend/src/components/sidebar.tsx` `navItems` array
7. **Test** — add test in `tests/`
8. **Verify** — `ruff check app/`, `pytest tests/ -v`, `cd frontend && npm run build`
