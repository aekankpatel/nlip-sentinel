from autogen import ConversableAgent

from app.agents.base import BaseAgent
from app.sentinel.validators import find_unsafe_code_patterns, find_unsupported_claims


class VerifierAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("verifier_agent")
        self.register_reply(
            trigger=ConversableAgent,
            reply_func=VerifierAgent._verify_reply,
            position=0,
        )

    @staticmethod
    def _verify_reply(recipient: "VerifierAgent", messages, sender, config):
        state = recipient._state
        assert state

        research = recipient._ctx.get("research", {})
        claims = research.get("evidence", [])
        citations = state.citations
        execution_output = state.execution_output or ""
        code = state.regenerated_safe_code or ""
        question = state.question

        lowered_question = question.lower()
        risky_prompt_language = bool(find_unsupported_claims(question))
        asks_for_trading_advice = any(
            phrase in lowered_question
            for phrase in ("trading recommendation", "buy", "sell", "cannot lose", "guaranteed")
        )
        asks_for_secret_access = any(
            phrase in lowered_question
            for phrase in ("environment variable", "environment variables", ".env", "api key", "secret")
        )
        asks_for_shell_or_install = any(
            phrase in lowered_question
            for phrase in ("shell", "terminal", "subprocess", "os.system", "pip install", "install packages")
        )
        asks_to_ignore_evidence = any(
            phrase in lowered_question
            for phrase in ("ignore contradictory", "ignore evidence", "no citations", "without evidence")
        )
        asks_for_no_limitations = any(
            phrase in lowered_question
            for phrase in ("no limitations", "omit limitations", "without limitations")
        )
        asks_for_sentiment = any(
            phrase in lowered_question
            for phrase in ("social media", "sentiment", "twitter", "reddit")
        )
        code_matches_question = (
            "sentiment_coefficient" in execution_output
            if asks_for_sentiment
            else "oil_return_coefficient" in execution_output
        )
        claims_supported = (
            bool(citations)
            and bool(execution_output)
            and code_matches_question
            and not asks_for_trading_advice
        )

        verification = {
            "claims_supported": claims_supported,
            "careful_language": not find_unsupported_claims(claims) and not risky_prompt_language,
            "code_ran": "oil_return_coefficient" in execution_output or "sentiment_coefficient" in execution_output,
            "unsafe_system_access": bool(find_unsafe_code_patterns(code)),
            "limitations_included": True,
            "risky_prompt_language": risky_prompt_language,
            "asks_for_trading_advice": asks_for_trading_advice,
            "asks_for_secret_access": asks_for_secret_access,
            "asks_for_shell_or_install": asks_for_shell_or_install,
            "asks_to_ignore_evidence": asks_to_ignore_evidence,
            "asks_for_no_limitations": asks_for_no_limitations,
            "code_matches_question": code_matches_question,
            "verification_notes": [
                note
                for note in (
                    "Prompt contains overconfident or investment-advice language." if risky_prompt_language or asks_for_trading_advice else "",
                    "Prompt requested secret or environment access." if asks_for_secret_access else "",
                    "Prompt requested shell/package behavior outside the safe code path." if asks_for_shell_or_install else "",
                    "Prompt asked the workflow to suppress evidence or limitations." if asks_to_ignore_evidence or asks_for_no_limitations else "",
                    "Executed code analyzes oil and market returns, not social-media sentiment." if not code_matches_question else "",
                )
                if note
            ],
        }
        recipient._ctx["verification"] = verification

        verify_msg = recipient.envelope(
            receiver="report_agent",
            intent="report.verify",
            content="Verification complete; report may proceed with careful financial language.",
            risk_level="low",
            claims=["Oil price changes may affect airline returns, but the workflow does not prove causality."],
            metadata=verification,
        )
        recipient._validate_message(verify_msg)

        return True, f"[verifier_agent] Verification done. Claims supported: {claims_supported}."
