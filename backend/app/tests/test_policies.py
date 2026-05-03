from app.schemas import AgentMessage
from app.sentinel.firewall import SentinelFirewall


def test_report_agent_cannot_call_shell_tools():
    message = AgentMessage(
        sender="report_agent",
        receiver="user",
        intent="report.final",
        content="Final report",
        requested_tools=["python_sandbox"],
    )
    decision = SentinelFirewall().check_message(message)
    assert decision.status == "blocked"
    assert "outside its role policy" in decision.reason

