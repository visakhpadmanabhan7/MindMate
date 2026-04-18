from app.core.guardrails import check_crisis


def test_detects_crisis_keywords():
    assert check_crisis("I want to kill myself") is not None
    assert check_crisis("thinking about suicide") is not None
    assert check_crisis("I don't want to live anymore") is not None
    assert check_crisis("I've been cutting myself") is not None


def test_no_false_positives():
    assert check_crisis("I feel sad today") is None
    assert check_crisis("I'm anxious about work") is None
    assert check_crisis("How do I manage stress?") is None
    assert check_crisis("Give me a journaling prompt") is None


def test_crisis_response_contains_resources():
    response = check_crisis("I want to end it all")
    assert response is not None
    assert "988" in response
    assert "741741" in response
