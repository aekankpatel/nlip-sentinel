from app.schemas import AgentMessage, ToolCallRequest
from app.sentinel.firewall import SentinelFirewall


def test_valid_message_passes():
    message = AgentMessage(
        sender="planner_agent",
        receiver="research_agent",
        intent="research.search",
        content="Find evidence.",
    )
    decision = SentinelFirewall().check_message(message)
    assert decision.status == "approved"
    assert decision.checks["schema"] is True


def test_research_agent_cannot_execute_code():
    request = ToolCallRequest(requester="research_agent", tool_name="python_sandbox", code="print('x')")
    decision = SentinelFirewall().check_tool(request)
    assert decision.status == "blocked"
    assert "not allowed" in decision.reason


def test_code_agent_cannot_access_tavily():
    request = ToolCallRequest(requester="code_agent", tool_name="tavily_search")
    decision = SentinelFirewall().check_tool(request)
    assert decision.status == "blocked"


def test_unsafe_python_code_is_blocked():
    request = ToolCallRequest(
        requester="sandbox_agent",
        tool_name="python_sandbox",
        code="import os\nprint(os.environ)",
    )
    decision = SentinelFirewall().check_tool(request)
    assert decision.status == "blocked"
    assert "os.environ" in decision.reason


def test_safe_python_code_requires_approval():
    request = ToolCallRequest(
        requester="sandbox_agent",
        tool_name="python_sandbox",
        code="print('safe regression')",
        risk_level="high",
    )
    decision = SentinelFirewall().check_tool(request)
    assert decision.status == "requires_approval"
    assert decision.requires_human is True

