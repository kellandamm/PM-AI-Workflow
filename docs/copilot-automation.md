# GitHub-hosted Copilot PM automation

## Who should use this guide

This setup is for a repository administrator who wants shared, GitHub-hosted
approvals. For individual use, follow the [user guide](copilot-workflow.md);
you do not need to set up this workflow.

Ask your administrator to configure the approval reviewers, approved Copilot
credential and pinned CLI version below. Once configured, your everyday steps
are: open **Actions**, start **Copilot PM synthetic walkthrough**, review each
checkpoint when approval is requested, and download the final story files.
This example uses only fictional data; it does not collect live requests.

## Included opt-in workflow

`.github/workflows/copilot-pm-demo.yml` is a manually started **synthetic**
walkthrough. It runs Copilot stages automatically between three required GitHub
environment approvals. No resource, credential, schedule or webhook is provisioned.
Workflow jobs have read-only repository permissions and never publish Jira issues.

prepare -> **pm-context review** -> analyses/scope -> **pm-scope review** ->
draft/edges/critic -> **pm-final review** -> validated export.

Environment approval is a deliberate synthetic PM decision: reviewers must
inspect the preceding job's checkpoint artifact, not simply approve a deployment.
Context/scope/final approval are separate environments. If the critic still
requests revisions after its bounded loop, final export fails rather than
automatically accepting findings.

## Configure once, then run

1. Review the workflow, runtime and local helper. Confirm your repository/plan
   supports required environment reviewers. A private repository's GitHub plan
   may not offer this feature; if unavailable use the local CLI gates instead.
2. In repository Settings -> Environments create `pm-context`, `pm-scope` and
   `pm-final`, each with **required reviewers**. Enable prevent-self-review and
   disallow administrator bypass where supported. The prepare job fails closed
   if required reviewers are missing. Do not bypass environment protection.
3. Set repository variable `PM_COPILOT_CLI_VERSION` to an exact reviewed npm
   `@github/copilot` version. No unpinned/latest install is used. Verify it supports
   the runner's documented CLI flags before selecting it.
4. Supply repository secret `PM_COPILOT_TOKEN`: an authorized supported credential
   with Copilot Requests permission and appropriate usage policy. It is not the
   ordinary read-only workflow GITHUB_TOKEN. Do not create or share a token in chat.
   Review GitHub's current organization-auth option before deciding on a PAT.
5. From Actions, choose **Copilot PM synthetic walkthrough** -> Run workflow and
   select an available model. This consumes Copilot usage and Actions runtime.
6. Review the pm-context checkpoint artifact's source/context before approving
   the context environment. Review complete scope before pm-scope, then stories,
   evidence, findings and history before pm-final.
7. Download pm-approved-handoff for stories.md, stories.json and review.json.

No source-system secrets are needed: this workflow only accepts the built-in
synthetic input. The adapter validates that the stored request exactly matches
the repository example (`SYNTHETIC-001:v2`, a generic shared-record change).
Real transcripts must not be put into this demo. Older `v1` checkpoints remain
resumable locally but are not accepted by this version of the hosted demo.

## State, recovery and limits

Immutable artifacts pass SQLite checkpoints between jobs in the same workflow
run. No job waits on a model or broker lock during environment approval. Checkpoints
and candidates are retained for seven days; **model-config and credentials are
never uploaded**. These artifacts are not a production durable storage service.

One synthetic workflow runs at a time. Each model call is timeout-bounded;
each advance stops at the next gate and limits automatic critic revisions to two.
Failures preserve checkpoints/candidates using always-upload. No failed job
auto-replays PM decisions. Download the latest checkpoint into an access-controlled
local workspace, inspect status, explicitly retry or request changes, and continue
with Copilot CLI using the [technical reference](copilot-reference.md).
Do not blindly rerun a partly completed workflow or replace its
database with an older artifact.

If required-reviewer configuration is unavailable, the workflow cannot run
safely under this design. If model/auth flags differ for your chosen release,
use the local synthetic workflow and fix compatibility before hosted use.
The supplied Actions workflow is structurally reviewed/tested via local logic,
but has not been executed against configured hosted environments.

## What is still needed for event-driven customer use

GitHub Actions is the first-party execution host; skills are not webhook listeners.
For live event-triggered intake, separately implement/verify an authenticated source
system to GitHub event path, source-service noninteractive authorization, idempotent event
acceptance, approver identity/role checks and durable state beyond artifact retention.
Use read-only source tools, version/hash-bound approval artifacts, redaction, usage
limits and an operations/recovery runbook. Do not treat arbitrary issue comments
or labels as authenticated approvals.

External publishing requires a separate explicit authorization and tested
idempotency/ambiguous-write recovery. Final story approval does not itself
authorize issue creation in any tracker. No live connector or publisher is enabled here.

For a broader hosted agent implementation evaluate GitHub Agentic Workflows,
which GitHub recommends for automation rather than handwritten CLI jobs:

- [CLI with Actions](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/automate-with-actions)
- [Programmatic CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically)
- [GitHub Agentic Workflows](https://github.com/github/gh-aw)
