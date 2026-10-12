"""Synthetic Actions adapter; environment reviewers authorize each gate."""

import json
import os
from pathlib import Path

from pm_story_agents.copilot_gates import CopilotWorkflow
from pm_story_agents.copilot_runner import advance, exclusive


def run_stage(flow: CopilotWorkflow, gate: str, model: str, output: Path) -> dict:
    rows = flow.listing()
    if len(rows) != 1 or rows[0]["request_key"] != "SYNTHETIC-001:v2":
        raise ValueError("Actions example permits exactly the built-in synthetic request.")
    run_id = rows[0]["run_id"]
    state = flow.load(run_id)
    sample = json.loads(Path("examples/copilot-intake.json").read_text(encoding="utf-8"))
    if state["input"] != sample:
        raise ValueError("Actions demo input differs from the built-in synthetic source.")
    if gate == "final" and state["artifacts"]["critic"]["status"] != "pass":
        raise ValueError("Unresolved findings cannot be auto-accepted. Download checkpoint and review locally.")
    if gate != "final" and not os.getenv("COPILOT_GITHUB_TOKEN"):
        raise ValueError("PM_COPILOT_TOKEN secret is required; no anonymous or credential fallback.")
    state = flow.decide(
        run_id, state["_revision"], gate, True,
        f"Required GitHub environment review for pm-{gate} approved this synthetic artifact revision.",
    )
    if gate == "final":
        flow.export(run_id, output)
    else:
        state = advance(flow, run_id, model)
    return {"run_id": run_id, "status": state["status"], "gate": state["gate"]}


def main():
    if os.getenv("GITHUB_ACTIONS") != "true":
        raise ValueError("This adapter runs only in the protected synthetic Actions workflow.")
    flow = CopilotWorkflow(".pm-work/runs.sqlite3")
    with exclusive(flow.path):
        result = run_stage(flow, os.environ["PM_GATE"], os.getenv("PM_MODEL", "auto"),
                           Path(".pm-work/handoff"))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as stream:
            stream.write(f"Checkpoint: `{result['status']}`; gate: `{result['gate']}`.\n")
            stream.write("Inspect the saved artifact before approving the next environment.\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
