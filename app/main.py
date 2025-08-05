from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from app.db.setup_db import reset_db
from app.db.user_manager import create_user, get_user_by_email
from app.langraph_runner import app_flow
from app.db.view_records import fetch_sample_records
from langfuse import get_client, observe
get_client()
app = FastAPI()


# -------------------------
#  Request Models
# -------------------------

class ChatRequest(BaseModel):
    message: str
    email: EmailStr


class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str | None = None


# -------------------------
#  Main Chat Endpoint
# -------------------------

@observe(name="chat_request", as_type="tool")
@app.post("/chat")
async def chat(req: ChatRequest):
    user = await get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

    langfuse = get_client()
    langfuse.update_current_trace(
        session_id=str(user.id),
        metadata={
            "email": user.email,
            "chat_input": req.message
        }
    )

    result = await app_flow.ainvoke({
        "input": req.message,
        "user_id": user.id
    })
    result['email'] = user.email
    return result


# -------------------------
# Register New User
# -------------------------

@app.post("/register_user")
async def register_user(user: UserCreateRequest):
    existing = await get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    result = await create_user(email=user.email, name=user.name)
    return result


# -------------------------
#  Dev Utilities
# -------------------------

@app.get("/get_all_sample_records")
async def get_all_sample_records():
    return await fetch_sample_records(limit=5)


@app.get("/reset_state")
async def reset_state():
    return await reset_db()


@app.post("/user_exists")
async def user_exists(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = await get_user_by_email(email)
    if user:
        return {"exists": True}
    else:
        raise HTTPException(status_code=404, detail="User not found")
