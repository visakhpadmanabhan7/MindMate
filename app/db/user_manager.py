from datetime import datetime
import uuid

from sqlalchemy import insert, select
from app.db.models import users
from app.db.setup_db import engine




async def create_user(email: str, name: str = None):
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    async with engine.begin() as conn:
        # Check for existing user
        result = await conn.execute(
            select(users).where(users.c.email == email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return {
                "status": "exists",
                "message": "User already exists",
                "user": {
                    "id": existing.id,
                    "email": existing.email,
                    "name": existing.name,
                    "created_at": str(existing.created_at)
                }
            }

        # Create new user
        await conn.execute(
            insert(users).values(
                id=user_id,
                email=email,
                name=name,
                is_active=True,
                created_at=created_at
            )
        )

        return {
            "status": "created",
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "created_at": str(created_at)
            }
        }

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
        return result.scalar_one_or_none()




async def get_user_email_by_id(user_id: str) -> str | None:
    async with engine.begin() as conn:
        result = await conn.execute(
            select(users.c.email).where(users.c.id == user_id)
        )
        return result.scalar_one_or_none()
