from pydantic import ValidationError

from app.schemas import AgentMessage
from app.sentinel.policies import BLOCKED_CODE_PATTERNS, UNSUPPORTED_FINANCIAL_CLAIMS


def validate_agent_message(payload: dict) -> tuple[bool, AgentMessage | None, str]:
    try:
        return True, AgentMessage.model_validate(payload), "Schema valid"
    except ValidationError as exc:
        return False, None, f"Invalid AgentMessage schema: {exc.errors()[0]['msg']}"


def find_unsafe_code_patterns(code: str) -> list[str]:
    lowered = code.lower()
    return [pattern for pattern in BLOCKED_CODE_PATTERNS if pattern.lower() in lowered]


def find_unsupported_claims(text: str | list[str]) -> list[str]:
    combined = " ".join(text) if isinstance(text, list) else text
    lowered = combined.lower()
    return [phrase for phrase in UNSUPPORTED_FINANCIAL_CLAIMS if phrase in lowered]

