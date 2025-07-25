# MINDMATE – AI‑Powered Mental Wellness Companion

MindMate is a mental‑health companion that helps users reflect, journal and get supportive self‑care guidance. It orchestrates multiple GPT‑based tools through a LangGraph workflow, logs entries and moods to a PostgreSQL database, and exposes a simple FastAPI interface.

## Features

### 🧠 Intent Detection  
- Classifies whether user input is a journaling request or a self‑care query using an LLM prompt.

### 📓 Journaling Agent  
- Generates reflective prompts.
- Stores journal entries in a PostgreSQL database.
- Classifies input as a journal entry or a prompt request.

### ❤️ Self‑Care Agent  
- Classifies input into mood tracking, wellness reminders, or advice.
- Tracks moods and stores them with timestamps.
- Stub tools for reminders and advice (under development).

### 🛠 Tech Stack  
- **FastAPI** + **Uvicorn**: REST API.
- **LangGraph** + **LangChain**: Tool routing and orchestration.
- **OpenAI API**: All GPT calls (classification and generation).
- **PostgreSQL** + **pgvector**: Logging journals and moods.
- **SQLAlchemy (async)**: Database access.

---

## Architecture

```text
User Input
    ↓
Intent Detection (journal or self‑care)
    ↓
──────────────────────────────
↓                             ↓
Journaling Agent          Self‑Care Agent
↓                             ↓
Prompt or entry          Mood/reminder/advice
↓                             ↓
Database log              Mood log
```

---

## Project Structure

| Path                      | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| `app/main.py`             | FastAPI app + API routes                 |
| `app/langraph_runner.py`  | LangGraph definition & tool wiring       |
| `app/core/`               | OpenAI client & prompt utils             |
| `app/prompts/`            | Prompt templates                         |
| `app/tools/journaling/`   | Journal logic: prompt generator, storage |
| `app/tools/selfcare/`     | Mood tracking, input classification      |
| `app/db/`                 | Database models, setup, views            |

---

## Database Models

### journal_entries  
- `id`: UUID  
- `user_id`: Text  
- `content`: Text  
- `created_at`: Timestamp

### mood_logs  
- `id`: UUID  
- `user_id`: Text  
- `message`: Text  
- `mood_label`: Text  
- `timestamp`: Timestamp

---

## Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/visakhpadmanabhan7/MindMate.git
cd MindMate
```

### 2. Environment Setup
Create a `.env` file with the following:
```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mindmate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run PostgreSQL (via Docker)
```bash
docker-compose up -d
```

### 5. Initialize DB
```bash
python app/db/setup_db.py
```

### 6. Start the API Server
```bash
uvicorn app.main:app --reload
```

---

## API Endpoints

### `POST /chat`
```json
{
  "message": "I feel overwhelmed today."
}
```
Returns:
```json
{
  "response": "Your entry has been saved. Would you like a prompt?",
  "intent": "journal",
  "tool_class": "entry"
}
```

### `GET /get_all_sample_records`
Returns last 5 journal entries and mood logs.

### `GET /reset_state`
Drops and recreates database tables (for dev/test).

---

## Roadmap

- [ ] Implement wellness reminders
- [ ] Add RAG-based self-care advice with pgvector
- [ ] Visual frontend (Streamlit or Chainlit)
- [ ] Mood tracking visualization

---

## Disclaimer

MindMate is not a replacement for professional mental health care. It is a research tool designed for self-reflection and educational use. For medical or mental health emergencies, seek professional help.

---



## API Endpoints

### `POST /chat`
Sends a message to MindMate and returns a structured response based on the detected intent.

#### Example 1 – Journal Entry
**Request:**
```json
{
  "message": "Today was a bad dat at work. i could not do a lot of work"
}
```

**Response:**
```json
{
  "intent": "journal",
  "response": "Entry saved as journal. Feel free to share more or ask for a prompt.",
  "tool_class": "entry"
}
```

#### Example 2 – Ask for a journaling prompt
**Request:**
```json
{
  "message": "Can you give me something to write about?"
}
```

**Response:**
```json
{
  "response": "Here's a prompt: What's something you've learned about yourself recently?",
  "intent": "journal",
  "tool_class": "prompt_request"
}
```

#### Example 3 – Mood tracking
**Request:**
```json
{
  "message": "I’ve been feeling super anxious all day."
}
```

**Response:**
```json
{
  "response": "Got it. I’ve logged your mood as 'anxious'. Take a moment to breathe.",
  "intent": "selfcare",
  "tool_class": "mood"
}
```

---

### `GET /get_all_sample_records`
Fetches the latest 5 entries from both `journal_entries` and `mood_logs`.

**Response:**
```json
{
  "journal_entries": [
    {
      "user_id": "user_1",
      "content": "Today was a hard day at work...",
      "created_at": "2025-07-24T10:42:11"
    }
  ],
  "mood_logs": [
    {
      "user_id": "user_1",
      "message": "I feel burnt out",
      "mood_label": "exhausted",
      "timestamp": "2025-07-24T10:43:00"
    }
  ]
}
```

---

### `GET /reset_state`
Drops and recreates the `journal_entries` and `mood_logs` tables. Useful for resetting the app during development or testing.

**Response:**
```json
{
  "status": "reset_successful"
}
```
