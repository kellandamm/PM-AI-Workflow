from importlib import util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = util.spec_from_file_location("pm_install", ROOT / "scripts" / "install.py")
installer = util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_installs_every_target_with_rewritten_paths(self):
        self.assertEqual(installer.main(["--target", "all", "--home", str(self.home)]), 0)
        root = self.home / ".pm-ai-workflow"
        self.assertTrue((root / "scripts" / "pm.py").is_file())
        for path in [self.home / ".claude/skills/pm-intake/SKILL.md",
                     self.home / ".claude/agents/pm-coordinator.md",
                     self.home / ".copilot/skills/pm-intake/SKILL.md",
                     self.home / ".copilot/agents/pm-coordinator.agent.md",
                     self.home / ".agents/skills/pm-intake/SKILL.md",
                     self.home / ".agents/skills/pm-coordinator/SKILL.md"]:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", text, path)
        self.assertIn(str(root), (self.home / ".claude/skills/pm-intake/SKILL.md").read_text())

    def test_copilot_agent_uses_copilot_tool_names(self):
        installer.main(["--target", "copilot", "--home", str(self.home)])
        text = (self.home / ".copilot/agents/pm-coordinator.agent.md").read_text()
        self.assertIn('tools: ["read", "search", "edit", "execute", "agent", "skill", "ask_user"]', text)
        self.assertNotIn("AskUserQuestion", text)
        self.assertFalse((self.home / ".claude").exists())

    def test_dry_run_writes_nothing(self):
        installer.main(["--target", "all", "--dry-run", "--home", str(self.home)])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_uninstall_removes_only_installed_files(self):
        other = self.home / ".claude/skills/mine/SKILL.md"
        other.parent.mkdir(parents=True)
        other.write_text("keep")
        installer.main(["--target", "all", "--home", str(self.home)])
        installer.main(["--uninstall", "--home", str(self.home)])
        self.assertTrue(other.is_file())
        self.assertFalse((self.home / ".pm-ai-workflow").exists())
        self.assertFalse((self.home / ".claude/skills/pm-intake").exists())


if __name__ == "__main__":
    unittest.main()
