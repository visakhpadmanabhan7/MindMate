import pytest

from app.db.message_store import get_recent_messages, save_message


@pytest.mark.asyncio
async def test_save_and_retrieve_messages():
    await save_message(user_id="user1", role="user", content="Hello")
    await save_message(user_id="user1", role="assistant", content="Hi there!")

    messages = await get_recent_messages("user1", limit=10)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there!"


@pytest.mark.asyncio
async def test_messages_ordered_chronologically():
    for i in range(5):
        await save_message(user_id="user2", role="user", content=f"msg {i}")

    messages = await get_recent_messages("user2", limit=10)
    assert len(messages) == 5
    assert messages[0]["content"] == "msg 0"
    assert messages[4]["content"] == "msg 4"


@pytest.mark.asyncio
async def test_messages_limit():
    for i in range(10):
        await save_message(user_id="user3", role="user", content=f"msg {i}")

    messages = await get_recent_messages("user3", limit=3)
    assert len(messages) == 3
    # Should return the last 3 messages
    assert messages[0]["content"] == "msg 7"


@pytest.mark.asyncio
async def test_messages_per_user():
    await save_message(user_id="alice", role="user", content="alice msg")
    await save_message(user_id="bob", role="user", content="bob msg")

    alice_msgs = await get_recent_messages("alice", limit=10)
    bob_msgs = await get_recent_messages("bob", limit=10)

    assert len(alice_msgs) == 1
    assert len(bob_msgs) == 1
    assert alice_msgs[0]["content"] == "alice msg"
    assert bob_msgs[0]["content"] == "bob msg"
