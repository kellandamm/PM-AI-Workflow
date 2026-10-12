# PM-AI-Workflow

Turn design notes, meeting decisions and product requirements into evidence-backed
user stories with **GitHub Copilot**. You review the context, proposed scope and
final stories. Copilot handles analysis, drafting and saving progress.

The starter works with your product's terminology and sources. The included
sample is fictional and covers confirming a shared-record change.

## Get started

1. Install [Python 3.11 or newer](https://www.python.org/downloads/) and
   [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli).
   You need an account with Copilot access.
2. Choose **Code -> Download ZIP** on this repository, extract it, and open a
   terminal in the extracted folder.
3. Run the launcher:

```powershell
python scripts\start_pm.py
```

On macOS/Linux, use `python3 scripts/start_pm.py`. First use prepares the Python
tools. Sign in to Copilot if prompted.

In Copilot, type `/agent`, select **pm-coordinator**, and say:

```text
Start the sample PM workflow. Guide me through it and pause for my approval
at each review step.
```

## Everyday use

Say **"Start a new PM request"**, **"Show my PM requests"**, **"Resume my request"**
or **"Export the approved stories"**. Copilot guides you through the required
details; you do not need to type helper commands or write JSON.

Review before approving. Your files and progress stay in the local `.pm-work`
folder; keep it private. Exports do not automatically create tracker issues.
Live source connections need your organization's authorization.

## Guides

- [Step-by-step user guide](docs/copilot-workflow.md)
- [Administrator guide for shared automation](docs/copilot-automation.md)
- [Plan and checklist for event-driven intake](docs/event-driven-plan.md)
- [Technical reference](docs/copilot-reference.md)

Rehearse the sample with your account before a live demonstration. A complete
live model journey and configured hosted walkthrough have not been verified here.
