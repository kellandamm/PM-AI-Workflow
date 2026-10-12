"""Local state and validated inputs for Copilot PM workflows."""

from hashlib import sha256
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field

from .documents import DocumentModel
from .run_store import SQLiteRunStore


class Intake(DocumentModel):
    request_key: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=5, max_length=500)
    metadata: dict[str, str]
    sources: dict[str, str]
    provenance: dict[str, str]


def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class CopilotState:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.store = SQLiteRunStore(path)

    def load(self, run_id: str) -> dict:
        state = self.store.load(run_id)
        if state is None:
            raise ValueError("Saved request not found. List your PM requests and select an existing one.")
        if digest(state["input"]) != state["source_hash"]:
            raise ValueError("Sources changed. Start a new versioned run and reapprove context.")
        if set(state["artifacts"]) != set(state["artifact_hashes"]):
            raise ValueError("Artifact manifest changed outside the workflow.")
        for name, value in state["artifacts"].items():
            if digest(value) != state["artifact_hashes"][name]:
                raise ValueError(f"{name} changed outside the workflow.")
        return state

    def start(self, raw: dict) -> dict:
        request = Intake.model_validate(raw).model_dump()
        if set(request["sources"]) != {"design", "transcript", "product"}:
            raise ValueError("Provide design, transcript and product source content.")
        if set(request["provenance"]) != set(request["sources"]):
            raise ValueError("Provenance is required for each source.")
        for name, text in request["sources"].items():
            if not 20 <= len(text.strip()) <= 100000 or (
                text.strip().startswith(("https://", "http://")) and "\n" not in text.strip()
            ):
                raise ValueError(f"{name}: provide collected text, not a link (20-100000 characters).")
            if not request["provenance"][name].strip():
                raise ValueError(f"{name}: provenance is empty.")
        for key in ("project", "component", "priority", "assignee", "sprint"):
            if not request["metadata"].get(key, "").strip():
                raise ValueError(f"Delivery context is missing {key}.")
        run_id = str(uuid5(NAMESPACE_URL, "copilot-pm:" + request["request_key"]))
        if self.store.load(run_id):
            state = self.load(run_id)
            if state["source_hash"] != digest(request):
                raise ValueError("Request exists with different input. Use a new versioned key.")
        else:
            self.store.create(run_id, {
                "status": "pending_approval", "stage": "context", "gate": "context",
                "input": request, "source_hash": digest(request), "artifacts": {},
                "artifact_hashes": {}, "history": [], "critic_rounds": 0,
            })
        return {"run_id": run_id, **self.load(run_id)}

    def listing(self) -> list[dict]:
        result = []
        for row in self.store.list_runs(limit=100):
            state = self.load(row["run_id"])
            result.append({
                **row, "request_key": state["input"]["request_key"],
                "title": state["input"]["title"], "gate": state["gate"],
                "revision": state["_revision"], "error": state.get("error"),
            })
        return result

    def change(self, run_id: str, revision: int) -> dict:
        state = self.load(run_id)
        if state["_revision"] != revision:
            raise ValueError("Stale revision. Inspect status before acting.")
        return state
