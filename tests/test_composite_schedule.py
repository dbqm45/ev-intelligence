"""Tests for skills/ev-energy-smart-charging-expert/scripts/composite_schedule.py (stdlib unittest).

Cases built from OCA documents in the source register (sources/oca-ocpp.yaml):
- OCPP 2.0.1 Part 6 test cases [201-P6]: TC_K_41_CS (combining purposes, TxProfile ends before TxDefaultProfile),
  TC_K_40_CS (stacking), TC_K_09_CS / TC_K_22_CS / TC_K_23_CS / TC_K_21_CS (no profile → "Local limit of Charging
  Station", validTo, startSchedule in the future, validFrom). The test cases give periods as "(100 - x)", x = time
  between startSchedule and the request; here x = 5 s and <limit multiplier> = 1 (unit A).
- examples in Part 2: daily profile 11 kW / 6 kW [201-P2 K §3.6] [16 §3.13.7], stacked exceptions (Sunday,
  Christmas) [201-P2 K §3.6.1] — its startSchedule values have no time zone offset, its "duration": 1080 for 17:00–20:00
  is checked literally and as 10800; LocalGeneration 5000 W + 2000 / 1000 W = 7000 / 6000 W [21-P2 K27].
Other cases are synthetic and check single rules (tags at each test).
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
SCRIPT = ROOT / "skills" / "ev-energy-smart-charging-expert" / "scripts" / "composite_schedule.py"


def load():
    spec = importlib.util.spec_from_file_location("composite_schedule", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = load()
S = "2026-11-27T10:00:00Z"          # startSchedule of the test-case profiles
X5 = "2026-11-27T10:00:05Z"         # request received x = 5 s later


def per(*items):
    """(startPeriod, limit[, numberPhases]) tuples → chargingSchedulePeriod."""
    out = []
    for it in items:
        d = {"startPeriod": it[0], "limit": it[1]}
        if len(it) > 2:
            d["numberPhases"] = it[2]
        out.append(d)
    return out


def p2(pid, purpose, periods, evse=1, level=0, kind="Absolute", unit="A", start=S, duration=None, **extra):
    """SetChargingProfileRequest (2.0.1 / 2.1)."""
    sch = {"id": 1, "chargingRateUnit": unit, "chargingSchedulePeriod": periods}
    if start is not None and kind != "Relative":
        sch["startSchedule"] = start
    if duration is not None:
        sch["duration"] = duration
    sch.update(extra.pop("schedule", {}))
    prof = {"id": pid, "stackLevel": level, "chargingProfilePurpose": purpose, "chargingProfileKind": kind,
            "chargingSchedule": [sch], **extra}
    return {"evseId": evse, "chargingProfile": prof}


def report(evse, *msgs, source="EMS"):
    """ReportChargingProfilesRequest from SetChargingProfileRequest-shaped helpers."""
    return {"requestId": 1, "chargingLimitSource": source, "evseId": evse,
            "chargingProfile": [m["chargingProfile"] for m in msgs]}


def p16(pid, purpose, periods, connector=1, level=0, kind="Absolute", unit="A", start=S, duration=None, **extra):
    """SetChargingProfile.req (1.6)."""
    sch = {"chargingRateUnit": unit, "chargingSchedulePeriod": periods}
    if start is not None:
        sch["startSchedule"] = start
    if duration is not None:
        sch["duration"] = duration
    prof = {"chargingProfileId": pid, "stackLevel": level, "chargingProfilePurpose": purpose,
            "chargingProfileKind": kind, "chargingSchedule": sch, **extra}
    return {"connectorId": connector, "csChargingProfiles": prof}


def run(data, **kw):
    kw.setdefault("ocpp", "2.0.1")
    kw.setdefault("evse", 1)
    kw.setdefault("start", X5)
    return M.compute(data, M.options(**kw))


def lims(r):
    return [(s["startPeriod"], s["limit"]) for s in r["periods"]]


class TestCasesPart6(unittest.TestCase):
    def test_tc_k_41_combining_purposes(self):
        """TC_K_41_CS [201-P6]: Max 10, TxDefault 300 s, TxProfile 260 s; TxProfile end → TxDefault [201-P2 K02.FR.08]."""
        data = [p2(1, "ChargingStationMaxProfile", per((0, 10)), evse=0, duration=86400),
                p2(2, "TxDefaultProfile", per((0, 6), (60, 10), (120, 8), (180, 15), (260, 8)), duration=300),
                p2(3, "TxProfile", per((0, 8), (50, 11), (140, 16), (200, 6), (240, 12)), duration=260,
                   transactionId="tx-1")]
        r = run(data, duration=400, transaction_id="tx-1")
        self.assertEqual(lims(r), [(0, 8), (45, 10), (195, 6), (235, 10), (255, 8), (295, 10)])
        srcs = [s["sources"][0] for s in r["periods"]]
        self.assertEqual(srcs, ["TxProfile#3", "ChargingStationMaxProfile#1", "TxProfile#3",
                                "ChargingStationMaxProfile#1", "TxDefaultProfile#2", "ChargingStationMaxProfile#1"])
        self.assertTrue(r["complete"])
        self.assertEqual(r["undefined"], [])
        self.assertEqual(r["response"]["schedule"]["evseId"], 1)
        self.assertEqual(r["response"]["schedule"]["scheduleStart"], X5)

    def test_tc_k_40_stacking(self):
        """TC_K_40_CS [201-P6]: stackLevel 1 (150 s) over stackLevel 0 (400 s) [201-P2 K §3.5] [201-P2 K08.FR.06]."""
        data = [p2(1, "TxDefaultProfile", per((0, 6), (100, 8), (200, 10)), level=0, duration=400),
                p2(2, "TxDefaultProfile", per((0, 7), (100, 9)), level=1, duration=150)]
        r = run(data, duration=350)
        self.assertEqual(lims(r), [(0, 7), (95, 9), (145, 8), (195, 10)])
        self.assertTrue(r["complete"])

    def test_tc_k_09_no_profiles_local_limit(self):
        """TC_K_09_CS [201-P6]: after clearing, limit = local limit of the station; OCPP gives no number."""
        before = [p2(1, "TxDefaultProfile", per((0, 6)), duration=400)]
        self.assertEqual(lims(run(before, duration=300, transaction_id="t")), [(0, 6)])
        r = run([], duration=300, unit="A", transaction_id="t")
        self.assertEqual(lims(r), [(0, None)])
        self.assertEqual(r["periods"][0]["status"], "BRAK_PROFILU")
        self.assertFalse(r["complete"])
        self.assertIsNone(r["response"])
        self.assertEqual(lims(run([], duration=300, unit="A", local_limit=32)), [(0, 32)])

    def test_tc_k_22_valid_to(self):
        """TC_K_22_CS [201-P6]: validTo exclusive [201-P2 K01.FR.37]."""
        data = [p2(1, "TxDefaultProfile", per((0, 6)), validFrom=S, validTo="2026-11-27T10:05:00Z")]
        self.assertEqual(lims(run(data, start=S, duration=400, local_limit=32)), [(0, 6), (300, 32)])

    def test_tc_k_23_start_schedule_future(self):
        """TC_K_23_CS [201-P6]: limit only from startSchedule [201-P2 K01.FR.30]."""
        data = [p2(1, "TxDefaultProfile", per((0, 6)), start="2026-11-27T10:01:00Z")]
        self.assertEqual(lims(run(data, start=S, duration=300, local_limit=32)), [(0, 32), (60, 6)])

    def test_tc_k_21_valid_from_relative(self):
        """TC_K_21_CS [201-P6]: Relative TxDefault, validFrom +300 s; no transaction → as if one started now
        [201-P2 K08.FR.06]; validFrom inclusive [201-P2 K01.FR.36]."""
        data = [p2(1, "TxDefaultProfile", per((0, 6)), kind="Relative", validFrom="2026-11-27T10:05:00Z")]
        r = run(data, start=S, duration=400, charging_start=S, local_limit=32)
        self.assertEqual(lims(r), [(0, 32), (300, 6)])
        self.assertTrue(any("RECOMMENDED" in w for w in r["warnings"]))


class SpecExamples(unittest.TestCase):
    DAILY = {"id": 100, "stackLevel": 0, "chargingProfilePurpose": "TxDefaultProfile",
             "chargingProfileKind": "Recurring", "recurrencyKind": "Daily",
             "chargingSchedule": [{"id": 1, "duration": 86400, "startSchedule": "2013-01-01T00:00Z",
                                   "chargingRateUnit": "W",
                                   "chargingSchedulePeriod": per((0, 11000, 3), (28800, 6000, 3), (72000, 11000, 3))}]}

    def test_daily_profile_2_0_1(self):
        """[201-P2 K §3.6]: 11 kW / 6 kW 08:00–20:00, every 24 h from startSchedule [201-P2 §3.68]."""
        r = run([{"evseId": 0, "chargingProfile": self.DAILY}], start="2026-11-27T07:00:00Z", duration=14 * 3600)
        self.assertEqual(lims(r), [(0, 11000), (3600, 6000), (13 * 3600, 11000)])
        self.assertEqual(r["periods"][0]["numberPhases"], 3)

    def test_daily_profile_1_6(self):
        """[16 §3.13.7]: the same profile in 1.6 (chargingSchedule object, chargingProfileId)."""
        prof = {**self.DAILY, "chargingProfileId": 100, "chargingSchedule": dict(self.DAILY["chargingSchedule"][0])}
        del prof["id"]
        del prof["chargingSchedule"]["id"]
        r = run([{"connectorId": 0, "csChargingProfiles": prof}], ocpp="1.6", start="2026-11-27T19:00:00Z",
                duration=7200, transaction_id="1")
        self.assertEqual(lims(r), [(0, 6000), (3600, 11000)])
        self.assertIn("chargingSchedule", r["response"])
        self.assertNotIn("startSchedule", r["response"]["chargingSchedule"])  # [16E §3.57]

    def stacked(self, duration):
        """[201-P2 K §3.6.1] with 'Z' added (the example has no offset)."""
        return [p2(10, "TxDefaultProfile", per((0, 2000)), evse=0, level=1, kind="Recurring", unit="W",
                   start="2020-01-09T17:00:00Z", duration=duration, recurrencyKind="Daily"),
                p2(11, "TxDefaultProfile", per((0, 999999)), evse=0, level=2, kind="Recurring", unit="W",
                   start="2020-01-05T00:00:00Z", duration=86400, recurrencyKind="Weekly"),
                p2(12, "TxDefaultProfile", per((0, 999999)), evse=0, level=3, unit="W",
                   start="2020-12-25T00:00:00Z", duration=86400, validFrom="2020-01-01T00:00:00Z",
                   validTo="2021-01-01T00:00:00Z")]

    def test_stacked_exceptions(self):
        monday = run(self.stacked(10800), start="2020-01-13T16:00:00Z", duration=5 * 3600, local_limit=11000)
        self.assertEqual(lims(monday), [(0, 11000), (3600, 2000), (4 * 3600, 11000)])
        sunday = run(self.stacked(10800), start="2020-01-12T17:30:00Z", duration=3600)
        self.assertEqual(lims(sunday), [(0, 999999)])
        christmas = run(self.stacked(10800), start="2020-12-25T17:30:00Z", duration=3600)  # Friday
        self.assertEqual(lims(christmas), [(0, 999999)])
        self.assertEqual(christmas["periods"][0]["sources"], ["TxDefaultProfile#12"])
        next_xmas = run(self.stacked(10800), start="2021-12-24T17:30:00Z", duration=3600)  # validTo 2021-01-01
        self.assertEqual(lims(next_xmas), [(0, 2000)])

    def test_stacked_example_literal_duration_1080(self):
        """Literal "duration": 1080 ends the 2 kW limit at 17:18 (see profile-ocpp.md §11: typo for 10800)."""
        r = run(self.stacked(1080), start="2020-01-13T17:00:00Z", duration=3600, local_limit=11000)
        self.assertEqual(lims(r), [(0, 2000), (1080, 11000)])

    def test_example_without_offset(self):
        """RFC 3339 needs an offset [201-P2 §2.1.4]; the example writes none → error unless --assume-utc."""
        data = [p2(10, "TxDefaultProfile", per((0, 2000)), evse=0, kind="Recurring", unit="W",
                   start="2020-01-09T17:00:00", duration=10800, recurrencyKind="Daily")]
        with self.assertRaises(M.InputError):
            run(data, start="2020-01-13T17:30:00Z", duration=600)
        r = run(data, start="2020-01-13T17:30:00Z", duration=600, assume_utc=True)
        self.assertEqual(lims(r), [(0, 2000)])
        self.assertTrue(any("--assume-utc" in w for w in r["warnings"]))

    def test_local_generation_k27(self):
        """[21-P2 K27]: TxDefault 5000 W + LocalGeneration 2000 / 1000 W → 7000 / 6000 W [21-P2 K §3.6]."""
        lg = p2(-5, "LocalGeneration", per((0, 2000), (1800, 1000)), evse=0, unit="W")
        data = [p2(1, "TxDefaultProfile", per((0, 5000)), kind="Relative", unit="W"), report(0, lg)]
        r = run(data, ocpp="2.1", start=S, duration=3600, charging_start=S)
        self.assertEqual(lims(r), [(0, 7000), (1800, 6000)])
        self.assertIn("+ LocalGeneration#-5 [21-P2 K §3.6]", r["periods"][0]["sources"])
        with self.assertRaises(M.InputError):  # CSMS must not send LocalGeneration [21-E §2.16.2]
            run([lg], ocpp="2.1", start=S, duration=60)


class StackAndPurposes(unittest.TestCase):
    def test_external_constraints_minimum(self):
        """Lowest of Max, ExternalConstraints, TxDefault [201-P2 K §3.5]; External only via report [201-P2 K01.FR.22]."""
        ext = p2(7, "ChargingStationExternalConstraints", per((0, 12)), evse=0)
        data = [p2(1, "ChargingStationMaxProfile", per((0, 20)), evse=0),
                p2(2, "TxDefaultProfile", per((0, 16)), evse=0), report(0, ext)]
        r = run(data, duration=60)
        self.assertEqual(lims(r), [(0, 12)])
        self.assertEqual(r["periods"][0]["sources"], ["ChargingStationExternalConstraints#7"])
        with self.assertRaises(M.InputError):
            run([ext], duration=60)

    def test_external_not_in_1_6(self):
        with self.assertRaises(M.InputError):
            run([p16(1, "ChargingStationExternalConstraints", per((0, 10)), connector=0)], ocpp="1.6", duration=60)

    def test_tx_profile_before_start_undefined(self):
        """TxProfile valid, startSchedule later: K §3.5 vs K01.FR.30 → reported, not guessed."""
        data = [p2(1, "TxDefaultProfile", per((0, 16))),
                p2(2, "TxProfile", per((0, 10)), start="2026-11-27T10:01:40Z", transactionId="t")]
        r = run(data, start=S, duration=300, transaction_id="t")
        self.assertEqual(lims(r), [(0, None), (100, 10)])
        self.assertEqual(r["periods"][0]["status"], "NIEOKRESLONE")
        self.assertEqual(len(r["undefined"]), 1)

    def test_tx_profile_needs_transaction(self):
        data = [p2(1, "TxDefaultProfile", per((0, 16))), p2(2, "TxProfile", per((0, 10)), transactionId="t")]
        r = run(data, duration=60)
        self.assertEqual(lims(r), [(0, 16)])
        self.assertIn("TxProfile#2", [x["profile"] for x in r["ignored"]])
        r = run(data, duration=60, transaction_id="other")
        self.assertEqual(lims(r), [(0, 16)])
        self.assertEqual(lims(run(data, duration=60, transaction_id="t")), [(0, 10)])

    def test_evse0_profile_applies_to_evse(self):
        """Profile on EVSE #0 active on all EVSEs [201-P2 K §3.4]; other EVSE ignored."""
        data = [p2(1, "TxDefaultProfile", per((0, 16)), evse=0, level=0),
                p2(2, "TxDefaultProfile", per((0, 8)), evse=2, level=1)]
        self.assertEqual(lims(run(data, duration=60)), [(0, 16)])
        self.assertEqual(lims(run(data, evse=2, duration=60)), [(0, 8)])

    def test_recurring_weekly_and_before_start(self):
        """Weekly: every 7 days from startSchedule [201-P2 §3.68]; not before startSchedule [201-P2 K01.FR.30]."""
        data = [p2(1, "TxDefaultProfile", per((0, 6)), kind="Recurring", recurrencyKind="Weekly",
                   start="2026-11-30T08:00:00Z", duration=3600)]
        early = run(data, start="2026-11-23T08:00:00Z", duration=3600, local_limit=32)  # one week before start
        self.assertEqual(lims(early), [(0, 32)])
        later = run(data, start="2026-12-14T07:30:00Z", duration=7200, local_limit=32)
        self.assertEqual(lims(later), [(0, 32), (1800, 6), (5400, 32)])

    def test_priority_charging_2_1(self):
        """PriorityCharging overrules TxProfile when activated [21-P2 K §3.6]; no duration [21-P2 K01.FR.70]."""
        data = [p2(1, "ChargingStationMaxProfile", per((0, 20)), evse=0),
                p2(2, "TxProfile", per((0, 10)), transactionId="t"),
                p2(3, "PriorityCharging", per((0, 32)))]
        self.assertEqual(lims(run(data, ocpp="2.1", duration=60, transaction_id="t")), [(0, 10)])
        self.assertEqual(lims(run(data, ocpp="2.1", duration=60, transaction_id="t", priority_charging=True)),
                         [(0, 20)])
        with self.assertRaises(M.InputError):
            run(data, ocpp="2.0.1", duration=60, transaction_id="t")  # purpose unknown in 2.0.1
        bad = [p2(3, "PriorityCharging", per((0, 32)), duration=600)]
        with self.assertRaises(M.InputError):
            run(bad, ocpp="2.1", duration=60)


