import json

from app.core.llm import get_llm
from app.prompts.prompt_texts import THERAPY_SESSION_PARSER


async def parse_session_notes(raw_notes: str) -> dict:
    """Parse freeform therapy session notes into structured fields using LLM."""
    llm = get_llm()
    result = await llm.extract(THERAPY_SESSION_PARSER, raw_notes)

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        # Try to extract JSON from the response if wrapped in markdown
        import re
        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            parsed = {
                "issues_discussed": [],
                "learnings": raw_notes,
                "action_items": [],
                "techniques": [],
            }

    return {
        "issues_discussed": parsed.get("issues_discussed", []),
        "learnings": parsed.get("learnings", ""),
        "action_items": parsed.get("action_items", []),
        "techniques": parsed.get("techniques", []),
    }
