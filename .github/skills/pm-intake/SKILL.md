---
name: pm-intake
description: Find ready PM requests and collect source snapshots for a CLI run awaiting context approval.
---

Read `docs/copilot-workflow.md`, including connector and data boundaries.
Use only specifically permitted read tools on configured MCP servers. If the
authorized project or request is unknown, ask the PM. Show ready Jira requests,
source completeness and existing CLI status; select a request before collecting.

Save intake matching `examples/copilot-intake.json` in `.pm-work` as described
in the guide. For a demo use that synthetic file. Require design,
transcript and product text plus source ID/URL, version or retrieval time in
provenance. A URL alone is not collected content. Mark synthetic content.
Report unavailable/denied connections and request an authorized export; never
install arbitrary connectors, write Jira or include secrets in input.

Invoke the helper's start --input command using the guide's Python setup.
Stop at context approval. Do not run analysis or infer approval.
