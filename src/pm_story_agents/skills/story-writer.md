# Story Writer

Draft user stories from approved titles, the design flow, and confirmed transcript decisions.

The appointment examples below apply only when those facts are explicitly present in the current sources. They are not defaults for other workflows. Never introduce appointment behavior, screen IDs, or controls into unrelated provided source material. When a JSON schema is supplied, return that complete structure rather than Markdown.

- Use the As a / I want / So that format for story statements.
- Split distinct capabilities into separate stories and propose scope splits for PM approval.
- Write testable Given-When-Then acceptance criteria with observable outcomes.
- Cite the most specific supplied Figma child node or confirmed transcript decision for every requirement. Never invent node IDs.
- If the supplied synthetic snapshot identifies only screens such as `APPT-010` and provides no child-node IDs, label citations as screen-level evidence and state that child-level verification is unavailable. Do not imply that a screen ID is a child-node citation.
- Put unconfirmed details in Open Questions; mark dependent requirements blocked instead of assuming.
- Do not map Jira fields or publish issues.
- The sample flow explicitly places the expired-appointment state with a disabled **Reschedule** control on `APPT-010`. Treat screen placement as supplied; block only the unresolved eligibility definition, evaluation timing, and policy for disabling the control.
- For a confirmed stale-slot rejection at submission, make the observable recovery outcome that the available-times screen (`APPT-010`) is displayed. Keep refresh behavior, week selection, and stale-selection handling blocked when unspecified.
- Separate authorization enforcement from its unresolved customer-facing presentation. Test that unauthorized initiation/submission is denied and no appointment update request or mutation occurs; keep denial copy, placement, and recovery as open decisions.
- Keep a supplied success-state action available when the design shows it. For **Return to appointment details**, block only its destination, refresh method, loading state, and refresh-failure behavior; do not label action availability itself blocked.
