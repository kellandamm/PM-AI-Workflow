"""Validated transitions for human-approved Copilot artifacts."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from .copilot_state import CopilotState, digest
from .documents import DocumentModel, markdown_export, parse_json, validate_stories, validate_titles


class Analysis(DocumentModel):
    text: str = Field(min_length=20, max_length=100000)


class Critique(DocumentModel):
    status: Literal["pass", "revise"]
    findings: list[str]
    revision_instructions: str


ROLES = {
    "lead": "story-lead", "transcript": "transcript-analyst",
    "design": "figma-flow-analyst", "scope": "story-writer",
    "draft": "story-writer", "edges": "edge-case-hunter", "critic": "ac-critic",
}
ORDER = tuple(ROLES)


class CopilotWorkflow(CopilotState):
    def save(self, run_id: str, state: dict, event: dict) -> dict:
        state["history"].append({
            **event, "revision": state["_revision"],
            "at": datetime.now(timezone.utc).isoformat(),
        })
        self.store.save(run_id, state)
        return self.load(run_id)

    def record(self, run_id: str, revision: int, stage: str, raw: dict) -> dict:
        state = self.change(run_id, revision)
        if state["status"] != "running" or state["stage"] != stage or stage not in ROLES:
            raise ValueError("Stage not authorized. Inspect the pending gate or failed stage.")
        if stage == "scope":
            value = parse_json(validate_titles(json.dumps(raw)))
        elif stage == "draft":
            value = parse_json(validate_stories(
                json.dumps(raw), json.dumps(state["artifacts"]["scope"]), state["input"]["sources"],
            ))
        elif stage == "critic":
            value = Critique.model_validate(raw).model_dump()
            if value["status"] == "pass" and value["findings"]:
                raise ValueError("Passing critique cannot contain unresolved findings.")
            if value["status"] == "revise" and not any(item.strip() for item in value["findings"]):
                raise ValueError("Revision verdict must identify findings.")
        else:
            value = Analysis.model_validate(raw).model_dump()
        state["artifacts"][stage] = value
        state["artifact_hashes"][stage] = digest(value)
        state.pop("error", None)
        if stage == "scope":
            state.update(status="pending_approval", stage="scope", gate="scope")
        elif stage == "critic":
            if value["status"] == "revise" and state["critic_rounds"] < 2:
                state["critic_rounds"] += 1
                state["stage"] = "draft"
                # Keep the prior draft and critique available to the revision writer.
            else:
                state.update(status="pending_approval", stage="final", gate="final")
        else:
            state["stage"] = ORDER[ORDER.index(stage) + 1]
        return self.save(run_id, state, {"kind": "artifact", "stage": stage, "value": value})

    def decide(self, run_id: str, revision: int, gate: str, approve: bool,
               decision: str, accept_findings: bool = False) -> dict:
        state = self.change(run_id, revision)
        if state["status"] != "pending_approval" or state["gate"] != gate:
            raise ValueError("This gate is not pending.")
        if len(decision.strip()) < 5:
            raise ValueError("Record the PM's explicit decision, not a tool permission.")
        if approve and gate == "final":
            if state["artifacts"]["critic"]["status"] != "pass" and not accept_findings:
                raise ValueError("Explicit acceptance of unresolved findings is required.")
        if not approve:
            state.update(status="stopped", gate=None)
        elif gate == "final":
            state.update(status="completed", stage="completed", gate=None)
        else:
            state.update(status="running", stage="lead" if gate == "context" else "draft", gate=None)
        return self.save(run_id, state, {
            "kind": "decision", "gate": gate, "approved": approve,
            "decision": decision, "accept_findings": accept_findings,
            "source_hash": state["source_hash"], "artifact_hashes": dict(state["artifact_hashes"]),
        })

    def revise(self, run_id: str, revision: int, feedback: str) -> dict:
        state = self.change(run_id, revision)
        gate = state["gate"]
        if state["status"] != "pending_approval" or gate not in {"scope", "final"}:
            raise ValueError("Revise at scope/final gates. Input changes need a new versioned run.")
        if len(feedback.strip()) < 5:
            raise ValueError("PM feedback is required.")
        state.update(status="running", stage="scope" if gate == "scope" else "draft",
                     gate=None, feedback=feedback, critic_rounds=0)
        return self.save(run_id, state, {"kind": "revision", "gate": gate, "feedback": feedback})

    def fail(self, run_id: str, revision: int, message: str) -> dict:
        state = self.change(run_id, revision)
        if state["status"] != "running" or not message.strip():
            raise ValueError("Only active stages can fail, with a nonempty error.")
        state.update(status="failed", error=message)
        return self.save(run_id, state, {"kind": "failure", "stage": state["stage"], "error": message})

    def retry(self, run_id: str, revision: int) -> dict:
        state = self.change(run_id, revision)
        if state["status"] != "failed":
            raise ValueError("Only a failed stage can be explicitly retried.")
        state.update(status="running")
        state.pop("error", None)
        return self.save(run_id, state, {"kind": "retry", "stage": state["stage"]})

    def export(self, run_id: str, output: Path) -> None:
        state = self.load(run_id)
        if state["status"] != "completed":
            raise ValueError("Final PM approval is required before handoff.")
        stories = validate_stories(json.dumps(state["artifacts"]["draft"]),
                                   json.dumps(state["artifacts"]["scope"]), state["input"]["sources"])
        output.mkdir(parents=True, exist_ok=False)
        (output / "review.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        (output / "stories.json").write_text(stories, encoding="utf-8")
        (output / "stories.md").write_text(
            markdown_export(stories).replace("Draft output. Jira publishing disabled.",
                                            "PM-approved handoff. No external issues were created."),
            encoding="utf-8",
        )
