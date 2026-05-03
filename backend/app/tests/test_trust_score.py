from app.config import mask_secret
from app.schemas import FirewallDecision
from app.sentinel.trust_score import calculate_trust_score


def test_trust_score_calculation_works():
    decisions = [
        FirewallDecision(
            subject="python_sandbox",
            status="blocked",
            reason="Blocked unsafe code patterns: os.environ.",
            checks={"permission": True, "tool_safety": False},
        )
    ]
    score = calculate_trust_score(decisions, claims_supported=True, code_ran=True)
    assert score.total == 96
    assert score.tool_safety == 16


def test_mask_secret_does_not_leak_full_keys():
    secret = "demo_secret_value_123456"
    masked = mask_secret(secret)
    assert masked == "demo...3456"
    assert secret not in masked
    assert mask_secret("short") == "****"
