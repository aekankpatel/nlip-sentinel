from app.schemas import FirewallDecision, TrustScore


def calculate_trust_score(
    decisions: list[FirewallDecision],
    claims_supported: bool,
    code_ran: bool,
    verification: dict | None = None,
) -> TrustScore:
    verification = verification or {}
    blocked_unsafe = any(d.status == "blocked" and "unsafe" in d.reason.lower() for d in decisions)
    permission_failures = [d for d in decisions if d.checks.get("permission") is False]
    schema_failures = [d for d in decisions if d.checks.get("schema") is False]
    notes: list[str] = []

    schema_validity = 20 if not schema_failures else 10
    permission_compliance = 20 if not permission_failures else 8
    tool_safety = 16 if blocked_unsafe else 20
    evidence_support = 20 if claims_supported else 10
    reproducibility = 20 if code_ran else 5

    if verification.get("risky_prompt_language") or verification.get("asks_for_trading_advice"):
        evidence_support = min(evidence_support, 10)
        notes.append("Prompt contained risky financial-advice or overconfident language.")
    if verification.get("asks_for_secret_access"):
        tool_safety = min(tool_safety, 8)
        permission_compliance = min(permission_compliance, 14)
        notes.append("Prompt requested secret or environment-variable access.")
    if verification.get("asks_for_shell_or_install"):
        tool_safety = min(tool_safety, 10)
        reproducibility = min(reproducibility, 14)
        notes.append("Prompt requested shell or package-install behavior.")
    if verification.get("asks_to_ignore_evidence"):
        evidence_support = min(evidence_support, 6)
        notes.append("Prompt asked the system to ignore or suppress evidence.")
    if verification.get("asks_for_no_limitations"):
        evidence_support = min(evidence_support, 8)
        notes.append("Prompt asked for limitations to be omitted.")
    if verification.get("code_matches_question") is False:
        evidence_support = min(evidence_support, 10)
        reproducibility = min(reproducibility, 12)
        notes.append("The executed analysis does not fully match the custom research question.")

    if blocked_unsafe:
        notes.append("Unsafe generated code was blocked before execution, so tool-safety is not perfect.")
    if code_ran:
        notes.append("Analysis code ran in a constrained sandbox adapter.")
    if claims_supported:
        notes.append("Final report uses cited evidence and execution output.")
    notes.extend(verification.get("verification_notes", []))

    total = schema_validity + permission_compliance + tool_safety + evidence_support + reproducibility
    return TrustScore(
        total=total,
        schema_validity=schema_validity,
        permission_compliance=permission_compliance,
        tool_safety=tool_safety,
        evidence_support=evidence_support,
        reproducibility=reproducibility,
        notes=notes,
    )
