from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high", "critical"]
DecisionStatus = Literal["approved", "warning", "requires_approval", "blocked"]


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sender: str
    receiver: str
    intent: str
    content: str
    requested_tools: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = "low"
    claims: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requester: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    code: str | None = None
    risk_level: RiskLevel = "low"


class FirewallDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    subject: str
    status: DecisionStatus
    reason: str
    checks: dict[str, bool] = Field(default_factory=dict)
    risk_level: RiskLevel = "low"
    requires_human: bool = False


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str
    action: str
    status: str
    detail: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrustScore(BaseModel):
    total: int
    schema_validity: int
    permission_compliance: int
    tool_safety: int
    evidence_support: int
    reproducibility: int
    notes: list[str] = Field(default_factory=list)


class FinalReport(BaseModel):
    title: str
    research_question: str
    methodology: str
    evidence: list[str]
    code_execution_summary: str
    key_result: str
    limitations: list[str]
    trust_score: TrustScore
    audit_summary: str


class HumanApprovalRequest(BaseModel):
    approval_id: str = Field(default_factory=lambda: str(uuid4()))
    action: str
    reason: str
    risk_level: RiskLevel
    approved: bool = False


class WorkflowState(BaseModel):
    question: str
    messages: list[AgentMessage] = Field(default_factory=list)
    firewall_decisions: list[FirewallDecision] = Field(default_factory=list)
    audit_events: list[AuditEvent] = Field(default_factory=list)
    unsafe_code_attempt: str | None = None
    blocked_reason: str | None = None
    regenerated_safe_code: str | None = None
    execution_output: str | None = None
    citations: list[str] = Field(default_factory=list)
    final_report: FinalReport | None = None
    trust_score: TrustScore | None = None
    approval_requests: list[HumanApprovalRequest] = Field(default_factory=list)

