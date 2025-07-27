from datetime import datetime
from sqlalchemy import insert, select
from app.db.models import users
from app.db.setup_db import engine

async def create_user(user_id: str, email: str, name: str = None):
    async with engine.begin() as conn:
        result = await conn.execute(
            select(users).where(users.c.id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return {"status": "exists", "message": "User already exists"}

        await conn.execute(
            insert(users).values(
                id=user_id,
                email=email,
                name=name,
                is_active=True,
                created_at=datetime.utcnow()
            )
        )
        return {"status": "created", "user_id": user_id}
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