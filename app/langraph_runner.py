from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

from app.tools.journaling.journalling_prompt_generator import generate_prompt
from app.tools.journaling.journal_store import save_journal_entry
from app.tools.journaling.prompt_utils import classify_journal_input
from app.tools.selfcare.mood_tracker import log_mood, classify_mood
from app.tools.selfcare.selcare_input_classifier import classify_selfcare_input

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
    user_input = state.input
    tool_class = await classify_selfcare_input(user_input)

    if tool_class == "mood":
        mood_label = await classify_mood(user_input)
        await log_mood(user_input, mood_label)
        response = f"[SelfCareAgent • MoodTracker] Mood logged as '{mood_label}'. You're not alone — thank you for checking in."

    elif tool_class == "reminder":
        # Stub: Reminder tool coming soon
        response = "[SelfCareAgent • Reminder] This feature is not available yet. Stay tuned!"

    else:  # tool_class == "advice"
        # Stub: RAGTool advice coming soon
        response = "[SelfCareAgent • Advice] This feature is under development. Thanks for your patience!"

    return state.model_copy(update={"response": response})

# Journaling agent node Stub
async def journaling_node(state: State) -> State:
    classification = await classify_journal_input(state.input)

    if classification == "prompt_request":
        prompt = await generate_prompt(state.input)
        response = f"[JournalingAgent] Prompt: {prompt}"
    else:
        await save_journal_entry(content=state.input)
        response = "[JournalingAgent] Entry saved. Feel free to share more or ask for a prompt."

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