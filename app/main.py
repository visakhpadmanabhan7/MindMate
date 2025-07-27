from fastapi import HTTPException,FastAPI


from app.db.setup_db import reset_db
from app.db.user_manager import create_user, get_user_by_id
from app.langraph_runner import app_flow

from app.db.view_records import fetch_sample_records
from pydantic import BaseModel

app = FastAPI()



class ChatRequest(BaseModel):
    message: str
    user_id: str

class UserCreateRequest(BaseModel):
    id: str
    email: str
    name: str | None = None


@app.post("/chat")
async def chat(req: ChatRequest):
    user = await get_user_by_id(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

    result = await app_flow.ainvoke({
        "input": req.message,
        "user_id": req.user_id
    })
    return result

@app.get("/get_all_sample_records")
async def get_all_sample_records():
    return await fetch_sample_records(limit=5)


@app.get("/reset_state")
async def reset_state():
    return await reset_db()


@app.post("/register_user")
async def register_user(user: UserCreateRequest):
    result = await create_user(user_id=user.id, email=user.email, name=user.name)
    return result
