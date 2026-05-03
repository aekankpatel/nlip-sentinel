from app.sentinel.validators import find_unsupported_claims, validate_agent_message


def test_invalid_schema_fails():
    valid, message, reason = validate_agent_message({"sender": "planner_agent"})
    assert valid is False
    assert message is None
    assert "Invalid AgentMessage schema" in reason


def test_financial_advice_claims_are_flagged():
    flagged = find_unsupported_claims("This proves a risk-free certain profit.")
    assert "proves" in flagged
    assert "risk-free" in flagged
    assert "certain profit" in flagged

