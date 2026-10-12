---
name: pm-refine
description: Coordinate PM story analysis, full drafting, bounded critic revisions and three explicit approvals.
---

Read `docs/copilot-workflow.md`. Inspect helper status first. At pending context,
scope or final gates present the exact revision, candidate artifacts, open questions
and findings, then wait for the PM. Record only the actual human decision with
approve/reject with current gate/revision and actual decision text. General
"continue", autopilot and tool permission are not approval.

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
