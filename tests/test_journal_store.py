import pytest

from app.tools.journaling.journal_analytics import get_journal_entries
from app.tools.journaling.journal_store import save_journal_entry


@pytest.mark.asyncio
async def test_save_and_retrieve_journal():
    await save_journal_entry(content="Today was a good day", user_id="user1")
    await save_journal_entry(content="I learned something new", user_id="user1")

    result = await get_journal_entries("user1")
    assert result["count"] == 2


@pytest.mark.asyncio
async def test_journal_search():
    await save_journal_entry(content="I felt anxious at work", user_id="user2")
    await save_journal_entry(content="Had a great workout", user_id="user2")
    await save_journal_entry(content="Anxiety before the meeting", user_id="user2")

    result = await get_journal_entries("user2", search="anxi")
    assert result["count"] == 2


@pytest.mark.asyncio
async def test_journal_per_user():
    await save_journal_entry(content="Alice's entry", user_id="alice")
    await save_journal_entry(content="Bob's entry", user_id="bob")

    alice = await get_journal_entries("alice")
    bob = await get_journal_entries("bob")
    assert alice["count"] == 1
    assert bob["count"] == 1
