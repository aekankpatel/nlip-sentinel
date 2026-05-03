ALLOWED_MESSAGE_ROUTES: set[tuple[str, str]] = {
    ("user", "planner_agent"),
    ("planner_agent", "research_agent"),
    ("planner_agent", "code_agent"),
    ("research_agent", "verifier_agent"),
    ("code_agent", "sandbox_agent"),
    ("sandbox_agent", "verifier_agent"),
    ("verifier_agent", "report_agent"),
    ("report_agent", "user"),
}

ALLOWED_INTENTS: dict[str, set[str]] = {
    "user": {"workflow.start"},
    "planner_agent": {"research.search", "code.generate"},
    "research_agent": {"evidence.summarize"},
    "code_agent": {"code.execute.request"},
    "sandbox_agent": {"execution.result"},
    "verifier_agent": {"report.verify"},
    "report_agent": {"report.final"},
}

ALLOWED_TOOLS: dict[str, set[str]] = {
    "research_agent": {"tavily_search"},
    "sandbox_agent": {"python_sandbox"},
    "verifier_agent": set(),
    "report_agent": set(),
    "code_agent": set(),
    "planner_agent": set(),
}

BLOCKED_CODE_PATTERNS: tuple[str, ...] = (
    "os.environ",
    "getenv(",
    "subprocess",
    "os.system",
    "shutil.rmtree",
    ".unlink(",
    ".rmdir(",
    "open('/etc/",
    'open("/etc/',
    "eval(",
    "exec(",
    "open('.env",
    'open(".env',
    "read_text('.env",
    'read_text(".env',
    "pip install",
    "requests.",
    "urllib",
    "socket.",
)

UNSUPPORTED_FINANCIAL_CLAIMS: tuple[str, ...] = (
    "definitely buy",
    "guaranteed",
    "proves",
    "risk-free",
    "100% accurate",
    "certain profit",
    "cannot lose",
)
