---
name: pm-intake
description: Start a sample or new PM request, gather its sources and pause for your review.
---

Read `docs/copilot-workflow.md` for the user journey and `docs/copilot-reference.md`
for commands and source requirements.

For "Start the sample PM workflow", use `examples/copilot-intake.json`.
For a new request, ask one question at a time: feature description, delivery
details, design/flow notes, meeting decisions and product requirements. Explain
missing fields in ordinary language; the user should not have to write JSON.
Use the user's supplied values. An explicit "Not used" sprint is valid when true.
Choose a unique product-qualified versioned request key; never silently overwrite
an existing request or reuse a key with different sources.

Use only specifically permitted read tools on configured MCP servers. If the
authorized project or request is unknown, ask the PM. Show ready requests from
the authorized source system (if configured), source completeness and existing
CLI status; select a request before collecting.

Save intake matching `examples/copilot-intake.json` in `.pm-work` as described
in the guide. For a demo use that synthetic file. Require design,
transcript and product text plus source ID/URL, version or retrieval time in
provenance. A URL alone is not collected content. Mark synthetic content.
Report unavailable/denied connections and request an authorized export; never
install arbitrary connectors, modify source systems or include secrets in input.

Create the intake JSON yourself from authorized collected content. Invoke the
helper's start --input command with `.venv-copilot`'s Python and the `src`
PYTHONPATH. Show the request, delivery details, source summaries and evidence
limitations in plain language. Stop for explicit context approval; do not run
analysis or infer approval.
