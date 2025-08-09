from datetime import datetime
from sqlalchemy import insert

from app.core.openai_utils import run_classification_prompt
from app.db.models import mood_logs
from app.db.engine import engine
from app.prompts.prompt_texts import MOOD_CLASSIFIER, NEGATIVE_MOOD_PROMPT

# Classify mood using LLM
async def classify_mood(user_input: str) -> str:
    """
    Uses GPT to classify the user's mood in one word (e.g., happy, sad, anxious).
    """

    return await run_classification_prompt(MOOD_CLASSIFIER, user_input)

async def is_negative_mood(user_input: str) -> bool:
    mood_type = await run_classification_prompt(NEGATIVE_MOOD_PROMPT, user_input)
    print(f"Classified mood type: {mood_type}")
    return mood_type == "negative"


# Log mood to the DB
async def log_mood(message: str, mood_label: str, user_id: str = "anonymous"):
    """
    Inserts a mood log into the `mood_logs` table.
    """
    async with engine.begin() as conn:  # BEGIN = transactional
        stmt = insert(mood_logs).values(
            user_id=user_id,
            message=message,
            mood_label=mood_label,
            timestamp=datetime.utcnow()
        )
        await conn.execute(stmt)
