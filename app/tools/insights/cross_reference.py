"""Cross-reference therapy sessions, journals, and CBT books for holistic feedback."""

import json
import logging

from app.core.llm import get_llm
from app.prompts.prompt_texts import CBT_FEEDBACK_PROMPT, THERAPY_RECALL_PROMPT
from app.tools.selfcare.rag_tool import get_cbt_recommendation
from app.tools.therapy.therapy_store import get_sessions

logger = logging.getLogger(__name__)


async def find_relevant_therapy_sessions(user_id: str, current_input: str, mood: str) -> list[dict]:
    """Find therapy sessions where similar issues were discussed."""
    sessions = await get_sessions(user_id, limit=10)
    if not sessions:
        return []

    # Simple keyword matching between current input and session issues
    input_lower = current_input.lower()
    relevant = []
    for session in sessions:
        issues = session.get("issues_discussed", [])
        learnings = session.get("learnings", "")
        action_items = session.get("action_items", [])

        # Check if any issue keyword appears in current input
        all_text = " ".join(issues + action_items + [learnings]).lower()
        score = sum(
            1 for word in input_lower.split()
            if len(word) > 3 and word in all_text
        )
        if score > 0:
            relevant.append({**session, "_relevance": score})

    relevant.sort(key=lambda s: s["_relevance"], reverse=True)
    return relevant[:3]


async def get_therapy_aware_feedback(
    user_id: str,
    current_input: str,
    mood: str,
) -> str | None:
    """Generate feedback that references past therapy sessions and CBT science.

    Returns None if no relevant therapy sessions found.
    """
    relevant_sessions = await find_relevant_therapy_sessions(user_id, current_input, mood)

    if not relevant_sessions:
        return None

    # Build therapy context
    therapy_context = ""
    for s in relevant_sessions:
        issues = ", ".join(s.get("issues_discussed", []))
        therapy_context += (
            f"\nSession #{s['session_number']} ({s['date']}):\n"
            f"  Issues: {issues}\n"
            f"  Learnings: {s.get('learnings', '')[:200]}\n"
            f"  Action items: {', '.join(s.get('action_items', []))}\n"
        )

    # Get CBT context via RAG
    try:
        cbt_context = await get_cbt_recommendation(
            f"What techniques help with {mood}?",
        )
    except Exception:
        cbt_context = "Practice self-compassion and mindful breathing."

    llm = get_llm()
    prompt = THERAPY_RECALL_PROMPT.format(
        current_input=current_input[:200],
        mood=mood,
        therapy_context=therapy_context,
        cbt_context=cbt_context[:500],
    )

    try:
        response = await llm.chat(
            [{"role": "system", "content": prompt}],
            temperature=0.3,
        )
        return response
    except Exception:
        logger.exception("Failed to generate therapy-aware feedback")
        return None
