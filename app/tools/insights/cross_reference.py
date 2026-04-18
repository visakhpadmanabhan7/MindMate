"""Cross-reference therapy sessions, journals, moods, and CBT knowledge for holistic feedback."""

import logging

from app.core.llm import get_llm
from app.prompts.prompt_texts import HISTORY_SYNTHESIS_PROMPT
from app.tools.journaling.journal_analytics import get_journal_entries
from app.tools.selfcare.mood_analytics import get_mood_analytics
from app.tools.selfcare.rag_tool import get_cbt_recommendation
from app.tools.therapy.therapy_store import get_sessions

logger = logging.getLogger(__name__)


async def find_relevant_therapy_sessions(
    user_id: str, current_input: str, mood: str
) -> list[dict]:
    """Find therapy sessions where similar issues were discussed."""
    sessions = await get_sessions(user_id, limit=10)
    if not sessions:
        return []

    input_lower = current_input.lower()
    relevant = []
    for session in sessions:
        issues = session.get("issues_discussed", [])
        learnings = session.get("learnings", "")
        action_items = session.get("action_items", [])

        all_text = " ".join(issues + action_items + [learnings]).lower()
        score = sum(
            1 for word in input_lower.split() if len(word) > 3 and word in all_text
        )
        if score > 0:
            relevant.append({**session, "_relevance": score})

    relevant.sort(key=lambda s: s["_relevance"], reverse=True)
    return relevant[:3]


async def gather_user_context(
    user_id: str, current_input: str, mood: str
) -> dict:
    """Gather all relevant user history: moods, journals, therapy sessions."""
    context = {"mood_context": "", "journal_context": "", "therapy_context": ""}

    # Recent mood trends
    try:
        mood_data = await get_mood_analytics(user_id)
        if mood_data.get("timeline"):
            recent = mood_data["timeline"][-10:]
            mood_counts: dict[str, int] = {}
            for entry in recent:
                m = entry.get("mood", "unknown")
                mood_counts[m] = mood_counts.get(m, 0) + 1
            mood_summary = ", ".join(f"{m} ({c}x)" for m, c in mood_counts.items())
            context["mood_context"] = (
                f"Recent moods (last {len(recent)} entries): {mood_summary}. "
                f"Total mood entries: {mood_data.get('total_entries', 0)}. "
                f"Current streak: {mood_data.get('streak', 0)} days."
            )
    except Exception:
        logger.debug("Could not fetch mood context")

    # Recent journal entries
    try:
        journal_data = await get_journal_entries(user_id, limit=5)
        entries = journal_data.get("entries", [])
        if entries:
            journal_lines = []
            for e in entries[:5]:
                date = str(e.get("created_at", ""))[:10]
                mood_label = e.get("mood_label", "")
                themes = ", ".join(e.get("themes", [])[:3])
                snippet = (e.get("content", ""))[:100]
                journal_lines.append(
                    f"  - {date} (mood: {mood_label}, themes: {themes}): \"{snippet}...\""
                )
            context["journal_context"] = "Recent journal entries:\n" + "\n".join(
                journal_lines
            )
    except Exception:
        logger.debug("Could not fetch journal context")

    # Relevant therapy sessions
    try:
        relevant_sessions = await find_relevant_therapy_sessions(
            user_id, current_input, mood
        )
        if relevant_sessions:
            therapy_lines = []
            for s in relevant_sessions:
                issues = ", ".join(s.get("issues_discussed", []))
                therapy_lines.append(
                    f"  Session #{s['session_number']} ({s['date']}): "
                    f"Issues: {issues}. "
                    f"Learnings: {s.get('learnings', '')[:150]}. "
                    f"Action items: {', '.join(s.get('action_items', []))}"
                )
            context["therapy_context"] = "Relevant therapy sessions:\n" + "\n".join(
                therapy_lines
            )
        else:
            # Even if no keyword match, include recent sessions for context
            all_sessions = await get_sessions(user_id, limit=3)
            if all_sessions:
                therapy_lines = []
                for s in all_sessions:
                    issues = ", ".join(s.get("issues_discussed", []))
                    therapy_lines.append(
                        f"  Session #{s['session_number']} ({s['date']}): Issues: {issues}"
                    )
                context["therapy_context"] = (
                    "Recent therapy sessions:\n" + "\n".join(therapy_lines)
                )
    except Exception:
        logger.debug("Could not fetch therapy context")

    return context


async def generate_history_section(
    user_id: str, current_input: str, mood: str
) -> str | None:
    """Generate the 'Based on your history' section by synthesizing all user data."""
    context = await gather_user_context(user_id, current_input, mood)

    # Only generate if we have meaningful context
    has_content = any(context.values())
    if not has_content:
        return None

    llm = get_llm()
    prompt = HISTORY_SYNTHESIS_PROMPT.format(
        current_input=current_input[:200],
        mood=mood,
        mood_context=context["mood_context"] or "No mood data available.",
        journal_context=context["journal_context"] or "No journal entries.",
        therapy_context=context["therapy_context"] or "No therapy sessions.",
    )

    try:
        response = await llm.chat(
            [{"role": "system", "content": prompt}],
            temperature=0.3,
        )
        return response.strip()
    except Exception:
        logger.exception("Failed to generate history section")
        return None


async def generate_science_section(mood: str) -> str | None:
    """Generate the 'What science says' section via RAG."""
    try:
        result = await get_cbt_recommendation(
            f"What evidence-based techniques help with feeling {mood}?"
        )
        if result and len(result) > 20:
            return result
    except Exception:
        logger.debug("Could not generate science section")
    return None


async def get_split_feedback(
    user_id: str, current_input: str, mood: str
) -> str | None:
    """Generate split feedback: 'Based on your history' + 'What science says'.

    Returns the combined formatted string, or None if nothing relevant.
    """
    history = await generate_history_section(user_id, current_input, mood)
    science = await generate_science_section(mood)

    parts = []
    if history:
        parts.append(f"**Based on your history:**\n{history}")
    if science:
        parts.append(f"**What science says:**\n{science}")

    if not parts:
        return None

    return "\n\n".join(parts)


# Keep backward compat
async def get_therapy_aware_feedback(
    user_id: str, current_input: str, mood: str
) -> str | None:
    """Generate feedback that references past therapy sessions and CBT science."""
    return await get_split_feedback(user_id, current_input, mood)
