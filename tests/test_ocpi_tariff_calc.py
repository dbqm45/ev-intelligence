"""Tests for skills/ev-billing-tariff-expert/scripts/ocpi_tariff_calc.py (stdlib unittest).

Tariffs are copied from the examples in the OCPI PDFs from the source register (sources/evrf-ocpi.yaml):
OCPI 2.3.0 [OCPI230 §10.3.1] [OCPI230 §10.3.1.1] [OCPI230 §11.3.1.1] [OCPI230 §11.4.2] [OCPI230 §11.4.2.1]
[OCPI230 §11.4.7.1] [OCPI230 §11.4.7.2] and the same examples in OCPI 2.2.1-d2 [OCPI221 §11.3.1.1]
[OCPI221 §11.4.2.1]. Where an example is internally inconsistent, the test checks the rule from the text, not the
example's arithmetic:
- complex tariff, Saturday: 2.28 for 114 min x 1.25/h (= 2.375), total 12.28 / 13.861 [OCPI230 §11.3.1.1];
- "switching to Free-of-Charge Tariff Element": 0.80, while 12 min x 2.40/h + 15 min x 1.00/h = 0.73
  [OCPI230 §11.4.2.1];
- PROFILE_CHEAP tariff: the text gives 5.13 / 5.64 for energy (20.45 kWh billed as 20.5 kWh, step_size 100), the
  breakdown table 5.11 / 5.62 (no step) [OCPI230 §11.3.1.1]; the 2.2.1 table has 5.13 [OCPI221 §11.3.1.1].
The Warsaw case (PLN, 23 % VAT) is the pack-ev example ocpi-tariff-cdr (synthetic data, not from a specification).
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
SCRIPT = ROOT / "skills" / "ev-billing-tariff-expert" / "scripts" / "ocpi_tariff_calc.py"


def load():
    spec = importlib.util.spec_from_file_location("ocpi_tariff_calc", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = load()
WD = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]


def pc(type_, price, step=1, vat=None):
    c = {"type": type_, "price": price, "step_size": step}
    if vat is not None:
        c["vat"] = vat
    return c


def tariff(*elements, **extra):
    """Tariff without tax_included (2.2.1 model) unless given in extra."""
    return {"country_code": "DE", "party_id": "ALL", "id": "T1", "currency": "EUR",
            "elements": [{"price_components": list(comps), **({"restrictions": r} if r else {})} for comps, r in elements],
            "last_updated": "2026-10-20T00:00:00Z", **extra}


def tariff23(*elements, tax="NO", **extra):
    return tariff(*elements, tax_included=tax, **extra)


def session(start: str, *periods, digits=6):
    """periods: (minutes, {dimension: volume}) — TIME and PARKING_TIME given in minutes, the rest in OCPI units."""
    t = dt.datetime.fromisoformat(start.replace("Z", "+00:00"))
    out = []
    for minutes, dims in periods:
        d = [{"type": k, "volume": round(v / 60, digits) if k in ("TIME", "PARKING_TIME") else v} for k, v in dims.items()]
        out.append({"start_date_time": t.isoformat().replace("+00:00", "Z"), "dimensions": d})
        t += dt.timedelta(minutes=minutes)
    return {"start_date_time": out[0]["start_date_time"], "end_date_time": t.isoformat().replace("+00:00", "Z"),
            "charging_periods": out}


def c22(r, key="total_cost"):
    return (r[key]["excl_vat"], r[key]["incl_vat"]) if r.get(key) else None


def c23(r, key="total_cost"):
    return (r[key]["before_taxes"], r[key]["after_taxes"]) if r.get(key) else None


def calc22(t, s, **kw):
    return M.calculate(t, s, version="2.2.1", **kw)


# Tariff 22 — step_size when switching elements [OCPI230 §11.4.2.1]
T22 = [([pc("TIME", 1.20, 1800), pc("PARKING_TIME", 1.00, 900)], {"start_time": "00:00", "end_time": "17:00"}),
       ([pc("TIME", 2.40, 900), pc("PARKING_TIME", 1.00, 900)], {"start_time": "17:00", "end_time": "20:00"}),
       ([pc("TIME", 2.40, 900)], {"start_time": "20:00", "end_time": "00:00"})]
# Tariff 14 — complex tariff [OCPI230 §11.3.1.1]
T14 = [([pc("FLAT", 2.50, 1, 15.0)], None),
       ([pc("TIME", 1.00, 900, 20.0)], {"max_current": 32.0}),
       ([pc("TIME", 2.00, 600, 20.0)], {"min_current": 32.0, "day_of_week": WD}),
       ([pc("TIME", 1.25, 600, 20.0)], {"min_current": 32.0, "day_of_week": ["SATURDAY", "SUNDAY"]}),
       ([pc("PARKING_TIME", 5.0, 300, 10.0)], {"start_time": "09:00", "end_time": "18:00", "day_of_week": WD}),
       ([pc("PARKING_TIME", 6.0, 300, 10.0)], {"start_time": "10:00", "end_time": "17:00", "day_of_week": ["SATURDAY"]})]
MONDAY = ("2026-10-19T09:30:00Z", (165, {"TIME": 165, "MAX_CURRENT": 16}), (42, {"PARKING_TIME": 42}))
SATURDAY = ("2026-10-24T13:30:00Z", (114, {"TIME": 114, "MIN_CURRENT": 43, "MAX_CURRENT": 43}), (71, {"PARKING_TIME": 71}))
T_POW = [([pc("ENERGY", 0.20, 1, 20.0)], {"max_power": 16.0}), ([pc("ENERGY", 0.35, 1, 20.0)], {"max_power": 32.0}),
         ([pc("ENERGY", 0.50, 1, 20.0)], None)]
S_POW = ("2026-10-20T10:00:00Z", (10, {"ENERGY": 1, "MAX_POWER": 6}), (50, {"ENERGY": 40, "MAX_POWER": 48}),
         (8, {"ENERGY": 0.5, "MAX_POWER": 4}))
T_DUR = [([pc("ENERGY", 0.0, 1, 20.0)], {"max_duration": 1800}), ([pc("ENERGY", 0.25, 1, 20.0)], {"max_duration": 3600}),
         ([pc("ENERGY", 0.40, 1, 20.0)], None)]
S_DUR = ("2026-10-20T10:00:00Z", (30, {"ENERGY": 5}), (10, {"ENERGY": 1.2}))

# CDR example: 2.2.1 [OCPI221 §10.3.1.1] and 2.3.0 [OCPI230 §10.3.1.1]
T_CDR = tariff(([pc("TIME", 2.0, 300, 10.0)], None))
S_CDR = {"start_date_time": "2015-06-29T21:39:09Z", "end_date_time": "2015-06-29T23:37:32Z",
         "charging_periods": [{"start_date_time": "2015-06-29T21:39:09Z", "dimensions": [{"type": "TIME", "volume": 1.973}]}]}
CDR22 = {**S_CDR, "currency": "EUR", "tariffs": [T_CDR], "total_cost": {"excl_vat": 4.0, "incl_vat": 4.4},
         "total_energy": 15.342, "total_time": 1.973, "total_time_cost": {"excl_vat": 4.0, "incl_vat": 4.4}}
T_CDR23 = {**T_CDR, "id": "12"}  # as in the 2.3.0 example: no tax_included in the tariff inside the CDR
CDR23 = {"start_date_time": "2024-12-05T17:39:09Z", "end_date_time": "2024-12-05T19:37:32Z", "currency": "EUR",
         "tariffs": [T_CDR23],
         "charging_periods": [{"start_date_time": "2024-12-05T17:39:09Z",
                               "dimensions": [{"type": "TIME", "volume": 1.973}], "tariff_id": "12"}],
         "total_cost": {"before_taxes": 4.00, "taxes": [{"name": "VAT", "amount": 0.40}]},
         "total_energy": 15.342, "total_time": 1.973,
         "total_time_cost": {"before_taxes": 4.00, "taxes": [{"name": "VAT", "amount": 0.40}]}}


class Ocpi221Test(unittest.TestCase):
    """The original pack-ev cases (OCPI 2.2.1 price model: excl_vat / incl_vat)."""

    def test_spec_cdr_example(self):
        r = calc22(T_CDR, S_CDR)
        self.assertEqual(c22(r), (4.0, 4.4))  # 1.973 h, step 300 s → 2 h × 2 €/h, VAT 10 %
        self.assertEqual(c22(r, "total_time_cost"), (4.0, 4.4))
        self.assertAlmostEqual(r["total_time"], 1.9731, places=3)  # total_time = whole session in hours

    def test_step_switching_elements(self):
        t = tariff(*T22)
        r = calc22(t, session("2026-10-20T16:35:00Z", (25, {"TIME": 25}), (10, {"TIME": 10})))
        self.assertEqual(c22(r), (1.3, 1.3))  # example #2: 35 → 45 min, 25 × 1.20 + 20 × 2.40
        r = calc22(t, session("2026-10-20T16:55:00Z", (5, {"TIME": 5}), (5, {"TIME": 5}), (2, {"PARKING_TIME": 2})))
        self.assertEqual(c22(r), (0.55, 0.55))  # example #1: TIME not rounded, parking 2 → 15 min
        self.assertEqual(c22(r, "total_parking_cost"), (0.25, 0.25))

    def test_step_free_parking_after_20(self):
        r = calc22(tariff(*T22), session("2026-10-20T19:40:00Z", (12, {"TIME": 12}), (8, {"PARKING_TIME": 8}),
                                         (12, {"PARKING_TIME": 12})))
        self.assertEqual(c22(r), (0.73, 0.73))  # spec says 0.80; tariff prices give 0.48 + 0.25
        self.assertEqual(c22(r, "total_parking_cost"), (0.25, 0.25))
        self.assertEqual(r["total_parking_time"], 0.3333)  # actual time, not rounded
        last = [x for x in r["lines"] if x["type"] == "PARKING_TIME"][-1]
        self.assertEqual((last["period"], last["billed"]), (1, 0.25))  # surplus in the last paid period (19:52–20:00)

    def test_step_volume_precision(self):
        r = calc22(tariff(([pc("PARKING_TIME", 1.00, 300)], None)),
                   session("2026-10-20T19:00:00Z", (20, {"TIME": 20}), (40, {"PARKING_TIME": 40})))
        self.assertEqual(c22(r, "total_parking_cost"), (0.6667, 0.6667))  # 0.666667 h is not an extra step

    def test_step_energy_500(self):
        r = calc22(tariff(([pc("ENERGY", 0.25, 500)], None)), session("2026-10-20T10:00:00Z", (10, {"ENERGY": 0.1})))
        self.assertEqual(c22(r), (0.125, 0.125))

    def test_complex_monday(self):
        r = calc22(tariff(*T14), session(*MONDAY))
        self.assertEqual(c22(r), (9.0, 10.3))
        self.assertEqual(c22(r, "total_fixed_cost"), (2.5, 2.875))

    def test_complex_saturday(self):
        r = calc22(tariff(*T14), session(*SATURDAY))
        self.assertEqual(c22(r), (12.375, 13.975))  # spec: 12.28 / 13.861 (2.28 instead of 2.375)

    def test_complex_wednesday_40a(self):
        r = calc22(tariff(*T14), session("2026-10-21T10:00:00Z", (60, {"TIME": 60, "MIN_CURRENT": 40, "MAX_CURRENT": 40})))
        self.assertEqual(c22(r), (4.5, 5.275))

    def test_restriction_max_power(self):
        self.assertEqual(c22(calc22(tariff(*T_POW), session(*S_POW))), (20.3, 24.36))

    def test_restriction_max_duration(self):
        self.assertEqual(c22(calc22(tariff(*T_DUR), session(*S_DUR))), (0.3, 0.36))

    def test_time_window_over_midnight(self):
        night = tariff(([pc("ENERGY", 0.30)], {"start_time": "22:00", "end_time": "06:00"}), ([pc("ENERGY", 0.50)], None))
        s = session("2026-10-20T21:30:00Z", (60, {"ENERGY": 10}))
        self.assertEqual(c22(calc22(night, s, tz="Europe/Warsaw")), (3.0, 3.0))  # 23:30 local
        self.assertEqual(c22(calc22(night, s)), (5.0, 5.0))  # default UTC: 21:30 outside the window

    def test_max_kwh_exclusive(self):
        kwh = tariff(([pc("ENERGY", 0.40)], {"max_kwh": 10}), ([pc("ENERGY", 0.30)], None))
        r = calc22(kwh, session("2026-10-20T10:00:00Z", (30, {"ENERGY": 10}), (30, {"ENERGY": 5})))
        self.assertEqual(c22(r), (5.5, 5.5))

    def test_min_and_max_price(self):
        t = tariff(([pc("ENERGY", 0.25, 1, 10.0)], None), min_price={"excl_vat": 0.50, "incl_vat": 0.55})
        r = calc22(t, session("2026-10-20T10:00:00Z", (5, {"ENERGY": 1})))
        self.assertEqual(c22(r), (0.5, 0.55))
        self.assertTrue(any("min_price" in w for w in r["warnings"]))
        r = calc22(tariff(([pc("ENERGY", 0.25)], None), max_price={"excl_vat": 2.0, "incl_vat": 2.0}),
                   session("2026-10-20T10:00:00Z", (60, {"ENERGY": 20})))
        self.assertEqual(c22(r), (2.0, 2.0))

    def test_no_vat_and_unpriced_dimension(self):
        r = calc22(tariff(([pc("ENERGY", 0.25)], None)), session("2026-10-20T10:00:00Z", (60, {"ENERGY": 4, "TIME": 60})))
        self.assertEqual(c22(r), (1.0, 1.0))
        self.assertEqual(r["warnings"], [])

    def test_reservation_skipped(self):
        resv = tariff(([pc("TIME", 5.0)], {"reservation": "RESERVATION"}), ([pc("ENERGY", 0.25)], None))
        r = calc22(resv, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 4})))
        self.assertEqual(c22(r), (1.0, 1.0))
        self.assertTrue(any("rezerwac" in w for w in r["warnings"]))

    def test_lines(self):
        lines = calc22(tariff(*T14), session(*MONDAY))["lines"]
        self.assertTrue(any(x["type"] == "PARKING_TIME" and x["billed"] == 0.75 and x["element"] == 4 for x in lines))

    def test_compare_cdr(self):
        self.assertEqual(M.compare(calc22(T_CDR, S_CDR), CDR22), [])
        bad = {**CDR22, "total_cost": {"excl_vat": 4.2, "incl_vat": 4.62}}
        self.assertEqual([d["field"] for d in M.compare(calc22(T_CDR, S_CDR), bad)],
                         ["total_cost.excl_vat", "total_cost.incl_vat"])

    def test_warsaw_example(self):
        """pack-ev example ocpi-tariff-cdr: parking window 08–20 by mistake, 08–18 corrected (Europe/Warsaw)."""
        def t(end):
            return tariff(([pc("ENERGY", 1.79, 1, 23.0)], None),
                          ([pc("PARKING_TIME", 12.0, 300, 23.0)], {"start_time": "08:00", "end_time": end, "day_of_week": WD}),
                          currency="PLN")
        s = {"start_date_time": "2026-10-20T15:00:00Z", "end_date_time": "2026-10-20T17:10:00Z",
             "charging_periods": [
                 {"start_date_time": "2026-10-20T15:00:00Z", "dimensions": [
                     {"type": "ENERGY", "volume": 16.5}, {"type": "TIME", "volume": 1.5}, {"type": "MAX_POWER", "volume": 11.0}]},
                 {"start_date_time": "2026-10-20T16:30:00Z", "dimensions": [{"type": "PARKING_TIME", "volume": 0.666667}]}]}
        self.assertEqual(c22(calc22(t("20:00"), s, tz="Europe/Warsaw")), (37.535, 46.1681))
        self.assertEqual(c22(calc22(t("18:00"), s, tz="Europe/Warsaw")), (29.535, 36.3281))


class Ocpi230Test(unittest.TestCase):
    """OCPI 2.3.0 price model: tax_included, PriceLimit, Price {before_taxes, taxes}."""

    def test_simple_energy(self):
        t = tariff23(([pc("ENERGY", 0.25, 1, 10.0)], None))
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 20})))
        self.assertEqual(r["ocpi_version"], "2.3.0")
        self.assertEqual(r["total_cost"], {"before_taxes": 5.0, "taxes": [{"name": "VAT", "percentage": 10.0, "amount": 0.5}],
                                           "after_taxes": 5.5})
        self.assertEqual(r["warnings"], [])

    def test_start_fee_taxes_per_rate(self):
        t = tariff23(([pc("FLAT", 0.50, 1, 20.0), pc("ENERGY", 0.25, 1, 10.0)], None))
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 20})))
        self.assertEqual(c23(r), (5.5, 6.1))
        self.assertEqual({x["percentage"]: x["amount"] for x in r["total_cost"]["taxes"]}, {10.0: 0.5, 20.0: 0.1})

    def test_min_price_limit(self):
        t = tariff23(([pc("ENERGY", 0.25, 1, 10.0)], None), min_price={"before_taxes": 0.50, "after_taxes": 0.55})
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (5, {"ENERGY": 1})))
        self.assertEqual(c23(r), (0.5, 0.55))
        self.assertEqual(r["total_cost"]["taxes"], [{"name": "VAT", "amount": 0.05}])
        self.assertTrue(any("min_price" in w for w in r["warnings"]))
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 20})))
        self.assertEqual(c23(r), (5.0, 5.5))

    def test_max_price_limit(self):
        t = tariff23(([pc("FLAT", 0.50, 1, 20.0), pc("ENERGY", 0.25, 1, 10.0)], None),
                     max_price={"before_taxes": 10.00, "after_taxes": 11.00})
        self.assertEqual(c23(M.calculate(t, session("2026-10-20T10:00:00Z", (120, {"ENERGY": 50})))), (10.0, 11.0))
        self.assertEqual(c23(M.calculate(t, session("2026-10-20T10:00:00Z", (90, {"ENERGY": 30})))), (8.0, 8.85))

    def test_max_price_before_taxes_only(self):
        t = tariff23(([pc("ENERGY", 0.25, 1, 10.0)], None), max_price={"before_taxes": 2.0})
        self.assertEqual(c23(M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 20})))), (2.0, 5.5))

    def test_parking_and_start_fee(self):
        t = tariff23(([pc("FLAT", 0.50, 1, 20.0), pc("ENERGY", 0.25, 1, 10.0), pc("PARKING_TIME", 2.00, 900, 20.0)], None))
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 20}), (40, {"PARKING_TIME": 40})))
        self.assertEqual(c23(r), (7.0, 7.9))  # 40 → 45 min of parking

    def test_time_and_parking(self):
        t = tariff23(([pc("TIME", 2.00, 60, 10.0)], None))
        self.assertEqual(c23(M.calculate(t, session("2026-10-20T10:00:00Z", (150, {"TIME": 150})))), (5.0, 5.5))
        t = tariff23(([pc("TIME", 3.00, 60, 10.0), pc("PARKING_TIME", 5.00, 300, 20.0)], None))
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (150, {"TIME": 150}), (42, {"PARKING_TIME": 42})))
        self.assertEqual(c23(r), (11.25, 12.75))

    def test_north_american_tax_not_included(self):
        t = tariff23(([pc("TIME", 2.00, 1)], None), currency="CAD")
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (150, {"TIME": 150})))
        self.assertEqual(r["total_cost"], {"before_taxes": 5.0, "taxes": [], "after_taxes": 5.0})
        self.assertTrue(any("bez vat" in w for w in r["warnings"]))  # taxes outside the tariff are not calculated

    def test_north_american_tax_included(self):
        t = tariff23(([pc("TIME", 2.10, 1)], None), tax="YES", currency="CAD")
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (150, {"TIME": 150})))
        self.assertEqual(c23(r), (None, 5.25))
        self.assertTrue(any("tax_included YES" in w for w in r["warnings"]))

    def test_tax_included_yes_with_vat(self):
        t = tariff23(([pc("ENERGY", 0.30, 1, 20.0)], None), tax="YES")
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 10})))
        self.assertEqual(c23(r), (2.5, 3.0))
        self.assertEqual(r["total_cost"]["taxes"], [{"name": "VAT", "percentage": 20.0, "amount": 0.5}])

    def test_tax_not_applicable(self):
        t = tariff23(([pc("ENERGY", 0.30, 1, 20.0)], None), tax="N/A")
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 10})))
        self.assertEqual(r["total_cost"], {"before_taxes": 3.0, "taxes": [], "after_taxes": 3.0})
        self.assertTrue(any("N/A" in w for w in r["warnings"]))

    def test_profile_cheap_step_100(self):
        t = tariff23(([pc("FLAT", 0.50, 1, 20.0), pc("ENERGY", 0.25, 100, 10.0)], None), type="PROFILE_CHEAP")
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (90, {"ENERGY": 20.45})))
        self.assertEqual(c23(r, "total_energy_cost"), (5.125, 5.6375))  # 20.5 kWh; spec text 5.13 / 5.64
        self.assertEqual(c23(r), (5.625, 6.2375))  # spec text 5.63 / 6.24, spec table 5.61 / 6.22

    def test_complex_monday_taxes(self):
        r = M.calculate(tariff23(*T14), session(*MONDAY))
        self.assertEqual(c23(r), (9.0, 10.3))
        self.assertEqual({x["percentage"]: x["amount"] for x in r["total_cost"]["taxes"]}, {10.0: 0.375, 15.0: 0.375, 20.0: 0.55})

    def test_complex_saturday(self):
        self.assertEqual(c23(M.calculate(tariff23(*T14), session(*SATURDAY))), (12.375, 13.975))

    def test_restrictions_examples(self):
        self.assertEqual(c23(M.calculate(tariff23(*T_POW), session(*S_POW))), (20.3, 24.36))
        self.assertEqual(c23(M.calculate(tariff23(*T_DUR), session(*S_DUR))), (0.3, 0.36))

    def test_tariff_22_four_decimals(self):
        """Tariff 22 examples with CDR volumes in 4 decimals [OCPI230 §17.7]: 5 min = 0.0833 h, so a cost may differ
        from the example by 0.0001 (precision of the input, not of the rule)."""
        t = tariff23(*T22)

        def near(r, expected):
            for got, exp in zip(c23(r), expected):
                self.assertAlmostEqual(got, exp, delta=0.0005)
        r = M.calculate(t, session("2026-10-20T16:55:00Z", (5, {"TIME": 5}), (5, {"TIME": 5}), (2, {"PARKING_TIME": 2}), digits=4))
        near(r, (0.55, 0.55))
        r = M.calculate(t, session("2026-10-20T16:35:00Z", (25, {"TIME": 25}), (10, {"TIME": 10}), digits=4))
        near(r, (1.3, 1.3))
        r = M.calculate(t, session("2026-10-20T19:40:00Z", (12, {"TIME": 12}), (8, {"PARKING_TIME": 8}),
                                   (12, {"PARKING_TIME": 12}), digits=4))
        near(r, (0.73, 0.73))

    def test_cdr_step_size_examples(self):
        """Examples from the CDR object description [OCPI230 §10.3.1]."""
        e = tariff23(([pc("ENERGY", 0.20, 500)], {"end_time": "17:00"}), ([pc("ENERGY", 0.27, 500)], None))
        r = M.calculate(e, session("2026-10-20T16:00:00Z", (60, {"ENERGY": 4.3}), (30, {"ENERGY": 1.1})))
        self.assertEqual([x["billed"] for x in r["lines"]], [4.3, 1.2])  # 5.4 → 5.5 kWh, not 1.1 → 1.5
        tm = tariff23(([pc("TIME", 5.0, 600)], {"end_time": "17:00"}), ([pc("TIME", 7.0, 600)], None))
        r = M.calculate(tm, session("2026-10-20T16:54:00Z", (6, {"TIME": 6}), (22, {"TIME": 22})))
        self.assertEqual(c23(r), (3.3, 3.3))  # 28 → 30 min: 6 min × 5 + 24 min × 7
        tp = tariff23(([pc("TIME", 1.0, 600), pc("PARKING_TIME", 2.0, 600)], None))
        r = M.calculate(tp, session("2026-10-20T10:00:00Z", (21, {"TIME": 21}), (16, {"PARKING_TIME": 16})))
        self.assertEqual([x["billed"] for x in r["lines"]], [0.35, 0.3333])  # charging 21 min, parking 16 → 20 min
        t5 = tariff23(([pc("TIME", 1.0, 300), pc("PARKING_TIME", 1.0, 300)], None))
        r = M.calculate(t5, session("2026-10-20T10:00:00Z", (21, {"TIME": 21}), (7, {"PARKING_TIME": 7})))
        self.assertEqual([x["billed"] for x in r["lines"]], [0.35, 0.1667])  # 21 min (not 25), parking 10 min

    def test_energy_step_note(self):
        """115.2 Wh at 0.25 €/kWh: step 1 → 116 Wh, step 25 → 125 Wh, step 500 → 500 Wh [OCPI230 §11.4.2]."""
        for step, cost in ((1, 0.029), (25, 0.0313), (500, 0.125)):
            t = tariff23(([pc("ENERGY", 0.25, step)], None))
            self.assertEqual(c23(M.calculate(t, session("2026-10-20T10:00:00Z", (5, {"ENERGY": 0.1152}))))[0], cost)

    def test_day_of_week_empty_list(self):
        t = tariff23(([pc("ENERGY", 0.10)], {"day_of_week": []}), ([pc("ENERGY", 0.50)], None))
        self.assertEqual(c23(M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"ENERGY": 10})))), (5.0, 5.0))

    def test_min_current_inclusive(self):
        t = tariff23(([pc("TIME", 2.0)], {"min_current": 32.0}), ([pc("TIME", 1.0)], None))
        r = M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"TIME": 60, "MIN_CURRENT": 32, "MAX_CURRENT": 32})))
        self.assertEqual(c23(r), (2.0, 2.0))
        t = tariff23(([pc("TIME", 2.0)], {"max_current": 32.0}), ([pc("TIME", 1.0)], None))
        self.assertEqual(c23(M.calculate(t, session("2026-10-20T10:00:00Z", (60, {"TIME": 60, "MAX_CURRENT": 32})))), (1.0, 1.0))

    def test_cdr_example_230(self):
        """CDR example (no tax_included in its tariff): version from the CDR prices, compare with taxes."""
        version, known = M.detect_version(T_CDR23, CDR23)
        self.assertEqual((version, known), ("2.3.0", True))
        r = M.calculate(T_CDR23, CDR23, version=version)
        self.assertEqual(c23(r), (4.0, 4.4))
        self.assertTrue(any("tax_included" in w for w in r["warnings"]))
        self.assertEqual(M.compare(r, CDR23), [])
        bad = {**CDR23, "total_cost": {"before_taxes": 4.00, "taxes": [{"name": "VAT", "amount": 0.80}]}}
        self.assertEqual([d["field"] for d in M.compare(r, bad)], ["total_cost.taxes"])
        self.assertEqual(M.calculate([T_CDR23], CDR23, version="2.3.0")["total_cost"]["before_taxes"], 4.0)

    def test_tariff_id_other_than_tariff(self):
        s = {**CDR23, "charging_periods": [{**CDR23["charging_periods"][0], "tariff_id": "99"}]}
        r = M.calculate(T_CDR23, s, version="2.3.0")
        self.assertTrue(any("tariff_id 99" in w for w in r["warnings"]))


class VersionAndErrorsTest(unittest.TestCase):
    def test_auto_detection(self):
        s = session("2026-10-20T10:00:00Z", (60, {"ENERGY": 10}))
        self.assertEqual(M.calculate(tariff23(([pc("ENERGY", 0.3)], None)), s)["ocpi_version"], "2.3.0")
        r = M.calculate(tariff(([pc("ENERGY", 0.3)], None)), s)
        self.assertEqual(r["ocpi_version"], "2.2.1")
        self.assertTrue(any("nieustalona" in w for w in r["warnings"]))
        t = tariff(([pc("ENERGY", 0.3)], None), min_price={"excl_vat": 1.0})
        self.assertEqual(M.calculate(t, s)["ocpi_version"], "2.2.1")
        with self.assertRaises(M.InputError):
            M.calculate(tariff23(([pc("ENERGY", 0.3)], None), min_price={"excl_vat": 1.0}), s)

    def test_errors(self):
        s = session("2026-10-20T10:00:00Z", (60, {"ENERGY": 10}))
        with self.assertRaises(M.InputError):
            M.calculate(tariff23(([pc("ENERGY", 0.3)], None), tax="MAYBE"), s)
        with self.assertRaises(M.InputError):
            M.calculate(tariff(([pc("ENERGY", 0.3)], None), min_price={"before_taxes": 1.0}), s, version="2.2.1")
        with self.assertRaises(M.InputError):
            M.compare(calc22(T_CDR, S_CDR), CDR23)  # CDR in 2.3.0, calculation in 2.2.1
        with self.assertRaises(M.InputError):
            M.calculate([T_CDR23, {**T_CDR23, "id": "13"}], S_CDR)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as t:
            def w(name, obj):
                p = Path(t) / name
                p.write_text(json.dumps(obj), encoding="utf-8")
                return str(p)

            tp, sp, cp = w("t.json", T_CDR), w("s.json", S_CDR), w("c.json", CDR22)
            bp = w("b.json", {**CDR22, "total_cost": {"excl_vat": 4.2, "incl_vat": 4.62}})
            c3, t3 = w("c3.json", CDR23), w("t3.json", T_CDR23)

            def run(*a):
                return subprocess.run([sys.executable, str(SCRIPT), *a], capture_output=True, text=True)

            p = run(tp, sp, "--json")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["total_cost"]["excl_vat"], 4.0)
            p = run(tp, cp, "--cdr", cp)
            self.assertEqual(p.returncode, 0, p.stdout)
            self.assertIn("4.4", p.stdout)
            p = run(tp, bp, "--cdr", bp)
            self.assertEqual(p.returncode, 1)
            self.assertIn("total_cost", p.stdout)
            p = run(t3, c3, "--cdr", c3)  # version from the CDR
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("OCPI 2.3.0", p.stdout)
            p = run(t3, c3, "--cdr", c3, "--ocpi", "2.2.1")
            self.assertEqual(p.returncode, 2)
            self.assertEqual(run(tp, str(Path(t) / "brak.json")).returncode, 2)
            (Path(t) / "zly.json").write_text("{nie json")
            self.assertEqual(run(str(Path(t) / "zly.json"), sp).returncode, 2)
            self.assertEqual(run(tp, sp, "--tz", "Nie/Ma").returncode, 2)


if __name__ == "__main__":
    unittest.main()
