from datetime import datetime, timezone

from sqlalchemy import desc, insert, select, update

from app.db.engine import engine
from app.db.models import messages


async def save_message(
    user_id: str,
    role: str,
    content: str,
    intent: str | None = None,
    tool_class: str | None = None,
) -> int:
    """Save a message and return its ID."""
    async with engine.begin() as conn:
        result = await conn.execute(
            insert(messages).values(
                user_id=user_id,
                role=role,
                content=content,
                intent=intent,
                tool_class=tool_class,
                created_at=datetime.now(timezone.utc),
            )
        )
        return result.inserted_primary_key[0]


async def get_recent_messages(user_id: str, limit: int = 20) -> list[dict]:
    async with engine.begin() as conn:
        result = await conn.execute(
            select(messages)
            .where(messages.c.user_id == user_id)
            .order_by(desc(messages.c.created_at))
            .limit(limit)
        )
        rows = result.fetchall()

    return [
        {
            "id": row.id,
            "role": row.role,
            "content": row.content,
            "intent": row.intent,
            "tool_class": row.tool_class,
        }
        for row in reversed(rows)
    ]


async def update_message(message_id: int, user_id: str, new_content: str) -> dict | None:
    """Update a user message (only role='user' allowed)."""
    now = datetime.now(timezone.utc)

    async with engine.begin() as conn:
        # Get original content for backup
        result = await conn.execute(
            select(messages).where(
                messages.c.id == message_id,
                messages.c.user_id == user_id,
                messages.c.role == "user",
            )
        )
        row = result.fetchone()
        if not row:
            return None

        await conn.execute(
            update(messages)
            .where(messages.c.id == message_id)
            .values(
                content=new_content,
                original_content=row.content,
                updated_at=now,
            )
        )

    return {
        "id": message_id,
        "content": new_content,
        "updated_at": str(now),
    }
