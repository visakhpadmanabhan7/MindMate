import asyncio

from app.db.engine import engine
from app.db.models import metadata


async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    return {"status": "reset_successful"}


if __name__ == "__main__":
    asyncio.run(setup())
