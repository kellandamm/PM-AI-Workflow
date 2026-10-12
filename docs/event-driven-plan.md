# Event-driven PM workflow: implementation plan

## Outcome and current status

A request marked ready in an approved source system starts the PM workflow
automatically. The PM reviews the request and sources, proposed story list and
final stories in GitHub. Agents work between reviews; they never approve them.
Approved stories are saved as a handoff.

**Prepared in this repository:** skills, agent profiles, local checkpoint
validation, three approval gates, bounded agent work, local exports and a
protected synthetic Actions example.

**Still to build:** live webhook intake, unattended source collection, shared
durable storage, trusted approval identity records, a live Actions adapter,
operational controls and end-to-end integration tests. No services, permissions,
credentials or live workflows are provisioned by this document.

## First pilot scope

Start with one source system, one project and one event: a request moves to an
agreed "ready for refinement" state. The source can be an issue tracker, intake
form or another system with a supported webhook.

Collect the three required source categories: design/flow notes, meeting
decisions and product requirements. Use supported read APIs or approved exports;
interactive MCP sign-in alone does not establish unattended access. Missing
sources pause collection with a visible error, not fabricated evidence.

Keep the first pilot export-only. Add more connectors and publishing only after
the pilot meets the launch criteria. Keep the synthetic walkthrough unchanged.

## Target process

1. The source sends a ready event to an HTTPS intake service.
2. The service verifies the sender, allowed project and event, then durably
   records receipt and queues collection. It acknowledges only after persistence.
3. A collector reads the allowed sources, records their versions and provenance,
   validates/redacts them and saves an immutable input snapshot.
4. A durable outbox requests a GitHub Actions run with an opaque request reference,
   not source content or credentials. Dispatch failure is retried without
   creating another logical request.
5. Actions authenticates to the state service, loads the exact saved request and
   exposes its context review. No model work starts before PM context approval.
6. After approval, agents analyze and propose scope, then pause for scope review.
7. After scope approval, agents draft, review edge cases and critique, then pause
   for final review. At most two automatic critic revision rounds run.
8. Authorized final approval saves a durable handoff. Unresolved findings require
   changes or explicit, recorded acceptance through a trusted decision path.

Use `repository_dispatch` with a fixed event type such as `pm_request_ready`.
The workflow must exist on the default branch. A dispatch reference is a lookup
key, **not authorization**: Actions must verify its repository/organization
binding and retrieve it from the configured state service.

Do not accept source-provided shell commands, models, repository destinations,
workflow refs or arbitrary URLs. Execute reviewed code from a protected,
approved revision; pin runtime and action dependencies. Never interpolate
untrusted source content into shell commands.

## Administrator checklist

Complete this with the product owner and implementation team. Store decisions
in an approved internal location, not credentials or proprietary data in Git.

| Decision or setup | Owner | Required information |
| --- | --- | --- |
| Pilot source | Product owner | Source system, allowed project, ready-state rule, request owner and source categories. |
| Data approval | Data/security owner | Allowed content, exclusions, processing location, model/vendor policies and retention. |
| Reviewers | PM lead | Who may approve each gate, reject or request changes; whether multiple approvals are required. |
| GitHub repository | Repository admin | Approved private repository, protected default branch, trusted workflow editors and Actions policy. |
| GitHub plan | Repository admin | Verify required-reviewer protection works for the repository visibility and plan; fail closed if unavailable. |
| Intake hosting | Platform owner | Approved HTTPS host, durable queue/outbox, state database, object storage and operating owner. |
| Source credentials | Source admin | Supported noninteractive read identity, allowed projects/documents, expiry and rotation owner. |
| Dispatch identity | GitHub admin | Repository-scoped app installation or other approved identity with the minimum endpoint permissions. |
| Runner identity | Platform admin | Short-lived identity, preferably OIDC where supported, with request-scoped state access. |
| Copilot runtime | GitHub admin | Allowed model, exact CLI version, supported authentication, usage billing and policy. |
| Review environments | Repository admin | `pm-context`, `pm-scope`, `pm-final`, allowed reviewers, prevent-self-review and bypass controls where supported. |
| Limits | Operations/product owners | Numeric per-request/day budgets, payload/source sizes, concurrency, retry limits and approval expiry. |
| Recovery | Operations owner | Alert destination, on-call owner, backup/restore targets, dead-letter review and stop switch. |

