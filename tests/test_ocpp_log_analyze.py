"""Tests for skills/ev-evse-diagnostics-expert/scripts/ocpp_log_analyze.py (stdlib unittest).

Synthetic JSON Lines logs: a correct OCPP 1.6 session and a correct 2.0.1 transaction, then single deviations
(missing response, CALLERROR, duplicate id, open / unknown transaction, transactionId = -1, seqNo gap and duplicate,
decreasing meter, clock skew, reboot, unreadable lines, 2.1 frame types 5 and 6) and the command line.
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
SCRIPT = ROOT / "skills" / "ev-evse-diagnostics-expert" / "scripts" / "ocpp_log_analyze.py"


def load():
    spec = importlib.util.spec_from_file_location("ocpp_log_analyze", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = load()
UP, DOWN = "cp>csms", "csms>cp"


def ln(ts: str, cp: str, d: str, frame: list) -> str:
    return json.dumps({"ts": f"2026-10-20T{ts}Z", "cp": cp, "dir": d, "frame": frame})


def log16_ok() -> list:
    """Correct OCPP 1.6 session: Boot, Start, MeterValues, Stop — no findings."""
    return [
        ln("08:00:00", "CP1", UP, [2, "b1", "BootNotification", {"chargePointVendor": "V", "chargePointModel": "M"}]),
        ln("08:00:01", "CP1", DOWN, [3, "b1", {"status": "Accepted", "currentTime": "2026-10-20T08:00:01Z", "interval": 300}]),
        ln("08:01:00", "CP1", UP, [2, "s1", "StartTransaction", {"connectorId": 1, "idTag": "T1", "meterStart": 1000,
                                                                  "timestamp": "2026-10-20T08:01:00Z"}]),
        ln("08:01:01", "CP1", DOWN, [3, "s1", {"transactionId": 42, "idTagInfo": {"status": "Accepted"}}]),
        ln("08:10:00", "CP1", UP, [2, "m1", "MeterValues", {"connectorId": 1, "transactionId": 42, "meterValue": [
            {"timestamp": "2026-10-20T08:10:00Z", "sampledValue": [{"value": "2.5", "unit": "kWh",
                                                                    "measurand": "Energy.Active.Import.Register"}]}]}]),
        ln("08:10:01", "CP1", DOWN, [3, "m1", {}]),
        ln("08:20:00", "CP1", UP, [2, "e1", "StopTransaction", {"transactionId": 42, "meterStop": 4000,
                                                                 "timestamp": "2026-10-20T08:20:00Z"}]),
        ln("08:20:01", "CP1", DOWN, [3, "e1", {}]),
    ]


def te(ts, mid, ev, seq, tx="T-1", wh=None):
    p = {"eventType": ev, "timestamp": f"2026-10-20T{ts}Z", "triggerReason": "Authorized", "seqNo": seq,
         "transactionInfo": {"transactionId": tx}}
    if wh is not None:
        p["meterValue"] = [{"timestamp": f"2026-10-20T{ts}Z", "sampledValue": [{"value": wh}]}]
    return [ln(ts, "CP2", UP, [2, mid, "TransactionEvent", p]), ln(ts, "CP2", DOWN, [3, mid, {}])]


def codes(res: dict) -> list:
    return sorted(f["code"] for f in res["findings"])


class Ocpp16(unittest.TestCase):
    def test_correct_session(self):
        r = M.analyze(log16_ok())
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["stations"]["CP1"], {"ocpp": "1.6", "frames": 8})

    def test_open_transaction_with_evidence_lines(self):
        r = M.analyze(log16_ok()[:6])
        self.assertEqual(codes(r), ["open-transaction"])
        self.assertEqual(r["findings"][0]["severity"], "high")
        self.assertEqual(r["findings"][0]["lines"], [3, 4])

    def test_unknown_transaction(self):
        lines = log16_ok() + [ln("08:30:00", "CP1", UP, [2, "e2", "StopTransaction", {
            "transactionId": 99, "meterStop": 1, "timestamp": "2026-10-20T08:30:00Z"}]), ln("08:30:01", "CP1", DOWN, [3, "e2", {}])]
        r = M.analyze(lines)
        self.assertEqual(codes(r), ["unknown-transaction"])
        self.assertEqual(r["findings"][0]["lines"], [9])

    def test_transaction_id_minus_one_is_its_own_finding(self):
        # errata 1.6 §3.18: no StartTransaction.conf → transactionId = -1, CS responds as if valid
        lines = log16_ok()[:2] + [ln("08:30:00", "CP1", UP, [2, "e2", "StopTransaction", {
            "transactionId": -1, "meterStop": 1, "timestamp": "2026-10-20T08:30:00Z"}]), ln("08:30:01", "CP1", DOWN, [3, "e2", {}])]
        r = M.analyze(lines)
        self.assertEqual(codes(r), ["transaction-id-minus-1"])
        self.assertEqual(r["findings"][0]["severity"], "low")

    def test_meter_decrease(self):
        lines = log16_ok()
        lines[6] = ln("08:20:00", "CP1", UP, [2, "e1", "StopTransaction", {"transactionId": 42, "meterStop": 2000,
                                                                            "timestamp": "2026-10-20T08:20:00Z"}])
        self.assertEqual(codes(M.analyze(lines)), ["meter-decrease"])


class Rpc(unittest.TestCase):
    def test_call_without_response(self):
        r = M.analyze(log16_ok()[:2] + [ln("09:00:00", "CP1", DOWN, [2, "r1", "RemoteStartTransaction", {"idTag": "T1"}])])
        self.assertEqual(codes(r), ["call-no-response"])
        self.assertEqual(r["findings"][0]["severity"], "high")

    def test_timeout_is_a_tool_threshold(self):
        late = [ln("09:00:00", "CP1", DOWN, [2, "r1", "RemoteStartTransaction", {"idTag": "T1"}]),
                ln("09:01:00", "CP1", UP, [3, "r1", {"status": "Accepted"}])]
        self.assertEqual(codes(M.analyze(late, timeout=30)), ["call-no-response"])
        self.assertEqual(codes(M.analyze(late, timeout=120)), [])

    def test_callerror_names_code_and_action(self):
        r = M.analyze([ln("09:00:00", "CP1", DOWN, [2, "c1", "ChangeConfiguration", {"key": "X", "value": "1"}]),
                       ln("09:00:01", "CP1", UP, [4, "c1", "NotSupported", "brak", {}])])
        self.assertEqual(codes(r), ["callerror"])
        self.assertIn("NotSupported", r["findings"][0]["message"])
        self.assertIn("ChangeConfiguration", r["findings"][0]["message"])

    def test_duplicate_message_id(self):
        r = M.analyze([ln("09:00:00", "CP1", UP, [2, "h1", "Heartbeat", {}]), ln("09:00:01", "CP1", DOWN, [3, "h1", {"currentTime": "x"}]),
                       ln("09:05:00", "CP1", UP, [2, "h1", "Heartbeat", {}]), ln("09:05:01", "CP1", DOWN, [3, "h1", {"currentTime": "x"}])])
        self.assertEqual(codes(r), ["duplicate-message-id"])

    def test_ocpp21_send_and_callresulterror_are_valid_frames(self):
        r = M.analyze([ln("09:00:00", "CP3", UP, [6, "n1", "NotifyPeriodicEventStream", {"id": 1, "pending": 0, "basetime": "x", "data": []}]),
                       ln("09:00:01", "CP3", UP, [2, "h1", "Heartbeat", {}]),
                       ln("09:00:02", "CP3", DOWN, [3, "h1", {"currentTime": "x"}]),
                       ln("09:00:03", "CP3", UP, [5, "h1", "FormatViolation", "bad response", {}])])
        self.assertEqual(r["findings"], [])           # SEND expects no response; type 5 is not an unreadable line
        self.assertEqual(r["stations"]["CP3"]["ocpp"], "2.1")


class ClockAndReboot(unittest.TestCase):
    def test_clock_skew_and_threshold(self):
        lines = log16_ok()
        lines[2] = ln("08:01:00", "CP1", UP, [2, "s1", "StartTransaction", {"connectorId": 1, "idTag": "T1", "meterStart": 1000,
                                                                             "timestamp": "2026-10-20T07:30:00Z"}])
        r = M.analyze(lines)
        self.assertEqual(codes(r), ["clock-skew"])
        self.assertIn("1860", r["findings"][0]["message"])
        self.assertEqual(codes(M.analyze(lines, skew=3600)), [])

    def test_reboot(self):
        self.assertIn("reboot", codes(M.analyze(log16_ok() + log16_ok()[:2])))


class Ocpp201(unittest.TestCase):
    OK = te("10:00:00", "t1", "Started", 0, wh=100) + te("10:05:00", "t2", "Updated", 1, wh=500) + te("10:10:00", "t3", "Ended", 2, wh=900)

    def test_correct_transaction(self):
        r = M.analyze(self.OK)
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["stations"]["CP2"]["ocpp"], "2.0.1")

    def test_seqno_gap_and_open(self):
        r = M.analyze(te("10:00:00", "t1", "Started", 0) + te("10:05:00", "t2", "Updated", 3))
        self.assertEqual(codes(r), ["open-transaction", "seqno-gap"])

    def test_seqno_need_not_start_at_zero(self):
        # starting at 0 is only a SHOULD; a continuous counter is allowed (+1 per TransactionEvent is SHALL)
        r = M.analyze(te("10:00:00", "t1", "Started", 7) + te("10:05:00", "t2", "Ended", 8))
        self.assertEqual(r["findings"], [])

    def test_seqno_duplicate(self):
        r = M.analyze(te("10:00:00", "t1", "Started", 0) + te("10:05:00", "t2", "Updated", 1) + te("10:06:00", "t3", "Updated", 1)
                      + te("10:10:00", "t4", "Ended", 2))
        self.assertEqual(codes(r), ["seqno-duplicate"])

    def test_meter_decrease(self):
        r = M.analyze(te("10:00:00", "t1", "Started", 0, wh=500) + te("10:05:00", "t2", "Ended", 1, wh=300))
        self.assertEqual(codes(r), ["meter-decrease"])

    def test_forced_version(self):
        self.assertEqual(M.analyze(self.OK, ocpp="1.6")["stations"]["CP2"]["ocpp"], "1.6")


class InputAndCli(unittest.TestCase):
    def test_bad_lines_do_not_stop_analysis(self):
        r = M.analyze(["nie json", json.dumps({"ts": "x"})] + log16_ok())
        self.assertEqual(codes(r), ["invalid-line", "invalid-line"])
        self.assertEqual(r["stations"]["CP1"]["frames"], 8)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "log.jsonl"
            f.write_text("\n".join(log16_ok()[:6]) + "\n", encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), str(f), "--json"], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual([x["code"] for x in json.loads(p.stdout)["findings"]], ["open-transaction"])
            p = subprocess.run([sys.executable, str(SCRIPT), "-"], input=f.read_text(encoding="utf-8"),
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0)
            self.assertIn("open-transaction", p.stdout)
            p = subprocess.run([sys.executable, str(SCRIPT), str(Path(t) / "brak.jsonl")], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
