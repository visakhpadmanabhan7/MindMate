# MindMate

AI-powered mental health companion with journaling, mood tracking, CBT-based advice (RAG), therapy session support, and crisis guardrails.

## Quick Start

```bash
# Backend
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY
python -m app.scripts.index_pdfs  # First time only
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev

# Tests
pytest tests/ -v
```

## Architecture

- **Backend:** FastAPI + LangGraph + OpenAI + SQLite + ChromaDB
- **Frontend:** Next.js + TypeScript + Tailwind + shadcn/ui
- **Database:** SQLite locally, PostgreSQL-ready via config swap
- **Vectors:** ChromaDB locally, pgvector-ready for production

## Key Conventions

- All settings via `app.core.config.get_settings()` — no `os.getenv()` scatter
- All DB modules import engine from `app.db.engine` — single source
- API endpoints under `/api/v1/`
- All DB operations and LLM calls are async
- LLM calls go through `app.core.llm.get_llm()` provider abstraction
- Crisis check runs before intent routing in LangGraph

## LangGraph Flow

```
load_history -> detect_intent -> route
  -> crisis (if crisis detected) -> save_messages -> END
  -> selfcare -> save_messages -> END
  -> journal -> save_messages -> END
  -> therapy -> save_messages -> END
  -> general -> save_messages -> END
```

## Commands

```bash
uvicorn app.main:app --reload --port 8000  # Backend
cd frontend && npm run dev                  # Frontend
python -m app.scripts.index_pdfs           # Index PDFs
pytest tests/ -v                           # Tests
ruff check app/ tests/                     # Lint
```
