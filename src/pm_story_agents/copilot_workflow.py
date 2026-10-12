"""Command-line entry point for Copilot PM checkpoint operations."""

import argparse
import json
import os
from pathlib import Path
import sys

from .copilot_gates import Analysis, CopilotWorkflow, Critique, ORDER
from .copilot_runner import advance, exclusive, prompt
from .copilot_state import Intake
from .documents import StorySet, TitleSet, parse_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=os.getenv("PM_COPILOT_DB", ".pm-work/runs.sqlite3"))
    sub = parser.add_subparsers(dest="action", required=True)
    start = sub.add_parser("start")
    start.add_argument("--input", required=True, type=Path)
    sub.add_parser("list")
    sub.add_parser("schemas")
    for action in ("status", "prompt", "export", "advance", "record", "approve", "reject", "revise", "retry", "fail"):
        command = sub.add_parser(action)
        command.add_argument("--run", required=True)
        if action in {"record", "approve", "reject", "revise", "retry", "fail"}:
            command.add_argument("--revision", type=int, required=True)
        if action == "record":
            command.add_argument("--stage", choices=ORDER, required=True)
            command.add_argument("--input", type=Path, required=True)
        if action in {"approve", "reject"}:
            command.add_argument("--gate", choices=("context", "scope", "final"), required=True)
            command.add_argument("--decision", required=True)
            command.add_argument("--accept-findings", action="store_true")
        if action == "revise":
            command.add_argument("--feedback", required=True)
        if action == "fail":
            command.add_argument("--message", required=True)
        if action == "export":
            command.add_argument("--output", type=Path, required=True)
        if action == "advance":
            command.add_argument("--model", required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "schemas":
            print(json.dumps({name: cls.model_json_schema() for name, cls in {
                "intake": Intake, "analysis": Analysis, "scope": TitleSet,
                "draft": StorySet, "critic": Critique,
            }.items()}, indent=2))
            return 0
        flow = CopilotWorkflow(args.db)
        with exclusive(flow.path):
            if args.action == "start":
                result = flow.start(parse_json(args.input.read_text(encoding="utf-8")))
            elif args.action == "list":
                result = flow.listing()
            elif args.action == "record":
                result = flow.record(args.run, args.revision, args.stage, parse_json(args.input.read_text(encoding="utf-8")))
            elif args.action in {"approve", "reject"}:
                result = flow.decide(args.run, args.revision, args.gate, args.action == "approve",
                                     args.decision, args.accept_findings)
            elif args.action == "revise":
                result = flow.revise(args.run, args.revision, args.feedback)
            elif args.action == "fail":
                result = flow.fail(args.run, args.revision, args.message)
            elif args.action == "retry":
                result = flow.retry(args.run, args.revision)
            elif args.action == "advance":
                result = advance(flow, args.run, args.model)
            elif args.action == "export":
                flow.export(args.run, args.output)
                result = {"exported": str(args.output)}
            elif args.action == "prompt":
                print(prompt(flow.load(args.run)))
                return 0
            else:
                result = flow.load(args.run)
            print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
