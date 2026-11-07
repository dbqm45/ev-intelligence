"""Testy wydań (docs/RELEASING.md): Conventional Commits → SemVer → wpis CHANGELOG i pełny przebieg scripts/release.py
w tymczasowym repozytorium git. Na podstawie tests/test_release.py z tf (MIT)."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cc = load(SCRIPTS / "conventional.py", "conventional")
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
       "PYTHONDONTWRITEBYTECODE": "1"}


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=ENV).stdout


class TestConventional(unittest.TestCase):
    def test_lint(self):
        for ok in ["feat(ocpi): add OICP 2.3 reference", "fix: drop empty answer", "feat(mcp)!: rename tool",
                   "chore(release): 0.2.0", "docs: describe releases\n\nWhy.\n\nRefs: #3", "Merge branch 'main'"]:
            self.assertEqual(cc.lint_message(ok), [], ok)
        for bad, why in [("Dodaj OICP", "<typ>"), ("feature: x", "nieznany typ"), ("feat(OCPI): x", "zakres"),
                         ("fix: x.", "kropk"), (f"feat: {'x' * 73}", "73 znaki"), ("fix: a\nbody", "pustą linię")]:
            self.assertIn(why, "\n".join(cc.lint_message(bad)), bad)

    def test_bump(self):
        self.assertIsNone(cc.bump_kind(["docs: a", "test: b", "chore: c"]))
        self.assertEqual(cc.bump_kind(["fix: a"]), "patch")
        self.assertEqual(cc.bump_kind(["fix: a", "feat: b"]), "minor")
        self.assertEqual(cc.bump_kind(["refactor: a\n\nBREAKING CHANGE: gone"]), "major")
        self.assertEqual(cc.next_version("0.1.0", "minor"), "0.1.1")      # faza 0.y.z: feat → patch
        self.assertEqual(cc.next_version("0.1.0", "major"), "0.2.0")      # zmiana niezgodna → minor
        self.assertEqual(cc.next_version("1.4.2", "minor"), "1.5.0")

    def test_changelog_entry(self):
        e = cc.changelog_entry("0.2.0", "2026-11-08", ["feat(ocpi): add OICP (#4)", "fix(sources): fix SHA", "docs: x"])
        self.assertEqual(e, "## [0.2.0] — 2026-11-08\n### Added\n- **ocpi:** add OICP (#4)\n"
                            "### Fixed\n- **sources:** fix SHA\n")

    def test_repo_changelog_has_current_version(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertTrue(cc.is_release(version))
        self.assertIsNotNone(cc.release_notes((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version))


class TestReleaseE2E(unittest.TestCase):
    def run_script(self, repo, script, *args):
        return subprocess.run([sys.executable, str(repo / "scripts" / script), *args], cwd=repo, capture_output=True,
                              text=True, timeout=60, env=ENV)

    def test_release_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            shutil.copytree(SCRIPTS, repo / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
            (repo / "VERSION").write_text("0.1.0\n", encoding="utf-8")
            (repo / "CHANGELOG.md").write_text("# Changes\n\n## [0.1.0] — 2026-11-07\n### Added\n- x\n", encoding="utf-8")
            git(repo, "init", "-q", "-b", "main")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "chore(release): 0.1.0")
            r = self.run_script(repo, "release.py", "--dry-run")
            self.assertEqual(r.returncode, 1)
            self.assertIn("v0.1.0", r.stderr)                  # pierwszy tag tworzy workflow
            git(repo, "tag", "-a", "v0.1.0", "-m", "Release 0.1.0")
            git(repo, "commit", "-q", "--allow-empty", "-m", "docs: readme")
            r = self.run_script(repo, "release.py", "--ci")
            self.assertEqual(r.returncode, 0)
            self.assertIn("nic do wydania", r.stdout)
            git(repo, "commit", "-q", "--allow-empty", "-m", "feat(ocpi): add OCHP reference")
            r = self.run_script(repo, "release.py", "--ci")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((repo / "VERSION").read_text(), "0.1.1\n")
            log = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertTrue(log.startswith("# Changes\n\n## [0.1.1] — "))
            self.assertIn("- **ocpi:** add OCHP reference", log)
            r = self.run_script(repo, "release_notes.py", "0.1.1")
            self.assertEqual(r.returncode, 0)
            self.assertTrue(r.stdout.startswith("### Added"))

    def test_hook_is_executable(self):
        hook = ROOT / ".githooks" / "commit-msg"
        self.assertTrue(hook.exists() and os.access(hook, os.X_OK))


if __name__ == "__main__":
    unittest.main()
