from autogen import ConversableAgent

from app.agents.base import BaseAgent
from app.schemas import ToolCallRequest


class ResearchAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("research_agent")
        self._research_data: list[dict] = []
        self.register_reply(
            trigger=ConversableAgent,
            reply_func=ResearchAgent._research_reply,
            position=0,
        )

    def set_research_data(self, data: list[dict]) -> None:
        self._research_data = data

    @staticmethod
    def _research_reply(recipient: "ResearchAgent", messages, sender, config):
        state = recipient._state
        assert state

        # Check the tool call through Sentinel before using Tavily
        tool_request = ToolCallRequest(
            requester="research_agent",
            tool_name="tavily_search",
            arguments={"query": state.question},
            risk_level="low",
        )
        tool_decision = recipient._firewall.check_tool(tool_request)
        state.firewall_decisions.append(tool_decision)
        recipient._audit.add(
            "sentinel_firewall", "check_tool", tool_decision.status, tool_decision.reason
        )

        citations = [item["url"] for item in recipient._research_data]
        state.citations = citations

        evidence = [
            "Oil prices are a major input-cost variable for airlines because jet fuel is typically one of their largest operating expenses.",
            "Airline stock returns also respond to broad equity-market moves, demand, capacity, hedging, and macroeconomic expectations.",
            "A small regression demo can test whether oil returns have incremental explanatory power after controlling for market returns.",
        ]
        recipient._ctx["research"] = {"evidence": evidence, "citations": citations}

        msg = recipient.envelope(
            receiver="verifier_agent",
            intent="evidence.summarize",
            content="Research summarized with citations.",
            risk_level="low",
            citations=citations,
            claims=evidence,
        )
        recipient._validate_message(msg)
        recipient._audit.add(
            "research_agent", "summarize_evidence", "completed",
            f"Collected {len(citations)} citations."
        )

        return True, f"[research_agent] Research complete. Citations: {len(citations)}"
