---
name: pm-resume
description: Resume PM work from verified checkpoints rather than conversational memory.
---

Read the guide and helper status. Missing or hash-invalid state is an error,
not permission to recreate work. Present the actual stage/gate/revision.
For pending approval use pm-refine and wait for an explicit decision. Failed runs
need inspection and explicit retry before model work. Running runs may continue
with pm-refine when requested. Stopped runs are terminal; completed runs need
only pm-handoff. New sources/context require a new versioned request key and
new context approval. Do not imply session history replaces the checkpoint store.
Do not migrate remote Foundry response IDs or silently reset decisions.
