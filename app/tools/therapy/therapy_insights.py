
from app.core.llm import get_llm
from app.db.message_store import get_recent_messages
from app.prompts.prompt_texts import THERAPY_PATTERN_PROMPT, THERAPY_PREP_PROMPT
from app.tools.therapy.therapy_store import get_sessions


async def get_therapy_patterns(user_id: str) -> str:
    """Analyze patterns across therapy sessions."""
    sessions = await get_sessions(user_id, limit=20)

    if not sessions:
        return "No therapy sessions recorded yet. Log your first session to start tracking patterns."

    llm = get_llm()

    session_summary = ""
    for s in sessions:
        session_summary += (
            f"\nSession {s['session_number']} ({s['date']}):\n"
            f"  Issues: {', '.join(s['issues_discussed'])}\n"
            f"  Learnings: {s['learnings'][:200]}\n"
            f"  Action items: {', '.join(s['action_items'])}\n"
            f"  Techniques: {', '.join(s['techniques'])}\n"
        )

    messages = [
        {"role": "system", "content": THERAPY_PATTERN_PROMPT},
        {"role": "user", "content": f"Here are my therapy sessions:\n{session_summary}"},
    ]

    return await llm.chat(messages, temperature=0.3)


async def prepare_for_session(user_id: str) -> str:
    """Generate a prep summary for an upcoming therapy session."""
    sessions = await get_sessions(user_id, limit=5)
    recent_messages = await get_recent_messages(user_id, limit=30)

    llm = get_llm()

    context_parts = []

    if sessions:
        last_session = sessions[-1]
        context_parts.append(
            f"Last therapy session (#{last_session['session_number']}, {last_session['date']}):\n"
            f"  Issues: {', '.join(last_session['issues_discussed'])}\n"
            f"  Action items: {', '.join(last_session['action_items'])}\n"
            f"  Techniques: {', '.join(last_session['techniques'])}"
        )

    if recent_messages:
        mood_messages = [
            m["content"] for m in recent_messages
            if m["role"] == "user"
        ][:10]
        if mood_messages:
            context_parts.append(
                "Recent user messages:\n" +
                "\n".join(f"  - {m[:100]}" for m in mood_messages)
            )

    if not context_parts:
        return (
            "No previous data to prepare from yet. "
            "Start by logging a therapy session or tracking your mood!"
        )

    messages = [
        {"role": "system", "content": THERAPY_PREP_PROMPT},
        {"role": "user", "content": "\n\n".join(context_parts)},
    ]

    return await llm.chat(messages, temperature=0.3)
