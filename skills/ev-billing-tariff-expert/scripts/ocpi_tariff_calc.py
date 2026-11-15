#!/usr/bin/env python3
"""Cost of a charging session from an OCPI tariff (2.3.0 or 2.2.1) for CDR-style `charging_periods`, and comparison
with the costs in a CDR.

  python3 ocpi_tariff_calc.py <tariff.json> <periods.json> [--cdr <cdr.json>] [--ocpi auto|2.3.0|2.2.1]
      [--tz Europe/Warsaw] [--tolerance 0.01] [--json]

<periods.json>: an object with `start_date_time`, `end_date_time` and `charging_periods` (a CDR works as is). The
tariff and the CDR may be wrapped in an OCPI response (`{"data": ..., "status_code": ...}`); a tariff list is
accepted when it has one tariff, or when the periods name one of them in `tariff_id`.
Exit code: 0 — calculated (and consistent with the CDR), 1 — difference from the CDR above --tolerance,
2 — input error. Standard library only. Network: none.

Price model (--ocpi; default auto):
  2.3.0  `tax_included` (YES / NO / N/A) is required in Tariff [OCPI230 §11.3.1] [OCPI230 §11.4.9];
         `PriceComponent.price` is including or excluding taxes according to it [OCPI230 §11.4.2];
         `min_price` / `max_price` are PriceLimit {before_taxes, after_taxes?} [OCPI230 §11.4.3];
         costs are Price {before_taxes, taxes: [TaxAmount {name, percentage?, amount}]} [OCPI230 §17.8]
         [OCPI230 §17.9]. The output Price also has `after_taxes` = before_taxes + sum of taxes: a helper of this
         tool, NOT a field of the Price class — remove it before putting the value into a CDR.
  2.2.1  `price` is excl. VAT [OCPI221 §11.4.2]; `min_price` / `max_price` and costs are Price {excl_vat,
         incl_vat?} [OCPI221 §11.3.1] [OCPI221 §16.5].
  auto   2.3.0 when the tariff has `tax_included` or any limit/cost uses before_taxes/after_taxes; 2.2.1 when they
         use excl_vat/incl_vat; mixed markers = input error. No marker = 2.2.1 with a warning (in 2.3.0
         `tax_included` is required). The CDR example in [OCPI230 §10.3.1.1] has a tariff without `tax_included`:
         with 2.3.0 the tool then assumes NO and warns.

Rules (text of OCPI 2.3.0; OCPI 2.2.1-d2 has the same rules: elements [OCPI221 §11.3.1], restrictions
[OCPI221 §11.4.6], step_size [OCPI221 §10.3.1] [OCPI221 §11.4.2]):
- Element selection: for each dimension (ENERGY, TIME, PARKING_TIME, FLAT) separately, the first element in the
  list that has a Price Component of that dimension and matching restrictions; when none matches there are no costs
  for that dimension [OCPI230 §11.3.1] [OCPI230 §11.4.5].
- Restrictions are a logical AND [OCPI230 §11.4.7]. They are evaluated at the start of each charging period:
  the CPO SHALL start a new ChargingPeriod whenever another Price Component becomes active [OCPI230 §10.3.1],
  and a period ends when the next one starts [OCPI230 §10.4.6].
  start_time / end_time / start_date / end_date are local time of `Location.time_zone` [OCPI230 §11.4.7]: pass it
  with --tz (default UTC). end_time < start_time wraps to the next day; end_time 00:00 = end of the day
  [OCPI230 §11.4.7]. start_date inclusive, end_date exclusive; min_kwh inclusive, max_kwh exclusive (energy used
  in the session before the period); min_duration inclusive, max_duration exclusive (seconds since session
  start); min_current / min_power: active at "more than, or equal to", max_current / max_power: active at
  "less than" [OCPI230 §11.4.7]. day_of_week: [] means no day — 0 and [] are not "no restriction"
  [OCPI-TSG cz. 2 pkt 6].
  Not specified by OCPI, behaviour of this tool: (a) end_time exclusive ("valid until this time of the day" does
  not say); (b) for a window wrapping past midnight, day_of_week is checked on the local date of the period start;
  (c) current/power for min_* is taken from MIN_CURRENT / MIN_POWER, for max_* from MAX_CURRENT / MAX_POWER, then
  the period average CURRENT / POWER (Session only values [OCPI230 §10.4.3]), then the other extreme, then
  ENERGY / TIME for power; no value = element skipped with a warning.
- Units: ENERGY in kWh, TIME and PARKING_TIME in hours; step_size multiplier 1 Wh / 1 s; FLAT has no unit
  [OCPI230 §11.4.6] [OCPI230 §10.4.3]. FLAT is billed once per session, at the first period where it matches
  (OCPI does not state this explicitly; behaviour of this tool).
- step_size: amounts are rounded up to the smallest multiple of step_size [OCPI230 §11.4.2]; taken into account
  once per session for ENERGY and once for TIME and PARKING_TIME combined; the total of the session counts, not
  the last period; the step_size of the last relevant PriceComponent is used; when TIME and PARKING_TIME are both
  used only the total parking duration is rounded [OCPI230 §10.3.1]. Extra time is added to the last period with a
  time-based Price Component [OCPI230 §11.4.2.1] ("The extra 7 minutes are then added to the last period ...");
  for ENERGY OCPI does not say where the extra goes: the tool adds it to the last period with an ENERGY component
  as well. Tool threshold: before the step, the total is rounded to 1 s / 0.01 Wh, because CDR volumes have
  4 decimals [OCPI230 §17.7] (0.6667 h = 2400.12 s must not cost an extra step).
- Taxes (2.3.0): NO — VAT = price x vat %, a component without `vat` has no VAT [OCPI230 §11.4.2] (other taxes
  added outside the tariff, as in the North American example [OCPI230 §11.3.1.1], are not calculated); YES with
  `vat` — before_taxes = amount / (1 + vat %); YES without `vat` — before_taxes cannot be derived (null + warning);
  N/A — no taxes [OCPI230 §11.4.9], `vat` ignored with a warning. 2.2.1: missing `vat` = no VAT, different from
  0.0 [OCPI221 §11.4.2].
- min_price / max_price: both values apply, before and after taxes, each to its own total [OCPI230 §11.3.1]
  [OCPI221 §11.3.1]. How taxes are split after a limit changed the total is not specified: the tool gives one
  TaxAmount "VAT" with the difference and a warning.
- Rounding: OCPI gives no rounding rules ("The OCPI specification stays out of these matters") [OCPI230 §11.3.1].
  The tool computes in Decimal and rounds only the output to 4 decimals (ROUND_HALF_UP), as numbers in OCPI use
  4 decimals [OCPI230 §17.7]; rounding on the invoice belongs to the CPO, contracts and law.
- Not calculated (warning): elements with `reservation` and the RESERVATION_TIME dimension (total_reservation_cost);
  several tariffs in one session (period `tariff_id` [OCPI230 §10.4.6] other than the tariff id).
  All FLAT costs go to total_fixed_cost (the tool does not move FLAT of parking to total_parking_cost
  [OCPI230 §10.3.1]). total_time = whole session in hours, total_parking_time = sum of PARKING_TIME
  [OCPI230 §10.3.1].
Known errors in the specification examples (the tool follows the rule, not the arithmetic): the complex tariff on
Saturday gives 2.28 for 114 min x 1.25/h = 2.375 [OCPI230 §11.3.1.1]; "switching to Free-of-Charge Tariff Element"
gives 0.80, while the tariff prices give 12 min x 2.40/h + 15 min x 1.00/h = 0.73 [OCPI230 §11.4.2.1]
(the same in [OCPI221 §11.4.2.1]).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
PRICED = ("FLAT", "ENERGY", "TIME", "PARKING_TIME")
COST_KEY = {"FLAT": "total_fixed_cost", "ENERGY": "total_energy_cost", "TIME": "total_time_cost",
            "PARKING_TIME": "total_parking_cost"}
STEP_UNIT = {"ENERGY": Decimal(1000), "TIME": Decimal(3600), "PARKING_TIME": Decimal(3600)}  # Wh / s per price unit
VERSIONS = ("2.3.0", "2.2.1")
PRICE_KEYS = {"2.3.0": ("before_taxes", "after_taxes"), "2.2.1": ("excl_vat", "incl_vat")}
TAX_INCLUDED = ("YES", "NO", "N/A")
Q = Decimal("0.0001")


class InputError(Exception):
    pass


def _d(x) -> Decimal:
    return Decimal(str(x))


def _ts(value: str) -> dt.datetime:
    try:
        t = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as e:
        raise InputError(f"zła data/czas: {value!r}") from e
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def _hhmm(s: str) -> dt.time:
    try:
        return dt.time.fromisoformat(s)
    except ValueError as e:
        raise InputError(f"zły czas w restrykcji: {s!r}") from e


def _num(x: Decimal | None) -> float | None:
    return None if x is None else float(x.quantize(Q, rounding=ROUND_HALF_UP))


def _unwrap(obj):
    """Strip an OCPI response envelope ({"data": ..., "status_code": ...})."""
    if isinstance(obj, dict) and "data" in obj and "status_code" in obj:
        return obj["data"]
    return obj


def _time_ok(r: dict, local: dt.datetime) -> bool:
    """[start_time, end_time) in local time; end < start wraps past midnight; end 00:00 = end of day [OCPI230 §11.4.7].
    Exclusive end_time is a choice of this tool (the specification does not say)."""
    t = local.time()
    start = _hhmm(r["start_time"]) if r.get("start_time") else dt.time(0, 0)
    end = _hhmm(r["end_time"]) if r.get("end_time") else None
    if end is None or end == dt.time(0, 0):
        return t >= start
    return start <= t < end if start < end else (t >= start or t < end)


class _Ctx:
    """State at the start of a charging period: local time, seconds since session start, kWh used before it."""

    def __init__(self, local: dt.datetime, duration_s: float, energy_kwh: Decimal, dims: dict[str, Decimal]):
        self.local, self.duration_s, self.energy_kwh, self.dims = local, duration_s, energy_kwh, dims

    def value(self, kind: str, side: str) -> Decimal | None:
        """Current (CURRENT) or power (POWER) of the period: MIN_* for min_*, MAX_* for max_*, then the average,
        then the other extreme; power falls back to ENERGY / TIME. Choice of this tool, see the module docstring."""
        d = self.dims
        for k in (f"{side}_{kind}", kind, f"{'MIN' if side == 'MAX' else 'MAX'}_{kind}"):
            if k in d:
                return d[k]
        if kind == "POWER" and "ENERGY" in d and d.get("TIME"):
            return d["ENERGY"] / d["TIME"]
        return None


def _matches(r: dict | None, c: _Ctx, warn) -> bool:
    """All set restrictions must match (logical AND) [OCPI230 §11.4.7]."""
    if not r:
        return True
    if r.get("start_time") or r.get("end_time"):
        if not _time_ok(r, c.local):
            return False
    date = c.local.date().isoformat()
    if r.get("start_date") and date < r["start_date"]:
        return False
    if r.get("end_date") and date >= r["end_date"]:
        return False
    # [] = no day of the week, not "no restriction" [OCPI-TSG cz. 2 pkt 6]
    if r.get("day_of_week") is not None and DAYS[c.local.weekday()] not in r["day_of_week"]:
        return False
    if r.get("min_kwh") is not None and c.energy_kwh < _d(r["min_kwh"]):
        return False
    if r.get("max_kwh") is not None and c.energy_kwh >= _d(r["max_kwh"]):
        return False
    if r.get("min_duration") is not None and c.duration_s < r["min_duration"]:
        return False
    if r.get("max_duration") is not None and c.duration_s >= r["max_duration"]:
        return False
    for kind in ("CURRENT", "POWER"):
        for side in ("MIN", "MAX"):
            limit = r.get(f"{side.lower()}_{kind.lower()}")
            if limit is None:
                continue
            v = c.value(kind, side)
            if v is None:
                warn(f"restrykcja {side.lower()}_{kind.lower()} bez danych w okresie ({side}_{kind}/{kind}) — element pominięty")
                return False
            if (side == "MIN" and v < _d(limit)) or (side == "MAX" and v >= _d(limit)):
                return False
    return True


def _markers(obj) -> set[str]:
    """Versions suggested by the price fields of a tariff, CDR or periods object."""
    out: set[str] = set()
    if not isinstance(obj, dict):
        return out
    if "tax_included" in obj:
        out.add("2.3.0")
    for key in ("min_price", "max_price", "total_cost", *COST_KEY.values()):
        v = obj.get(key)
        if isinstance(v, dict):
            if "before_taxes" in v or "after_taxes" in v or "taxes" in v:
                out.add("2.3.0")
            if "excl_vat" in v or "incl_vat" in v:
                out.add("2.2.1")
    for t in obj.get("tariffs") or []:
        out |= _markers(t)
    return out


def detect_version(*objs) -> tuple[str, bool]:
    """(version, known): known = False when no object carries a version marker (2.2.1 is then assumed)."""
    found: set[str] = set()
    for o in objs:
        found |= _markers(_unwrap(o))
    if len(found) > 1:
        raise InputError("mieszane modele cen: pola 2.3.0 (before_taxes/tax_included) i 2.2.1 (excl_vat/incl_vat) — podaj --ocpi")
    return (found.pop(), True) if found else ("2.2.1", False)


def _pick_tariff(tariff, periods: list[dict]) -> dict:
    tariff = _unwrap(tariff)
    if isinstance(tariff, list):
        if len(tariff) == 1:
            return tariff[0]
        ids = [p.get("tariff_id") for p in periods if p.get("tariff_id")]
        hit = [t for t in tariff if ids and t.get("id") == ids[0]]
        if not hit:
            raise InputError(f"lista {len(tariff)} taryf, a okresy nie wskazują tariff_id jednej z nich")
        return hit[0]
    if not isinstance(tariff, dict):
        raise InputError("taryfa musi być obiektem JSON")
    return tariff


def _line_cost(amount: Decimal, vat, version: str, tax_included: str):
    """(excl, incl, vat %) of one line; excl None = cannot be derived (2.3.0, YES without vat)."""
    v = None if vat is None else _d(vat)
    if version == "2.2.1" or tax_included == "NO":
        return amount, amount * (1 + v / 100) if v is not None else amount, v
    if tax_included == "YES":
        return (amount / (1 + v / 100) if v is not None else None), amount, v
    return amount, amount, None  # N/A: no taxes


def calculate(tariff, session, tz: str = "UTC", version: str = "auto") -> dict:
    session = _unwrap(session)
    try:
        zone = ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError) as e:
        raise InputError(f"nieznana strefa czasowa: {tz}") from e
    warnings: list[str] = []

    def warn(msg):
        if msg not in warnings:
            warnings.append(msg)

    try:
        periods = sorted(session["charging_periods"], key=lambda p: _ts(p["start_date_time"]))
        start, end = _ts(session["start_date_time"]), _ts(session["end_date_time"])
    except (KeyError, TypeError) as e:
        raise InputError(f"brak pola {e} w taryfie lub okresach") from e
    if not periods:
        raise InputError("brak charging_periods")
    tariff = _pick_tariff(tariff, periods)
    try:
        elements = tariff["elements"]
    except (KeyError, TypeError) as e:
        raise InputError(f"brak pola {e} w taryfie lub okresach") from e

    if version == "auto":
        version, known = detect_version(tariff, session)
        if not known:
            warn("wersja OCPI nieustalona z danych (brak tax_included, before_taxes, excl_vat) — przyjęto 2.2.1; podaj --ocpi")
    if version not in VERSIONS:
        raise InputError(f"nieznana wersja OCPI: {version}")
    tax_included = None
    if version == "2.3.0":
        tax_included = tariff.get("tax_included")
        if tax_included is None:
            tax_included = "NO"
            warn("taryfa bez wymaganego w 2.3.0 pola tax_included — przyjęto NO")
        elif tax_included not in TAX_INCLUDED:
            raise InputError(f"zła wartość tax_included: {tax_included!r} (YES, NO, N/A)")

    if any((el.get("restrictions") or {}).get("reservation") for el in elements):
        warn("elementy taryfy z restrykcją reservation (rezerwacja) pominięte — kalkulator nie liczy kosztów rezerwacji")
    if any(d.get("type") == "RESERVATION_TIME" for p in periods for d in p.get("dimensions", [])):
        warn("wymiar RESERVATION_TIME pominięty — kalkulator nie liczy total_reservation_cost")
    for key, cmp in (("start_date_time", lambda t: start < t), ("end_date_time", lambda t: start >= t)):
        if tariff.get(key) and cmp(_ts(tariff[key])):
            warn(f"sesja poza okresem ważności taryfy ({key} = {tariff[key]})")

    lines: list[dict] = []
    energy_so_far = Decimal(0)
    flat_done = False
    for i, p in enumerate(periods):
        p_start = _ts(p["start_date_time"])
        if p.get("tariff_id") and tariff.get("id") and p["tariff_id"] != tariff["id"]:
            warn(f"okres {i}: tariff_id {p['tariff_id']} ≠ id taryfy {tariff['id']} — kalkulator liczy wszystkie okresy jedną taryfą")
        try:
            dims = {d["type"]: _d(d["volume"]) for d in p.get("dimensions", [])}
        except (KeyError, TypeError) as e:
            raise InputError(f"okres {i}: zły wymiar ({e})") from e
        ctx = _Ctx(p_start.astimezone(zone), (p_start - start).total_seconds(), energy_so_far, dims)
        chosen: dict[str, tuple[int, dict]] = {}
        for idx, el in enumerate(elements):
            r = el.get("restrictions")
            if r and r.get("reservation"):
                continue
            # only dimensions that can cost something in this period (FLAT, or a volume present)
            types = {c["type"] for c in el.get("price_components", [])
                     if c["type"] == "FLAT" or c["type"] in dims} - set(chosen)
            if not types or not _matches(r, ctx, warn):
                continue
            for c in el["price_components"]:
                if c["type"] in types and c["type"] not in chosen:
                    chosen[c["type"]] = (idx, c)
        for typ in PRICED:
            if typ not in chosen:
                continue
            idx, comp = chosen[typ]
            if typ == "FLAT":
                if flat_done:
                    continue
                flat_done, volume = True, Decimal(1)
            elif typ in dims:
                volume = dims[typ]
            else:
                continue
            lines.append({"period": i, "start": p["start_date_time"], "type": typ, "element": idx, "volume": volume,
                          "billed": volume, "price": _d(comp["price"]), "vat": comp.get("vat"),
                          "step_size": int(comp.get("step_size") or 1)})
        energy_so_far += dims.get("ENERGY", Decimal(0))

    _apply_step(lines, ("ENERGY",))
    _apply_step(lines, ("TIME", "PARKING_TIME"))

    excl_name, incl_name = PRICE_KEYS[version]
    totals = {k: {"excl": Decimal(0), "incl": Decimal(0), "taxes": {}} for k in COST_KEY.values()}
    for ln in lines:
        if tax_included == "N/A" and ln["vat"] is not None:
            warn("tax_included N/A, a składnik ma vat — vat pominięty (brak podatków)")
        excl, incl, v = _line_cost(ln["billed"] * ln["price"], ln["vat"], version, tax_included)
        if excl is None:
            warn("tax_included YES i składnik bez vat — kwoty przed podatkami nie da się wyliczyć z taryfy")
        if tax_included == "NO" and ln["vat"] is None and ln["price"]:
            warn("składnik bez vat: VAT nie ma zastosowania; inne podatki doliczane poza taryfą kalkulator pomija")
        ln[f"cost_{excl_name}"], ln[f"cost_{incl_name}"] = excl, incl
        t = totals[COST_KEY[ln["type"]]]
        t["excl"] = None if excl is None or t["excl"] is None else t["excl"] + excl
        t["incl"] += incl
        if v is not None and excl is not None:
            t["taxes"][v] = t["taxes"].get(v, Decimal(0)) + (incl - excl)

    excl_all: Decimal | None = Decimal(0)
    incl_all = Decimal(0)
    taxes_all: dict[Decimal, Decimal] = {}
    for t in totals.values():
        excl_all = None if excl_all is None or t["excl"] is None else excl_all + t["excl"]
        incl_all += t["incl"]
        for v, a in t["taxes"].items():
            taxes_all[v] = taxes_all.get(v, Decimal(0)) + a
    limited = False
    for name, op in (("min_price", max), ("max_price", min)):
        lim = tariff.get(name)
        if not lim:
            continue
        if not isinstance(lim, dict) or not (set(lim) & {excl_name, incl_name}):
            raise InputError(f"{name}: oczekiwano pól {excl_name}/{incl_name} (model OCPI {version})")
        new_excl, new_incl = excl_all, incl_all
        if lim.get(excl_name) is not None:
            if excl_all is None:
                warn(f"{name}.{excl_name} nie zastosowane — brak kwoty przed podatkami")
            else:
                new_excl = op(excl_all, _d(lim[excl_name]))
        if lim.get(incl_name) is not None:
            new_incl = op(incl_all, _d(lim[incl_name]))
        if tax_included == "N/A":
            new_incl = new_excl
        if (new_excl, new_incl) != (excl_all, incl_all):
            warn(f"{name} zastosowane: {_num(excl_all)}/{_num(incl_all)} → {_num(new_excl)}/{_num(new_incl)}")
            limited = True
        excl_all, incl_all = new_excl, new_incl
    if limited and version == "2.3.0":
        taxes_all = {} if excl_all is None or incl_all == excl_all else {None: incl_all - excl_all}
        if taxes_all:
            warn("podział podatków po min_price/max_price nie jest określony w OCPI — taxes = jedna pozycja z różnicą")

    def price(excl, incl, taxes) -> dict:
        if version == "2.2.1":
            return {"excl_vat": _num(excl), "incl_vat": _num(incl)}
        tax_list = [{"name": "VAT", **({"percentage": float(v)} if v is not None else {}), "amount": _num(a)}
                    for v, a in sorted(taxes.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))]
        return {"before_taxes": _num(excl), "taxes": tax_list, "after_taxes": _num(incl)}

    used = {COST_KEY[ln["type"]] for ln in lines}
    out = {"ocpi_version": version, "currency": tariff.get("currency")}
    if version == "2.3.0":
        out["tax_included"] = tax_included
    out["total_cost"] = price(excl_all, incl_all, taxes_all)
    for key, t in totals.items():
        out[key] = price(t["excl"], t["incl"], t["taxes"]) if key in used else None

    def dim_sum(kind):
        return sum((_d(d["volume"]) for p in periods for d in p.get("dimensions", []) if d["type"] == kind), Decimal(0))

    out["total_energy"] = _num(dim_sum("ENERGY"))
    out["total_time"] = _num(_d((end - start).total_seconds()) / 3600)
    out["total_parking_time"] = _num(dim_sum("PARKING_TIME"))
    num_keys = ("volume", "billed", "price", f"cost_{excl_name}", f"cost_{incl_name}")
    out["lines"] = [{**ln, **{k: _num(ln[k]) for k in num_keys}} for ln in lines]
    out["warnings"] = warnings
    out["_has_energy"] = any(d["type"] == "ENERGY" for p in periods for d in p.get("dimensions", []))
    return out


def _apply_step(lines: list[dict], types: tuple[str, ...]) -> None:
    """step_size once per session [OCPI230 §10.3.1]: the session total of the dimension, step of its last paid
    component, extra amount to the last paid period of that dimension (for time [OCPI230 §11.4.2.1]; for ENERGY a
    choice of this tool). With TIME and
    PARKING_TIME both paid only parking is rounded [OCPI230 §10.3.1]."""
    relevant = [ln for ln in lines if ln["type"] in types]
    if not relevant:
        return
    typ = "PARKING_TIME" if any(ln["type"] == "PARKING_TIME" for ln in relevant) else relevant[-1]["type"]
    same = [ln for ln in relevant if ln["type"] == typ]
    last = same[-1]
    unit = STEP_UNIT[typ]
    total = sum(ln["billed"] for ln in same) * unit
    # CDR volumes have 4 decimals [OCPI230 §17.7] (0.6667 h ≠ 2400 s): round to 1 s / 0.01 Wh before the step
    total = total.quantize(Decimal("0.01") if typ == "ENERGY" else Decimal("1"), rounding=ROUND_HALF_UP)
    step = Decimal(max(last["step_size"], 1))
    rounded = Decimal(math.ceil(total / step)) * step
    others = sum(ln["billed"] for ln in same if ln is not last)
    last["billed"] = max(rounded / unit - others, last["billed"])


def _price_parts(p: dict, version: str) -> dict:
    """Comparable parts of a Price: 2.2.1 excl_vat / incl_vat, 2.3.0 before_taxes / taxes (sum of amounts)."""
    if version == "2.2.1":
        return {k: p.get(k) for k in ("excl_vat", "incl_vat") if p.get(k) is not None}
    out = {}
    if p.get("before_taxes") is not None:
        out["before_taxes"] = p["before_taxes"]
    if "taxes" in p:
        out["taxes"] = float(sum((_d(t.get("amount", 0)) for t in p.get("taxes") or []), Decimal(0)))
    return out


def compare(result: dict, cdr, tolerance: float = 0.01) -> list[dict]:
    """Differences between the calculation and the costs and times in the CDR (only fields present in the CDR)."""
    cdr = _unwrap(cdr)
    version = result["ocpi_version"]
    found = _markers({k: cdr.get(k) for k in ("total_cost", *COST_KEY.values())})
    if found and version not in found:
        raise InputError(f"CDR w modelu cen {'/'.join(sorted(found))}, a obliczenie w {version} — podaj --ocpi")
    tol = _d(tolerance)
    diffs = []
    for key in ("total_cost", *COST_KEY.values()):
        theirs = cdr.get(key)
        if not theirs:
            continue
        mine_price = result.get(key)
        if mine_price is None:
            ours = None  # dimension not priced by the tariff: compare with 0
        elif version == "2.3.0" and mine_price["before_taxes"] is None:
            continue  # not derivable from the tariff (tax_included YES without vat)
        else:
            ours = _price_parts(mine_price, version)
        for part, value in _price_parts(theirs, version).items():
            mine = 0.0 if ours is None else ours.get(part)
            if mine is None:
                continue
            if abs(_d(mine) - _d(value)) > tol:
                diffs.append({"field": f"{key}.{part}", "calculated": mine, "cdr": value})
    for key in ("total_energy", "total_time", "total_parking_time"):
        if cdr.get(key) is None or (key == "total_energy" and not result.get("_has_energy")):
            continue
        if abs(_d(result[key]) - _d(cdr[key])) > tol:
            diffs.append({"field": key, "calculated": result[key], "cdr": cdr[key]})
    return diffs


def _load(path: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise InputError(f"nie można odczytać {path}: {e.strerror}") from e
    except json.JSONDecodeError as e:
        raise InputError(f"{path}: zły JSON ({e.msg}, linia {e.lineno})") from e


def _fmt(p: dict, version: str) -> str:
    if version == "2.2.1":
        return f"{p['excl_vat']} / {p['incl_vat']}"
    taxes = ", ".join(f"{t['name']} {t.get('percentage', '?')}%: {t['amount']}" for t in p["taxes"])
    return f"{p['before_taxes']} / {p['after_taxes']}" + (f" ({taxes})" if taxes else "")


def describe(r: dict, diffs: list[dict] | None) -> str:
    cur = r["currency"] or ""
    v = r["ocpi_version"]
    tc = r["total_cost"]
    if v == "2.2.1":
        head = f"Koszt sesji (OCPI 2.2.1): {tc['excl_vat']} {cur} bez VAT, {tc['incl_vat']} {cur} z VAT"
    else:
        head = (f"Koszt sesji (OCPI 2.3.0, tax_included {r['tax_included']}): {tc['before_taxes']} {cur} przed podatkami, "
                f"{tc['after_taxes']} {cur} po podatkach")
    out = [head]
    for key in COST_KEY.values():
        if r.get(key):
            out.append(f"  {key}: {_fmt(r[key], v)}")
    out.append(f"  energia {r['total_energy']} kWh, czas sesji {r['total_time']} h, postój {r['total_parking_time']} h")
    excl = "cost_excl_vat" if v == "2.2.1" else "cost_before_taxes"
    incl = "cost_incl_vat" if v == "2.2.1" else "cost_after_taxes"
    for ln in r["lines"]:
        out.append(f"  okres {ln['period']} {ln['start']} {ln['type']}: {ln['volume']} → {ln['billed']} × {ln['price']}"
                   f" (element {ln['element']}, step {ln['step_size']}) = {ln[excl]} / {ln[incl]}")
    out += [f"  ⚠ {w}" for w in r["warnings"]]
    if diffs is not None:
        out.append("✓ zgodne z CDR" if not diffs else "✗ rozbieżności z CDR:")
        out += [f"  - {d['field']}: wyliczone {d['calculated']}, w CDR {d['cdr']}" for d in diffs]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Cena sesji z taryfy OCPI 2.3.0 / 2.2.1 i porównanie z CDR (bez sieci).")
    ap.add_argument("tariff", help="taryfa OCPI (JSON)")
    ap.add_argument("periods", help="obiekt z start_date_time, end_date_time i charging_periods (np. CDR)")
    ap.add_argument("--cdr", help="CDR do porównania kosztów")
    ap.add_argument("--ocpi", choices=("auto", *VERSIONS), default="auto", help="model cen (domyślnie z danych)")
    ap.add_argument("--tz", default="UTC", help="strefa czasowa lokacji (IANA), np. Europe/Warsaw")
    ap.add_argument("--tolerance", type=float, default=0.01, help="dopuszczalna różnica kwot i czasów")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        tariff, periods = _load(args.tariff), _load(args.periods)
        cdr = _load(args.cdr) if args.cdr else None
        version = args.ocpi
        if version == "auto":
            version, known = detect_version(tariff, periods, *([cdr] if cdr is not None else []))
            if not known:
                version = "auto"  # let calculate() add the warning
        result = calculate(tariff, periods, args.tz, version)
        diffs = compare(result, cdr, args.tolerance) if cdr is not None else None
    except InputError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2
    result.pop("_has_energy", None)
    if args.json:
        print(json.dumps({**result, **({"cdr_diffs": diffs} if diffs is not None else {})}, ensure_ascii=False, indent=1))
    else:
        print(describe(result, diffs))
    return 1 if diffs else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
