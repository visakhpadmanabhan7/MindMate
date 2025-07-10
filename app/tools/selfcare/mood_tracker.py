from datetime import datetime
from openai import AsyncOpenAI
from sqlalchemy import insert
from dotenv import load_dotenv

from app.db.models import mood_logs
from app.db.engine import engine

# Load env variables if not already loaded
load_dotenv()

# OpenAI client
client = AsyncOpenAI()

# Classify mood using LLM
async def classify_mood(user_input: str) -> str:
    """
    Uses GPT to classify the user's mood in one word (e.g., happy, sad, anxious).
    """
    system_prompt = (
        "Classify the user's mood in ONE word based on what they wrote. "
        "Examples: happy, sad, tired, anxious, overwhelmed, calm. "
        "Only return the word. Do not explain."
    )

    response = await client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content.strip().lower()

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
