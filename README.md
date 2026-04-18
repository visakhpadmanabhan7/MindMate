# MindMate - AI Mental Health Companion

A full-stack AI-powered mental health companion with journaling, mood tracking, CBT-based advice (RAG), therapy session support, and crisis guardrails — built with Next.js, FastAPI, LangGraph, and Groq.

## Demo

### Chat — Streaming responses with markdown, avatars, and session management
![Chat](https://via.placeholder.com/800x400?text=Chat+Interface)

### Mood Dashboard — Color-coded mood trends, interactive charts, source tracking
![Dashboard](https://via.placeholder.com/800x400?text=Mood+Dashboard)

### Journal — Mood-colored entries, weighted theme cloud, auto-analysis
![Journal](https://via.placeholder.com/800x400?text=Journal)

> *Replace the placeholder images above with actual screenshots of your running app.*

---

## Features

### Core
- **Chat with MindMate** — streaming responses via SSE, markdown rendering, conversation memory
- **Chat Sessions** — create, switch, and delete separate conversations
- **Intent Routing** — LangGraph automatically routes to the right tool (selfcare, journal, therapy, general)
- **Crisis Guardrails** — detects crisis language and responds with 988 Suicide & Crisis Lifeline resources

### Mood & Analytics
- **Passive Mood Detection** — picks up emotional signals from any message
- **Mood Dashboard** — interactive charts with mood-colored dots, distribution pie chart, streak tracking
- **Source Tracking** — see where moods come from (chat, journal, explicit)
- **Weekly Summary** — LLM-generated recap of your mood trends, journal themes, and therapy progress

### Journaling
- **Journal Editor** — write entries with auto mood/theme/entity extraction + sentiment scoring
- **Theme Cloud** — weighted by frequency, click to filter
- **Mood-Colored Entries** — left border matches detected mood
- **Delete & Edit** — full CRUD on entries

### Therapy
- **Log Sessions** — directly from the therapy page or through chat
- **Structured Parsing** — issues discussed, learnings, action items, techniques
- **Timeline View** — numbered session badges with connecting timeline
- **Pattern Analysis** — ask MindMate to find cross-session patterns
- **Session Prep** — get a summary of what to discuss in your next session

### Knowledge Base (RAG)
- **Upload PDFs** — mental health resources indexed into ChromaDB
- **Evidence-Based Advice** — responses cite specific pages from your uploaded documents
- **Search** — query your knowledge base directly with highlighted results

### Smart Responses
When you share something emotionally significant, MindMate responds with two sections:

> **Based on your history:**
> "You've felt anxious 3 times this week. In Session #3, you worked on cognitive reframing for similar frustration. Your journal from Monday mentioned work pressure and sleep issues."
>
> **What science says:**
> "Progressive muscle relaxation has shown effectiveness for anxiety management. Start by tensing your fists for 5 seconds, then releasing..."
>
> ---
> [1] *CBT Techniques for Anxiety*, p. 18

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui, Recharts |
| **Backend** | FastAPI, LangGraph, LangChain, Pydantic |
| **LLM** | Groq (Llama 3.3 70B) — free tier, or OpenAI as fallback |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) — runs locally |
| **Database** | SQLite (local), PostgreSQL-ready via config |
| **Vector Store** | ChromaDB (local), pgvector-ready for production |
| **CI/CD** | GitHub Actions (lint + test + build on PR) |

**Total cost: $0** — Groq free tier + local embeddings + SQLite + ChromaDB.

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 22+
- A [Groq API key](https://console.groq.com) (free)

### 1. Clone and setup backend

```bash
git clone https://github.com/visakhpadmanabhan7/MindMate.git
cd MindMate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 2. Index knowledge base (first time only)

```bash
python -m app.scripts.index_pdfs
```

This indexes the CBT/mental health PDFs in `app/data/` into ChromaDB for RAG.

### 3. Start backend

```bash
uvicorn app.main:app --reload --port 8000
```

Backend runs at http://localhost:8000. API docs at http://localhost:8000/docs.

### 4. Setup and start frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000.

### 5. Use it

1. Open http://localhost:3000
2. Register with any email and password (6+ chars)
3. Start chatting!

---

## Example Interactions

### Mood Tracking
```
You: I'm feeling really anxious about my presentation tomorrow
MindMate: Mood logged as anxious.

Here's something that might help:

**Based on your history:**
You've mentioned presentation anxiety in your journal last week...

**What science says:**
The 4-7-8 breathing technique can reduce acute anxiety...
[1] CBT Techniques for Anxiety, p. 23
```

### Journaling
```
You: Today I realized that my stress mostly comes from trying to please
     everyone at work. I need to set better boundaries.

MindMate: Entry saved to your journal. Feel free to share more or ask for a prompt.

# Auto-detected: mood=stressed, themes=["people-pleasing at work", "boundary setting"],
# entities=["work"]
```

### Therapy Session Logging
```
You: Here are my therapy notes from today: We discussed my anxiety around
     social situations. My therapist suggested exposure therapy starting
     with small groups. Homework is to attend one social event this week.

MindMate: Session #4 logged!
  Issues: social anxiety
  Techniques: exposure therapy
  Action items: attend one social event this week
```

### Getting a Journaling Prompt
```
You: Give me a journaling prompt about self-compassion

MindMate: When was the last time you made a mistake and treated yourself the
          way you would treat a close friend? What would that friend say to
          you right now?
```

### Crisis Detection
```
You: I want to hurt myself

MindMate: I'm really concerned about what you're sharing. Please reach out
          to these resources right away:

          📞 988 Suicide & Crisis Lifeline — Call or text 988
          💬 Crisis Text Line — Text HOME to 741741
```

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────────┐
│   Next.js 16    │────▶│            FastAPI Backend                │
│   React 19      │ SSE │                                          │
│   Tailwind v4   │◀────│  ┌─────────────────────────────────────┐ │
│   shadcn/ui     │     │  │         LangGraph Flow              │ │
└─────────────────┘     │  │                                     │ │
                        │  │  load_history → detect_intent → route│ │
                        │  │    → crisis / selfcare / journal /  │ │
                        │  │      therapy / general              │ │
                        │  │    → enrich_response (history +     │ │
                        │  │      science split)                 │ │
                        │  │    → save_messages                  │ │
                        │  └─────────────────────────────────────┘ │
                        │                                          │
                        │  ┌──────────┐  ┌──────────┐  ┌────────┐ │
                        │  │  SQLite  │  │ ChromaDB │  │  Groq  │ │
                        │  │ users,   │  │ PDF      │  │ Llama  │ │
                        │  │ messages,│  │ vectors  │  │ 3.3    │ │
                        │  │ journals │  │          │  │ 70B    │ │
                        │  └──────────┘  └──────────┘  └────────┘ │
                        └──────────────────────────────────────────┘
```

## Project Structure

```
app/                           # FastAPI backend
  main.py                      # API routes and startup
  langraph_runner.py            # LangGraph state machine
  core/
    config.py                   # Centralized settings (no os.getenv scatter)
    llm.py                      # LLM provider abstraction (Groq/OpenAI)
    vectorstore.py              # ChromaDB client
    guardrails.py               # Crisis keyword detection
  db/
    engine.py                   # Async SQLAlchemy engine
    models.py                   # Table definitions (users, messages, journals, etc.)
    message_store.py            # Chat sessions + message CRUD
    setup_db.py                 # Schema creation + migrations
  tools/
    journaling/                 # Journal prompts, storage, analytics, themes
    selfcare/                   # Mood tracking, RAG tool, reminders
    therapy/                    # Session parsing, insights, pattern analysis
    insights/                   # Cross-reference engine, weekly summary
  prompts/
    prompt_texts.py             # All LLM prompts in one place
  data/
    *.pdf                       # Mental health PDFs for RAG
    mindmate.db                 # SQLite database (auto-created)
    chroma/                     # ChromaDB vector store (auto-created)

frontend/                       # Next.js app
  src/
    app/
      chat/page.tsx             # Chat with sessions, streaming, markdown
      dashboard/page.tsx        # Mood analytics with colored charts
      journal/page.tsx          # Journal with mood borders, theme cloud
      therapy/page.tsx          # Therapy timeline with session creation
      summary/page.tsx          # Weekly AI-generated summary
      knowledge/page.tsx        # PDF upload, search with highlighting
      settings/page.tsx         # Account, export, tech stack info
    components/
      sidebar.tsx               # Navigation with sage green theme
      markdown.tsx              # react-markdown renderer
      mood-detail-panel.tsx     # Mood detail popup
    lib/
      api.ts                    # API client with all endpoints
      utils.ts                  # Mood colors, cn() helper

tests/                          # pytest suite
.github/workflows/ci.yml       # CI pipeline (lint + test + build)
docker-compose.yml              # Local Docker setup
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Chat** | | |
| POST | `/api/v1/chat/stream` | Streaming chat via SSE |
| POST | `/api/v1/chat/sessions` | Create new chat session |
| GET | `/api/v1/chat/sessions` | List chat sessions |
| DELETE | `/api/v1/chat/sessions/{id}` | Delete a chat session |
| **Messages** | | |
| GET | `/api/v1/messages` | Message history (with session filter) |
| GET | `/api/v1/messages/search` | Search messages by text/intent |
| PUT | `/api/v1/messages/{id}` | Edit a message |
| **Journal** | | |
| POST | `/api/v1/journal/entries` | Create entry (auto-analysis) |
| GET | `/api/v1/journal/entries` | List entries (with search) |
| PUT | `/api/v1/journal/entries/{id}` | Edit entry |
| DELETE | `/api/v1/journal/entries/{id}` | Delete entry |
| GET | `/api/v1/journal/themes` | Aggregated theme cloud |
| **Mood** | | |
| GET | `/api/v1/mood/analytics` | Timeline, distribution, streaks |
| GET | `/api/v1/mood/{id}/detail` | Mood detail with source content |
| **Therapy** | | |
| POST | `/api/v1/therapy/sessions` | Create therapy session |
| GET | `/api/v1/therapy/sessions` | List therapy sessions |
| PUT | `/api/v1/therapy/sessions/{id}` | Edit session |
| **Other** | | |
| GET | `/api/v1/summary/weekly` | AI-generated weekly summary |
| POST | `/api/v1/knowledge/upload` | Upload PDF to knowledge base |
| POST | `/api/v1/knowledge/search` | Search knowledge base |
| GET | `/api/v1/export` | Export all user data as JSON |

## Running Tests

```bash
# Backend
source venv/bin/activate
pytest tests/ -v
ruff check app/ tests/

# Frontend
cd frontend
npm run build
```

## Docker

```bash
docker compose up --build
```

Backend at http://localhost:8000, frontend at http://localhost:3000.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | — | Free from [console.groq.com](https://console.groq.com) |
| `LLM_PROVIDER` | No | `groq` | `groq` or `openai` |
| `OPENAI_API_KEY` | No | — | Only if using OpenAI provider |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///app/data/mindmate.db` | PostgreSQL for production |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated allowed origins |
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000` | Backend URL for frontend |

## Disclaimer

MindMate is not a substitute for professional mental health support. If you are in crisis, please contact the **988 Suicide & Crisis Lifeline** (call or text 988) or the **Crisis Text Line** (text HOME to 741741).

This is a personal portfolio project for learning and self-reflection.

---

Built with Groq, LangGraph, Next.js, and FastAPI.
