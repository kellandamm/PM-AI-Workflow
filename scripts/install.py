"""Install the PM workflow for Claude Code, GitHub Copilot CLI and/or Codex.

    python3 scripts/install.py                 # every tool found on this computer
    python3 scripts/install.py --target claude # one tool: claude, copilot, codex, all
    python3 scripts/install.py --uninstall     # remove what this script installed
    python3 scripts/install.py --dry-run       # show what would change

The agents/ and skills/ folders are the single source. For each tool this copies
the shared tools to ~/.pm-ai-workflow and writes that tool's user-level skills
(and agents where the tool has them), so the workflow is available in every
session without further setup. Nothing is written outside the chosen home folder.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1]
SHARED = ("src", "docs", "examples", "scripts", "conventions.md", "requirements-copilot.txt")
TOKEN = "${CLAUDE_PLUGIN_ROOT}"
MARKER = ".pm-ai-workflow-installed"
COPILOT_TOOLS = {"Read": "read", "Grep": "search", "Glob": "search", "Write": "edit",
                 "Edit": "edit", "Bash": "execute", "Agent": "agent", "Skill": "skill",
                 "AskUserQuestion": "ask_user"}
BINARIES = {"claude": "claude", "copilot": "copilot", "codex": "codex"}


def split(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not match:
        raise ValueError("Missing front matter.")
    meta = dict(line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line)
    return meta, match.group(2)


def join(meta: dict[str, str], body: str) -> str:
    return "---\n" + "\n".join(f"{k}: {v}" for k, v in meta.items()) + "\n---\n" + body


def copilot_agent(text: str) -> str:
    meta, body = split(text)
    names = []
    for tool in (t.strip() for t in meta["tools"].split(",")):
        mapped = COPILOT_TOOLS[tool]
        if mapped not in names:
            names.append(mapped)
    meta["tools"] = json.dumps(names)
    meta["include-custom-instructions"] = "true"
    return join(meta, body.replace("AskUserQuestion", "ask_user"))


def codex_coordinator(text: str, root: Path) -> str:
    """Codex has no known custom-agent file; the coordinator becomes a skill."""
    meta, body = split(text)
    meta = {"name": meta["name"], "description": meta["description"]}
    note = (f"\nCodex has no separate specialist agents here. For each stage, read the matching "
            f"role file in `{root}/src/pm_story_agents/skills/` (story-lead, transcript-analyst, "
            f"figma-flow-analyst, story-writer, edge-case-hunter, ac-critic) and perform it "
            f"yourself, returning candidate JSON. Ask the user questions directly, one at a time.\n")
    return join(meta, body.replace("AskUserQuestion", "a direct question") + note)


def targets(home: Path) -> dict[str, dict[str, Path]]:
    return {
        "claude": {"skills": home / ".claude" / "skills", "agents": home / ".claude" / "agents"},
        "copilot": {"skills": home / ".copilot" / "skills", "agents": home / ".copilot" / "agents"},
        "codex": {"skills": home / ".agents" / "skills"},
    }


def render(root: Path, target: str) -> dict[str, tuple[str, str]]:
    """Return {relative path: (kind, content)} for a target."""
    files: dict[str, tuple[str, str]] = {}
    for skill in sorted((SOURCE / "skills").iterdir()):
        text = (skill / "SKILL.md").read_text(encoding="utf-8").replace(TOKEN, str(root))
        files[f"{skill.name}/SKILL.md"] = ("skills", text)
    for agent in sorted((SOURCE / "agents").glob("*.md")):
        text = agent.read_text(encoding="utf-8").replace(TOKEN, str(root))
        if target == "claude":
            files[agent.name] = ("agents", text)
        elif target == "copilot":
            files[f"{agent.stem}.agent.md"] = ("agents", copilot_agent(text))
        elif target == "codex" and agent.stem == "pm-coordinator":
            files["pm-coordinator/SKILL.md"] = ("skills", codex_coordinator(text, root))
    return files


def detect() -> list[str]:
    return [name for name, binary in BINARIES.items() if shutil.which(binary)]


def install(home: Path, chosen: list[str], dry_run: bool) -> list[str]:
    log: list[str] = []
    root = home / ".pm-ai-workflow"
    log.append(f"shared tools -> {root}")
    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)
        for name in SHARED:
            src = SOURCE / name
            dest = root / name
            if src.is_dir():
                shutil.copytree(src, dest, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(src, dest)
        (root / MARKER).write_text("installed by scripts/install.py\n", encoding="utf-8")
    for target in chosen:
        locations = targets(home)[target]
        for rel, (kind, content) in render(root, target).items():
            dest = locations[kind] / rel
            log.append(f"{target}: {dest}")
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
    return log


def uninstall(home: Path, dry_run: bool) -> list[str]:
    log: list[str] = []
    root = home / ".pm-ai-workflow"
    for target, locations in targets(home).items():
        for rel, (kind, _) in render(root, target).items():
            path = locations[kind] / rel
            if path.exists():
                log.append(f"remove {path}")
                if not dry_run:
                    path.unlink()
                    if path.parent.name != locations[kind].name and not any(path.parent.iterdir()):
                        path.parent.rmdir()
    if (root / MARKER).exists():
        log.append(f"remove {root} (saved PM requests in .pm-work folders are not touched)")
        if not dry_run:
            shutil.rmtree(root)
    return log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", choices=["auto", "all", *BINARIES], default="auto")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--home", type=Path, default=Path(os.path.expanduser("~")),
                        help="Install under this folder instead of your home folder.")
    args = parser.parse_args(argv)
    if args.uninstall:
        lines = uninstall(args.home, args.dry_run)
        print("\n".join(lines) or "Nothing to remove.")
        return 0
    chosen = list(BINARIES) if args.target == "all" else detect() if args.target == "auto" else [args.target]
    if not chosen:
        print("No supported tool found (claude, copilot, codex). Use --target to install anyway.",
              file=sys.stderr)
        return 1
    print("\n".join(install(args.home, chosen, args.dry_run)))
    print("\n(dry run, nothing written)" if args.dry_run else
          "\nDone. Start a new session and say: Start the sample PM workflow.\n"
          "Helper tools need Python 3.11+ and set themselves up on first use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
