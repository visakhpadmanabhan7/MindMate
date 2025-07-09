# MINDMATE – AI Agent Mental Health Companion

MINDMATE is an AI-powered mental wellness assistant that helps users reflect, journal, and get supportive self-care guidance — all driven by multi-agent LangGraph architecture and GPT-based reasoning.

## Features

* SelfCareAgent (Agentic RAG) Understands mental health queries and provides safe, grounded advice using tools like:

  * RAGTool (CBT/WHO document retrieval via pgvector)
  * MoodTrackerTool (logs mood to Postgres)
  * WellnessReminderTool (schedules check-ins)
  * Built-in prompt safety guardrails

* JournalingAgent Encourages self-reflection and emotional awareness through:

  * PromptGeneratorTool (GPT-based reflective questions)
  * JournalStoreTool (stores entries in Postgres)

## Agent Flow (LangGraph)

User Input ↓ Intent Detection (gpt-4.1-nano) ↓ Journaling      Self-Care ↓              ↓ Prompt / Save   Advice / Tools

## Tech Stack

| Layer         | Tool / Library             |
| ------------- | -------------------------- |
| API Server    | FastAPI                    |
| Agent Engine  | LangGraph                  |
| LLMs          | OpenAI (gpt-4.1-nano/mini) |
| Vector DB     | pgvector + PostgreSQL      |
| Relational DB | PostgreSQL (Dockerized)    |
| ORM/Access    | SQLAlchemy (async)         |
| Env Mgmt      | python-dotenv              |

## Getting Started

### 1. Clone the repo

```
git clone https://github.com/yourusername/mindmate_proj.git
cd mindmate_proj
```

### 2. Set up .env

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mindmate
OPENAI_API_KEY=your-key-here
```

### 3. Start Postgres with pgvector

```
docker-compose up -d
```

### 4. Set up the database

```
python app/db/setup_db.py
```

### 5. Install dependencies

```
pip install -r requirements.txt
```

### 6. Run the API server

```
uvicorn app.main:app --reload
```

## Example Requests

### Journal Entry

```
POST /chat
{
  "message": "Today was a rough day"
}

Saves entry to DB with gentle response
```

### Prompt Request

```
{
  "message": "Give me a prompt to journal"
}

GPT-generated reflective prompt
```

### Self-Care Advice

```
{
  "message": "How do I reduce anxiety?"
}

Grounded, safe tip using SelfCareAgent
```

## Project Structure

mindmate\_proj/

```
app/
    langraph_runner.py       - LangGraph agents and routing
    main.py                  - FastAPI server
    db/                      - DB setup scripts
    tools/                   - Journaling and RAG tools

docker-compose.yml           - pgvector-enabled Postgres
.env                         - Secrets and config
requirements.txt
```

## Coming Soon

* Agentic RAG with document embedding and retrieval
* Daily wellness reminders via Telegram
* Mood tracking history
* Local frontend with Streamlit or Chainlit

## License

MIT License

Built with care to support mental clarity, reflection, and gentle growth.
