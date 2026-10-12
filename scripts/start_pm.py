"""Prepare the local PM tools and open Copilot in this repository."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


ROOT = Path(__file__).resolve().parents[1]


def prepare(root: Path) -> Path:
    if sys.version_info < (3, 11):
        raise RuntimeError("Install Python 3.11 or newer, then run this command again.")
    environment = root / ".venv-copilot"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not environment.exists():
        print("Preparing the PM tools for first use...", flush=True)
        venv.create(environment, with_pip=True)
    if not python.is_file():
        raise RuntimeError(
            f"The Python environment is incomplete: {environment}. "
            "Ask your administrator to repair it before continuing."
        )
    dependency = subprocess.run(
        [str(python), "-c",
         "import importlib.metadata; "
         "v=tuple(map(int, importlib.metadata.version('pydantic').split('.')[:2])); "
         "raise SystemExit(0 if (2,12)<=v<(3,0) else 1)"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if dependency.returncode != 0:
        print("Installing the required Python package...", flush=True)
        subprocess.run(
            [str(python), "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
             "-r", str(root / "requirements-copilot.txt")],
            cwd=root, check=True,
        )
    return python


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup-only", action="store_true",
                        help="Prepare tools without opening Copilot.")
    args = parser.parse_args(argv)
    try:
        binary = shutil.which("copilot")
        if not args.setup_only and not binary:
            raise RuntimeError(
                "Copilot CLI was not found. Install it using the link in README.md, "
                "then reopen your terminal and run this command again."
            )
        python = prepare(ROOT)
        print(f"PM tools ready: {python}", flush=True)
        if args.setup_only:
            return 0
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
        print("Choose pm-coordinator with /agent, then say: Start the sample PM workflow.",
              flush=True)
        return subprocess.run([binary], cwd=ROOT, env=env, check=False).returncode
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Setup could not finish: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
