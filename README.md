# MindMate - AI Mental Health Companion

A full-stack AI-powered mental health companion with journaling, mood tracking, CBT-based advice (RAG), and therapy session support.

## Tech Stack

**Backend:** FastAPI, LangGraph, LangChain, OpenAI, SQLAlchemy, SQLite/PostgreSQL, ChromaDB

**Frontend:** Next.js, TypeScript, Tailwind CSS, shadcn/ui, Recharts

**Testing:** pytest, pytest-asyncio, Ruff

## Architecture

```
Next.js (Vercel)  -->  FastAPI REST API  -->  LangGraph  -->  OpenAI
                             |
                   SQLite (local) / PostgreSQL (prod)
                   ChromaDB (local) / pgvector (prod)
```

### LangGraph Workflow

```
User Input --> detect_intent
  |-> "selfcare"  --> mood logging / CBT advice (RAG) / reminders
  |-> "journal"   --> prompt generation / entry storage
  |-> "therapy"   --> session logging / prep / review / patterns
  |-> "general"   --> friendly conversation
  |-> crisis      --> safety resources (988 hotline)
```

## Features

- **Intent-based routing** via LangGraph state machine
- **Conversation memory** - context-aware across messages
- **Mood tracking** with analytics dashboard (charts, streaks)
- **RAG-based CBT advice** from 8 vectorized mental health PDFs
- **Therapy companion** - log sessions, parse notes, detect cross-session patterns, prepare for sessions
- **Journal** with search and history
- **Crisis guardrails** - detects crisis language and responds with professional resources
- **Streaming responses** via Server-Sent Events
- **Data export** - download all data as JSON
- **Dark mode** UI with responsive design

## Quick Start

### Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Index CBT PDFs (first time only)
python -m app.scripts.index_pdfs

# Start backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

### Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send message, get response |
| POST | `/api/v1/chat/stream` | Streaming chat via SSE |
| POST | `/api/v1/register_user` | Register new user |
| POST | `/api/v1/user_exists` | Check if user exists |
| GET | `/api/v1/mood/analytics` | Mood trends and stats |
| GET | `/api/v1/journal/entries` | Journal history with search |
| GET | `/api/v1/therapy/sessions` | Therapy session history |
| GET | `/api/v1/messages` | Chat message history |
| GET | `/api/v1/export` | Export all user data |

## Project Structure

```
app/                        # FastAPI backend
  main.py                   # API routes and startup
  langraph_runner.py        # LangGraph state machine
  core/
    config.py               # Centralized settings
    llm.py                  # LLM provider abstraction
    vectorstore.py          # ChromaDB client
    guardrails.py           # Crisis detection
  db/
    engine.py               # Async SQLAlchemy engine
    models.py               # Table definitions
    message_store.py        # Conversation memory
  tools/
    journaling/             # Journal prompts, storage, analytics
    selfcare/               # Mood tracking, RAG, reminders
    therapy/                # Session parsing, insights, prep
frontend/                   # Next.js app
  src/app/
    chat/                   # Chat with streaming
    dashboard/              # Mood analytics charts
    journal/                # Journal history
    therapy/                # Therapy sessions
    settings/               # Export, account
tests/                      # pytest suite (22 tests)
```

## Disclaimer

MindMate is not a substitute for professional mental health support. It is a personal project for self-reflection and learning.
