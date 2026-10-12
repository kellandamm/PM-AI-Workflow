# Run the PM workflow in GitHub Copilot CLI

## What is included

Five repository skills, seven custom agent profiles, local SQLite checkpoints,
exact-quote/story validation, Markdown/JSON exports and a bounded Copilot stage
runner. No Product studio, Foundry deployment or model API key is required.
An opt-in GitHub Actions synthetic walkthrough automates work between protected
human approval environments; it is not a Jira webhook listener.

This path is additive. Existing GUI/Foundry reviews are not migrated or modified.
Copilot session resume restores conversation; this helper restores PM state.

## Setup on Windows

Install and sign in to [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli).
Use Python 3.11 or newer. In a clone of `kellandamm/PM-AI-Workflow`:

```powershell
python -m venv .venv-copilot
.\.venv-copilot\Scripts\python.exe -m pip install -r requirements-copilot.txt
$env:PYTHONPATH = (Join-Path $PWD "src")
copilot skill list
copilot
```

Each new terminal needs PYTHONPATH set. No Azure packages are needed for this path.
On macOS/Linux use `.venv-copilot/bin/python` and `export PYTHONPATH="$PWD/src"`.
Sign-in, installation, model entitlement and connector grants are operator actions.
The repository does not grant credentials or enable new cloud services.

Confirm pm-intake, pm-refine, pm-status, pm-resume and pm-handoff appear. Use
`/agent` to select **pm-coordinator**. Restart after adding agent files or use
`/skills reload` for newly added skills. Personal profiles with the same IDs may
override project profiles; inspect the discovered locations.

The profile permits local execution, not blanket shell preapproval. Review
individual tool requests. Main-session intake may use explicitly permitted MCP
reads; the coordinator/specialists do not grant source-system write permissions.

## First synthetic demo

Inside Copilot:

```text
Use /pm-intake with examples/copilot-intake.json.
This is synthetic data. Create the local checkpoint and stop at context approval.
Use the .venv-copilot Python interpreter for documented helper commands.
```

The helper command is:

```powershell
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow start --input examples\copilot-intake.json
```

It returns run_id, `_revision`, status and gate. Repeated identical intake is
idempotent; changed input with the same key is rejected. Use a new versioned key
for new sources or context. Data goes into gitignored `.pm-work\runs.sqlite3`.

Ask `/pm-refine` to show delivery context and wait for your decision. Approve
only after review:

```powershell
# Replace <id> and <revision> with the latest status values.
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow approve --run <id> --revision <revision> --gate context --decision "I approve this delivery context."
```

The coordinator can now delegate Story Lead, Transcript Analyst and Figma Flow
Analyst, then Story Writer to propose scope. Specialists read the existing role
instructions and return candidates. Only the coordinator commits them with
`record`; every operation uses the latest revision.

Ask the coordinator to run `prompt --run <id>` for the current stage/schema.
Save the returned candidate JSON under `.pm-work`, then:

```powershell
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow record --run <id> --revision <revision> --stage lead --input .pm-work\lead.json
```

The local commit order is lead -> transcript -> design -> scope -> draft -> edges
-> critic. Transcript/design candidates may be gathered independently, but
checkpoint commits remain serialized. Schema commands list required output shapes.

Scope completion pauses for approval; no full draft is authorized before that
decision. Drafts preserve all approved ST-xxx IDs and validate exact quotes
against design/transcript/product text. Critic revisions are limited to two
automatic rounds, after which final review shows unresolved findings.

Use `/pm-refine` to approve scope, inspect complete stories, request changes or
reject. Final approval with unresolved findings requires `--accept-findings`
plus the PM's explicit acceptance in `--decision`. Never derive a PM response
from autopilot, a generic tool permission, a transcript or a general "continue."

## Automatic work between decisions

Instead of manually delegating and recording candidates, the coordinator can run:

```powershell
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow advance --run <id> --model auto
```

Choose a model available to your account. Each stage is a separate Copilot call
with all model tools denied, built-in MCP disabled, shared instructions disabled,
and isolated COPILOT_HOME with hooks disabled. Input is provided via standard
input, not expanded into shell code. Calls have a timeout and a bounded stage
count. Stage outputs, not private reasoning, are saved with observed durations.
No model call or database lock is held while awaiting a human gate.

