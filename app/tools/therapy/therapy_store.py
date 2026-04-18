import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _safe_json_loads(data: str | None, default: list | None = None) -> list:
    if not data:
        return default or []
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse JSON: %s", data[:100])
        return default or []

from sqlalchemy import desc, func, insert, select, update

from app.db.engine import engine
from app.db.models import therapy_sessions


async def save_session(
    user_id: str,
    issues_discussed: list[str],
    learnings: str,
    action_items: list[str],
    techniques: list[str],
    raw_notes: str | None = None,
    date: str | None = None,
) -> dict:
    # Auto-increment session number per user
    async with engine.begin() as conn:
        result = await conn.execute(
            select(func.max(therapy_sessions.c.session_number))
            .where(therapy_sessions.c.user_id == user_id)
        )
        max_num = result.scalar() or 0
        session_number = max_num + 1

        await conn.execute(
            insert(therapy_sessions).values(
                user_id=user_id,
                session_number=session_number,
                date=date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                issues_discussed=json.dumps(issues_discussed),
                learnings=learnings,
                action_items=json.dumps(action_items),
                techniques=json.dumps(techniques),
                raw_notes=raw_notes,
                created_at=datetime.now(timezone.utc),
            )
        )

    return {"session_number": session_number, "status": "saved"}


async def get_sessions(user_id: str, limit: int = 10) -> list[dict]:
    async with engine.begin() as conn:
        result = await conn.execute(
            select(therapy_sessions)
            .where(therapy_sessions.c.user_id == user_id)
            .order_by(desc(therapy_sessions.c.created_at))
            .limit(limit)
        )
        rows = result.fetchall()

    sessions = []
    for row in reversed(rows):
        sessions.append({
            "id": row.id,
            "session_number": row.session_number,
            "date": row.date,
            "issues_discussed": _safe_json_loads(row.issues_discussed),
            "learnings": row.learnings or "",
            "action_items": _safe_json_loads(row.action_items),
            "techniques": _safe_json_loads(row.techniques),
            "raw_notes": row.raw_notes,
            "created_at": str(row.created_at),
        })
    return sessions


async def get_session_by_id(session_id: int) -> dict | None:
    async with engine.begin() as conn:
        result = await conn.execute(
            select(therapy_sessions)
            .where(therapy_sessions.c.id == session_id)
        )
        row = result.fetchone()

    if not row:
        return None

    return {
        "id": row.id,
        "session_number": row.session_number,
        "date": row.date,
        "issues_discussed": json.loads(row.issues_discussed or "[]"),
        "learnings": row.learnings or "",
        "action_items": json.loads(row.action_items or "[]"),
        "techniques": json.loads(row.techniques or "[]"),
        "raw_notes": row.raw_notes,
        "created_at": str(row.created_at),
    }


async def update_session(session_id: int, user_id: str, updates: dict) -> dict | None:
    """Update a therapy session's fields."""
    now = datetime.now(timezone.utc)
    values: dict = {"updated_at": now}

    for field in ("issues_discussed", "action_items", "techniques"):
        if field in updates:
            values[field] = json.dumps(updates[field])
    for field in ("learnings", "raw_notes", "date"):
        if field in updates:
            values[field] = updates[field]

    async with engine.begin() as conn:
        result = await conn.execute(
            update(therapy_sessions)
            .where(
                therapy_sessions.c.id == session_id,
                therapy_sessions.c.user_id == user_id,
            )
            .values(**values)
        )
        if result.rowcount == 0:
            return None

    return await get_session_by_id(session_id)
