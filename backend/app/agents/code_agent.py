from autogen import ConversableAgent

from app.agents.base import BaseAgent
from app.schemas import HumanApprovalRequest, ToolCallRequest


REGRESSION_HELPERS = """
def transpose(matrix):
    return [list(row) for row in zip(*matrix)]

def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]

def invert_3x3(m):
    det = (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )
    if abs(det) < 1e-12:
        raise ValueError("Regression matrix is singular")
    return [
        [(m[1][1] * m[2][2] - m[1][2] * m[2][1]) / det, (m[0][2] * m[2][1] - m[0][1] * m[2][2]) / det, (m[0][1] * m[1][2] - m[0][2] * m[1][1]) / det],
        [(m[1][2] * m[2][0] - m[1][0] * m[2][2]) / det, (m[0][0] * m[2][2] - m[0][2] * m[2][0]) / det, (m[0][2] * m[1][0] - m[0][0] * m[1][2]) / det],
        [(m[1][0] * m[2][1] - m[1][1] * m[2][0]) / det, (m[0][1] * m[2][0] - m[0][0] * m[2][1]) / det, (m[0][0] * m[1][1] - m[0][1] * m[1][0]) / det],
    ]

def run_regression(primary_signal, market_return, airline_return):
    x = [[1.0, primary_signal[i], market_return[i]] for i in range(len(airline_return))]
    y = [[value] for value in airline_return]
    xt = transpose(x)
    beta = matmul(matmul(invert_3x3(matmul(xt, x)), xt), y)
    predicted = [sum(x[i][j] * beta[j][0] for j in range(3)) for i in range(len(x))]
    y_mean = sum(airline_return) / len(airline_return)
    ss_res = sum((actual - fitted) ** 2 for actual, fitted in zip(airline_return, predicted))
    ss_tot = sum((actual - y_mean) ** 2 for actual in airline_return)
    return beta, predicted, 1 - ss_res / ss_tot

def svg_polyline(values, predicted, color):
    min_y = min(values + predicted)
    max_y = max(values + predicted)
    points = []
    for idx, value in enumerate(values):
        x_pos = 36 + idx * (520 / (len(values) - 1))
        y_pos = 250 - ((value - min_y) / (max_y - min_y)) * 190
        points.append(f"{x_pos:.1f},{y_pos:.1f}")
    return f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{" ".join(points)}" />'
"""


class CodeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("code_agent")
        self.register_reply(
            trigger=ConversableAgent,
            reply_func=CodeAgent._code_reply,
            position=0,
        )

    @staticmethod
    def _code_reply(recipient: "CodeAgent", messages, sender, config):
        state = recipient._state
        assert state

        question = state.question
        scenario = recipient._scenario(question)

        # Intentionally generate unsafe code first to demonstrate Sentinel blocking
        safe_draft = recipient._safe_code(scenario)
        unsafe_code = (
            "import os\n"
            f"analysis_scenario = {scenario!r}\n"
            "# Unsafe debug attempt inserted before sandbox execution.\n"
            "print(os.environ)\n\n"
            f"{safe_draft}"
        )
        state.unsafe_code_attempt = unsafe_code

        # Sentinel blocks the unsafe tool call
        unsafe_request = ToolCallRequest(
            requester="sandbox_agent",
            tool_name="python_sandbox",
            code=unsafe_code,
            risk_level="critical",
        )
        unsafe_decision = recipient._firewall.check_tool(unsafe_request)
        state.firewall_decisions.append(unsafe_decision)
        state.blocked_reason = unsafe_decision.reason
        recipient._audit.add(
            "sentinel_firewall", "block_unsafe_code",
            unsafe_decision.status, unsafe_decision.reason
        )

        # Regenerate safe code after block
        safe_code = safe_draft
        state.regenerated_safe_code = safe_code

        # Human-in-the-loop approval for high-risk execution
        approval = HumanApprovalRequest(
            action="Execute regenerated regression code",
            reason="Python execution is high risk and requires visible approval in production. Demo mode auto-approves after showing the warning.",
            risk_level="high",
            approved=True,
        )
        state.approval_requests.append(approval)
        recipient._audit.add("human_approval", "approve_risky_action", "approved", approval.reason)

        # Validate the approved execute message through Sentinel
        execute_msg = recipient.envelope(
            receiver="sandbox_agent",
            intent="code.execute.request",
            content="Execute regenerated safe Python regression code.",
            risk_level="high",
        )
        execute_decision = recipient._validate_message(execute_msg)
        if execute_decision.status == "requires_approval" and approval.approved:
            execute_decision.status = "approved"
            execute_decision.reason = "High-risk execution message required approval; demo approval granted."
            execute_decision.requires_human = False

        recipient._audit.add(
            "code_agent", "generate_safe_code", "completed",
            "Unsafe attempt blocked; safe regression code regenerated and approved."
        )

        return True, f"[code_agent] Unsafe code blocked by Sentinel. Safe code ready ({len(safe_code)} chars)."

    @staticmethod
    def _scenario(question: str) -> str:
        lowered = question.lower()
        if any(term in lowered for term in ("social media", "sentiment", "twitter", "reddit")):
            return "sentiment"
        return "oil"

    @staticmethod
    def _safe_code(scenario: str) -> str:
        if scenario == "sentiment":
            return CodeAgent._sentiment_regression_code()
        return CodeAgent._oil_regression_code()

    @staticmethod
    def _oil_regression_code() -> str:
        return f"""import json
from pathlib import Path

months = list(range(1, 25))
oil_return = [-0.04, 0.03, 0.05, -0.02, 0.01, 0.06, -0.03, 0.02, 0.04, -0.05, 0.01, 0.03,
              -0.02, 0.05, 0.07, -0.04, 0.00, 0.02, -0.01, 0.04, 0.03, -0.06, 0.02, 0.01]
market_return = [0.01, 0.02, 0.03, -0.01, 0.02, 0.04, -0.02, 0.01, 0.03, -0.03, 0.00, 0.02,
                 0.01, 0.03, 0.04, -0.02, 0.01, 0.02, 0.00, 0.03, 0.02, -0.04, 0.01, 0.02]
airline_return = [0.018, 0.008, 0.006, 0.006, 0.017, 0.008, 0.010, 0.009, 0.010, 0.022, 0.006, 0.012,
                  0.012, 0.004, 0.002, 0.015, 0.006, 0.009, 0.006, 0.006, 0.008, 0.018, 0.007, 0.010]
{REGRESSION_HELPERS}
beta, predicted, r_squared = run_regression(oil_return, market_return, airline_return)
chart_path = Path("airline_oil_regression.svg")
chart_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="620" height="320" viewBox="0 0 620 320">
  <rect width="620" height="320" fill="#f8fbf7"/>
  <text x="36" y="32" font-size="18" font-family="Arial" fill="#17201b">Oil return regression demo</text>
  <line x1="36" y1="250" x2="580" y2="250" stroke="#7a867e"/>
  <line x1="36" y1="48" x2="36" y2="250" stroke="#7a867e"/>
  {{svg_polyline(airline_return, predicted, "#24555b")}}
  {{svg_polyline(predicted, predicted, "#c94a30")}}
</svg>'''
chart_path.write_text(chart_svg, encoding="utf-8")
result = {{
    "analysis_type": "oil_price_regression",
    "intercept": round(beta[0][0], 5),
    "oil_return_coefficient": round(beta[1][0], 5),
    "market_return_coefficient": round(beta[2][0], 5),
    "r_squared": round(r_squared, 4),
    "interpretation": "Synthetic oil returns have a negative incremental association with airline returns after controlling for market returns.",
    "chart": str(chart_path),
}}
print(json.dumps(result, indent=2))
"""

    @staticmethod
    def _sentiment_regression_code() -> str:
        return f"""import json
from pathlib import Path

weeks = list(range(1, 25))
sentiment_score = [0.12, 0.21, -0.08, 0.04, 0.18, 0.31, -0.16, 0.07, 0.11, -0.22, 0.05, 0.14,
                   -0.05, 0.19, 0.24, -0.11, 0.02, 0.09, -0.03, 0.17, 0.10, -0.18, 0.06, 0.08]
market_return = [0.01, 0.02, 0.03, -0.01, 0.02, 0.04, -0.02, 0.01, 0.03, -0.03, 0.00, 0.02,
                 0.01, 0.03, 0.04, -0.02, 0.01, 0.02, 0.00, 0.03, 0.02, -0.04, 0.01, 0.02]
airline_return = [0.010, 0.014, 0.002, 0.008, 0.012, 0.021, -0.004, 0.009, 0.012, -0.006, 0.007, 0.011,
                  0.004, 0.015, 0.018, 0.001, 0.006, 0.010, 0.005, 0.014, 0.011, -0.003, 0.008, 0.009]
{REGRESSION_HELPERS}
beta, predicted, r_squared = run_regression(sentiment_score, market_return, airline_return)
chart_path = Path("airline_sentiment_regression.svg")
chart_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="620" height="320" viewBox="0 0 620 320">
  <rect width="620" height="320" fill="#f8fbf7"/>
  <text x="36" y="32" font-size="18" font-family="Arial" fill="#17201b">Sentiment regression demo</text>
  <line x1="36" y1="250" x2="580" y2="250" stroke="#7a867e"/>
  <line x1="36" y1="48" x2="36" y2="250" stroke="#7a867e"/>
  {{svg_polyline(airline_return, predicted, "#24555b")}}
  {{svg_polyline(predicted, predicted, "#c94a30")}}
</svg>'''
chart_path.write_text(chart_svg, encoding="utf-8")
result = {{
    "analysis_type": "sentiment_regression",
    "intercept": round(beta[0][0], 5),
    "sentiment_coefficient": round(beta[1][0], 5),
    "market_return_coefficient": round(beta[2][0], 5),
    "r_squared": round(r_squared, 4),
    "interpretation": "In this synthetic sample, social sentiment has a positive but limited association with short-term airline returns after controlling for market returns.",
    "chart": str(chart_path),
}}
print(json.dumps(result, indent=2))
"""
