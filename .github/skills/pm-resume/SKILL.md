---
name: pm-resume
description: Continue a saved PM request from where you left off.
---

For "Resume my request", list saved requests and ask which one if needed.
Use the commands in `docs/copilot-reference.md` yourself. Read helper status.
Missing or hash-invalid state is an error,
not permission to recreate work. Present the actual stage/gate/revision.
For pending approval use pm-refine and wait for an explicit decision. Failed runs
need inspection and explicit retry before model work. Running runs may continue
with pm-refine when requested. Stopped runs are terminal; completed runs need
only pm-handoff. New sources/context require a new versioned request key and
new context approval. Do not imply session history replaces the checkpoint store.
Do not silently reset decisions.
Explain the next action in plain language. Do not ask the user to locate run
IDs or rewrite saved input files.
