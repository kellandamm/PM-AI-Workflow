import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pm_launcher", ROOT / "scripts" / "start_pm.py")
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.python = self.root / ".venv-copilot" / (
            "Scripts/python.exe" if os.name == "nt" else "bin/python"
        )

    def make_environment(self, *args, **kwargs):
        self.python.parent.mkdir(parents=True)
        self.python.touch()

    def test_first_setup_creates_environment_and_installs_missing_dependency(self):
        with patch.object(launcher.venv, "create", side_effect=self.make_environment) as create, \
                patch.object(launcher.subprocess, "run", side_effect=[
                    subprocess.CompletedProcess([], 1, "", "Package not found"),
                    subprocess.CompletedProcess([], 0),
                ]) as run:
            self.assertEqual(launcher.prepare(self.root), self.python)
            create.assert_called_once_with(self.root / ".venv-copilot", with_pip=True)
            self.assertEqual(run.call_count, 2)
            self.assertIn(str(self.root / "requirements-copilot.txt"), run.call_args.args[0])
            self.assertTrue(run.call_args.kwargs["check"])

    def test_repeat_setup_preserves_existing_environment(self):
        self.make_environment()
        with patch.object(launcher.venv, "create") as create, \
                patch.object(launcher.subprocess, "run",
                             return_value=subprocess.CompletedProcess([], 0)) as run:
            self.assertEqual(launcher.prepare(self.root), self.python)
            create.assert_not_called()
            self.assertEqual(run.call_count, 1)

    def test_incomplete_environment_fails_without_replacing_it(self):
        self.python.parent.mkdir(parents=True)
        with patch.object(launcher.venv, "create") as create:
            with self.assertRaisesRegex(RuntimeError, "incomplete"):
                launcher.prepare(self.root)
            create.assert_not_called()

    def test_missing_copilot_reports_failure_before_setup(self):
        with patch.object(launcher.shutil, "which", return_value=None), \
                patch.object(launcher, "prepare") as prepare:
            self.assertEqual(launcher.main([]), 1)
            prepare.assert_not_called()

    def test_setup_only_does_not_launch_copilot(self):
        with patch.object(launcher.shutil, "which", return_value=None), \
                patch.object(launcher, "prepare", return_value=self.python), \
                patch.object(launcher.subprocess, "run") as run:
            self.assertEqual(launcher.main(["--setup-only"]), 0)
            run.assert_not_called()

    def test_launch_sets_repository_context_and_preserves_exit_code(self):
        with patch.object(launcher, "ROOT", self.root), \
                patch.object(launcher.shutil, "which", return_value="copilot"), \
                patch.object(launcher, "prepare", return_value=self.python), \
                patch.object(launcher.subprocess, "run",
                             return_value=subprocess.CompletedProcess([], 7)) as run:
            self.assertEqual(launcher.main([]), 7)
            self.assertEqual(run.call_args.args[0], ["copilot"])
            self.assertEqual(run.call_args.kwargs["cwd"], self.root)
            self.assertEqual(run.call_args.kwargs["env"]["PYTHONPATH"], str(self.root / "src"))

    def test_install_failure_is_reported(self):
        with patch.object(launcher.shutil, "which", return_value="copilot"), \
                patch.object(launcher, "prepare",
                             side_effect=subprocess.CalledProcessError(1, ["pip", "install"])):
            self.assertEqual(launcher.main([]), 1)


if __name__ == "__main__":
    unittest.main()
