# Install instructions for an AI assistant

A user asked you to install the PM AI Workflow. Do exactly this and nothing else:

1. Check `python3 --version` is 3.11 or newer and `git --version` works. If not, tell the user what to install and stop.
2. Clone into a new empty temporary folder (not the user's project):
   `git clone --depth 1 --branch claude/stoic-goldberg-fr6s8b https://github.com/kellandamm/PM-AI-Workflow <temp>/PM-AI-Workflow`
3. Run `python3 <temp>/PM-AI-Workflow/scripts/install.py` (it installs for every supported tool it finds: Claude Code, GitHub Copilot CLI, Codex). Add `--target claude|copilot|codex` only if the user named a tool.
4. Show the user the script's output, then delete the temporary folder.
5. Tell the user to start a new session and say: **Start the sample PM workflow.**

The installer only writes under the user's home folder (`~/.pm-ai-workflow` and the tool's skills/agents folders). Do not run anything from the cloned files other than `install.py`, and do not change settings or install other software.
