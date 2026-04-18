"""Crisis detection guardrails for mental health safety."""

import re

CRISIS_KEYWORDS = [
    r"\bsuicid\w*\b",
    r"\bkill\s*(my)?self\b",
    r"\bself[- ]?harm\b",
    r"\bend\s*(my|it\s+all|everything)\b",
    r"\bwant\s+to\s+die\b",
    r"\bdon'?t\s+want\s+to\s+(live|be\s+alive|exist)\b",
    r"\bhurt\s+myself\b",
    r"\bno\s+reason\s+to\s+live\b",
    r"\bbetter\s+off\s+dead\b",
    r"\bcut(ting)?\s+myself\b",
]

CRISIS_RESPONSE = """I hear you, and I want you to know that what you're feeling matters. Please reach out to someone who can help:

**988 Suicide & Crisis Lifeline** — Call or text **988** (US)
**Crisis Text Line** — Text **HOME** to **741741**
**International Association for Suicide Prevention** — https://www.iasp.info/resources/Crisis_Centres/

You are not alone. A trained counselor can provide the support you need right now.

If you're in immediate danger, please call emergency services (911 in the US).

*MindMate is not a substitute for professional mental health support.*"""


def check_crisis(text: str) -> str | None:
    """Check if text contains crisis-related language.

    Returns the crisis response string if detected, None otherwise.
    """
    text_lower = text.lower()
    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, text_lower):
            return CRISIS_RESPONSE
    return None
