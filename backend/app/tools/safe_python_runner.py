import subprocess
import sys
import tempfile
from pathlib import Path

from app.sentinel.validators import find_unsafe_code_patterns


class SafePythonRunner:
    def run(self, code: str, timeout_seconds: int = 6) -> str:
        unsafe = find_unsafe_code_patterns(code)
        if unsafe:
            raise ValueError(f"Unsafe code patterns blocked: {', '.join(unsafe)}")

        with tempfile.TemporaryDirectory(prefix="nlip_sentinel_") as tmp:
            tmp_path = Path(tmp)
            script_path = tmp_path / "analysis.py"
            script_path.write_text(code, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=tmp,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            output = result.stdout.strip()
            if result.stderr.strip():
                output += f"\nSTDERR:\n{result.stderr.strip()}"
            if result.returncode != 0:
                raise RuntimeError(f"Sandboxed code failed with exit {result.returncode}:\n{output}")
            return output

