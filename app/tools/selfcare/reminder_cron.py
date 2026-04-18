import asyncio
from datetime import datetime, timedelta

from sqlalchemy import and_, select

from app.core.email_utils import send_email
from app.db.engine import engine
from app.db.models import reminders
from app.db.user_manager import get_user_email_by_id


async def run_reminder_check():
    now = datetime.now()

    # Define a window of +/-5 minutes
    lower = (now - timedelta(minutes=5)).strftime("%H:%M")
    upper = (now + timedelta(minutes=5)).strftime("%H:%M")

    print(f"Checking reminders between {lower} and {upper}...")

    async with engine.begin() as conn:
        result = await conn.execute(
            select(reminders).where(
                and_(
                    reminders.c.frequency == "daily",
                    reminders.c.active.is_(True),
                    reminders.c.time_of_day.between(lower, upper),
                )
            )
        )
        due_reminders = result.fetchall()

    for reminder in due_reminders:
        email = await get_user_email_by_id(reminder.user_id)
        if email:
            await send_email(
                to=email,
                subject="MindMate Daily Check-In",
                body=reminder.message,
            )
            print(f"Reminder sent to {email}: {reminder.message}")
        else:
            print(f"No email found for user {reminder.user_id}")


if __name__ == "__main__":
    asyncio.run(run_reminder_check())
