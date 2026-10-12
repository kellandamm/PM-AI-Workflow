"""SQLite-backed persistence for approval-gated workflow runs."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class SQLiteRunStore:
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = str(database_path)
        if self._database_path == ":memory:":
            raise ValueError("Workflow runs require a persistent SQLite file.")
        Path(self._database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    run_id TEXT PRIMARY KEY,
                    revision INTEGER NOT NULL,
                    state_json TEXT NOT NULL
                )
                """
            )

    def create(self, run_id: str, state: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO workflow_runs (run_id, revision, state_json) VALUES (?, 0, ?)",
                (run_id, json.dumps(state, ensure_ascii=False)),
            )

    def load(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT revision, state_json FROM workflow_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        state = json.loads(row[1])
        state["_revision"] = row[0]
        return state

    def save(self, run_id: str, state: dict[str, Any]) -> None:
        revision = state.get("_revision")
        if not isinstance(revision, int):
            raise ValueError("Run state revision is missing.")
        persisted_state = {key: value for key, value in state.items() if key != "_revision"}
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE workflow_runs
                SET revision = revision + 1, state_json = ?
                WHERE run_id = ? AND revision = ?
                """,
                (json.dumps(persisted_state, ensure_ascii=False), run_id, revision),
            )
        if cursor.rowcount != 1:
            raise RuntimeError(f"Workflow run {run_id!r} changed concurrently or no longer exists.")
        state["_revision"] = revision + 1

    def submit_decision(
        self,
        run_id: str,
        gate: str,
        decision: dict[str, Any],
        expected_revision: int | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT revision, state_json FROM workflow_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Workflow run {run_id!r} does not exist.")
            if expected_revision is not None and row[0] != expected_revision:
                raise ValueError("Review changed. Refresh before submitting another decision.")
            state = json.loads(row[1])
            if state.get("status") != "pending_approval" or state.get("pending_gate") != gate:
                raise ValueError(f"Workflow run {run_id!r} is not waiting at gate {gate!r}.")
            if state.get("decision") is not None:
                raise ValueError(f"Workflow run {run_id!r} already has a decision for gate {gate!r}.")
            state["decision"] = decision
            cursor = connection.execute(
                """
                UPDATE workflow_runs
                SET revision = revision + 1, state_json = ?
                WHERE run_id = ? AND revision = ?
                """,
                (json.dumps(state, ensure_ascii=False), run_id, row[0]),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(f"Workflow run {run_id!r} changed concurrently.")

    def list_runs(self, limit: int = 30) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT run_id, state_json FROM workflow_runs ORDER BY rowid DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            {"run_id": run_id, "status": json.loads(raw)["status"], "stage": json.loads(raw)["stage"]}
            for run_id, raw in rows
        ]

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path, timeout=30)
        connection.execute("PRAGMA busy_timeout = 30000")
        try:
            with connection:
                yield connection
        finally:
            connection.close()
