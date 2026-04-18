import logging

from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from app.core.guardrails import check_crisis
from app.core.llm import get_llm
from app.db.message_store import get_recent_messages, save_message
from app.prompts.prompt_texts import (
    GENERAL_CHAT_PROMPT,
    INTENT_DETECTOR,
)
from app.tools.journaling.journal_store import save_journal_entry
from app.tools.journaling.journalling_prompt_generator import generate_prompt
from app.tools.journaling.prompt_utils import classify_journal_input
from app.tools.selfcare.mood_tracker import (
    classify_mood,
    classify_mood_passive,
    is_negative_mood,
    log_mood,
    log_mood_with_source,
)
from app.tools.selfcare.rag_tool import get_cbt_recommendation
from app.tools.selfcare.selcare_input_classifier import classify_selfcare_input
from app.tools.selfcare.wellness_reminder import set_reminder
from app.tools.therapy.therapy_router import handle_therapy
from app.tools.insights.cross_reference import get_therapy_aware_feedback

logger = logging.getLogger(__name__)


class State(BaseModel):
    input: str
    user_id: str
    intent: str | None = None
    response: str | None = None
    tool_class: str | None = None
    message_history: list[dict] = []
    detected_mood: str | None = None


async def load_history(state: State) -> State:
    history = await get_recent_messages(state.user_id, limit=20)
    return state.model_copy(update={"message_history": history})


async def detect_intent(state: State) -> State:
    llm = get_llm()

    context = ""
    if state.message_history:
        recent = state.message_history[-6:]
        context = "Recent conversation:\n"
        for msg in recent:
            context += f"  {msg['role']}: {msg['content'][:100]}\n"
        context += "\nNow classify this new message:\n"

    intent = await llm.classify(INTENT_DETECTOR, context + state.input)

    if intent not in ("selfcare", "journal", "therapy", "general"):
        intent = "general"

    return state.model_copy(update={"intent": intent})


def route(state: State) -> str:
    crisis = check_crisis(state.input)
    if crisis:
        return "crisis"
    return state.intent


async def crisis_node(state: State) -> State:
    crisis_response = check_crisis(state.input)
    return state.model_copy(update={
        "response": crisis_response,
        "intent": "crisis",
        "tool_class": "crisis",
    })


async def selfcare_node(state: State) -> State:
    user_input = state.input
    user_id = state.user_id

    try:
        tool_class = await classify_selfcare_input(user_input)

        if tool_class == "mood":
            mood_label = await classify_mood(user_input)
            await log_mood(message=user_input, mood_label=mood_label, user_id=user_id)

            if await is_negative_mood(user_input):
                advice = await get_cbt_recommendation(
                    f"What can I do if I feel {mood_label}?"
                )
                response = (
                    f"Mood logged as **{mood_label}**.\n\n"
                    f"Here's something that might help:\n\n{advice}"
                )
            else:
                response = (
                    f"Mood logged as **{mood_label}**.\n\n"
                    f"That's great! Keep up the good work and stay mindful."
                )
            return state.model_copy(update={
                "response": response,
                "tool_class": tool_class,
                "detected_mood": mood_label,
            })

        elif tool_class == "advice":
            response = await get_cbt_recommendation(user_input)
        elif tool_class == "reminder":
            response = await set_reminder(
                user_input=user_input,
                user_id=user_id,
                message="Time to journal and check in",
                frequency="daily",
            )
        else:
            response = await get_cbt_recommendation(user_input)
            tool_class = "advice"
    except Exception:
        logger.exception("Error in selfcare_node")
        response = "I'm having trouble processing that right now. Could you try rephrasing?"
        tool_class = "error"

    return state.model_copy(update={
        "response": response,
        "tool_class": tool_class,
    })


async def journaling_node(state: State) -> State:
    try:
        classify_journal = await classify_journal_input(state.input)

        if classify_journal == "prompt_request":
            prompt = await generate_prompt(state.input)
            response = prompt
        else:
            await save_journal_entry(content=state.input, user_id=state.user_id)
            response = "Entry saved to your journal. Feel free to share more or ask for a prompt."
            classify_journal = "entry"
    except Exception:
        logger.exception("Error in journaling_node")
        response = "I couldn't process your journal request right now. Please try again."
        classify_journal = "error"

    return state.model_copy(update={
        "response": response,
        "tool_class": classify_journal,
    })


