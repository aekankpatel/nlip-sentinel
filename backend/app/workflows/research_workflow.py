import asyncio

from autogen import GroupChat, GroupChatManager, UserProxyAgent

from app.agents.code_agent import CodeAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.report_agent import ReportAgent
from app.agents.research_agent import ResearchAgent
from app.agents.sandbox_agent import SandboxExecutionAgent
from app.agents.verifier_agent import VerifierAgent
from app.schemas import AgentMessage, WorkflowState
from app.sentinel.audit import AuditTrail
from app.sentinel.firewall import SentinelFirewall
from app.tools.gemini_tool import GeminiTool
from app.tools.sandbox_tool import SandboxTool
from app.tools.tavily_tool import TavilySearchTool


DEFAULT_QUESTION = (
    "Research whether oil price changes meaningfully affect airline stock returns, write Python analysis code, "
    "run it safely, and produce a final evidence-based report."
)


class ResearchWorkflow:
    def __init__(self) -> None:
        self.firewall = SentinelFirewall()
        self.audit = AuditTrail()
        self.tavily = TavilySearchTool()
        self.gemini = GeminiTool()

        # AG2 agents — each a ConversableAgent with a registered Sentinel-aware reply function
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.code_agent = CodeAgent()
        self.sandbox_agent = SandboxExecutionAgent(SandboxTool())
        self.verifier = VerifierAgent()
        self.reporter = ReportAgent()

    async def run(self, question: str = DEFAULT_QUESTION) -> WorkflowState:
        state = WorkflowState(question=question)
        self.audit.add("user", "submitted_task", "received", question)

        # Record the initial user → planner message through Sentinel
        user_message = AgentMessage(
            sender="user",
            receiver="planner_agent",
            intent="workflow.start",
            content=question,
            risk_level="low",
        )
        decision = self.firewall.check_message(user_message)
        state.messages.append(user_message)
        state.firewall_decisions.append(decision)

        # --- Phase 1: async pre-work (Tavily search cannot run inside the sync GroupChat) ---
        research_data = await self.tavily.search(question)
        state.citations = [item["url"] for item in research_data]
        self.researcher.set_research_data(research_data)

        # --- Phase 2: bind all AG2 agents to shared state, firewall, audit, and ctx ---
        ctx: dict = {}
        agents = [
            self.planner,
            self.researcher,
            self.code_agent,
            self.sandbox_agent,
            self.verifier,
            self.reporter,
        ]
        for agent in agents:
            agent.bind_workflow(self.firewall, self.audit, state, ctx)

        # --- Phase 3: AG2 GroupChat with round-robin speaker selection ---
        #
        # Each specialized agent speaks exactly once in pipeline order:
        #   planner → researcher → code_agent → sandbox_agent → verifier → reporter
        #
        # The Sentinel Firewall runs inside every agent's registered reply function,
        # validating messages and tool calls before they proceed.
        # max_round = agents + 1 because the initial user_proxy message counts as round 1
        groupchat = GroupChat(
            agents=agents,
            messages=[],
            speaker_selection_method="round_robin",
            max_round=len(agents) + 1,
        )
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=False,
        )
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=lambda msg: True,  # stop after GroupChat completes
        )

        # Run the blocking AG2 GroupChat in a thread so we don't block FastAPI's event loop
        await asyncio.to_thread(
            user_proxy.initiate_chat,
            manager,
            message=question,
        )

        # --- Phase 4: async Gemini enhancement of the report's key_result ---
        if state.final_report:
            research = ctx.get("research", {})
            evidence = research.get("evidence", [])
            gemini_summary = await self.gemini.generate_text(
                "Write a concise, careful, non-investment-advice summary for this agent safety demo. "
                "Do not use words like guaranteed, proves, risk-free, certain profit, or cannot lose. "
                f"Question: {question}\nEvidence: {evidence}\n"
                f"Execution output: {(state.execution_output or '')[:1200]}"
            )
            if gemini_summary:
                state.final_report.key_result = gemini_summary

        state.audit_events = self.audit.events
        return state
