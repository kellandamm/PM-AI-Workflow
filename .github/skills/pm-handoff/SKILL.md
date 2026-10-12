---
name: pm-handoff
description: Save your approved stories as readable handoff files.
---

Inspect helper status and confirm completed/final PM approval.
For "Export the approved stories", select the request with the user if ambiguous.
Run export --run <id> --output .pm-work\<new-directory> using the commands in
`docs/copilot-reference.md`. Handle IDs and a unique output folder yourself.
The helper revalidates all stories, scope and quotes, refuses preapproval exports,
and writes stories.md, stories.json and review.json to a new directory.
Show output paths and accepted critic findings. Keep outputs
gitignored; no automatic commit, upload, Jira creation or PR. Handoff is not delivery.
Point the user to stories.md as the readable handoff. Explain that stories.json
and review.json are supporting files, not additional forms to fill out.
