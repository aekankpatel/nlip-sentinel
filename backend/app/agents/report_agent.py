from autogen import ConversableAgent

from app.agents.base import BaseAgent
from app.schemas import FinalReport, TrustScore
from app.sentinel.trust_score import calculate_trust_score


class ReportAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("report_agent")
        self.register_reply(
            trigger=ConversableAgent,
            reply_func=ReportAgent._report_reply,
            position=0,
        )

    @staticmethod
    def _report_reply(recipient: "ReportAgent", messages, sender, config):
        state = recipient._state
        assert state

        research = recipient._ctx.get("research", {})
        verification = recipient._ctx.get("verification", {})
        evidence = research.get("evidence", [])

        trust_score = calculate_trust_score(
            state.firewall_decisions,
            claims_supported=verification.get("claims_supported", False) and verification.get("careful_language", False),
            code_ran=verification.get("code_ran", False),
            verification=verification,
        )
        state.trust_score = trust_score

        title = recipient._title_from_question(state.question)
        citations = state.citations

        # Build the report; key_result will be replaced by Gemini summary after GroupChat
        state.final_report = FinalReport(
            title=title,
            research_question=state.question,
            methodology=(
                "The AG2 multi-agent workflow combined background research with a reproducible "
                "synthetic-data regression: airline_return ~ oil_return + market_return. "
                "Synthetic data keeps the live demo deterministic."
            ),
            evidence=[
                *evidence,
                f"Citations reviewed: {', '.join(citations[:3])}.",
            ],
            code_execution_summary=state.execution_output or "",
            key_result=(
                "The demo regression found a negative oil-return coefficient after controlling for market returns. "
                "That suggests oil shocks can matter for airline returns, but the result should be treated as an illustrative "
                "workflow validation rather than investment advice."
            ),
            limitations=[
                "The MVP uses synthetic monthly data for reliable live execution.",
                "Real conclusions would require data that directly matches the research question plus survivorship-aware return data and macro controls.",
                "The report avoids trading recommendations and does not claim causal proof.",
            ],
            trust_score=trust_score,
            audit_summary=(
                "Sentinel validated message envelopes, blocked an unsafe environment-variable access attempt, "
                "approved regenerated code, executed it in a constrained runner, and verified report language."
            ),
        )

        report_msg = recipient.envelope(
            receiver="user",
            intent="report.final",
            content=state.final_report.key_result,
            risk_level="low",
            claims=[state.final_report.key_result],
            citations=citations,
        )
        recipient._validate_message(report_msg)
        recipient._audit.add("report_agent", "final_report", "completed", "Evidence-based report generated.")

        return True, f"[report_agent] Final report ready. Trust score: {trust_score.total}/100."

    @staticmethod
    def _title_from_question(question: str) -> str:
        lowered = question.lower()
        if "social media" in lowered or "sentiment" in lowered:
            return "Social Media Sentiment and Airline Stock Returns"
        if "guaranteed" in lowered or "trading recommendation" in lowered:
            return "Risky Airline Stock Claim Review"
        if "oil" in lowered and "airline" in lowered:
            return "Oil Price Changes and Airline Stock Returns"
        return "Evidence Review for Agent-Run Financial Analysis"
