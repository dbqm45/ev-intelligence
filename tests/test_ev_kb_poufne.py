"""Testy źródeł poufnych (tools/ev_kb_poufne.py): werdykt bez treści, limity, izolacja od rejestru cytowalnego."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ev_kb  # noqa: E402
import ev_kb_poufne as P  # noqa: E402

SECRET = "Message SecretOperation_X carries field hiddenFieldAlpha with value GammaMode.\n"


class TestConfidential(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sources" / "poufne").mkdir(parents=True)
        src = self.root / "doc.txt"
        src.write_text(SECRET, encoding="utf-8")
        sha = ev_kb.sha256_file(src)
        (self.root / "sources" / "poufne" / "test.yaml").write_text(
            f"source: testproto\nklucze: [testproto]\nlicence: poufna\naccess_url: https://example.org/download\n"
            f"documents:\n  - id: TP-1\n    title: Test protocol\n    sha256: {sha}\n", encoding="utf-8")
        os.environ["EV_KB_POUFNE"] = str(self.root / "cache")
        self.assertEqual(P.cmd_index([str(src)], self.root)[0]["status"], "OK")

    def tearDown(self):
        os.environ.pop("EV_KB_POUFNE", None)
        self.tmp.cleanup()

    def test_verdict_without_content(self):
        r = P.verify(["SecretOperation_X", "hiddenFieldAlpha", "NoSuchThing"], "testproto", self.root, limiter=None)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(r["results"], {"SecretOperation_X": "WYSTEPUJE", "hiddenFieldAlpha": "WYSTEPUJE",
                                        "NoSuchThing": "NIE_WYSTEPUJE"})
        dumped = repr(r)
        self.assertNotIn("GammaMode", dumped)        # treść spoza zapytania nie wycieka
        self.assertNotIn("carries", dumped)
        self.assertIn("https://example.org/download", r["notice"])

    def test_limits(self):
        self.assertEqual(P.verify([f"t{i:03d}" for i in range(11)], "testproto", self.root, limiter=None)["status"],
                         "ZLE_ZAPYTANIE")
        self.assertEqual(P.verify(["ab"], "testproto", self.root, limiter=None)["status"], "ZLE_ZAPYTANIE")
        self.assertEqual(P.verify(["x.*"], "testproto", self.root, limiter=None)["status"], "ZLE_ZAPYTANIE")
        lim = P._RateLimiter(3)
        self.assertEqual(P.verify(["aaa", "bbb", "ccc"], "testproto", self.root, limiter=lim)["status"], "OK")
        self.assertEqual(P.verify(["ddd"], "testproto", self.root, limiter=lim)["status"], "LIMIT")

    def test_unknown_source(self):
        self.assertEqual(P.verify(["aaa"], "inne", self.root, limiter=None)["status"], "NIEZNANE_ZRODLO")

    def test_confidential_ids_are_not_citable(self):
        sources = ev_kb.load_sources(ROOT)
        for d in P.load_confidential(ROOT):
            self.assertNotIn(d["id"], sources)

    def test_no_skill_cites_confidential_ids(self):
        ids = {d["id"] for d in P.load_confidential(ROOT)}
        for path in (ROOT / "skills").rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for i in ids:
                self.assertNotIn(i, text, f"{path} wymienia poufne źródło {i}")


if __name__ == "__main__":
    unittest.main()
