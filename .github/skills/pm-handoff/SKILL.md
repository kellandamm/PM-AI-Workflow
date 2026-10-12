---
name: pm-handoff
description: Export final-approved PM stories and history without creating external issues.
---

Inspect helper status and confirm completed/final PM approval.
Run export --run <id> --output .pm-work\<new-directory> with the guide's setup.
The helper revalidates all stories, scope and quotes, refuses preapproval exports,
and writes stories.md, stories.json and review.json to a new directory.
Show output paths and accepted critic findings. Keep outputs
gitignored; no automatic commit, upload, Jira creation or PR. Handoff is not delivery.
