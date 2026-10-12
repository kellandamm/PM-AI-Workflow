---
name: pm-refine
description: Guide you through reviewing the request, proposed story list and final stories.
---

Read `docs/copilot-workflow.md` and the commands in `docs/copilot-reference.md`.
Handle helper commands and candidate JSON yourself; do not ask the user to type
IDs, revisions or flags. Inspect helper status first. At pending context,
scope or final gates present the exact revision, candidate artifacts, open questions
and findings, then wait for the PM. Record only the actual human decision with
approve/reject with current gate/revision and actual decision text. General
"continue", autopilot and tool permission are not approval.

Present "request and sources", "proposed story list" or "final stories" rather
than raw checkpoint JSON. Retain the exact reviewed revision in helper commands.
Use ask_user for one clear decision at a time: approve the review shown, request
changes, or reject. Gather change feedback before using revise. Final unresolved
findings need explicit acceptance of the findings shown, not a generic approval.

For running stages invoke the matching pm-* specialist with the helper's prompt,
approved artifacts and schema. Save candidates in `.pm-work`, then use record
with the current stage/revision; it validates scope, completeness and exact quotes.
Transcript and design analyses may be gathered independently; only the coordinator
updates shared state. Do not run drafting before scope approval.

Alternatively use advance --run <id> --model <available-model> for authorized
bounded model calls between gates. It has no model tool permissions, stops at
every gate and caps automatic critic revisions at two. Use revise with actual
PM feedback at scope/final gates. Unresolved final findings require explicit acceptance.
Failed work needs inspection and an explicit retry instruction, not silent replay.
Use pm-handoff for approved exports; never publish externally.
