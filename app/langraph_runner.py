from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from app.core.openai_client import client
from app.prompts.prompt_texts import INTENT_DETECTOR
from app.tools.journaling.journalling_prompt_generator import generate_prompt
from app.tools.journaling.journal_store import save_journal_entry
from app.tools.journaling.prompt_utils import classify_journal_input
from app.tools.selfcare.mood_tracker import log_mood, classify_mood
from app.tools.selfcare.selcare_input_classifier import classify_selfcare_input
from app.core.openai_utils import run_classification_prompt


# shared state model
class State(BaseModel):
    input: str
    intent: str | None = None
    response: str | None = None
    tool_class: str | None = None

# Async Intent Detection Node
async def detect_intent(state: State) -> State:
    user_input = state.input

    intent = await run_classification_prompt(INTENT_DETECTOR, user_input)
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
        response = f"Mood logged as '{mood_label}'. You're not alone — thank you for checking in."

    elif tool_class == "reminder":
        # Stub: Reminder tool coming soon
        response = "[SelfCareAgent • Reminder] This feature is not available yet. Stay tuned!"

    else:  # tool_class == "advice"
        # Stub: RAGTool advice coming soon
        response = "[SelfCareAgent • Advice] This feature is under development. Thanks for your patience!"

    return state.model_copy(update={"response": response,
                                    "intent": state.intent,
                                    "tool_class": tool_class})
# Journaling agent node Stub
async def journaling_node(state: State) -> State:
    classify_journal = await classify_journal_input(state.input)

    if classify_journal == "prompt_request":
        prompt = await generate_prompt(state.input)
        response = f"{prompt}"
    else:
        await save_journal_entry(content=state.input)
        response = "Entry saved as journal. Feel free to share more or ask for a prompt."

    return state.model_copy(update={"response": response,
                                    "intent": state.intent,
                                    "tool_class": classify_journal})

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