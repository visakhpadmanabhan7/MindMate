from datetime import datetime, time
from sqlalchemy import insert
from app.db.models import reminders
from app.db.setup_db import engine
from app.core.openai_utils import run_extraction_prompt
from app.prompts.prompt_texts import REMINDER_TIME_EXTRACTOR


async def set_reminder(user_input: str, user_id: str, message: str = "Time to check in", frequency: str = "daily") -> str:
    # Extract time from input
    reminder_time_str = await run_extraction_prompt(REMINDER_TIME_EXTRACTOR, user_input)
    reminder_time_str = reminder_time_str.strip() or "20:00"

    hour, minute = map(int, reminder_time_str.split(":"))
    reminder_time = time(hour, minute)
    #  Store in DB
    async with engine.begin() as conn:
        await conn.execute(
            insert(reminders).values(
                user_id=user_id,
                message=message,
                frequency=frequency,
                time_of_day=reminder_time,
                created_at=datetime.now()
            )
        )

    return f"Daily reminder set at {reminder_time_str}!"
