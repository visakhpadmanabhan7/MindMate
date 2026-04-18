import re
from datetime import datetime, timezone

from sqlalchemy import insert

from app.core.openai_utils import run_extraction_prompt
from app.db.engine import engine
from app.db.models import reminders
from app.prompts.prompt_texts import REMINDER_TIME_EXTRACTOR


async def set_reminder(
    user_input: str,
    user_id: str,
    message: str = "Time to check in",
    frequency: str = "daily",
) -> str:
    reminder_time_str = await run_extraction_prompt(REMINDER_TIME_EXTRACTOR, user_input)
    reminder_time_str = reminder_time_str.strip() or "20:00"

    # Validate HH:MM format, fallback to 20:00
    if not re.match(r"^\d{2}:\d{2}$", reminder_time_str):
        reminder_time_str = "20:00"

    async with engine.begin() as conn:
        await conn.execute(
            insert(reminders).values(
                user_id=user_id,
                message=message,
                frequency=frequency,
                time_of_day=reminder_time_str,
                created_at=datetime.now(timezone.utc),
            )
        )

    return f"Daily reminder set at {reminder_time_str}!"
