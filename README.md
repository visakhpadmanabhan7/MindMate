# MINDMATE – AI‑Powered Mental Wellness Companion

**MindMate** is an AI‑powered mental health companion that helps users reflect, journal, and receive supportive self‑care guidance. It orchestrates GPT‑based tools using LangGraph workflows, tracks moods, and stores journal entries in a PostgreSQL database. It also features a Streamlit frontend for interaction.

---

## ✨ Features

### 🧠 Intent Detection  
Classifies whether user input is a journal entry, a self‑care request, or a prompt request using GPT-based LLM.

### 📓 Journaling Agent  
- Generates reflective prompts using templates and prompt utilities.  
- Stores journal entries with timestamps and user ID.  
- Classifies between journaling prompt requests and direct entries.

### ❤️ Self‑Care Agent  
- Classifies input into mood logs, reminders, or advice.  
- Stores mood data in PostgreSQL with mood classification.  
- Provides advice based on CBT documents via a RAG pipeline.  
- Stubbed support for scheduled wellness reminders.

### 🔍 Retrieval-Augmented Generation (RAG)  
- Extracts advice from CBT-based PDFs using pgvector and LangChain.  
- Populates vector DB from `/app/data/*.pdf`.

### 👥 User Management  
- Endpoints for user creation, checking existence, and future authentication.

---

## 🧱 Architecture

```text
            User Input
                 ↓
         Intent Detection (LLM)
             ↓           ↓
       Journal         Self-Care
        ↓     ↓         ↓     ↓
  Prompt?   Entry    Mood   Advice
                 ↓         ↓
               Database & RAG
```               
---
## 🗂️ Project Structure

| Path                     | Description                             |
| ------------------------ | --------------------------------------- |
| `app/main.py`            | FastAPI app & API endpoints             |
| `app/langraph_runner.py` | LangGraph flow for routing GPT tools    |
| `app/core/`              | OpenAI client and utility functions     |
| `app/prompts/`           | Templates for prompts                   |
| `app/tools/journaling/`  | Journal tools (prompts, storage, utils) |
| `app/tools/selfcare/`    | Mood logging, reminders, RAG advice     |
| `app/db/`                | SQLAlchemy models and DB ops            |
| `app/streamlit_app.py`   | Streamlit UI with journal/mood tabs     |

---
## 🛠️ Tech Stack
FastAPI + Uvicorn – Backend REST API

LangGraph + LangChain – Agent routing + RAG

OpenAI GPT API – Classification + Generation

PostgreSQL + pgvector – Journal + mood storage + vector DB

SQLAlchemy (async) – Database ORM

Streamlit – Frontend UI

Docker / docker-compose – Deployment

---

##  🧾 Database Models
### journal_entries
- id: UUID 
- user_id: Text 
- content: Text 
- created_at: Timestamp

### mood_logs
- id: UUID 
- user_id: Text 
- message: Text 
- mood_label: Text 
- timestamp: Timestamp
---

## 🚀 Getting Started
### Clone the Repository
- git clone https://github.com/visakhpadmanabhan7/MindMate.git
- cd MindMate
### Environment Variables
Create a .env file:
- OPENAI_API_KEY=your_openai_key
- DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mindmate

### Install Dependencies
- pip install -r requirements.txt

### Run PostgreSQL, frontend and backend with Docker
- docker-compose up -d

### Run the FastAPI App
- uvicorn app.main:app --reload

### Run the Streamlit App
- streamlit run app/streamlit_app.py

---
## 📡 API Endpoints

### POST /chat
Classifies input and responds with intent:
```json
{
  "message": "I feel anxious today."
}
```
Response:
```json
{
  "response": "Your message has been classified as a self-care request.",
  "intent": "selfcare"
}
```
### POST /chat
Classifies input and responds with intent:

```json
{
  "response": "Logged your mood as 'anxious'.",
  "intent": "selfcare",
  "tool_class": "mood"
}
```

### POST /register_user
- Registers a new user.

### GET /user_exists/{user_id}
- Checks if a user exists.

### GET /get_all_sample_records
- Returns last 5 mood and journal entries.

### GET /reset_state
- Drops and recreates all tables.
---

## 📊 Streamlit Frontend
- Journaling and mood logging with real-time feedback

- Sentiment detection using GPT

- Mood color visualization

- Easy self-care tip generation

- Generation
---

## 📌 Roadmap

- [x] Streamlit frontend  
- [x] Mood detection and logging
- [x] Journal entry
- [x] Journal prompt generation
- [x] RAG-based self-care using CBT PDFs
- [ ] Guardrails  
- [ ] Chat-style memory window
- [ ] Scheduled reminders and push notifications  
- [ ] Auth system (JWT/session)  
---

## ⚠️ Disclaimer
MindMate is not a substitute for professional mental health support. It is a prototype for self-reflection and research use only.

## 📄 License
MIT License – see LICENSE for details.
