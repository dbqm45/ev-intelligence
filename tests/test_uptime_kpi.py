"""Tests for skills/ev-charging-operations-expert/scripts/uptime_kpi.py (stdlib unittest).

NEVI rules from 23 CFR 680 (sources/us-prawo.yaml, eCFR 2026-11-24): formula and 525,600 basis, exclusions with the
demonstration proviso and hours of operation [US-23CFR680 §680.116(b)(3)], "up" with minimum power
[US-23CFR680 §680.116(b)(1)] [US-23CFR680 §680.106(d)], monthly calculation for the previous twelve months
[US-23CFR680 §680.116(b)(2)], threshold "greater than 97%" [US-23CFR680 §680.116(b)], previous 3 months and the
duration of each outage [US-23CFR680 §680.112(a)]. Info mode: AFIR-655 Table F vocabulary
[AFIR-655 Annex, tabela F], OCPP Operative/Inoperative [201-P2 §3.23] [16 §7.7]. Data are synthetic.
"""
import datetime as dt
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
SCRIPT = ROOT / "skills" / "ev-charging-operations-expert" / "scripts" / "uptime_kpi.py"


def load():
    spec = importlib.util.spec_from_file_location("uptime_kpi", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = load()
Y0 = dt.datetime(2025, 11, 1, tzinfo=dt.timezone.utc)  # window for --month 2026-10: 2025-11-01 .. 2026-11-01
Y1 = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)  # 365 days = 525,600 min


def iso(t):
    return t.isoformat().replace("+00:00", "Z")


def year(port="P1", downs=(), up_state="Available", power_ok=True, start=Y0, end=Y1):
    """Whole window `up`, with outage intervals (offset_min, duration_min, extra fields) carved out."""
    rows, t = [], start
    for off, dur, extra in sorted(downs, key=lambda d: d[0]):
        s = start + dt.timedelta(minutes=off)
        e = s + dt.timedelta(minutes=dur)
        if s > t:
            rows.append({"port": port, "start": iso(t), "end": iso(s), "state": up_state, "power_ok": power_ok})
        rows.append({"port": port, "start": iso(s), "end": iso(e), "state": "Faulted", **extra})
        t = e
    if t < end:
        rows.append({"port": port, "start": iso(t), "end": iso(end), "state": up_state, "power_ok": power_ok})
    return rows


def nevi(rows, month="2026-10", mapping=(), **kw):
    return M.nevi(M.normalize(rows, M.parse_map(list(mapping))), month, **kw)


def port(r, pid="P1", i=-1):
    return r["months"][i]["ports"][pid]


