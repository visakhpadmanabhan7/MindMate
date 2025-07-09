from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Async OpenAI client
client = AsyncOpenAI()

# shared state model
class State(BaseModel):
    input: str
    intent: str | None = None
    response: str | None = None

# Async Intent Detection Node
async def detect_intent(state: State) -> State:
    user_input = state.input

    response = await client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": "Classify this input as either 'selfcare' or 'journal'. Only return one of those two words.",
            },
            {"role": "user", "content": user_input},
        ],
    )

    intent = response.choices[0].message.content.strip().lower()
    return state.model_copy(update={"intent": intent})

# Routing logic
def route(state: State) -> str:
    return state.intent

# SelfCare agent node Stub
async def selfcare_node(state: State) -> State:
    response = f"[SelfCareAgent] You said: {state.input}. Here's a grounding tip: Take a deep breath and count to 4."
    return state.model_copy(update={"response": response})

# Journaling agent node Stub
async def journaling_node(state: State) -> State:
    response = "[JournalingAgent] Prompt: What's something you felt strongly about today?"
    return state.model_copy(update={"response": response})

# Define LangGraph
graph = StateGraph(State)
graph.add_node("intent", detect_intent)
graph.add_node("selfcare", selfcare_node)
graph.add_node("journal", journaling_node)

graph.set_entry_point("intent")
graph.add_conditional_edges("intent", route)
graph.add_edge("selfcare", END)
graph.add_edge("journal", END)

# Compile the graph
app_flow = graph.compile()

# Optional: For CLI testing
if __name__ == "__main__":
    import asyncio

    user_input = input("You: ")
    result = asyncio.run(app_flow.ainvoke({"input": user_input}))
    print("MINDMATE:", result["response"])