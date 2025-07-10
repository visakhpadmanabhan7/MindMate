from fastapi import FastAPI, Request

from app.db.setup_db import reset_db
from app.langraph_runner import app_flow

from app.db.view_records import fetch_sample_records

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message")

    # Run the LangGraph flow
    result = await app_flow.ainvoke({"input": user_input})

    return {"response": result.get("response")}

@app.get("/get_all_sample_records")
async def get_all_sample_records():
    return await fetch_sample_records(limit=5)

@app.get("/reset_state")
async def reset_state():
    return await reset_db()