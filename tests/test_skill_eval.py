"""Testy runnera ewaluacji (tools/skill_eval.py) z atrapą klienta — bez API i bez kosztów."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill_eval as se  # noqa: E402


class FakeMessages:
    def __init__(self, route_to, answer):
        self.route_to, self.answer, self.calls = route_to, answer, []

    def create(self, **kw):
        self.calls.append(kw)
        usage = NS(input_tokens=1000, output_tokens=100, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        if "output_config" in kw and "format" in kw["output_config"]:
            text = json.dumps({"skill": self.route_to})
        else:
            text = self.answer
        return NS(content=[NS(type="text", text=text)], stop_reason="end_turn", usage=usage)


class TestSkillEval(unittest.TestCase):
    def runner(self, route_to, answer, budget=10.0):
        client = NS(messages=FakeMessages(route_to, answer))
        return se.Runner(client, "claude-haiku-5-5", budget), client.messages

    def test_grade(self):
        checks = {"all": [["kWh"], ["minut\\w*", "czas"]], "none": ["nie wymaga"]}
        self.assertTrue(se.grade("Cena za kWh i za minutę.", checks)["ok"])
        g = se.grade("Cena za kWh. AFIR nie wymaga.", checks)
        self.assertEqual(g["missing"], [["minut\\w*", "czas"]])
        self.assertEqual(g["forbidden"], ["nie wymaga"])

    def test_trigger_and_no_trigger(self):
        items = [("ev-ocpp-expert", {"id": "t1", "expect": "trigger", "prompt": "p",
                                      "checks": {"all": [["Heartbeat"]]}}),
                 ("ev-ocpp-expert", {"id": "n1", "expect": "no-trigger", "neighbor": "ev-ocpi-roaming-expert",
                                      "prompt": "q"})]
        r, msgs = self.runner("ev-ocpp-expert", "Heartbeat co 300 s")
        res = se.evaluate(r, items, se.catalog())
        self.assertTrue(res[0]["ok"])
        self.assertFalse(res[1]["ok"])               # no-trigger wybrał ten sam skill
        self.assertEqual(len(msgs.calls), 3)          # routing ×2 + odpowiedź ×1
        enum = msgs.calls[0]["output_config"]["format"]["schema"]["properties"]["skill"]["enum"]
        self.assertIn("none", enum)
        self.assertIn("ev-ocpp-expert", msgs.calls[1]["system"][:200])   # system odpowiedzi = SKILL.md

    def test_budget_stops_run(self):
        items = [("ev-ocpp-expert", {"id": f"t{i}", "expect": "no-trigger", "neighbor": "x", "prompt": "p"})
                 for i in range(5)]
        r, msgs = self.runner("none", "", budget=0.0002)
        res = se.evaluate(r, items, se.catalog())
        self.assertIn("budżet", res[-1]["error"])
        self.assertLess(len(msgs.calls), 5)

    def test_cost(self):
        u = NS(input_tokens=1_000_000, output_tokens=1_000_000, cache_creation_input_tokens=0,
               cache_read_input_tokens=1_000_000)
        self.assertAlmostEqual(se.cost("claude-sonnet-5-5", u), 2.0 + 10.0 + 0.2)


if __name__ == "__main__":
    unittest.main()
