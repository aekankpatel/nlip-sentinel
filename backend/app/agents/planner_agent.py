from autogen import ConversableAgent

from app.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("planner_agent")
        self.register_reply(
            trigger=ConversableAgent,
            reply_func=PlannerAgent._plan_reply,
            position=0,
        )

    @staticmethod
    def _plan_reply(recipient: "PlannerAgent", messages, sender, config):
        question = ""
        for msg in reversed(messages or []):
            content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
            if content:
                question = content
                break

        plan = {
            "question": question,
            "steps": ["research", "code_generation", "sandbox_execution", "verification", "report"],
        }

        research_msg = recipient.envelope(
            receiver="research_agent",
            intent="research.search",
            content="Find sources relevant to the research question.",
            metadata=plan,
        )
        recipient._validate_message(research_msg)

        code_msg = recipient.envelope(
            receiver="code_agent",
            intent="code.generate",
            content="Generate Python analysis code for the research question.",
            risk_level="medium",
        )
        recipient._validate_message(code_msg)

        recipient._audit.add("planner_agent", "create_plan", "completed", f"Plan created for: {question[:80]}")

        return True, f"[planner_agent] Plan created. Steps: {plan['steps']}"
