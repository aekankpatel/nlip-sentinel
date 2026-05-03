from autogen import ConversableAgent

from app.schemas import AgentMessage, FirewallDecision, WorkflowState
from app.sentinel.audit import AuditTrail
from app.sentinel.firewall import SentinelFirewall


class BaseAgent(ConversableAgent):
    """AG2 ConversableAgent with Sentinel Firewall middleware built in."""

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(
            name=name,
            human_input_mode="NEVER",
            llm_config=False,
            code_execution_config=False,
            **kwargs,
        )
        self._firewall: SentinelFirewall | None = None
        self._audit: AuditTrail | None = None
        self._state: WorkflowState | None = None
        self._ctx: dict = {}

    def bind_workflow(
        self,
        firewall: SentinelFirewall,
        audit: AuditTrail,
        state: WorkflowState,
        ctx: dict,
    ) -> None:
        self._firewall = firewall
        self._audit = audit
        self._state = state
        self._ctx = ctx

    def _validate_message(self, msg: AgentMessage) -> FirewallDecision:
        assert self._firewall and self._state and self._audit
        decision = self._firewall.check_message(msg)
        self._state.messages.append(msg)
        self._state.firewall_decisions.append(decision)
        self._audit.add(
            "sentinel_firewall",
            "check_message",
            decision.status,
            decision.reason,
            subject=decision.subject,
        )
        return decision

    def envelope(
        self,
        receiver: str,
        intent: str,
        content: str,
        requested_tools: list[str] | None = None,
        risk_level: str = "low",
        claims: list[str] | None = None,
        citations: list[str] | None = None,
        metadata: dict | None = None,
    ) -> AgentMessage:
        return AgentMessage(
            sender=self.name,
            receiver=receiver,
            intent=intent,
            content=content,
            requested_tools=requested_tools or [],
            risk_level=risk_level,
            claims=claims or [],
            citations=citations or [],
            metadata=metadata or {},
        )
