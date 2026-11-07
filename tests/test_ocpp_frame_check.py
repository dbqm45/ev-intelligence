"""Tests for skills/ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py (stdlib unittest).

The real OCA schemas are not in the repository (CC BY-ND); these tests build tiny schemas in a temp dir with the same
file naming conventions as the official packages (1.6: <Action>.json / <Action>Response.json; 2.x: <Action>Request.json /
<Action>Response.json).
"""
import importlib.util
import sys as _sys

_sys.dont_write_bytecode = True  # do not leave __pycache__ inside the skill directory
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "ev-evse-diagnostics-expert" / "scripts" / "ocpp_frame_check.py"


def load():
    spec = importlib.util.spec_from_file_location("ocpp_frame_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BOOT_REQ = {"$schema": "http://json-schema.org/draft-04/schema#", "type": "object",
            "properties": {"chargePointVendor": {"type": "string", "maxLength": 20},
                           "chargePointModel": {"type": "string", "maxLength": 20}},
            "additionalProperties": False, "required": ["chargePointVendor", "chargePointModel"]}
BOOT_RES = {"$schema": "http://json-schema.org/draft-04/schema#", "type": "object",
            "properties": {"status": {"type": "string", "enum": ["Accepted", "Pending", "Rejected"]},
                           "currentTime": {"type": "string"}, "interval": {"type": "integer"}},
            "additionalProperties": False, "required": ["status", "currentTime", "interval"]}
HB_REQ_201 = {"$schema": "http://json-schema.org/draft-06/schema#", "type": "object",
              "properties": {"customData": {"type": "object"}}, "additionalProperties": False}


class FrameCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()
        cls.tmp = tempfile.TemporaryDirectory()
        d16 = Path(cls.tmp.name) / "v16"
        d201 = Path(cls.tmp.name) / "v201"
        d16.mkdir()
        d201.mkdir()
        (d16 / "BootNotification.json").write_text(json.dumps(BOOT_REQ))
        (d16 / "BootNotificationResponse.json").write_text(json.dumps(BOOT_RES))
        (d201 / "HeartbeatRequest.json").write_text(json.dumps(HB_REQ_201))
        cls.d16, cls.d201 = d16, d201

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, lines, version="1.6", schemas=None):
        return self.m.check_lines(lines, version, schemas or (self.d16 if version == "1.6" else self.d201))

    def test_valid_call_and_result_pairing(self):
        res = self.check(['[2,"a1","BootNotification",{"chargePointVendor":"V","chargePointModel":"M"}]',
                          '[3,"a1",{"status":"Accepted","currentTime":"2026-01-01T00:00:00Z","interval":300}]'])
        self.assertEqual([r["ok"] for r in res], [True, True])
        self.assertEqual(res[1]["action"], "BootNotification")

    def test_missing_required_field_is_reported(self):
        res = self.check(['[2,"a2","BootNotification",{"chargePointVendor":"V"}]'])
        self.assertFalse(res[0]["ok"])
        self.assertTrue(any("chargePointModel" in e for e in res[0]["errors"]))

    def test_enum_violation_in_result(self):
        res = self.check(['[2,"a3","BootNotification",{"chargePointVendor":"V","chargePointModel":"M"}]',
                          '[3,"a3",{"status":"OK","currentTime":"x","interval":1}]'])
        self.assertFalse(res[1]["ok"])

    def test_result_without_matching_call(self):
        res = self.check(['[3,"zz",{"status":"Accepted"}]'])
        self.assertFalse(res[0]["ok"])
        self.assertTrue(any("CALL" in e for e in res[0]["errors"]))

    def test_unknown_action_has_no_schema(self):
        res = self.check(['[2,"a4","FooBar",{}]'])
        self.assertFalse(res[0]["ok"])
        self.assertTrue(any("FooBar" in e for e in res[0]["errors"]))

    def test_callerror_code_by_version(self):
        ok16 = self.check(['[4,"a5","FormationViolation","bad",{}]'], "1.6")
        bad16 = self.check(['[4,"a6","FormatViolation","bad",{}]'], "1.6")
        ok201 = self.check(['[4,"a7","FormatViolation","bad",{}]'], "2.0.1")
        bad201 = self.check(['[4,"a8","FormationViolation","bad",{}]'], "2.0.1")
        self.assertTrue(ok16[0]["ok"])
        self.assertFalse(bad16[0]["ok"])
        self.assertTrue(ok201[0]["ok"])
        self.assertFalse(bad201[0]["ok"])

    def test_201_request_schema_naming(self):
        res = self.check(['[2,"h1","Heartbeat",{}]'], "2.0.1")
        self.assertTrue(res[0]["ok"], res[0]["errors"])

    def test_extracts_frame_from_log_line(self):
        res = self.check(['2026-01-01 10:00:00 IN CP01 [2,"a9","BootNotification",'
                          '{"chargePointVendor":"V","chargePointModel":"M"}]'])
        self.assertTrue(res[0]["ok"])

    def test_malformed_frame(self):
        res = self.check(['[2,"only-two"]'])
        self.assertFalse(res[0]["ok"])

    def test_message_type_5_and_6_only_in_21(self):
        self.assertFalse(self.check(['[6,"s1","NotifyPeriodicEventStream",{}]'], "2.0.1")[0]["ok"])

    def test_cli_first_line_is_verdict(self):
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as f:
            f.write('[2,"a2","BootNotification",{"chargePointVendor":"V"}]\n')
            log = f.name
        out = subprocess.run([sys.executable, str(SCRIPT), "--version", "1.6", "--schemas", str(self.d16), log],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 1)
        self.assertTrue(out.stdout.splitlines()[0].startswith("Werdykt: BŁĘDY"))


if __name__ == "__main__":
    unittest.main()
