from app.schemas import DecisionStatus, RiskLevel


def status_for_risk(risk_level: RiskLevel) -> tuple[DecisionStatus, bool]:
    if risk_level == "low":
        return "approved", False
    if risk_level == "medium":
        return "warning", False
    if risk_level == "high":
        return "requires_approval", True
    return "blocked", False

