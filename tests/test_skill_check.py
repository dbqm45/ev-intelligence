"""Testy bramki tools/skill_check.py (bez uruchamiania całej bramki, żeby nie wywołać testów rekurencyjnie)."""
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill_check as sc  # noqa: E402


class TestSkillCheck(unittest.TestCase):
    def test_all_skills_pass_structure_and_scenarios(self):
        names = sorted(p.parent.name for p in sc.SKILLS.glob("*/SKILL.md"))
        self.assertTrue(names)
        for n in names:
            self.assertEqual(sc.check_structure(n), [], n)
            self.assertEqual(sc.check_scenarios(n, set(names)), [], n)

    def test_frontmatter_parse(self):
        fm, body = sc.frontmatter("---\nname: ev-x\n---\n# T\n")
        self.assertEqual(fm, {"name": "ev-x"})
        self.assertEqual(body, "# T\n")
        self.assertEqual(sc.frontmatter("bez")[0], {})

    def test_fingerprint_is_stable(self):
        self.assertEqual(sc.fingerprint("ev-ocpp-expert"), sc.fingerprint("ev-ocpp-expert"))


if __name__ == "__main__":
    unittest.main()
