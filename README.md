# PM-AI-Workflow

Build evidence-backed product stories directly in **GitHub Copilot CLI**, without
a separate app or Foundry deployment. Five skills and seven agents coordinate
source intake, design/meeting analysis, scope, drafting, edge cases and critique.
Local checkpoint helpers preserve explicit **context, scope and final-story**
decisions, validate complete story sets and source quotes, and export the handoff.

## Quick start

Install/sign in to Copilot CLI and install Python 3.11+. In this repository:

```powershell
python -m venv .venv-copilot
.\.venv-copilot\Scripts\python.exe -m pip install -r requirements-copilot.txt
$env:PYTHONPATH = (Join-Path $PWD "src")
copilot skill list
copilot
```

Select **pm-coordinator** with `/agent`. Ask:

```text
Use /pm-intake with examples/copilot-intake.json.
Create a synthetic run and stop at context approval.
Use /pm-refine to guide me through context, scope and final-story decisions.
Use the .venv-copilot Python interpreter for helper commands.
```

Use `/pm-status`, `/pm-resume` and `/pm-handoff` as needed.
The helper's `advance` automates model work between decisions, never approves.
No Azure dependencies are required. Authorize the isolated runner's Copilot account
as explained in the guide; do not put tokens in chat or source.

## Directions and automation

- [Setup, command reference, MCP integration and customer demo](docs/copilot-workflow.md)
- [Opt-in GitHub Actions walkthrough and approval setup](docs/copilot-automation.md)
- [Synthetic input](examples/copilot-intake.json)
- [Checkpoint tests](tests/test_copilot_workflow.py)

The Actions example uses synthetic data and requires three protected approval
environments, an explicitly reviewed CLI version and authorized Copilot credential.
It is not automatically enabled on clone and is not a live Jira webhook integration.

Figma/Jira/Confluence/Google connections require provider authorization and verified
read tools; none are preconfigured. Keep customer work under gitignored `.pm-work`.
Local owner access is not tamper-proof multi-user governance. No Jira publishing
or quality/cost uplift is claimed. Live model and hosted Actions verification remain
dependent on operator authentication/configuration; read the guide's status.