class Ocpp16(unittest.TestCase):
    def test_highest_without_duration_blocks_lower(self):
        """[16E §3.7]: highest stack level without duration → lower never executed."""
        data = [p16(1, "TxDefaultProfile", per((0, 16)), level=0),
                p16(2, "TxDefaultProfile", per((0, 10)), level=1)]
        r = run(data, ocpp="1.6", duration=7200, transaction_id="1")
        self.assertEqual(lims(r), [(0, 10)])
        self.assertTrue(r["complete"])
        self.assertEqual(r["undefined"], [])

    def test_fallback_after_duration_warns(self):
        """Recurring after duration → lower stackLevel [16 §5.16.4]; non-recurring: Wniosek from [16E §3.7]."""
        data = [p16(1, "TxDefaultProfile", per((0, 16)), level=0),
                p16(2, "TxDefaultProfile", per((0, 10)), level=1, duration=3600)]
        r = run(data, ocpp="1.6", start=S, duration=7200, transaction_id="1")
        self.assertEqual(lims(r), [(0, 10), (3600, 16)])
        self.assertTrue(any("Wniosek" in w and "16E §3.7" in w for w in r["warnings"]))
        rec = [p16(1, "TxDefaultProfile", per((0, 16)), level=0),
               p16(2, "TxDefaultProfile", per((0, 10)), level=1, duration=3600, kind="Recurring",
                   recurrencyKind="Daily")]
        r = run(rec, ocpp="1.6", start=S, duration=7200, transaction_id="1")
        self.assertEqual(lims(r), [(0, 10), (3600, 16)])
        self.assertTrue(any("16E §3.43" in w for w in r["warnings"]))

    def test_tx_profile_ended_undefined_in_1_6(self):
        """1.6 has no K02.FR.08: TxProfile valid but past its duration, TxDefault present → reported."""
        data = [p16(1, "TxDefaultProfile", per((0, 16)), connector=0),
                p16(2, "TxProfile", per((0, 10)), duration=600)]
        r = run(data, ocpp="1.6", start=S, duration=1200, transaction_id="1")
        self.assertEqual(lims(r), [(0, 10), (600, None)])
        self.assertEqual(r["periods"][1]["status"], "NIEOKRESLONE")
        same_201 = [p2(1, "TxDefaultProfile", per((0, 16)), evse=0),
                    p2(2, "TxProfile", per((0, 10)), duration=600, transactionId="t")]
        self.assertEqual(lims(run(same_201, start=S, duration=1200, transaction_id="t")), [(0, 10), (600, 16)])

    def test_no_transaction_tx_default_undefined(self):
        data = [p16(1, "TxDefaultProfile", per((0, 16)), connector=0)]
        r = run(data, ocpp="1.6", duration=60)
        self.assertEqual(lims(r), [(0, 16)])
        self.assertTrue(any("K08.FR.06" in u for u in r["undefined"]))

    def test_connector_tx_default_replaces_connector0(self):
        """[16 §3.13.1]: TxDefault on the connector replaces the one from connector 0 for that connector."""
        data = [p16(1, "TxDefaultProfile", per((0, 16)), connector=0, level=0),
                p16(2, "TxDefaultProfile", per((0, 20)), connector=1, level=0)]
        r = run(data, ocpp="1.6", duration=60, transaction_id="1")
        self.assertEqual(lims(r), [(0, 20)])
        self.assertEqual(lims(run(data, ocpp="1.6", evse=2, duration=60, transaction_id="1")), [(0, 16)])
        diff = [data[0], p16(2, "TxDefaultProfile", per((0, 20)), connector=1, level=1)]
        r = run(diff, ocpp="1.6", duration=60, transaction_id="1")
        self.assertEqual(len(r["undefined"]), 1)

    def test_absolute_without_start_schedule_1_6(self):
        """1.6: without startSchedule the schedule is relative to start of charging [16 §7.13]."""
        data = [p16(1, "TxProfile", per((0, 10), (600, 6)), start=None)]
        with self.assertRaises(M.InputError):
            run(data, ocpp="1.6", duration=1200, transaction_id="1")
        r = run(data, ocpp="1.6", start=S, duration=1200, transaction_id="1", charging_start=S)
        self.assertEqual(lims(r), [(0, 10), (600, 6)])


