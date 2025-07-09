from fastapi import FastAPI, Request
from app.langraph_runner import app_flow

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message")

    # Run the LangGraph flow
    result = await app_flow.ainvoke({"input": user_input})

    return {"response": result.get("response")}