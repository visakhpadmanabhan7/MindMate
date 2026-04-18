from datetime import datetime, timezone

from sqlalchemy import insert

from app.core.openai_utils import run_classification_prompt
from app.db.engine import engine
from app.db.models import mood_logs
from app.prompts.prompt_texts import MOOD_CLASSIFIER, NEGATIVE_MOOD_PROMPT, PASSIVE_MOOD_CLASSIFIER


async def classify_mood(user_input: str) -> str:
    return await run_classification_prompt(MOOD_CLASSIFIER, user_input)


async def classify_mood_passive(user_input: str) -> str:
    """Classify mood from any text. Returns 'none' if no emotional content."""
    return await run_classification_prompt(PASSIVE_MOOD_CLASSIFIER, user_input)


async def is_negative_mood(user_input: str) -> bool:
    mood_type = await run_classification_prompt(NEGATIVE_MOOD_PROMPT, user_input)
    return mood_type == "negative"


async def log_mood(message: str, mood_label: str, user_id: str = "anonymous"):
    """Log mood from explicit selfcare route."""
    await log_mood_with_source(
        message=message,
        mood_label=mood_label,
        user_id=user_id,
        source_type="explicit",
    )


async def log_mood_with_source(
    message: str,
    mood_label: str,
    user_id: str = "anonymous",
    source_type: str = "explicit",
    source_id: int | None = None,
    confidence: str = "high",
):
    """Log mood with source tracking."""
    async with engine.begin() as conn:
        await conn.execute(
            insert(mood_logs).values(
                user_id=user_id,
                message=message,
                mood_label=mood_label,
                timestamp=datetime.now(timezone.utc),
                source_type=source_type,
                source_id=source_id,
                confidence=confidence,
            )
        )
