from app.core.openai_utils import run_classification_prompt
from app.prompts.prompt_texts import THERAPY_INPUT_CLASSIFIER
from app.tools.therapy.session_parser import parse_session_notes
from app.tools.therapy.therapy_insights import get_therapy_patterns, prepare_for_session
from app.tools.therapy.therapy_store import get_sessions, save_session


async def handle_therapy(
    user_input: str,
    user_id: str,
    message_history: list[dict],
) -> tuple[str, str]:
    """Route therapy intent to the appropriate handler.

    Returns (response, tool_class).
    """
    tool_class = await run_classification_prompt(THERAPY_INPUT_CLASSIFIER, user_input)

    if tool_class == "log_session":
        parsed = await parse_session_notes(user_input)
        result = await save_session(
            user_id=user_id,
            issues_discussed=parsed["issues_discussed"],
            learnings=parsed["learnings"],
            action_items=parsed["action_items"],
            techniques=parsed["techniques"],
            raw_notes=user_input,
        )

        issues = ", ".join(parsed["issues_discussed"]) if parsed["issues_discussed"] else "none extracted"
        actions = "\n".join(f"  - {a}" for a in parsed["action_items"]) if parsed["action_items"] else "  - none"
        techniques = ", ".join(parsed["techniques"]) if parsed["techniques"] else "none mentioned"

        response = (
            f"**Session #{result['session_number']} saved.**\n\n"
            f"**Issues discussed:** {issues}\n"
            f"**Learnings:** {parsed['learnings'][:300]}\n"
            f"**Action items:**\n{actions}\n"
            f"**Techniques:** {techniques}\n\n"
            f"Great work reflecting on your session!"
        )
        return response, "log_session"

    elif tool_class == "prepare":
        response = await prepare_for_session(user_id)
        return response, "prepare"

    elif tool_class == "review":
        sessions = await get_sessions(user_id, limit=5)
        if not sessions:
            return "No therapy sessions recorded yet. Share your session notes to get started!", "review"

        response = "**Your recent therapy sessions:**\n\n"
        for s in sessions:
            issues = ", ".join(s["issues_discussed"]) if s["issues_discussed"] else "—"
            response += (
                f"**Session #{s['session_number']}** ({s['date']})\n"
                f"  Issues: {issues}\n"
                f"  Learnings: {s['learnings'][:150]}...\n\n"
            )
        return response, "review"

    elif tool_class == "pattern":
        response = await get_therapy_patterns(user_id)
        return response, "pattern"

    else:
        # Default to logging
        parsed = await parse_session_notes(user_input)
        result = await save_session(
            user_id=user_id,
            issues_discussed=parsed["issues_discussed"],
            learnings=parsed["learnings"],
            action_items=parsed["action_items"],
            techniques=parsed["techniques"],
            raw_notes=user_input,
        )
        return f"Session #{result['session_number']} saved. Share more details anytime!", "log_session"
