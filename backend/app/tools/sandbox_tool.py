from app.config import get_settings
from app.tools.safe_python_runner import SafePythonRunner


class DaytonaAdapter:
    def run_python(self, code: str) -> str:
        settings = get_settings()
        try:
            from daytona import Daytona, DaytonaConfig

            api_key = settings.daytona_api_key or settings.daytona_api_token
            config = DaytonaConfig(api_key=api_key) if api_key else None
            daytona = Daytona(config) if config else Daytona()
            sandbox = daytona.create()
            try:
                response = sandbox.process.code_run(code)
                result = getattr(response, "result", "")
                exit_code = getattr(response, "exit_code", 0)
                if exit_code != 0:
                    raise RuntimeError(f"Daytona execution failed with exit {exit_code}: {result}")
                return str(result).strip()
            finally:
                sandbox.delete()
        except Exception:
            return SafePythonRunner().run(code)


class SandboxTool:
    def __init__(self) -> None:
        settings = get_settings()
        self.runner = DaytonaAdapter() if settings.has_daytona else SafePythonRunner()

    def run_python(self, code: str) -> str:
        return self.runner.run(code) if isinstance(self.runner, SafePythonRunner) else self.runner.run_python(code)
