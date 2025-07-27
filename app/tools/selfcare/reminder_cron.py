import asyncio
from datetime import datetime, timedelta, time as dt_time

from sqlalchemy import select, and_
from app.db.models import reminders
from app.db.setup_db import engine
from app.db.user_manager import get_user_email_by_id

from app.email_utils import send_email  # you'll write this too


async def run_reminder_check():
    now = datetime.now()
    now_time = now.time()

    # Define a window of ±5 minutes
    lower_bound = (datetime.combine(now.date(), now_time) - timedelta(minutes=5)).time()
    upper_bound = (datetime.combine(now.date(), now_time) + timedelta(minutes=5)).time()

    print(f" Checking reminders between {lower_bound} and {upper_bound}...")

    async with engine.begin() as conn:
        result = await conn.execute(
            select(reminders).where(
                and_(
                    reminders.c.frequency == "daily",
                    reminders.c.active == True,
                    reminders.c.time_of_day.between(lower_bound, upper_bound)
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
                body=reminder.message
            )
            print(f" Reminder sent to {email}: {reminder.message}")
        else:
            print(f" No email found for user {reminder.user_id}")


if __name__ == "__main__":
    asyncio.run(run_reminder_check())