class NeviFormula(unittest.TestCase):
    def test_formula_and_basis(self):
        r = nevi(year(downs=[(1000, 5760, {}), (20000, 7200, {"exclusion": "utility", "evidence": "ticket 42"})]))
        p = port(r)
        self.assertEqual(p["t_outage_min"], 12960)
        self.assertEqual(p["t_excluded_min"], 7200)
        self.assertAlmostEqual(p["uptime_pct"], (525600 - 5760) / 525600 * 100, places=4)
        self.assertTrue(p["meets"])
        self.assertEqual(r["basis_minutes"], 525600)
        self.assertEqual(r["months"][0]["window"]["minutes"], 525600)

    def test_exactly_97_is_not_greater(self):
        r = nevi(year(downs=[(0, 15768, {})]))  # 3 % of 525,600
        self.assertEqual(port(r)["uptime_pct"], 97.0)
        self.assertFalse(port(r)["meets"])
        self.assertEqual(r["below_threshold"], [{"month": "2026-10", "port": "P1", "uptime_pct": 97.0}])

    def test_just_above_97(self):
        r = nevi(year(downs=[(0, 15767, {})]))
        self.assertTrue(port(r)["meets"])
        self.assertEqual(r["below_threshold"], [])

    def test_partial_minutes_counted_exactly(self):
        rows = year()
        s = Y0 + dt.timedelta(minutes=10)
        rows = [{"port": "P1", "start": iso(Y0), "end": iso(s), "state": "up", "power_ok": True},
                {"port": "P1", "start": iso(s), "end": iso(s + dt.timedelta(seconds=30)), "state": "Faulted"},
                {"port": "P1", "start": iso(s + dt.timedelta(seconds=30)), "end": iso(Y1), "state": "up",
                 "power_ok": True}]
        self.assertEqual(port(nevi(rows))["t_outage_min"], 0.5)

    def test_months_series(self):
        r = nevi(year(), months=3)
        self.assertEqual([m["month"] for m in r["months"]], ["2026-08", "2026-09", "2026-10"])
        self.assertEqual(r["months"][0]["window"]["start"], "2025-09-01T00:00:00Z")
        # data start 2025-11-01: August window has 2 months without data -> outage by default
        self.assertEqual(port(r, i=0)["no_data_min"], (30 + 31) * 1440)
        self.assertFalse(port(r, i=0)["meets"])

    def test_timezone_month_boundaries(self):
        r = nevi(year(), tz="Europe/Warsaw")
        self.assertEqual(r["months"][0]["window"]["start"], "2025-10-31T23:00:00Z")
        self.assertEqual(r["months"][0]["window"]["end"], "2026-10-31T23:00:00Z")

    def test_leap_window_uses_525600_and_warns(self):
        s, e = dt.datetime(2027, 3, 1, tzinfo=dt.timezone.utc), dt.datetime(2028, 3, 1, tzinfo=dt.timezone.utc)
        r = nevi(year(start=s, end=e), month="2028-02")
        self.assertEqual(r["months"][0]["window"]["minutes"], 527040)
        self.assertEqual(port(r)["uptime_pct"], 100.0)
        self.assertTrue(any("527040" in w for w in r["warnings"]))

    def test_unknown_timezone(self):
        with self.assertRaises(M.InputError):
            nevi(year(), tz="Mars/Base")

    def test_bad_month(self):
        with self.assertRaises(M.InputError):
            nevi(year(), month="2026-13")


class NeviExclusions(unittest.TestCase):
    def test_exclusion_without_evidence_stays_in_outage(self):
        r = nevi(year(downs=[(0, 600, {"exclusion": "vandalism"})]))
        p = port(r)
        self.assertEqual(p["t_excluded_min"], 0)
        self.assertEqual(p["exclusion_without_evidence_min"], 600)
        self.assertTrue(any("bez evidence" in w for w in r["warnings"]))

    def test_all_five_reasons_with_evidence(self):
        downs = [(i * 1000, 100, {"exclusion": x, "evidence": "doc"})
                 for i, x in enumerate(["utility", "vehicle", "maintenance", "vandalism", "disaster"])]
        p = port(nevi(year(downs=downs)))
        self.assertEqual(p["t_outage_min"], 500)
        self.assertEqual(p["t_excluded_min"], 500)
        self.assertEqual(p["uptime_pct"], 100.0)

    def test_outside_hours_needs_no_evidence(self):
        p = port(nevi(year(downs=[(0, 600, {"exclusion": "outside_hours"})])))
        self.assertEqual(p["t_excluded_min"], 600)

    def test_exclusion_on_up_interval_ignored(self):
        rows = year()
        rows[0]["exclusion"] = "maintenance"
        rows[0]["evidence"] = "plan"
        r = nevi(rows)
        self.assertEqual(port(r)["t_excluded_min"], 0)
        self.assertTrue(any("zignorowane" in w for w in r["warnings"]))

    def test_unknown_exclusion_is_input_error(self):
        with self.assertRaises(M.InputError):
            nevi(year(downs=[(0, 10, {"exclusion": "firmware"})]))


