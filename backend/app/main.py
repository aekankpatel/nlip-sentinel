from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AgentMessage, ToolCallRequest
from app.sentinel.firewall import SentinelFirewall
from app.sentinel.validators import validate_agent_message
from app.workflows.research_workflow import DEFAULT_QUESTION, ResearchWorkflow

app = FastAPI(title="NLIP Sentinel", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "NLIP Sentinel backend is running"}


@app.post("/api/run-workflow")
async def run_workflow(payload: dict) -> dict:
    question = payload.get("question") or DEFAULT_QUESTION
    state = await ResearchWorkflow().run(question)
    return state.model_dump(mode="json")


@app.get("/api/demo")
async def demo() -> dict:
    state = await ResearchWorkflow().run(DEFAULT_QUESTION)
    return state.model_dump(mode="json")


@app.post("/api/firewall/check-message")
def check_message(payload: dict) -> dict:
    valid, message, reason = validate_agent_message(payload)
    if not valid or message is None:
        return {
            "subject": "AgentMessage",
            "status": "blocked",
            "reason": reason,
            "checks": {"schema": False},
            "risk_level": "critical",
            "requires_human": False,
        }
    return SentinelFirewall().check_message(message).model_dump(mode="json")


@app.post("/api/firewall/check-tool")
def check_tool(request: ToolCallRequest) -> dict:
    return SentinelFirewall().check_tool(request).model_dump(mode="json")


@app.post("/api/human/approve")
def approve(payload: dict) -> dict:
    return {
        "approval_id": payload.get("approval_id", "demo-approval"),
        "approved": True,
        "message": "Risky action approved for demo execution.",
    }

