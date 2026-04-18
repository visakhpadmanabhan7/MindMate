import pytest

from app.tools.selfcare.mood_analytics import get_mood_analytics
from app.tools.selfcare.mood_tracker import log_mood


@pytest.mark.asyncio
async def test_log_and_analyze_mood():
    await log_mood(message="I feel happy today", mood_label="happy", user_id="user1")
    await log_mood(message="Feeling anxious", mood_label="anxious", user_id="user1")
    await log_mood(message="I'm calm now", mood_label="calm", user_id="user1")

    analytics = await get_mood_analytics("user1")
    assert analytics["total_entries"] == 3
    assert "happy" in analytics["distribution"]
    assert "anxious" in analytics["distribution"]
    assert len(analytics["timeline"]) == 3


@pytest.mark.asyncio
async def test_empty_mood_analytics():
    analytics = await get_mood_analytics("no_data_user")
    assert analytics["total_entries"] == 0
    assert analytics["timeline"] == []
    assert analytics["distribution"] == {}
