from datetime import datetime, timezone

from sqlalchemy import delete, desc, insert, select, update

from app.db.engine import engine
from app.db.models import chat_sessions, messages

# --- Chat Sessions ---


async def create_session(user_id: str, title: str | None = None) -> dict:
    """Create a new chat session and return it."""
    now = datetime.now(timezone.utc)
    async with engine.begin() as conn:
        result = await conn.execute(
            insert(chat_sessions).values(
                user_id=user_id,
                title=title or "New conversation",
                created_at=now,
            )
        )
        session_id = result.inserted_primary_key[0]
    return {"id": session_id, "title": title or "New conversation", "created_at": str(now)}


async def get_sessions(user_id: str, limit: int = 50) -> list[dict]:
    """List chat sessions for a user, newest first."""
    async with engine.begin() as conn:
        result = await conn.execute(
            select(chat_sessions)
            .where(chat_sessions.c.user_id == user_id)
            .order_by(desc(chat_sessions.c.created_at))
            .limit(limit)
        )
        rows = result.fetchall()
    return [
        {
            "id": row.id,
            "title": row.title,
            "created_at": str(row.created_at) if row.created_at else None,
            "updated_at": str(row.updated_at) if row.updated_at else None,
        }
        for row in rows
    ]


async def update_session_title(session_id: int, user_id: str, title: str) -> bool:
    """Update session title. Returns True if updated."""
    async with engine.begin() as conn:
        result = await conn.execute(
            update(chat_sessions)
            .where(
                chat_sessions.c.id == session_id,
                chat_sessions.c.user_id == user_id,
            )
            .values(title=title, updated_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0


async def delete_session(session_id: int, user_id: str) -> bool:
    """Delete a chat session and all its messages."""
    async with engine.begin() as conn:
        # Delete messages belonging to this session
        await conn.execute(
            delete(messages).where(
                messages.c.session_id == session_id,
                messages.c.user_id == user_id,
            )
        )
        # Delete the session
        result = await conn.execute(
            delete(chat_sessions).where(
                chat_sessions.c.id == session_id,
                chat_sessions.c.user_id == user_id,
            )
        )
        return result.rowcount > 0


# --- Messages ---


async def save_message(
    user_id: str,
    role: str,
    content: str,
    intent: str | None = None,
    tool_class: str | None = None,
    session_id: int | None = None,
) -> int:
    """Save a message and return its ID."""
    async with engine.begin() as conn:
        result = await conn.execute(
            insert(messages).values(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
                intent=intent,
                tool_class=tool_class,
                created_at=datetime.now(timezone.utc),
            )
        )
        return result.inserted_primary_key[0]


async def get_recent_messages(
    user_id: str, limit: int = 20, session_id: int | None = None
) -> list[dict]:
    stmt = select(messages).where(messages.c.user_id == user_id)
    if session_id is not None:
        stmt = stmt.where(messages.c.session_id == session_id)
    stmt = stmt.order_by(desc(messages.c.created_at)).limit(limit)

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        rows = result.fetchall()

    return [
        {
            "id": row.id,
            "role": row.role,
            "content": row.content,
            "intent": row.intent,
            "tool_class": row.tool_class,
            "created_at": str(row.created_at) if row.created_at else None,
        }
        for row in reversed(rows)
    ]


async def search_messages(
    user_id: str,
    query: str | None = None,
    intent: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Search messages by text content and/or intent."""
    stmt = select(messages).where(messages.c.user_id == user_id)
    if query:
        stmt = stmt.where(messages.c.content.contains(query))
    if intent:
        stmt = stmt.where(messages.c.intent == intent)
    stmt = stmt.order_by(desc(messages.c.created_at)).limit(limit).offset(offset)

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        rows = result.fetchall()

    return [
        {
            "id": row.id,
            "role": row.role,
            "content": row.content,
            "intent": row.intent,
            "tool_class": row.tool_class,
            "created_at": str(row.created_at) if row.created_at else None,
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
