import uuid
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import insert, select

from app.db.engine import engine
from app.db.models import users


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


async def create_user(email: str, password: str, name: str | None = None):
    user_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)

    async with engine.begin() as conn:
        result = await conn.execute(
            select(users).where(users.c.email == email)
        )
        existing = result.fetchone()

        if existing:
            return {
                "status": "exists",
                "message": "User already exists",
            }

        await conn.execute(
            insert(users).values(
                id=user_id,
                email=email,
                name=name,
                password_hash=_hash_password(password),
                is_active=True,
                created_at=created_at,
            )
        )

        return {
            "status": "created",
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "created_at": str(created_at),
            },
        }


async def authenticate_user(email: str, password: str):
    """Verify email + password. Returns user row or None."""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not user.password_hash:
        return None
    if not _verify_password(password, user.password_hash):
        return None
    return user


async def get_user_by_email(email: str):
    async with engine.begin() as conn:
        result = await conn.execute(
            select(users).where(users.c.email == email)
        )
        return result.fetchone()


async def get_user_by_id(user_id: str):
    async with engine.begin() as conn:
        result = await conn.execute(
            select(users).where(users.c.id == user_id)
        )
        return result.fetchone()


async def get_user_email_by_id(user_id: str) -> str | None:
    async with engine.begin() as conn:
        result = await conn.execute(
            select(users.c.email).where(users.c.id == user_id)
        )
        return result.scalar_one_or_none()
