from autogen import ConversableAgent

from app.agents.base import BaseAgent
from app.schemas import ToolCallRequest
from app.tools.sandbox_tool import SandboxTool


class SandboxExecutionAgent(BaseAgent):
    def __init__(self, sandbox: SandboxTool) -> None:
        super().__init__("sandbox_agent")
        self._sandbox = sandbox
        self.register_reply(
            trigger=ConversableAgent,
            reply_func=SandboxExecutionAgent._sandbox_reply,
            position=0,
        )

    @staticmethod
    def _sandbox_reply(recipient: "SandboxExecutionAgent", messages, sender, config):
        state = recipient._state
        assert state

        safe_code = state.regenerated_safe_code or ""
        approval = state.approval_requests[-1] if state.approval_requests else None

        # Validate the safe tool call through Sentinel
        safe_request = ToolCallRequest(
            requester="sandbox_agent",
            tool_name="python_sandbox",
            code=safe_code,
            risk_level="high",
        )
        safe_decision = recipient._firewall.check_tool(safe_request)
        if safe_decision.status == "requires_approval" and approval and approval.approved:
            safe_decision.status = "approved"
            safe_decision.reason = "Tool call required human approval; demo approval granted."
            safe_decision.requires_human = False
        state.firewall_decisions.append(safe_decision)
        recipient._audit.add(
            "sentinel_firewall", "check_safe_code",
            safe_decision.status, safe_decision.reason
        )

        execution_output = recipient._sandbox.run_python(safe_code)
        state.execution_output = execution_output
        recipient._audit.add(
            "sandbox_agent", "execute_python", "completed",
            "Safe regression code completed in sandbox."
        )

        execution_msg = recipient.envelope(
            receiver="verifier_agent",
            intent="execution.result",
            content=execution_output,
            risk_level="low",
        )
        recipient._validate_message(execution_msg)

        return True, f"[sandbox_agent] Code executed. Output length: {len(execution_output)} chars."
