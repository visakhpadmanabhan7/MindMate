import pytest

from app.tools.therapy.therapy_store import get_sessions, save_session


@pytest.mark.asyncio
async def test_save_and_retrieve_session():
    result = await save_session(
        user_id="user1",
        issues_discussed=["anxiety", "relationships"],
        learnings="Identified thought patterns",
        action_items=["Practice breathing", "Journal daily"],
        techniques=["CBT", "grounding"],
    )
    assert result["session_number"] == 1
    assert result["status"] == "saved"

    sessions = await get_sessions("user1")
    assert len(sessions) == 1
    assert sessions[0]["issues_discussed"] == ["anxiety", "relationships"]
    assert sessions[0]["action_items"] == ["Practice breathing", "Journal daily"]


@pytest.mark.asyncio
async def test_session_auto_increment():
    await save_session(
        user_id="user2",
        issues_discussed=["stress"],
        learnings="Take breaks",
        action_items=[],
        techniques=[],
    )
    result = await save_session(
        user_id="user2",
        issues_discussed=["sleep"],
        learnings="Sleep hygiene",
        action_items=["No screens before bed"],
        techniques=["relaxation"],
    )
    assert result["session_number"] == 2

    sessions = await get_sessions("user2")
    assert len(sessions) == 2
    assert sessions[0]["session_number"] == 1
    assert sessions[1]["session_number"] == 2
