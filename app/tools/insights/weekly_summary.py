"""Generate weekly summary from mood, journal, and therapy data."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.llm import get_llm
from app.db.engine import engine
from app.db.models import journal_entries, mood_logs, therapy_sessions

logger = logging.getLogger(__name__)

WEEKLY_SUMMARY_PROMPT = """
You are MindMate, a warm AI mental health companion. Generate a supportive weekly summary for the user based on their data from the past week.

**Mood Data:**
{mood_summary}

**Journal Entries:**
{journal_summary}

**Therapy Sessions:**
{therapy_summary}

Write a warm, personalized weekly recap with these sections:
1. **Mood trends** — patterns, most common moods, any shifts
2. **Journal highlights** — key themes and insights from their writing
3. **Therapy progress** — action items status, techniques practiced (if any sessions)
4. **Gentle recommendations** — 2-3 specific, actionable suggestions for the coming week based on patterns

Keep it warm, concise (under 300 words), and encouraging. Acknowledge progress. If data is sparse, keep it shorter and encourage more engagement.
"""


async def generate_weekly_summary(user_id: str) -> dict:
    """Generate a weekly summary from the past 7 days of user data."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Fetch mood data
    async with engine.begin() as conn:
        result = await conn.execute(
            select(mood_logs)
            .where(
                mood_logs.c.user_id == user_id,
                mood_logs.c.timestamp >= week_ago,
            )
            .order_by(mood_logs.c.timestamp)
        )
        mood_rows = result.fetchall()

    mood_summary = "No mood data this week."
    if mood_rows:
        mood_counts: dict[str, int] = {}
        for row in mood_rows:
            m = row.mood_label or "unknown"
            mood_counts[m] = mood_counts.get(m, 0) + 1
        mood_list = ", ".join(f"{m} ({c}x)" for m, c in mood_counts.items())
        mood_summary = f"{len(mood_rows)} mood entries: {mood_list}"

    # Fetch journal entries
    async with engine.begin() as conn:
        result = await conn.execute(
            select(journal_entries)
            .where(
                journal_entries.c.user_id == user_id,
                journal_entries.c.created_at >= week_ago,
            )
            .order_by(journal_entries.c.created_at)
        )
        journal_rows = result.fetchall()

    journal_summary = "No journal entries this week."
    if journal_rows:
        lines = []
        for row in journal_rows:
            date = str(row.created_at)[:10]
            mood = row.mood_label or "?"
            snippet = (row.content or "")[:100]
            lines.append(f"  - {date} (mood: {mood}): \"{snippet}...\"")
        journal_summary = f"{len(journal_rows)} entries:\n" + "\n".join(lines)

    # Fetch therapy sessions
    async with engine.begin() as conn:
        result = await conn.execute(
            select(therapy_sessions)
            .where(
                therapy_sessions.c.user_id == user_id,
                therapy_sessions.c.created_at >= week_ago,
            )
            .order_by(therapy_sessions.c.created_at)
        )
        therapy_rows = result.fetchall()

    therapy_summary = "No therapy sessions this week."
    if therapy_rows:
        import json

        lines = []
        for row in therapy_rows:
            issues = json.loads(row.issues_discussed or "[]")
            actions = json.loads(row.action_items or "[]")
            lines.append(
                f"  Session #{row.session_number} ({row.date}): "
                f"Issues: {', '.join(issues)}. "
                f"Action items: {', '.join(actions)}"
            )
        therapy_summary = f"{len(therapy_rows)} sessions:\n" + "\n".join(lines)

    # Generate summary via LLM
    llm = get_llm()
    prompt = WEEKLY_SUMMARY_PROMPT.format(
        mood_summary=mood_summary,
        journal_summary=journal_summary,
        therapy_summary=therapy_summary,
    )

    try:
        summary = await llm.chat(
            [{"role": "system", "content": prompt}],
            temperature=0.5,
        )
    except Exception:
        logger.exception("Failed to generate weekly summary")
        summary = "Unable to generate summary at this time."

    period_start = week_ago.strftime("%b %d")
    period_end = now.strftime("%b %d, %Y")

    return {
        "period": f"{period_start} - {period_end}",
        "summary": summary,
        "stats": {
            "mood_entries": len(mood_rows),
            "journal_entries": len(journal_rows),
            "therapy_sessions": len(therapy_rows),
        },
        "generated_at": str(now),
    }