class NeviUpDefinition(unittest.TestCase):
    def test_below_minimum_power_is_outage(self):
        rows = year(power_ok=False)
        p = port(nevi(rows))
        self.assertEqual(p["t_outage_min"], 525600)
        self.assertEqual(p["below_min_power_min"], 525600)
        self.assertEqual(p["uptime_pct"], 0.0)

    def test_missing_power_ok_warns(self):
        r = nevi(year(power_ok=None))
        self.assertTrue(port(r)["meets"])
        self.assertTrue(any("power_ok" in w for w in r["warnings"]))

    def test_offline_default_outage_and_map(self):
        rows = year(downs=[(0, 1440, {"state": "offline"})])
        self.assertEqual(port(nevi(rows))["t_outage_min"], 1440)
        self.assertEqual(port(nevi(rows, mapping=["offline=up"]))["t_outage_min"], 0)

    def test_reserved_up_with_warning_and_map(self):
        rows = year(up_state="Reserved")
        r = nevi(rows)
        self.assertEqual(port(r)["t_outage_min"], 0)
        self.assertTrue(any("Reserved" in w for w in r["warnings"]))
        self.assertEqual(port(nevi(rows, mapping=["Reserved=outage"]))["t_outage_min"], 525600)

    def test_unavailable_is_outage(self):
        rows = year(downs=[(0, 60, {})])
        rows[0]["state"] = "Unavailable"
        self.assertEqual(port(nevi(rows))["t_outage_min"], 60)

    def test_unknown_state_needs_map(self):
        rows = year()
        rows[0]["state"] = "PAUSED"
        with self.assertRaises(M.InputError):
            nevi(rows)
        self.assertEqual(port(nevi(rows, mapping=["PAUSED=outage"]))["t_outage_min"], 525600)


class NeviData(unittest.TestCase):
    def test_gaps_error(self):
        rows = year()[:1]
        rows[0]["end"] = iso(Y0 + dt.timedelta(days=10))
        with self.assertRaises(M.InputError):
            nevi(rows, gaps="error")
        self.assertEqual(port(nevi(rows))["no_data_min"], 525600 - 14400)

    def test_overlap_is_error(self):
        rows = year()
        rows.append({"port": "P1", "start": iso(Y0), "end": iso(Y0 + dt.timedelta(hours=1)), "state": "Faulted"})
        with self.assertRaises(M.InputError):
            nevi(rows)

    def test_end_before_start(self):
        with self.assertRaises(M.InputError):
            nevi([{"port": "P1", "start": iso(Y1), "end": iso(Y0), "state": "up"}])

    def test_outage_episodes_merged(self):
        s = Y1 - dt.timedelta(days=5)
        rows = [{"port": "P1", "start": iso(Y0), "end": iso(s), "state": "up", "power_ok": True},
                {"port": "P1", "start": iso(s), "end": iso(s + dt.timedelta(hours=2)), "state": "Faulted"},
                {"port": "P1", "start": iso(s + dt.timedelta(hours=2)), "end": iso(s + dt.timedelta(hours=3)),
                 "state": "outage", "exclusion": "utility", "evidence": "x"},
                {"port": "P1", "start": iso(s + dt.timedelta(hours=3)), "end": iso(Y1), "state": "up", "power_ok": True}]
        eps = nevi(rows)["outages_in_reported_months"]["P1"]
        self.assertEqual(eps, [{"start": iso(s), "end": iso(s + dt.timedelta(hours=3)), "duration_min": 180,
                                "excluded_min": 60}])

    def test_several_ports_separately(self):
        rows = year("A") + year("B", downs=[(0, 20000, {})])
        r = nevi(rows)
        self.assertTrue(port(r, "A")["meets"])
        self.assertFalse(port(r, "B")["meets"])
        self.assertEqual([b["port"] for b in r["below_threshold"]], ["B"])

    def test_tool_choices_flagged(self):
        r = nevi(year())
        self.assertTrue(r["tool_choices"])
        self.assertTrue(all("choice of the tool, not the rule" in c["note"] for c in r["tool_choices"]))