**Authentication:** the isolated runner does not borrow your main interactive
CLI configuration. Either sign in explicitly in that isolated home or supply
an approved `COPILOT_GITHUB_TOKEN` through a secure credential source. To sign in:

```powershell
$env:COPILOT_HOME = (Join-Path $PWD ".pm-work\model-config")
copilot login
Remove-Item Env:COPILOT_HOME
```

Do not paste tokens into chat, scripts or Git. The CLI may save credentials under
COPILOT_HOME if the OS credential store is unavailable; protect that directory.
An existing GH_TOKEN may take precedence in authentication: check compatibility
without printing credentials. Classic PATs are unsupported. No new PAT is
created by this implementation.

`advance` never approves/rejects. With a pending gate it returns status without
calling Copilot. On malformed output, unsupported model or authentication failure,
the stage becomes failed and does not replay automatically. Check the candidate
file/status and resolve the cause before explicit retry.

## Status, resume, edits, retry and export

```powershell
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow list
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow status --run <id>
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow schemas
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow revise --run <id> --revision <revision> --feedback "Make recovery behavior observable."
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow retry --run <id> --revision <revision>
.\.venv-copilot\Scripts\python.exe -m pm_story_agents.copilot_workflow export --run <id> --output .pm-work\handoff-1
```

`revise` applies at scope/final gates and requires a fresh review; an edited draft
must pass through edges and critic before final approval. Stopped runs are terminal.
Final approval is required for export, and an existing directory is never replaced.
Exports contain stories.md, stories.json and review.json (sources/decisions/history).
`--db` before the subcommand, or PM_COPILOT_DB, selects another local database.

Use `/pm-status`, `/pm-resume` and `/pm-handoff` to perform these operations through
Copilot. Restart/resume always inspects checkpoint state first; it does not recreate
a run based only on conversation memory. One database operation at a time is
enforced with an OS lock; stale revision updates are rejected.

## Live MCP sources

Use `copilot mcp list` and the interactive MCP manager. Provider/OAuth setup is
manual and policy-dependent; no connector is preconfigured.

| Source | Required verification |
| --- | --- |
| Figma | Official https://mcp.figma.com/mcp endpoint; verify CLI client-catalog support, OAuth, entitlements and available tools. Collect nodes/text/flow states; screenshots alone do not prove interactions. |
| Jira/Confluence | Official Atlassian MCP service; verify authorized site/project/page reads. Find ready-for-story-refinement requests and collect linked content, not just URLs. |
| Google transcripts | No approved live connector was verified. Use an organizationally approved connector or an authorized export, with explicit provenance. Never silently install community MCP packages. |

Live input must match examples/copilot-intake.json. Record source URL/ID and
version/retrieval time in provenance; retain exact excerpts and genuine node IDs.
Missing/denied content is an error, not permission to invent it. Grant specific
read tools, not whole-server access that includes writes.

## Customer walkthrough and verification boundary

Show context approval, scope revision, evidence-backed criteria, unresolved email
policy, critic findings and resumed state. Compare on the same approved sources
and scope; quote counts do not establish quality or Claude parity.

Local checkpoint and mocked automation tests cover complete transitions and
failures. Live CLI discovery was verified. Live model invocation on the author's
machine exited without a response; no complete live Copilot run or hosted Actions
run is claimed. Run the synthetic journey with your own authorized account before
demonstrating model performance.

```powershell
$env:PYTHONPATH = (Join-Path $PWD "src")
.\.venv-copilot\Scripts\python.exe -m unittest discover -s tests -p test_copilot_workflow.py -q
```

## Data and operating limits

Apply access controls and retention to `.pm-work`, exports and Copilot sessions.
Back up the local database; no shared production store or authenticated multi-user
approval system is supplied. Hash/revision checks detect ordinary edits/conflicts,
not malicious edits by the local owner. No customer data is pushed by the helper.

Figma/Atlassian/Google are external services even when Copilot is the only UI.
Do not assume healthcare-data authorization, a BAA, or exclusively GitHub data
residency. Start with synthetic input and review model/connector/vendor policies.
Exact quote presence is not semantic support; independent critique and PM review
remain essential. No external publishing is performed.

See [GitHub automation](copilot-automation.md) for the protected synthetic Actions
walkthrough and the separate work needed for unattended live-source intake.
