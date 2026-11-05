"""Run the PM checkpoint helper from an installed plugin.

Usage: python3 pm.py <helper command and flags>
Tools live in the plugin; progress is saved in .pm-work under the current folder.
"""

import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.getenv("CLAUDE_PLUGIN_DATA") or Path.home() / ".pm-ai-workflow")


def main() -> int:
    if sys.version_info < (3, 11):
        print("Install Python 3.11 or newer.", file=sys.stderr)
        return 1
    env_dir = DATA / "venv"
    python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        DATA.mkdir(parents=True, exist_ok=True)
        venv.create(env_dir, with_pip=True)
        subprocess.run([str(python), "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
                        "-r", str(ROOT / "requirements-copilot.txt")], check=True)
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    return subprocess.run([str(python), "-m", "pm_story_agents.copilot_workflow", *sys.argv[1:]],
                          env=env, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