class UnitsAndPhases(unittest.TestCase):
    def test_w_to_a_ac(self):
        """W → A per phase = W / (V × numberPhases), default 3 [201-P2 K01.FR.49] [201-P2 K01.FR.50]."""
        data = [p2(1, "ChargingStationMaxProfile", per((0, 11000)), evse=0, unit="W"),
                p2(2, "TxDefaultProfile", per((0, 16)))]
        r = run(data, duration=60, unit="A", supply="AC", voltage=230)
        self.assertAlmostEqual(r["periods"][0]["limit"], 11000 / 690, places=5)
        self.assertEqual(r["periods"][0]["numberPhases"], 3)
        self.assertTrue(any("jedną cyfrę" in w for w in r["warnings"]))
        r = run(data, duration=60, unit="W", supply="AC", voltage=230)   # A → W (inverse, Wniosek)
        self.assertEqual(lims(r), [(0, 11000)])
        data[1]["chargingProfile"]["chargingSchedule"][0]["chargingSchedulePeriod"] = per((0, 10))
        self.assertEqual(lims(run(data, duration=60, unit="W", supply="AC", voltage=230)), [(0, 6900)])

    def test_mixing_units_refused_without_rule(self):
        data = [p2(1, "ChargingStationMaxProfile", per((0, 11000)), evse=0, unit="W"),
                p2(2, "TxDefaultProfile", per((0, 16)))]
        with self.assertRaises(M.InputError):          # no output unit
            run(data, duration=60, supply="AC", voltage=230)
        with self.assertRaises(M.InputError):          # DC: no conversion rule
            run(data, duration=60, unit="A", supply="DC", voltage=400)
        with self.assertRaises(M.InputError):          # AC but no voltage
            run(data, duration=60, unit="A", supply="AC")

    def test_lowest_number_phases(self):
        """numberPhases = lowest of applicable periods [201-P2 K §3.7]; conflicting phaseToUse → error."""
        data = [p2(1, "ChargingStationMaxProfile", per((0, 32, 3)), evse=0),
                p2(2, "TxProfile", per((0, 16, 1)), transactionId="t")]
        r = run(data, duration=60, transaction_id="t", supply="AC")
        self.assertEqual(r["periods"][0]["numberPhases"], 1)
        a = p2(1, "ChargingStationMaxProfile", [{"startPeriod": 0, "limit": 32, "numberPhases": 1, "phaseToUse": 1}],
               evse=0)
        b = p2(2, "TxProfile", [{"startPeriod": 0, "limit": 16, "numberPhases": 1, "phaseToUse": 3}],
               transactionId="t")
        with self.assertRaises(M.InputError):
            run([a, b], duration=60, transaction_id="t", supply="AC")
        ok = run([a], duration=60, supply="AC")
        self.assertEqual(ok["response"]["schedule"]["chargingSchedulePeriod"][0]["phaseToUse"], 1)


