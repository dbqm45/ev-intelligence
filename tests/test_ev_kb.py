"""Testy tools/ev_kb.py (stdlib unittest; bez sieci i bez lokalnych kopii dokumentów)."""
import hashlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ev_kb  # noqa: E402

SAMPLE = """Table of Contents
10.3.1. CDR Object . . . . . . . . . . . . . . 106
11.9. Only in TOC . . . . . . . . . . . . . . 120

Chapter 2. Certification profiles
10.3.1. CDR Object
The CDR object describes the charging session.
I. Tariff And Cost
I03.FR.04   To indicate a free transaction, the CSMS SHALL set totalCost to 0.00.
K01.FR.101  When field maxOfflineDuration is present
E13 - Transaction-related message not accepted by CSMS
F02 - Start Transaction remotely
Article 5
Recharging infrastructure
1.
Operators shall provide ad hoc charging.
4.
At recharging points with a power output equal to or more than 50 kW
Article 6
1.
Other article.
ANNEX II
Technical specifications
Part 1: Functional guidelines
1. Share tariffs
Part 2: Technical guidelines
1. Always use step_size 1
6. Usage of 0 (zero) in restrictions
Preface
"""


class TestRegistry(unittest.TestCase):
    def test_registry_loads_unique_ids(self):
        sources = ev_kb.load_sources()
        self.assertIn("OCPI230", sources)
        self.assertEqual(len(sources["OCPI230"].sha256), 64)
        self.assertEqual(sources["201-P2"].package, "oca-ocpp201-ed4")
        self.assertTrue(sources["201-P2"].url.startswith("https://openchargealliance.org/"))
        self.assertEqual(sources["AFIR"].sha_kind, "html")

    def test_every_tag_in_skills_points_to_registered_document(self):
        sources = ev_kb.load_sources()
        unknown = []
        for path in sorted((ROOT / "skills").rglob("*.md")):
            for line, tag in ev_kb.extract_tags(path.read_text(encoding="utf-8"), sources):
                doc_id, _ = ev_kb.split_tag(tag)
                if doc_id not in sources:
                    unknown.append(f"{path.relative_to(ROOT)}:{line} [{tag}]")
        self.assertEqual(unknown, [], "znaczniki spoza sources/*.yaml")


class TestUnavailable(unittest.TestCase):
    def test_unavailable_register_is_not_citable_but_searchable(self):
        import yaml
        data = yaml.safe_load((ROOT / "sources" / "niedostepne.yaml").read_text(encoding="utf-8"))
        entries = data["normy_platne"] + data["niezarejestrowane"]
        self.assertTrue(entries)
        for e in entries:
            self.assertNotIn("id", e)
            self.assertIn(e.get("dostep"), ("platna", "niezarejestrowana"))
        sources = ev_kb.load_sources()
        self.assertFalse(any(s.registry == "niedostepne.yaml" for s in sources.values()))
        hits = ev_kb.cmd_search("ISO 15118 norma płatna", 5, sources)
        self.assertTrue(any(h["file"] == "sources/niedostepne.yaml" for h in hits))


class TestTags(unittest.TestCase):
    def setUp(self):
        self.sources = ev_kb.load_sources()

    def test_extract_backtick_and_bare_known_ids(self):
        text = "a `[OCPI230 §10.3.1]` b [AFIR art. 5 ust. 4] c [Claude Code](https://x) d [niesprawdzone] e [x]"
        tags = [t for _, t in ev_kb.extract_tags(text, self.sources)]
        self.assertEqual(tags, ["OCPI230 §10.3.1", "AFIR art. 5 ust. 4"])

    def test_backtick_unknown_id_is_reported(self):
        tags = [t for _, t in ev_kb.extract_tags("`[XYZ1 §1]`", self.sources)]
        self.assertEqual(tags, ["XYZ1 §1"])