The current synthetic adapter expects `PM_COPILOT_TOKEN`. For a new live workflow,
evaluate GitHub's organization-enabled `GITHUB_TOKEN` Copilot authentication or
an approved supported credential. Do not change authentication based on an
assumption that an organization policy is enabled. Dispatch, source reads,
Copilot use and state access are separate permissions.

## Implementation order

### 1. Agree the contract and hosting

Choose the pilot source, host and storage services before writing deployment
files. Prefer existing approved infrastructure. Use a managed database and
versioned object storage for live runs; the current local SQLite database remains
for individual use. Do not put a shared SQLite file on a network drive.

Define an event envelope with schema version, source/project ID, event ID,
request ID, source revision and occurrence/receipt times. Resolve organization
identity from the authenticated sender configuration, not an untrusted payload.
Dispatch only an opaque receipt ID and contract version.

Define source snapshots using the existing intake schema. Make `request_key`
organization/source/project/request/version-qualified. Keep all three source
slots and their provenance; record hashes before any approval.

### 2. Build authenticated intake and collection

Implement provider-supported signature verification over the raw body, replay
controls using delivery IDs/timestamps where available, body limits and source
allowlists. If the provider lacks signed webhooks, select its supported secure
alternative and document the threat model before enabling it.

Use an atomic unique receipt key for organization/source/event ID. Also deduplicate
logical work by source request and collected version/hash, since different events
can describe the same request. Reject conflicting reused event IDs. Never drop a
new request revision as a duplicate: collect it and require fresh approvals.

Commit receipt and outbox intent transactionally. Collection retries must be
bounded, with backoff and a dead-letter queue. Restrict linked-document hosts,
redirects and network access to prevent arbitrary URL retrieval. A denied source
must stay denied; report it rather than trying another identity.

### 3. Add durable state and worker recovery

Implement a store adapter with the existing optimistic revision semantics.
Use atomic compare-and-swap updates, immutable source/artifact versions and
an append-only audit trail. Store approver identity and access context separately
from model-generated content. Hashes detect changes but do not replace access
control or protect against administrators rewriting all records.

Use a per-request worker lease with expiry/fencing and conditional state writes.
GitHub concurrency groups are an extra limit, not the durable lock or queue.
Allow independent requests to proceed without overlapping work on the same one.

Record stage attempt IDs and persisted candidate references. After a crash,
reconcile state before retry: do not replay decisions or blindly repeat a model
call whose result may already exist. Durable storage, not Actions artifacts, is
the source of truth. Enforce retention and deletion across snapshots, sessions,
candidates, backups and exports according to the approved policy.

### 4. Build the live Actions and decision adapters

Add a separate workflow, proposed name `copilot-pm-live.yml`, and a live adapter;
do not remove the synthetic-only checks in `copilot_actions_stage.py`.
Fetch inputs from the state service, verify request access/version and pass only
validated sources to the existing tool-disabled runner. Apply timeouts and quotas.

Before each review, freeze an approval manifest containing request ID, gate,
revision, source hash, artifact hashes, expiry and trusted code/runtime version.
Make readable review content accessible only to authorized reviewers. Keep raw
customer content out of repository logs, dispatch payloads and public summaries.

Environment approval is an execution barrier, not a complete PM audit record.
Retrieve verified reviewer evidence through supported GitHub deployment/review
APIs and bind it to the manifest. `github.actor` alone identifies the workflow
initiator, not necessarily the approver. If reviewer evidence cannot be obtained,
fail closed and use a separately authenticated decision service.

Implement approve/reject/revise using the actual authorized human's identity,
decision text, gate and reviewed revision. Do not derive these from arbitrary
comments, labels or model output. A changed/expired manifest requires fresh
review. Revalidate reviewer membership at decision time. GitHub environments
may allow one of several listed reviewers; do not imply multi-party quorum
unless implemented and tested separately.