class Validation(unittest.TestCase):
    def bad(self, *msgs, **kw):
        kw.setdefault("duration", 60)
        with self.assertRaises(M.InputError):
            run(list(msgs), **kw)

    def test_k01_rules(self):
        self.bad(p2(1, "TxDefaultProfile", per((10, 6))))                                   # K01.FR.31
        self.bad(p2(1, "TxDefaultProfile", per((0, 6), (0, 8))))                            # K01.FR.35
        self.bad(p2(1, "ChargingStationMaxProfile", per((0, 6)), evse=0, kind="Relative"))  # K01.FR.38
        self.bad(p2(1, "TxDefaultProfile", per((0, 6)), start=None))                        # K01.FR.40
        self.bad(p2(1, "TxDefaultProfile", per((0, 6)), kind="Recurring"))                  # K01.FR.60
        self.bad(p2(1, "ChargingStationMaxProfile", per((0, 6)), evse=1))                   # K §3.2
        self.bad(p2(1, "TxProfile", per((0, 6)), evse=1), transaction_id="t")               # K01.FR.03
        self.bad(p2(1, "TxDefaultProfile", per((0, 6))), p2(2, "TxDefaultProfile", per((0, 8))))  # K01.FR.06
        self.bad(p2(1, "TxDefaultProfile", per((0, 6)), evse=0), p2(2, "TxDefaultProfile", per((0, 8))))  # K01.FR.52
        self.bad(p2(1, "TxDefaultProfile", per((0, 6))), p2(1, "TxDefaultProfile", per((0, 8)), level=1))  # same id
        self.bad(p16(1, "TxDefaultProfile", per((0, 6))), p16(2, "TxDefaultProfile", per((0, 8))), ocpp="1.6")
        self.bad(p16(1, "ChargePointMaxProfile", per((0, 6)), connector=1), ocpp="1.6")
        self.bad(p2(1, "TxDefaultProfile", per((0, 6))), evse=0)                            # EVSE 0 refused
        self.bad(p2(1, "TxDefaultProfile", per((0, 6))), start="2026-11-27T10:00:00")       # no offset
        self.bad({"chargingProfilePurpose": "TxDefaultProfile"})                            # no message wrapper
        two = p2(1, "TxProfile", per((0, 6)), transactionId="t")
        two["chargingProfile"]["chargingSchedule"].append(dict(two["chargingProfile"]["chargingSchedule"][0], id=2))
        self.bad(two, transaction_id="t")                                                   # K01.FR.34

    def test_2_1_refusals(self):
        def with_period(**fields):
            m = p2(1, "TxDefaultProfile", [{"startPeriod": 0, "limit": 6, **fields}])
            return m
        self.bad(with_period(operationMode="CentralSetpoint"), ocpp="2.1")
        self.bad(with_period(setpoint=3), ocpp="2.1")
        self.bad(with_period(limit_L2=6), ocpp="2.1")
        self.bad(with_period(evseSleep=True), ocpp="2.1")
        self.bad(p2(1, "TxDefaultProfile", per((0, -6))), ocpp="2.1")
        self.bad(p2(1, "TxDefaultProfile", per((0, 6)), kind="Dynamic"), ocpp="2.1")
        self.bad(p2(1, "TxDefaultProfile", per((0, 6)), schedule={"useLocalTime": True}), ocpp="2.1")
        self.bad(p2(1, "TxDefaultProfile", per((0, 6)), schedule={"limitAtSoC": {"soc": 80, "limit": 6}}), ocpp="2.1")
        rd = p2(1, "TxDefaultProfile", per((0, 6)), schedule={"randomizedDelay": 600})
        self.bad(rd, ocpp="2.1", transaction_id="t")
        r = run([rd], ocpp="2.1", duration=60)  # no transaction → randomizedDelay = 0 [21-P2 K08.FR.06]
        self.assertEqual(lims(r), [(0, 6)])
        self.assertTrue(any("K08.FR.06" in w for w in r["warnings"]))
        self.bad(p2(1, "ChargingStationMaxProfile", per((0, 6)), evse=0, schedule={"randomizedDelay": 60}),
                 ocpp="2.1")                                                               # K01.FR.95


