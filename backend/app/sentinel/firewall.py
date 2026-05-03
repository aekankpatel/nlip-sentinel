from app.schemas import AgentMessage, FirewallDecision, ToolCallRequest
from app.sentinel.policies import ALLOWED_INTENTS, ALLOWED_MESSAGE_ROUTES, ALLOWED_TOOLS
from app.sentinel.risk import status_for_risk
from app.sentinel.validators import find_unsafe_code_patterns, find_unsupported_claims


class SentinelFirewall:
    def check_message(self, message: AgentMessage) -> FirewallDecision:
        route_allowed = (message.sender, message.receiver) in ALLOWED_MESSAGE_ROUTES
        intent_allowed = message.intent in ALLOWED_INTENTS.get(message.sender, set())
        tool_allowed = all(
            tool in ALLOWED_TOOLS.get(message.sender, set())
            for tool in message.requested_tools
        )
        unsupported_claims = find_unsupported_claims(message.claims or message.content)

        checks = {
            "schema": True,
            "permission": route_allowed and intent_allowed,
            "tool_permission": tool_allowed,
            "evidence_language": not unsupported_claims,
        }
        if not route_allowed:
            return FirewallDecision(
                subject=f"{message.sender}->{message.receiver}",
                status="blocked",
                reason="Sender/receiver route is not allowed.",
                checks=checks,
                risk_level=message.risk_level,
            )
        if not intent_allowed:
            return FirewallDecision(
                subject=message.intent,
                status="blocked",
                reason=f"{message.sender} is not allowed to use intent {message.intent}.",
                checks=checks,
                risk_level=message.risk_level,
            )
        if not tool_allowed:
            return FirewallDecision(
                subject="requested_tools",
                status="blocked",
                reason=f"{message.sender} requested a tool outside its role policy.",
                checks=checks,
                risk_level=message.risk_level,
            )
        if unsupported_claims:
            return FirewallDecision(
                subject="claims",
                status="warning",
                reason=f"Unsupported financial language flagged: {', '.join(unsupported_claims)}.",
                checks=checks,
                risk_level="medium",
            )

        status, requires_human = status_for_risk(message.risk_level)
        return FirewallDecision(
            subject=f"{message.sender}->{message.receiver}",
            status=status,
            reason="Message approved by schema, route, intent, and evidence-language checks.",
            checks=checks,
            risk_level=message.risk_level,
            requires_human=requires_human,
        )

    def check_tool(self, request: ToolCallRequest) -> FirewallDecision:
        tool_allowed = request.tool_name in ALLOWED_TOOLS.get(request.requester, set())
        unsafe_patterns = find_unsafe_code_patterns(request.code or "")
        checks = {
            "permission": tool_allowed,
            "tool_safety": not unsafe_patterns,
        }
        if not tool_allowed:
            return FirewallDecision(
                subject=request.tool_name,
                status="blocked",
                reason=f"{request.requester} is not allowed to call {request.tool_name}.",
                checks=checks,
                risk_level=request.risk_level,
            )
        if unsafe_patterns:
            return FirewallDecision(
                subject=request.tool_name,
                status="blocked",
                reason=f"Blocked unsafe code patterns: {', '.join(unsafe_patterns)}.",
                checks=checks,
                risk_level="critical",
            )
        status, requires_human = status_for_risk(request.risk_level)
        return FirewallDecision(
            subject=request.tool_name,
            status=status,
            reason="Tool call passed role and safety checks.",
            checks=checks,
            risk_level=request.risk_level,
            requires_human=requires_human,
        )