class InfoMode(unittest.TestCase):
    def rows(self):
        t = [Y0 + dt.timedelta(hours=h) for h in range(0, 11)]
        return [{"port": "P1", "start": iso(t[0]), "end": iso(t[4]), "state": "Available"},
                {"port": "P1", "start": iso(t[4]), "end": iso(t[6]), "state": "Charging"},
                {"port": "P1", "start": iso(t[6]), "end": iso(t[7]), "state": "Reserved"},
                {"port": "P1", "start": iso(t[7]), "end": iso(t[8]), "state": "Faulted", "cause": "RCD trip"},
                {"port": "P1", "start": iso(t[8]), "end": iso(t[9]), "state": "Unavailable",
                 "exclusion": "maintenance"},
                {"port": "P1", "start": iso(t[9]), "end": iso(t[10]), "state": "offline"}]

    def test_share_and_breakdown(self):
        r = M.info(M.normalize(self.rows(), {}))
        p = r["ports"]["P1"]
        self.assertIsNone(r["legal_metric"])
        self.assertEqual(p["operational_share_pct"], 70.0)
        self.assertEqual(p["availability_min"], {"in_use": 120, "reserved": 60, "not_in_use": 240, "unspecified": 0})
        self.assertEqual(p["non_operational_by_cause_min"], {"RCD trip": 60, "maintenance": 60, "offline": 60})

    def test_window_and_gaps(self):
        r = M.info(M.normalize(self.rows(), {}), end=iso(Y0 + dt.timedelta(hours=20)))
        p = r["ports"]["P1"]
        self.assertEqual(p["no_data_min"], 600)
        self.assertEqual(p["operational_share_pct"], 35.0)
        self.assertEqual(p["non_operational_by_cause_min"]["no_data"], 600)
        with self.assertRaises(M.InputError):
            M.info(M.normalize(self.rows(), {}), end=iso(Y0 + dt.timedelta(hours=20)), gaps="error")


class Cli(unittest.TestCase):
    def run_cli(self, data, *args, suffix=".json"):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / f"in{suffix}"
            f.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
            return subprocess.run([sys.executable, "-B", str(SCRIPT), str(f), *args], capture_output=True, text=True)

    def test_exit_0_and_json(self):
        p = self.run_cli({"intervals": year()}, "--mode", "nevi", "--month", "2026-10", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["months"][0]["ports"]["P1"]["uptime_pct"], 100.0)

    def test_exit_1_below_threshold_text(self):
        p = self.run_cli(year(downs=[(0, 15768, {})]), "--mode", "nevi", "--month", "2026-10")
        self.assertEqual(p.returncode, 1)
        self.assertIn("choice of the tool, not the rule", p.stdout)
        self.assertIn("✗", p.stdout)

    def test_info_mode_exit_0_even_when_low(self):
        p = self.run_cli(year(power_ok=None, up_state="Faulted"), "--mode", "info")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("nie metryka prawna", p.stdout)

    def test_exit_2_input_errors(self):
        self.assertEqual(self.run_cli("{", "--mode", "info").returncode, 2)
        self.assertEqual(self.run_cli(year(), "--mode", "nevi").returncode, 2)  # no --month
        self.assertEqual(self.run_cli(year(), "--mode", "nevi", "--month", "2026-10", "--map", "x").returncode, 2)

    def test_csv_input(self):
        csv_text = ("port,start,end,state,cause,exclusion,evidence,power_ok\n"
                    f"P1,{iso(Y0)},{iso(Y0 + dt.timedelta(days=1))},outage,storm,disaster,NWS alert,\n"
                    f"P1,{iso(Y0 + dt.timedelta(days=1))},{iso(Y1)},up,,,,true\n")
        p = self.run_cli(csv_text, "--mode", "nevi", "--month", "2026-10", "--json", suffix=".csv")
        self.assertEqual(p.returncode, 0, p.stderr)
        pp = json.loads(p.stdout)["months"][0]["ports"]["P1"]
        self.assertEqual(pp["t_outage_min"], 1440)
        self.assertEqual(pp["t_excluded_min"], 1440)


if __name__ == "__main__":
    unittest.main()