For changes/rejections, provide a documented authenticated decision path in
GitHub or an approved service before rollout. Environment approval alone cannot
capture revision feedback or explicit unresolved-finding acceptance.

### 5. Add operations and rehearse

Provide authorized pause-intake and pause-agent controls, sanitized alerts,
receipt-to-request-to-Actions correlation IDs, approval reminders and quota
tracking. Enforce numeric limits before calls; do not merely display usage after
the budget is exceeded.

Run synthetic events through the actual receiver and approved test connectors,
then a small authorized pilot. Test backup restoration and credential rotation.
Only enable the live source webhook after acceptance and operating ownership.

Evaluate [GitHub Agentic Workflows](https://github.com/github/gh-aw) during the
host-selection phase. GitHub recommends it for most automation use cases.
It may supply orchestration guardrails but does not automatically implement these
source contracts, durable state, PM decisions or customer access boundaries.
Keep the existing runner until a replacement demonstrates equivalent controls.

## Launch criteria

| Test | Required result |
| --- | --- |
| Invalid sender/signature, expired replay, disallowed source | Rejected with sanitized audit record; no collection or model call. |
| Duplicate events and uncertain dispatch response | One logical saved request; safe outbox reconciliation. |
| Two workers or stale state update | At most one active lease; losing worker cannot commit. |
| Changed source or approval manifest | New version or invalidated gate; prior approval cannot authorize changed content. |
| Missing, denied or unsafe linked source | Visible collection failure; no fabricated evidence or arbitrary network fetch. |
| Prompt injection in sources | No tools, approvals, code execution or source writes authorized by that text. |
| Unauthorized reviewer or forged comment | Decision rejected; state unchanged. |
| Approval, rejection and requested revision | Verified actor and exact revision recorded; subsequent work follows the correct gate. |
| Final unresolved findings | Export blocked unless explicitly accepted by an authorized PM using the trusted decision path. |
| Crash before/after stage commit; credential expiry | Saved work recoverable; no automatic replay of PM decisions. |
| Quota exhaustion or pause switch | New model work stops; status explains the reason. |
| Artifact expiry and backup restoration | Full request, sources, decisions and handoff recover from durable storage. |
| Data isolation and logs | Another organization's references are denied; no source text/tokens in public output. |
| Live model rehearsal | Schema-valid output, all three gates, restart and final export observed with authorized runtime. |

## Operations runbook to complete before launch

**Intake failure:** verify delivery ID and sender configuration, inspect the
sanitized reason, then replay from the durable receipt/dead-letter tooling.
Do not resubmit the same event with a new identity to bypass rejection.

**Collection failure:** restore authorized read access or correct the source,
then retry collection. Changed content creates a new version and fresh review.

**Agent failure:** inspect saved status and candidate, resolve the cause, acquire
a new worker lease and explicitly retry the failed stage only.

**Review timeout or stale decision:** expire the manifest, notify the PM and
prepare a new review. Never approve on a timer.

**Incident or cost spike:** pause intake/agent work, preserve access-controlled
audit evidence, rotate affected credentials and reconcile receipts/state before
resuming. Stop external writes separately if a publisher exists.

**Restore:** restore database and objects consistently, verify hashes/versions
and audit records, invalidate old leases/manifests and reconcile queued work
before reopening processing.

## Optional publishing phase

Keep publishing disabled in the pilot. Later, an authorized PM must review the
exact destination, issue type, field mapping and payload, then approve publishing
separately from story approval.

Use a stable publishing intent key per request/version/story/destination and
store the confirmed external issue IDs. If a write times out, look up/reconcile
the intent before retrying; if the provider cannot safely reconcile it, pause
for operator review rather than creating a duplicate. Test partial success,
changed payloads, revoked permissions and duplicate delivery.

## Official references

- [External workflow triggers](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#repository_dispatch)
- [Repository dispatch API](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)
- [Environment protection](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
- [Copilot CLI with Actions](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/automate-with-actions)
- [Organization Copilot authentication](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-in-actions)
- [GitHub Agentic Workflows](https://github.com/github/gh-aw)