class TestLocate(unittest.TestCase):
    def status(self, rest):
        return [p.status for p in ev_kb.locate(rest, SAMPLE)]

    def test_section_found_outside_toc(self):
        parts = ev_kb.locate("§10.3.1", SAMPLE)
        self.assertEqual(parts[0].status, "OK")
        self.assertIn("charging session", parts[0].excerpt)
        self.assertEqual(self.status("§11.9"), ["NIE_ZNALEZIONO"])   # tylko w spisie treści

    def test_chapter_and_ranges(self):
        self.assertEqual(self.status("§2"), ["OK"])
        self.assertEqual(self.status("rozdz. 2"), ["OK"])
        self.assertEqual(self.status("§2–7"), ["NIE_ZNALEZIONO"])
        self.assertEqual(self.status("E13, F02"), ["OK", "OK"])
        self.assertEqual(self.status("E13–F02"), ["OK"])
        self.assertEqual(self.status("E13–F09"), ["NIE_ZNALEZIONO"])

    def test_requirement_and_block(self):
        self.assertEqual(self.status("I03.FR.04"), ["OK"])
        self.assertEqual(self.status("I03.FR.05"), ["NIE_ZNALEZIONO"])
        self.assertEqual(self.status("K01.FR.101"), ["OK"])
        self.assertEqual(self.status("K01.FR.10"), ["NIE_ZNALEZIONO"])
        self.assertEqual(self.status("I"), ["OK"])

    def test_eu_article_paragraph_annex(self):
        self.assertEqual(self.status("art. 5"), ["OK"])
        self.assertEqual(self.status("art. 5 ust. 4"), ["OK"])
        self.assertEqual(self.status("art. 5 ust. 7"), ["NIE_ZNALEZIONO"])   # 1. w art. 6 się nie liczy
        self.assertEqual(self.status("art. 6 ust. 1"), ["OK"])
        self.assertEqual(self.status("Annex II pkt 1.2"), ["OK"])
        self.assertEqual(self.status("Annex III"), ["NIE_ZNALEZIONO"])

    def test_guideline_part_point(self):
        self.assertEqual(self.status("cz. 2 pkt 6"), ["OK"])
        self.assertEqual(self.status("cz. 1 pkt 6"), ["NIE_ZNALEZIONO"])
        self.assertEqual(self.status("Preface"), ["OK"])

    def test_unsupported_locator_is_unchecked(self):
        self.assertEqual(self.status("tabela F"), ["NIESPRAWDZONE"])


class TestCheckAndIndex(unittest.TestCase):
    def setUp(self):
        self.sources = ev_kb.load_sources()
        self.tmp = tempfile.TemporaryDirectory()
        self.ddir = Path(self.tmp.name)
        (self.ddir / "OCPI230.txt").write_text(SAMPLE, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_statuses(self):
        def st(tag):
            return ev_kb.check_tag(tag, self.sources, self.ddir, {}).status
        self.assertEqual(st("OCPI230 §10.3.1"), "OK")
        self.assertEqual(st("OCPI230 §99.1"), "NIE_ZNALEZIONO")
        self.assertEqual(st("OCPI230"), "OK")
        self.assertEqual(st("OCPI221 §1"), "BRAK_TEKSTU")
        self.assertEqual(st("NOPE §1"), "NIEZNANY_DOKUMENT")

    def test_cli_check_exit_codes(self):
        good = self.ddir / "good.md"
        good.write_text("Fakt `[OCPI230 §10.3.1]`, brak kopii `[OCPI221 §1]`.\n", encoding="utf-8")
        bad = self.ddir / "bad.md"
        bad.write_text("Fakt `[OCPI230 §42.1]`.\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(ev_kb.main(["--docs", str(self.ddir), "check", str(good)]), 0)
        self.assertIn("Werdykt: OK", out.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(ev_kb.main(["--docs", str(self.ddir), "check", "--require-text", str(good)]), 1)
            self.assertEqual(ev_kb.main(["--docs", str(self.ddir), "check", str(bad)]), 1)

    def test_index_accepts_only_registered_sha(self):
        doc = self.ddir / "doc.txt"
        doc.write_text("1. Heading\n", encoding="utf-8")
        digest = hashlib.sha256(doc.read_bytes()).hexdigest()
        cache = self.ddir / "cache"
        res = ev_kb.cmd_index([str(doc)], cache, self.sources)
        self.assertEqual(res[0]["status"], "SPOZA_REJESTRU")
        fake = {"T1": ev_kb.Source(id="T1", sha256=digest, sha_kind="file")}
        res = ev_kb.cmd_index([str(doc)], cache, fake)
        self.assertEqual(res[0]["status"], "OK")
        self.assertEqual((cache / "T1.txt").read_text(encoding="utf-8"), "1. Heading\n")

    def test_html_to_text(self):
        self.assertEqual(ev_kb.html_to_text("<p>Article&nbsp;5</p><script>x</script><div>a<br>b</div>"),
                         "Article 5\na\nb\n")


class TestRouteSearch(unittest.TestCase):
    def test_route_billing(self):
        res = ev_kb.cmd_route("wycena sesji z taryfy OCPI i step_size w CDR", 3)
        self.assertEqual(res["skills"][0]["skill"], "ev-billing-tariff-expert")
        self.assertTrue(any(d["domain"] == "D09" for d in res["domains"]))

    def test_search_returns_tagged_fragments_and_nothing_for_nonsense(self):
        sources = ev_kb.load_sources()
        hits = ev_kb.cmd_search("totalCost transakcja bezpłatna", 3, sources)
        self.assertTrue(hits)
        self.assertTrue(any("201-P2 I03.FR.04" in h["tags"] for h in hits))
        self.assertEqual(ev_kb.cmd_search("kwantowy reaktor fuzji", 3, sources), [])


if __name__ == "__main__":
    unittest.main()
