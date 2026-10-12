# Use the PM workflow

You describe the work and review the results. Copilot handles the source files,
analysis, saved progress and story export.

## 1. Set up once

Install [Python 3.11 or newer](https://www.python.org/downloads/) and
[GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli).
You need a GitHub account with access to Copilot.

Download this repository using **Code -> Download ZIP**, extract it, and open a
terminal in the extracted folder. If you already use Git, cloning works too.

On Windows, right-click inside the extracted folder and choose **Open in
Terminal**. On macOS, right-click the folder in Finder and choose
**Services -> New Terminal at Folder** if available.

Run:

```powershell
python scripts\start_pm.py
```

On macOS/Linux, use `python3 scripts/start_pm.py`.

The launcher prepares the local Python tools and opens Copilot. It may download
the required Python package on first use. It does not configure accounts or
connect your organization's systems.

If Copilot asks you to sign in, follow its sign-in instructions. You can also
run `copilot login` from the terminal before starting the launcher.

## 2. Try the sample

In Copilot, type `/agent` and choose **pm-coordinator**. Then paste:

```text
Start the sample PM workflow. Show me the context to review, then guide me
through creating stories. Pause for my approval at each review step.
```

The sample is a fictional shared-record change. Copilot will show three reviews:

| Review | Your decision |
| --- | --- |
| Context | Check the request, source material and delivery details. |
| Scope | Check the proposed story list before full stories are written. |
| Final stories | Check the requirements, acceptance criteria, evidence and open questions. |

For the review currently shown, say **"I approve this context"**,
**"I approve this scope"** or **"I approve these final stories"**.
You can instead say **"Change the scope to..."**, **"Revise the stories to..."**
or **"Reject this request"**. Copilot asks before recording a decision.

Unresolved findings are shown for your review, not quietly approved. You can
request changes or explicitly accept the remaining findings with final approval.
Recommendations are not confirmed requirements until supported by your sources.

## 3. Use your own request

Tell Copilot:

```text
Start a new PM request for my product. Ask me for the request details and
source material one step at a time. Save progress locally and wait for
my approval before starting analysis.
```

Have these ready: a description of the feature, design or flow notes, meeting
notes or decisions, and product requirements. Copilot also asks for your delivery
project, component, priority, owner and sprint. If you do not use sprints, say so.
You do not need to write JSON or look up internal run IDs.

Use only material you are authorized to process. Copilot can read local files
you identify or use already authorized connectors. Missing access is reported;
connecting Figma, a tracker or a document service may need your administrator.

## 4. Continue later or export

Run the same launcher and select **pm-coordinator** again. Use ordinary requests:

| Say this | What happens |
| --- | --- |
| "Show my PM requests." | Lists saved requests and what needs your attention. |
| "Resume my request." | Asks which request if needed, then loads saved progress. |
| "Show the remaining questions." | Displays evidence gaps and reviewer findings. |
| "Export the approved stories." | Saves a readable Markdown file and supporting JSON files. |

Copilot provides the export folder. Export requires final approval; it does not
create issues in your tracker. Keep `.pm-work` private: it contains your inputs,
saved progress and exports. Do not upload it to the repository.

## Help

If `python` is not found, finish installing Python and reopen the terminal.
If `copilot` is not found, finish installing Copilot CLI and reopen the terminal.
If setup fails, the launcher prints the error; fix it before running again.
If a story stage fails, ask Copilot to explain the saved error. Retry only after
the cause is resolved; existing approvals are not silently repeated.

The helper's save/review logic is tested, but a complete live model journey has
not been verified here. Rehearse the sample with your account before a live demo.

For an administrator setting up shared automation, see the
[automation guide](copilot-automation.md). For commands, source formats and
connector setup, see the [technical reference](copilot-reference.md).