class Cli(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as t:
            def w(name, obj):
                p = Path(t) / name
                p.write_text(json.dumps(obj), encoding="utf-8")
                return str(p)

            def cli(*a):
                return subprocess.run([sys.executable, str(SCRIPT), *a], capture_output=True, text=True)

            ok = w("ok.json", {"profiles": [p2(1, "TxDefaultProfile", per((0, 6), (100, 8)), duration=400)]})
            p = cli(ok, "--ocpp", "2.0.1", "--evse", "1", "--start", X5, "--duration", "300", "--json")
            self.assertEqual(p.returncode, 0, p.stderr)
            resp = json.loads(p.stdout)["response"]["schedule"]
            self.assertEqual(resp["chargingSchedulePeriod"], [{"startPeriod": 0, "limit": 6},
                                                              {"startPeriod": 95, "limit": 8}])
            p = cli(ok, "--ocpp", "2.0.1", "--evse", "1", "--start", X5, "--duration", "600")
            self.assertEqual(p.returncode, 1, p.stdout)      # after 400 s: no profile, no local limit
            self.assertIn("BRAK_PROFILU", p.stdout)
            frame = w("frame.json", [[2, "abc", "SetChargingProfile", p2(1, "TxDefaultProfile", per((0, 6)))]])
            p = cli(frame, "--ocpp", "2.0.1", "--connector", "1", "--start", X5, "--duration", "60")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(cli(ok, "--ocpp", "1.6", "--evse", "1", "--start", X5, "--duration", "60").returncode, 2)
            (Path(t) / "zly.json").write_text("{nie json")
            self.assertEqual(cli(str(Path(t) / "zly.json"), "--ocpp", "2.0.1", "--evse", "1", "--start", X5,
                                 "--duration", "60").returncode, 2)
            self.assertEqual(cli(str(Path(t) / "brak.json"), "--ocpp", "2.0.1", "--evse", "1", "--start", X5,
                                 "--duration", "60").returncode, 2)


if __name__ == "__main__":
    unittest.main()
