import json
import logging
import re
from datetime import datetime, timezone

from sqlalchemy import delete, insert, select, update

from app.core.llm import get_llm
from app.db.engine import engine
from app.db.models import journal_entries
from app.prompts.prompt_texts import JOURNAL_ANALYZER
from app.tools.selfcare.mood_tracker import log_mood_with_source

logger = logging.getLogger(__name__)


async def _analyze_entry(content: str) -> dict:
    """Extract mood, themes, and entities from journal content via LLM."""
    llm = get_llm()
    result = await llm.extract(JOURNAL_ANALYZER, content)

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
        else:
            parsed = {"mood": "neutral", "themes": [], "entities": []}

    # Parse sentiment_score safely
    score = parsed.get("sentiment_score", 0.0)
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    return {
        "mood": parsed.get("mood", "neutral"),
        "themes": parsed.get("themes", []),
        "entities": parsed.get("entities", []),
        "sentiment_score": max(-1.0, min(1.0, score)),
        "summary": parsed.get("summary", ""),
    }


async def save_journal_entry(content: str, user_id: str = "anonymous") -> dict:
    """Save journal entry from chat with analysis + mood logging. Returns entry dict."""
    analysis = await _analyze_entry(content)
    now = datetime.now(timezone.utc)

    async with engine.begin() as conn:
        result = await conn.execute(
            insert(journal_entries).values(
                user_id=user_id,
                content=content,
                created_at=now,
                mood_label=analysis["mood"],
                themes=json.dumps(analysis["themes"]),
                entities=json.dumps(analysis["entities"]),
                sentiment_score=analysis["sentiment_score"],
                summary=analysis["summary"],
            )
        )
        entry_id = result.inserted_primary_key[0]

    # Log mood with source tracking
    if analysis["mood"] and analysis["mood"] != "neutral":
        await log_mood_with_source(
            message=content[:200],
            mood_label=analysis["mood"],
            user_id=user_id,
            source_type="journal",
            source_id=entry_id,
            confidence="medium",
        )

    return {
        "id": entry_id,
        "mood": analysis["mood"],
        "themes": analysis["themes"],
        "summary": analysis["summary"],
    }


async def save_journal_entry_direct(content: str, user_id: str) -> dict:
    """Save journal entry with auto mood + theme + entity extraction."""
    analysis = await _analyze_entry(content)
    now = datetime.now(timezone.utc)

    async with engine.begin() as conn:
        result = await conn.execute(
            insert(journal_entries).values(
                user_id=user_id,
                content=content,
                created_at=now,
                mood_label=analysis["mood"],
                themes=json.dumps(analysis["themes"]),
                entities=json.dumps(analysis["entities"]),
                sentiment_score=analysis["sentiment_score"],
                summary=analysis["summary"],
            )
        )
        entry_id = result.inserted_primary_key[0]

    # Log mood with source tracking
    if analysis["mood"] and analysis["mood"] != "neutral":
        await log_mood_with_source(
            message=content[:200],
            mood_label=analysis["mood"],
            user_id=user_id,
            source_type="journal",
            source_id=entry_id,
            confidence="medium",
        )

    return {
        "id": entry_id,
        "content": content,
        "mood_label": analysis["mood"],
        "themes": analysis["themes"],
        "entities": analysis["entities"],
        "sentiment_score": analysis["sentiment_score"],
        "summary": analysis["summary"],
        "created_at": str(now),
    }


async def update_journal_entry(entry_id: int, content: str, user_id: str) -> dict | None:
    """Update journal entry and re-run analysis."""
    logger.debug("update_journal_entry called: entry_id=%s, user_id=%s", entry_id, user_id)
    analysis = await _analyze_entry(content)
    now = datetime.now(timezone.utc)

    async with engine.begin() as conn:
        result = await conn.execute(
            update(journal_entries)
            .where(
                journal_entries.c.id == entry_id,
                journal_entries.c.user_id == user_id,
            )
            .values(
                content=content,
                updated_at=now,
                mood_label=analysis["mood"],
                themes=json.dumps(analysis["themes"]),
                entities=json.dumps(analysis["entities"]),
                sentiment_score=analysis["sentiment_score"],
                summary=analysis["summary"],
            )
        )
        if result.rowcount == 0:
            logger.warning("update_journal_entry: no rows matched entry_id=%s user_id=%s", entry_id, user_id)
            return None

    return {
        "id": entry_id,
        "content": content,
        "mood_label": analysis["mood"],
        "themes": analysis["themes"],
        "entities": analysis["entities"],
        "sentiment_score": analysis["sentiment_score"],
        "summary": analysis["summary"],
        "updated_at": str(now),
    }


async def get_journal_entry_by_id(entry_id: int, user_id: str) -> dict | None:
    async with engine.begin() as conn:
        result = await conn.execute(
            select(journal_entries).where(
                journal_entries.c.id == entry_id,
                journal_entries.c.user_id == user_id,
            )
        )
        row = result.fetchone()

    if not row:
        return None

    return {
        "id": row.id,
        "content": row.content,
        "mood_label": row.mood_label,
        "themes": json.loads(row.themes or "[]"),
        "entities": json.loads(row.entities or "[]"),
        "sentiment_score": row.sentiment_score if hasattr(row, "sentiment_score") else None,
        "summary": row.summary if hasattr(row, "summary") else None,
        "created_at": str(row.created_at),
        "updated_at": str(row.updated_at) if row.updated_at else None,
    }


async def delete_journal_entry(entry_id: int, user_id: str) -> bool:
    """Delete a journal entry. Returns True if deleted."""
    async with engine.begin() as conn:
        result = await conn.execute(
            delete(journal_entries).where(
                journal_entries.c.id == entry_id,
                journal_entries.c.user_id == user_id,
            )
        )
        return result.rowcount > 0
