import glob
import json
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr

from app.core.config import get_settings
from app.db import message_store
from app.db.message_store import (
    create_session,
    delete_session,
    get_recent_messages,
    search_messages,
    update_message,
    update_session_title,
)
from app.db.setup_db import setup
from app.db.user_manager import authenticate_user, create_user, get_user_by_email
from app.db.view_records import fetch_sample_records
from app.langraph_runner import app_flow
from app.tools.journaling.journal_analytics import get_journal_entries, get_journal_themes
from app.tools.journaling.journal_store import (
    delete_journal_entry,
    get_journal_entry_by_id,
    save_journal_entry_direct,
    update_journal_entry,
)
from app.tools.selfcare.mood_analytics import get_mood_analytics, get_mood_detail
from app.tools.therapy.therapy_store import get_sessions, save_session, update_session

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup()
    yield


app = FastAPI(title="MindMate API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request Models ---


class ChatRequest(BaseModel):
    message: str
    email: EmailStr
    session_id: int | None = None


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class JournalRequest(BaseModel):
    email: EmailStr
    content: str


class MessageUpdateRequest(BaseModel):
    email: EmailStr
    content: str


class TherapyUpdateRequest(BaseModel):
    email: EmailStr
    issues_discussed: list[str] | None = None
    learnings: str | None = None
    action_items: list[str] | None = None
    techniques: list[str] | None = None
    raw_notes: str | None = None


# --- Chat ---


@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

    result = await app_flow.ainvoke({
        "input": req.message,
        "user_id": user.id,
        "session_id": req.session_id,
    })
    return {
        "response": result["response"],
        "intent": result["intent"],
        "tool_class": result["tool_class"],
        "email": user.email,
    }


@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    result = await app_flow.ainvoke({
        "input": req.message,
        "user_id": user.id,
        "session_id": req.session_id,
    })

    response_text = result.get("response", "")
    intent = result.get("intent", "")
    tool_class = result.get("tool_class", "")

    # Auto-title session from first message
    if req.session_id:
        session_msgs = await get_recent_messages(user.id, limit=3, session_id=req.session_id)
        # If this is the first exchange (2 messages: user + assistant), set title
        if len(session_msgs) <= 2:
            title = req.message[:50] + ("..." if len(req.message) > 50 else "")
            await update_session_title(req.session_id, user.id, title)

    async def event_generator():
        yield f"data: {json.dumps({'type': 'meta', 'intent': intent, 'tool_class': tool_class})}\n\n"
        chunk_size = 8
        for i in range(0, len(response_text), chunk_size):
            yield f"data: {json.dumps({'type': 'token', 'content': response_text[i:i + chunk_size]})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


# --- Chat Sessions ---


class SessionCreateRequest(BaseModel):
    email: EmailStr


@app.post("/api/v1/chat/sessions")
async def create_chat_session(req: SessionCreateRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return await create_session(user.id)


@app.get("/api/v1/chat/sessions")
async def list_chat_sessions(email: str = Query(...), limit: int = Query(50, ge=1, le=200)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"sessions": await message_store.get_sessions(user.id, limit=limit)}


@app.delete("/api/v1/chat/sessions/{session_id}")
async def remove_chat_session(session_id: int, email: str = Query(...)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    deleted = await delete_session(session_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "id": session_id}


# --- Users ---


@app.post("/api/v1/register_user")
async def register_user(req: UserCreateRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    existing = await get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    return await create_user(email=req.email, password=req.password, name=req.name)


@app.post("/api/v1/login")
async def login(req: LoginRequest):
    user = await authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"status": "ok", "email": user.email, "name": user.name}


@app.post("/api/v1/user_exists")
async def user_exists(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    user = await get_user_by_email(email)
    if user:
        return {"exists": True}
    raise HTTPException(status_code=404, detail="User not found")


# --- Journal ---


@app.post("/api/v1/journal/entries")
async def create_journal_entry(req: JournalRequest):
    """Create journal entry with auto mood + theme + entity extraction."""
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await save_journal_entry_direct(content=req.content, user_id=user.id)


@app.put("/api/v1/journal/entries/{entry_id}")
async def edit_journal_entry(entry_id: int, req: JournalRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await update_journal_entry(entry_id, req.content, user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result


@app.delete("/api/v1/journal/entries/{entry_id}")
async def remove_journal_entry(entry_id: int, email: str = Query(...)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = await delete_journal_entry(entry_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted", "id": entry_id}


@app.get("/api/v1/journal/entries/{entry_id}")
async def get_journal_entry(entry_id: int, email: str = Query(...)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entry = await get_journal_entry_by_id(entry_id, user.id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@app.get("/api/v1/journal/entries")
async def journal_entries_endpoint(
    email: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None),
):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await get_journal_entries(user.id, limit=limit, offset=offset, search=search)


@app.get("/api/v1/journal/themes")
async def journal_themes_endpoint(email: str = Query(...)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await get_journal_themes(user.id)


# --- Mood Analytics ---


@app.get("/api/v1/mood/analytics")
async def mood_analytics(email: str = Query(...)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await get_mood_analytics(user.id)


@app.get("/api/v1/mood/{mood_id}/detail")
async def mood_detail_endpoint(mood_id: int, email: str = Query(...)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    detail = await get_mood_detail(mood_id, user.id)
    if not detail:
        raise HTTPException(status_code=404, detail="Mood record not found")
    return detail


# --- Therapy Sessions ---


class TherapyCreateRequest(BaseModel):
    email: EmailStr
    issues_discussed: list[str] = []
    learnings: str = ""
    action_items: list[str] = []
    techniques: list[str] = []
    date: str | None = None


@app.post("/api/v1/therapy/sessions")
async def create_therapy_session(req: TherapyCreateRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await save_session(
        user_id=user.id,
        issues_discussed=req.issues_discussed,
        learnings=req.learnings,
        action_items=req.action_items,
        techniques=req.techniques,
        date=req.date,
    )


@app.get("/api/v1/therapy/sessions")
async def therapy_sessions_endpoint(
    email: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"sessions": await get_sessions(user.id, limit=limit)}


@app.put("/api/v1/therapy/sessions/{session_id}")
async def edit_therapy_session(session_id: int, req: TherapyUpdateRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updates = req.model_dump(exclude={"email"}, exclude_none=True)
    result = await update_session(session_id, user.id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


# --- Messages ---


@app.get("/api/v1/messages")
async def messages_endpoint(
    email: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    session_id: int | None = Query(None),
):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"messages": await get_recent_messages(user.id, limit=limit, session_id=session_id)}


@app.get("/api/v1/messages/search")
async def search_messages_endpoint(
    email: str = Query(...),
    q: str | None = Query(None),
    intent: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"messages": await search_messages(user.id, query=q, intent=intent, limit=limit)}


@app.put("/api/v1/messages/{message_id}")
async def edit_message(message_id: int, req: MessageUpdateRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await update_message(message_id, user.id, req.content)
    if not result:
        raise HTTPException(status_code=404, detail="Message not found or not editable")
    return result


# --- Weekly Summary ---


@app.get("/api/v1/summary/weekly")
async def weekly_summary_endpoint(email: str = Query(...)):
    from app.tools.insights.weekly_summary import generate_weekly_summary

    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await generate_weekly_summary(user.id)


# --- Data Export ---


@app.get("/api/v1/export")
async def export_data(email: str = Query(...)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    mood_data = await get_mood_analytics(user.id)
    journal_data = await get_journal_entries(user.id, limit=1000)
    therapy_data = await get_sessions(user.id, limit=100)
    message_data = await get_recent_messages(user.id, limit=1000)

    export = {
        "user": {"email": user.email, "name": user.name},
        "moods": mood_data,
        "journals": journal_data,
        "therapy_sessions": therapy_data,
        "messages": message_data,
    }

    return StreamingResponse(
        iter([json.dumps(export, indent=2, default=str)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=mindmate_export.json"},
    )


# --- Knowledge Base / PDFs ---

PDF_DIR = Path(__file__).parent / "data"


@app.get("/api/v1/knowledge/documents")
async def list_documents():
    """List all PDF documents with metadata."""
    from app.core.vectorstore import get_document_chunk_count

    pdf_files = glob.glob(str(PDF_DIR / "*.pdf"))
    docs = []
    for path in sorted(pdf_files):
        name = os.path.basename(path)
        size_kb = round(os.path.getsize(path) / 1024)
        chunks = get_document_chunk_count(name)
        docs.append({
            "name": name,
            "size_kb": size_kb,
            "chunks": chunks,
            "indexed": chunks > 0,
        })
    return {"documents": docs}


@app.post("/api/v1/knowledge/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF and index it into the knowledge base."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    dest = PDF_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    from langchain_chroma import Chroma
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    from app.core.vectorstore import get_embedding_model

    loader = PyPDFLoader(str(dest))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source_doc"] = file.filename
        doc.metadata["page_number"] = doc.metadata.get("page", 0) + 1

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        collection_name="cbt_docs",
        persist_directory=settings.CHROMA_PATH,
    )

    return {"status": "indexed", "filename": file.filename, "chunks": len(chunks), "pages": len(docs)}


@app.delete("/api/v1/knowledge/{filename}")
async def delete_document(filename: str):
    """Delete a PDF and remove its vectors from the knowledge base."""
    from app.core.vectorstore import delete_document_vectors

    filepath = PDF_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove vectors from ChromaDB
    removed = delete_document_vectors(filename)

    # Remove the file
    filepath.unlink()

    return {"status": "deleted", "filename": filename, "vectors_removed": removed}


@app.post("/api/v1/knowledge/search")
async def search_documents(data: dict):
    """Search the knowledge base with a query."""
    from app.core.vectorstore import search_knowledge_base

    query = data.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    results = search_knowledge_base(query, k=data.get("k", 5))
    return {"results": results, "query": query}


# Keep old endpoint for backward compat
@app.get("/api/v1/pdfs")
async def list_pdfs_compat():
    result = await list_documents()
    return {"pdfs": result["documents"]}


# --- Dev Utilities ---


@app.get("/api/v1/dev/sample_records")
async def get_all_sample_records():
    return await fetch_sample_records(limit=5)
