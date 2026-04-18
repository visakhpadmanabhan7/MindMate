import pytest

from app.db.user_manager import create_user, get_user_by_email, get_user_by_id


@pytest.mark.asyncio
async def test_create_user():
    result = await create_user(email="test@example.com", name="Test")
    assert result["status"] == "created"
    assert result["user"]["email"] == "test@example.com"
    assert result["user"]["name"] == "Test"
    assert "id" in result["user"]


@pytest.mark.asyncio
async def test_create_duplicate_user():
    await create_user(email="dup@example.com", name="First")
    result = await create_user(email="dup@example.com", name="Second")
    assert result["status"] == "exists"


@pytest.mark.asyncio
async def test_get_user_by_email():
    await create_user(email="find@example.com")
    user = await get_user_by_email("find@example.com")
    assert user is not None
    assert user.email == "find@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
    user = await get_user_by_email("nonexistent@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_id():
    result = await create_user(email="byid@example.com")
    user_id = result["user"]["id"]
    user = await get_user_by_id(user_id)
    assert user is not None
    assert user.email == "byid@example.com"