async def therapy_node(state: State) -> State:
    try:
        response, tool_class = await handle_therapy(
            user_input=state.input,
            user_id=state.user_id,
            message_history=state.message_history,
        )
    except Exception:
        logger.exception("Error in therapy_node")
        response = "I couldn't process your therapy request right now. Please try again."
        tool_class = "error"

    return state.model_copy(update={
        "response": response,
        "tool_class": tool_class,
    })


async def general_node(state: State) -> State:
    llm = get_llm()

    msgs = [{"role": "system", "content": GENERAL_CHAT_PROMPT}]
    if state.message_history:
        msgs.extend(state.message_history[-6:])
    msgs.append({"role": "user", "content": state.input})

    try:
        response = await llm.chat(msgs, temperature=0.7)
    except Exception:
        logger.exception("Error in general_node")
        response = "Hey! I'm here to help with journaling, mood tracking, and self-care. What would you like to do?"

    return state.model_copy(update={
        "response": response,
        "tool_class": "general",
    })


async def enrich_response(state: State) -> State:
    """Passive mood detection + therapy-aware recall.

    Runs after intent nodes, before save_messages.
    """
    # Skip if mood was already explicitly detected (selfcare/mood path)
    if state.intent == "selfcare" and state.tool_class == "mood":
        return state

    # Skip for crisis
    if state.intent == "crisis":
        return state

    try:
        # Passive mood detection
        mood = await classify_mood_passive(state.input)

        if mood == "none":
            return state

        updates = {"detected_mood": mood}

        # Check if this mood/topic was discussed in therapy
        feedback = await get_therapy_aware_feedback(
            user_id=state.user_id,
            current_input=state.input,
            mood=mood,
        )

        if feedback and state.response:
            updates["response"] = (
                state.response + "\n\n---\n\n" + feedback
            )

        return state.model_copy(update=updates)

    except Exception:
        logger.exception("Error in enrich_response")
        return state


async def save_messages(state: State) -> State:
    """Save user + assistant messages. Log passive mood if detected."""
    user_msg_id = await save_message(
        user_id=state.user_id,
        role="user",
        content=state.input,
        intent=state.intent,
    )

    if state.response:
        await save_message(
            user_id=state.user_id,
            role="assistant",
            content=state.response,
            intent=state.intent,
            tool_class=state.tool_class,
        )

    # Log passive mood (if detected and not already logged explicitly)
    if (
        state.detected_mood
        and state.detected_mood != "none"
        and not (state.intent == "selfcare" and state.tool_class == "mood")
    ):
        await log_mood_with_source(
            message=state.input[:200],
            mood_label=state.detected_mood,
            user_id=state.user_id,
            source_type="chat",
            source_id=user_msg_id,
            confidence="medium",
        )

    return state


# Build the graph
graph = StateGraph(State)
graph.add_node("load_history", load_history)
graph.add_node("intent", detect_intent)
graph.add_node("crisis", crisis_node)
graph.add_node("selfcare", selfcare_node)
graph.add_node("journal", journaling_node)
graph.add_node("therapy", therapy_node)
graph.add_node("general", general_node)
graph.add_node("enrich_response", enrich_response)
graph.add_node("save_messages", save_messages)

graph.set_entry_point("load_history")
graph.add_edge("load_history", "intent")
graph.add_conditional_edges("intent", route)
graph.add_edge("crisis", "enrich_response")
graph.add_edge("selfcare", "enrich_response")
graph.add_edge("journal", "enrich_response")
graph.add_edge("therapy", "enrich_response")
graph.add_edge("general", "enrich_response")
graph.add_edge("enrich_response", "save_messages")
graph.add_edge("save_messages", END)

app_flow = graph.compile()


if __name__ == "__main__":
    import asyncio

    user_input = input("You: ")
    result = asyncio.run(app_flow.ainvoke({"input": user_input, "user_id": "test"}))
    print("MINDMATE:", result["response"])
