"""Przeglądarka wiedzy (tools/render_site.py): generuje się z repozytorium, linkuje znaczniki i nie zawiera tekstów źródeł."""
import importlib.util
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render_site", ROOT / "tools" / "render_site.py")
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)


class TestRenderSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = rs.build_data(ROOT)

    def test_every_skill_and_file_present(self):
        skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(sorted(self.data["skills"]), skills)
        for s in skills:
            refs = {p.name for p in (ROOT / "skills" / s / "references").glob("*.md")}
            self.assertEqual(set(self.data["skills"][s]["files"]), refs | {"SKILL.md"}, s)

    def test_tags_become_links_to_registered_sources(self):
        f = next(x for x in self.data["files"] if x["skill"] == "ev-ocpp-expert" and x["file"] == "SKILL.md")
        self.assertGreater(f["tags"], 0)
        self.assertEqual(f["html"].count('class="tag"'), f["tags"])
        for x in self.data["files"]:
            for d in x["docs"]:
                self.assertIn(d, self.data["sources"])

    def test_linker_and_markdown(self):
        lk = rs.Linker({"OCPI230": type("S", (), {"title": "OCPI"})()}, {"ev-x": ["SKILL.md", "a.md"]})
        h = rs.md_to_html("| A | B |\n|---|---|\n| `[OCPI230 §10.3.1]` | `references/a.md` |\n\n- **x** [OCPI230 §8]\n",
                          lk, "ev-x")
        self.assertIn('href="#/zrodlo/OCPI230"', h)
        self.assertIn('href="#/plik/ev-x/a.md"', h)
        self.assertIn("<strong>x</strong>", h)
        self.assertEqual(h.count('class="tag"'), 2)
        self.assertNotIn("<script", rs.md_to_html("<script>alert(1)</script>", lk, "ev-x"))

    def test_page_has_no_source_texts(self):
        page = rs.render(self.data)
        self.assertNotIn(".cache/ev-kb", page)
        self.assertNotIn("ev-kb-poufne", page)
        self.assertEqual(page.count("</script>"), 2)        # dane JSON nie mogą zamknąć znacznika <script>


if __name__ == "__main__":
    unittest.main()
