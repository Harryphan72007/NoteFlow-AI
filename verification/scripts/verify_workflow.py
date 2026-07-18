from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "verification" / "evidence" / "test-results" / "workflow_commands.json"


def run(name: str, command: list[str], cwd: Path) -> dict:
    env = os.environ.copy()
    env["CI"] = "true"
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=120, env=env)
    return {
        "name": name,
        "command": command,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "pass": proc.returncode == 0,
    }


def main() -> int:
    python = ROOT / ".venv" / "Scripts" / "python.exe"
    pnpm = Path(r"C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd")
    commands = [
        ("pytest_backend", [str(python), "-m", "pytest", "backend\\tests", "-q"], ROOT),
        ("frontend_build", [str(pnpm), "run", "build"], ROOT / "Frontend"),
    ]
    results = [run(name, command, cwd) for name, command, cwd in commands]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0 if all(item["pass"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
