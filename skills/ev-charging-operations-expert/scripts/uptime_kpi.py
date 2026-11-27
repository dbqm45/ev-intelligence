#!/usr/bin/env python3
"""Charging port availability from status/outage intervals: NEVI uptime (23 CFR 680) or an information-only
availability share with a per-cause breakdown (AFIR / OCPP vocabulary, no legal threshold).

  python3 uptime_kpi.py <intervals.json|.csv> --mode nevi --month 2026-10 [--months 3] [--tz UTC]
      [--gaps outage|error] [--map STATUS=up|outage ...] [--json]
  python3 uptime_kpi.py <intervals.json|.csv> --mode info [--from ISO] [--to ISO] [--gaps outage|error]
      [--map STATUS=up|outage ...] [--json]

Input: a JSON list of intervals, or {"intervals": [...]}, or a CSV with a header row. Interval fields:
  port (required), start, end (ISO 8601; no offset = UTC; the interval is [start, end)),
  state (required): "up" | "outage" | "offline" | an OCPP status (2.0.1 ConnectorStatusEnumType or 1.6
  ChargePointStatus), cause (free text, optional), exclusion (optional: utility | vehicle | maintenance | vandalism |
  disaster | outside_hours), evidence (optional reference to the proof, e.g. a utility ticket), power_ok (optional
  true/false: the port dispensed electricity at the minimum power level).
Exit code: 0 — calculated (NEVI: every port in every reported month above 97 %), 1 — NEVI: at least one port in at
least one reported month not above 97 %, 2 — input error. Standard library only. Network: none.

NEVI mode — rules (text of 23 CFR 680, eCFR 2026-11-24):
- Each charging port must have an average annual uptime of greater than 97 % [US-23CFR680 §680.116(b)]. The tool
  checks µ > 97 strictly: exactly 97.000 does not meet the rule.
- A port is "up" when its hardware and software are both online and available for use, or in use, and it
  successfully dispenses electricity in accordance with the minimum power level requirements
  [US-23CFR680 §680.116(b)(1)] (DCFC on AFC: 150 kW per port on request; AC Level 2: 6 kW per port
  [US-23CFR680 §680.106(d)]). The tool cannot measure power: an interval with power_ok false counts as outage; a
  missing power_ok is taken as the declared state (warning).
- Uptime is calculated on a monthly basis for the previous twelve months [US-23CFR680 §680.116(b)(2)] with
  µ = ((525,600 − (T_outage − T_excluded)) / 525,600) × 100, T_outage = total minutes of outage in the previous
  year, T_excluded = minutes of outage caused by: electric utility service interruptions, failure to charge due to
  the fault of the vehicle, scheduled maintenance, vandalism, natural disasters — "provided that the charging station
  operator can demonstrate that the charging port would otherwise be operational"; also excluded are hours outside
  the identified hours of operation of the charging station [US-23CFR680 §680.116(b)(3)]. The 525,600 basis is
  used as written.
- The quarterly data submittal contains uptime, T_outage and T_excluded for each of the previous 3 months and the
  duration of each outage [US-23CFR680 §680.112(a)]: --months 3 and the "outages" list give these values.
- A "charging port" charges one EV at a time, even with several connectors [US-23CFR680 §680.104]: one input
  "port" = one charging port (in OCPP 2.0.1 terms usually an EVSE, not a connector).
Choices of the tool, not the rule (the text does not specify them; listed in the output as tool_choices):
  (a) the 12-month window is the 12 calendar months ending with the reported month, month boundaries in --tz
      (default UTC), and µ of that window is compared with the "average annual uptime" threshold;
  (b) seconds are counted exactly (partial minutes as fractions of a minute); no rounding before the comparison,
      the output shows 4 decimals;
  (c) the window of a leap year has 527,040 minutes, the formula still uses 525,600 (warning);
  (d) an exclusion of the five listed reasons counts only with a non-empty "evidence"; without it the minutes stay in
      T_outage (warning). "outside_hours" does not need evidence: the proviso stands in the sentence with the five
      reasons, the hours of operation are a separate sentence; only outage minutes are excluded, so
      T_excluded <= T_outage and µ <= 100;
  (e) state mapping: OCPP Operative statuses [201-P2 §3.23] [16 §7.7] = up, Inoperative (Unavailable, Faulted) =
      outage; "offline" (no connection to the CSMS) = outage, although chargers must keep charging when the
      network is disrupted [US-23CFR680 §680.114(e)] — change with --map offline=up; Reserved and SuspendedEVSE are
      up unless --map says otherwise (warning);
  (f) minutes of the window not covered by any interval of the port: outage (--gaps outage, default) or input error
      (--gaps error); overlapping intervals of one port are an input error.

Info mode — no legal metric:
- AFIR (consolidated text 2026-01-08) and Implementing Regulation 2025/655 contain no uptime percentage. They require
  dynamic data "Operational status" and "Availability" [AFIR art. 20 ust. 2 lit. f], updated no later than one
  minute after a change [AFIR-655 art. 2]. Operational = "can be used in normal conditions during the opening time
  that is accessible to the public"; non-operational = "cannot be used due to a technical problem or maintenance
  works"; Availability = in use / reserved / not in use [AFIR-655 Annex, tabela F]. "Availability of data" means
  the existence of data in a machine-readable format [AFIR art. 2 pkt 9], not the availability of the charger.
- Poland: the operator transmits the availability of a charging point to EIPA immediately after it changes
  [PL-EMOB art. 42 ust. 6]; the register holds that availability [PL-EMOB art. 42 ust. 3]. The act defines no
  availability metric or threshold.
- OCPP: 2.0.1 Operative = Available, Reserved, Occupied; Inoperative = Unavailable, Faulted [201-P2 §3.23]; the
  AvailabilityState variable replicates ConnectorStatus values [201-APP §4]. 1.6 Operative = Available, Preparing,
  Charging, SuspendedEVSE, SuspendedEV, Finishing, Reserved; Inoperative = Unavailable, Faulted [16 §7.7].
- The tool gives the share of operational minutes in the window and a breakdown of non-operational minutes by cause
  (cause, else exclusion, else state). Mapping OCPP Operative -> AFIR operational and statuses -> in use / reserved
  / not in use is a choice of the tool; the window defaults to the span of the data.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

NEVI_BASIS_MIN = 525600
NEVI_THRESHOLD = 97
EXCLUSIONS = {
    "utility": "electric utility service interruptions",
    "vehicle": "failure to charge due to the fault of the vehicle",
    "maintenance": "scheduled maintenance",
    "vandalism": "vandalism",
    "disaster": "natural disasters",
    "outside_hours": "hours outside the identified hours of operation",
}
NO_EVIDENCE_NEEDED = {"outside_hours"}
# state -> (up?, AFIR availability or None). OCPP 2.0.1 [201-P2 §3.23] and 1.6 [16 §7.7].
STATES = {
    "up": (True, None), "outage": (False, None), "offline": (False, None),
    "Available": (True, "not_in_use"), "Occupied": (True, "in_use"), "Reserved": (True, "reserved"),
    "Preparing": (True, "in_use"), "Charging": (True, "in_use"), "SuspendedEVSE": (True, "in_use"),
    "SuspendedEV": (True, "in_use"), "Finishing": (True, "in_use"),
    "Unavailable": (False, None), "Faulted": (False, None),
}
DOUBTFUL = {"Reserved", "SuspendedEVSE", "offline"}
US = dt.timedelta(microseconds=1)
NOT_RULE = "wybór narzędzia, nie reguły (choice of the tool, not the rule)"

NEVI_CHOICES = [
    ("window", "okno = 12 miesięcy kalendarzowych kończących się miesiącem raportu, granice miesięcy w --tz; µ okna "
               "porównywane z progiem „average annual uptime”"),
    ("minutes", "sekundy liczone dokładnie (części minut jako ułamki), bez zaokrąglania przed porównaniem; wynik z 4 "
                "miejscami po przecinku"),
    ("basis", "podstawa 525 600 min także w oknie z rokiem przestępnym (527 040 min)"),
    ("evidence", "wyłączenie z pięciu przyczyn tylko z niepustym „evidence”; outside_hours bez dowodu; wyłączane są "
                 "tylko minuty przestoju"),
    ("states", "statusy OCPP Operative = up, Inoperative = przestój; offline = przestój; Reserved i SuspendedEVSE = up "
               "(zmiana: --map)"),
    ("gaps", "minuty bez danych: --gaps outage (przestój) albo error; nakładające się przedziały portu = błąd"),
]
INFO_CHOICES = [
    ("metric", "udział minut operational w oknie to miara informacyjna; AFIR, 2025/655 i ustawa o elektromobilności "
               "nie definiują wskaźnika ani progu dostępności"),
    ("states", "Operative OCPP = operational AFIR; Occupied/Preparing/Charging/Suspended*/Finishing = in use, "
               "Reserved = reserved, Available = not in use; offline = non-operational"),
    ("window", "okno domyślnie od najwcześniejszego początku do najpóźniejszego końca danych"),
    ("gaps", "minuty bez danych: --gaps outage (non-operational, przyczyna „no_data”) albo error"),
]


class InputError(Exception):
    pass


def _ts(value, field="czas") -> dt.datetime:
    try:
        t = dt.datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as e:
        raise InputError(f"zła data/czas w polu {field}: {value!r}") from e
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def _iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _min(seconds: Fraction) -> Fraction:
    return seconds / 60


def _f(x: Fraction, nd=4) -> float:
    return round(float(x), nd)


def _bool(v, field):
    if v is None or isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s == "":
        return None
    if s in ("true", "1", "yes", "tak"):
        return True
    if s in ("false", "0", "no", "nie"):
        return False
    raise InputError(f"{field}: oczekiwano true/false, jest {v!r}")


def load(path: str) -> list[dict]:
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise InputError(f"nie można odczytać {path}: {e.strerror}") from e
    if p.suffix.lower() == ".csv":
        rows = list(csv.DictReader(text.splitlines()))
        if not rows:
            raise InputError(f"{path}: pusty CSV")
        return [{k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in r.items() if k} for r in rows]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise InputError(f"{path}: zły JSON ({e.msg}, linia {e.lineno})") from e
    if isinstance(data, dict):
        data = data.get("intervals")
    if not isinstance(data, list):
        raise InputError("oczekiwano listy przedziałów albo obiektu {\"intervals\": [...]}")
    return data


def parse_map(items: list[str]) -> dict:
    out = {}
    for it in items or []:
        state, _, val = it.partition("=")
        if val not in ("up", "outage") or not state:
            raise InputError(f"--map: oczekiwano STATUS=up|outage, jest {it!r}")
        out[state] = val == "up"
    return out


def normalize(rows: list[dict], mapping: dict) -> dict[str, list[dict]]:
    """Validate intervals; return {port: [interval, ...]} sorted by start, without overlaps."""
    ports: dict[str, list[dict]] = {}
    for i, r in enumerate(rows, 1):
        if not isinstance(r, dict):
            raise InputError(f"przedział {i}: oczekiwano obiektu")
        port = r.get("port")
        if port in (None, ""):
            raise InputError(f"przedział {i}: brak pola port")
        state = r.get("state")
        if state not in STATES and state not in mapping:
            raise InputError(f"przedział {i} (port {port}): nieznany stan {state!r} — użyj up/outage/offline, statusu "
                             "OCPP albo --map STATUS=up|outage")
        start, end = _ts(r.get("start"), "start"), _ts(r.get("end"), "end")
        if end <= start:
            raise InputError(f"przedział {i} (port {port}): end musi być po start")
        excl = r.get("exclusion") or None
        if excl is not None and excl not in EXCLUSIONS:
            raise InputError(f"przedział {i} (port {port}): exclusion {excl!r} spoza listy 23 CFR 680.116(b)(3): "
                             + ", ".join(EXCLUSIONS))
        up, avail = STATES.get(state, (None, None))
        if state in mapping:
            up = mapping[state]
        ports.setdefault(str(port), []).append({
            "n": i, "start": start, "end": end, "state": state, "up": up, "availability": avail,
            "cause": r.get("cause") or None, "exclusion": excl, "evidence": (str(r.get("evidence") or "").strip() or None),
            "power_ok": _bool(r.get("power_ok"), f"przedział {i}: power_ok"),
        })
    for pid, ivs in ports.items():
        ivs.sort(key=lambda x: x["start"])
        for a, b in zip(ivs, ivs[1:]):
            if b["start"] < a["end"]:
                raise InputError(f"port {pid}: przedziały {a['n']} i {b['n']} nakładają się")
    return ports


def _clip(iv, ws, we):
    s, e = max(iv["start"], ws), min(iv["end"], we)
    return (s, e) if e > s else None


def _seconds(s, e) -> Fraction:
    return Fraction((e - s) // US, 1_000_000)


def _segments(ivs, ws, we):
    """Clipped segments in [ws, we) plus gaps (iv None)."""
    out, t = [], ws
    for iv in ivs:
        c = _clip(iv, ws, we)
        if not c:
            continue
        if c[0] > t:
            out.append((t, c[0], None))
        out.append((c[0], c[1], iv))
        t = c[1]
    if t < we:
        out.append((t, we, None))
    return out


def _month_bounds(month: str, tz: ZoneInfo, offset: int):
    try:
        y, m = (int(x) for x in month.split("-"))
        if not 1 <= m <= 12:
            raise ValueError
    except ValueError as e:
        raise InputError(f"--month: oczekiwano RRRR-MM, jest {month!r}") from e
    idx = y * 12 + (m - 1) + offset
    def first(i):
        return dt.datetime(i // 12, i % 12 + 1, 1, tzinfo=tz)
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}", first(idx - 11), first(idx), first(idx + 1)


def nevi(ports: dict, month: str, months: int = 1, tz: str = "UTC", gaps: str = "outage") -> dict:
    try:
        zone = ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError) as e:
        raise InputError(f"nieznana strefa czasowa {tz!r}") from e
    if months < 1:
        raise InputError("--months musi być >= 1")
    warnings: list[str] = []

    def warn(msg):
        if msg not in warnings:
            warnings.append(msg)

    results, below = [], []
    span_start = span_end = None
    for off in range(-(months - 1), 1):
        label, ws, mstart, we = _month_bounds(month, zone, off)
        span_start = span_start or mstart  # first reported month
        span_end = we
        wmin = _min(_seconds(ws, we))
        if wmin != NEVI_BASIS_MIN:
            warn(f"okno {label} ma {wmin} min, a wzór używa 525 600 — zastosowany dosłownie ({NOT_RULE})")
        per_port = {}
        for pid in sorted(ports):
            out_s = exc_s = gap_s = noev_s = lowp_s = Fraction(0)
            for s, e, iv in _segments(ports[pid], ws, we):
                sec = _seconds(s, e)
                if iv is None:
                    gap_s += sec
                    continue
                up = iv["up"]
                if up and iv["power_ok"] is False:
                    up = False
                    lowp_s += sec
                elif up and iv["power_ok"] is None:
                    warn("brak power_ok w przedziałach „up”: przyjęto zadeklarowany stan; reguła wymaga dostawy energii "
                         f"z mocą minimalną z § 680.106(d) ({NOT_RULE})")
                if iv["state"] in DOUBTFUL and iv["state"] != "offline" and iv["up"]:
                    warn(f"stan {iv['state']} policzony jako up ({NOT_RULE}); zmień --map {iv['state']}=outage")
                if iv["state"] == "offline" and not iv["up"]:
                    warn(f"offline policzony jako przestój ({NOT_RULE}); § 680.114(e) wymaga ładowania mimo "
                         "przerwy w łączności — zmień --map offline=up, jeśli port ładował")
                if up:
                    if iv["exclusion"]:
                        warn(f"port {pid}: exclusion w przedziale „up” (nr {iv['n']}) zignorowane")
                    continue
                out_s += sec
                ex = iv["exclusion"]
                if ex and (iv["evidence"] or ex in NO_EVIDENCE_NEEDED):
                    exc_s += sec
                elif ex:
                    noev_s += sec
                    warn(f"port {pid}: wyłączenie {ex} bez evidence (przedział {iv['n']}) — minuty zostają w T_outage; "
                         "reguła wymaga wykazania, że port inaczej by działał")
            if gap_s:
                if gaps == "error":
                    raise InputError(f"port {pid}: {_f(_min(gap_s), 3)} min bez danych w oknie {label} (--gaps error)")
                out_s += gap_s
                warn(f"port {pid}: minuty bez danych w oknie {label} policzone jako przestój ({NOT_RULE})")
            t_out, t_exc = _min(out_s), _min(exc_s)
            mu = (NEVI_BASIS_MIN - (t_out - t_exc)) / Fraction(NEVI_BASIS_MIN) * 100
            ok = mu > NEVI_THRESHOLD
            per_port[pid] = {"uptime_pct": _f(mu), "meets": ok, "t_outage_min": _f(t_out, 3),
                             "t_excluded_min": _f(t_exc, 3), "no_data_min": _f(_min(gap_s), 3),
                             "exclusion_without_evidence_min": _f(_min(noev_s), 3),
                             "below_min_power_min": _f(_min(lowp_s), 3)}
            if not ok:
                below.append({"month": label, "port": pid, "uptime_pct": _f(mu)})
        results.append({"month": label, "window": {"start": _iso(ws), "end": _iso(we), "minutes": _f(wmin, 3)},
                        "ports": per_port})
    outages = {pid: _episodes(ports[pid], span_start, span_end, gaps) for pid in sorted(ports)}
    return {"mode": "nevi", "rule": "23 CFR 680.116(b)", "basis_minutes": NEVI_BASIS_MIN,
            "threshold": f"> {NEVI_THRESHOLD} %", "tz": tz, "months": results,
            "outages_in_reported_months": outages, "below_threshold": below,
            "tool_choices": [{"code": c, "text": t, "note": NOT_RULE} for c, t in NEVI_CHOICES], "warnings": warnings}


def _episodes(ivs, ws, we, gaps):
    """Contiguous outage episodes within [ws, we) (duration of each outage, 23 CFR 680.112(a)(8))."""
    eps = []
    for s, e, iv in _segments(ivs, ws, we):
        if iv is None:
            if gaps != "outage":
                continue
            down, excluded = True, False
        else:
            down = not iv["up"] or iv["power_ok"] is False
            excluded = bool(iv["exclusion"] and (iv["evidence"] or iv["exclusion"] in NO_EVIDENCE_NEEDED))
        if not down:
            continue
        sec = _seconds(s, e)
        if eps and eps[-1]["_end"] == s:
            eps[-1]["_end"] = e
            eps[-1]["_sec"] += sec
            eps[-1]["_exc"] += sec if excluded else 0
        else:
            eps.append({"_start": s, "_end": e, "_sec": sec, "_exc": sec if excluded else Fraction(0)})
    return [{"start": _iso(x["_start"]), "end": _iso(x["_end"]), "duration_min": _f(_min(x["_sec"]), 3),
             "excluded_min": _f(_min(x["_exc"]), 3)} for x in eps]


def info(ports: dict, start: str | None = None, end: str | None = None, gaps: str = "outage") -> dict:
    all_iv = [iv for ivs in ports.values() for iv in ivs]
    if not all_iv:
        raise InputError("brak przedziałów")
    ws = _ts(start, "--from") if start else min(iv["start"] for iv in all_iv)
    we = _ts(end, "--to") if end else max(iv["end"] for iv in all_iv)
    if we <= ws:
        raise InputError("koniec okna musi być po początku")
    wsec = _seconds(ws, we)
    per_port = {}
    for pid in sorted(ports):
        op = nonop = gap = Fraction(0)
        avail = {"in_use": Fraction(0), "reserved": Fraction(0), "not_in_use": Fraction(0), "unspecified": Fraction(0)}
        causes: dict[str, Fraction] = {}
        for s, e, iv in _segments(ports[pid], ws, we):
            sec = _seconds(s, e)
            if iv is None:
                gap += sec
                continue
            if iv["up"]:
                op += sec
                avail[iv["availability"] or "unspecified"] += sec
            else:
                nonop += sec
                key = iv["cause"] or iv["exclusion"] or iv["state"]
                causes[key] = causes.get(key, Fraction(0)) + sec
        if gap:
            if gaps == "error":
                raise InputError(f"port {pid}: {_f(_min(gap), 3)} min bez danych w oknie (--gaps error)")
            nonop += gap
            causes["no_data"] = causes.get("no_data", Fraction(0)) + gap
        per_port[pid] = {
            "operational_share_pct": _f(op / wsec * 100), "operational_min": _f(_min(op), 3),
            "non_operational_min": _f(_min(nonop), 3), "no_data_min": _f(_min(gap), 3),
            "availability_min": {k: _f(_min(v), 3) for k, v in avail.items()},
            "non_operational_by_cause_min": {k: _f(_min(v), 3) for k, v in sorted(causes.items(), key=lambda kv: -kv[1])},
        }
    return {"mode": "info", "legal_metric": None,
            "note": "AFIR, rozporządzenie 2025/655 i ustawa o elektromobilności nie definiują wskaźnika ani progu "
                    "dostępności; wynik jest informacyjny, nie prawny.",
            "window": {"start": _iso(ws), "end": _iso(we), "minutes": _f(_min(wsec), 3)}, "ports": per_port,
            "tool_choices": [{"code": c, "text": t, "note": NOT_RULE} for c, t in INFO_CHOICES], "warnings": []}


def describe(r: dict) -> str:
    out = []
    if r["mode"] == "nevi":
        out.append(f"NEVI uptime (23 CFR 680.116(b)), podstawa 525 600 min, próg {r['threshold']}, strefa {r['tz']}")
        for m in r["months"]:
            out.append(f" miesiąc {m['month']} (okno {m['window']['start']} → {m['window']['end']}):")
            out.append(f"  {'port':<14} {'µ %':>9} {'T_outage':>11} {'T_excl.':>10} {'bez danych':>11}")
            for pid, p in m["ports"].items():
                mark = "✓" if p["meets"] else "✗"
                out.append(f"  {pid:<14} {p['uptime_pct']:>9.4f} {p['t_outage_min']:>11} {p['t_excluded_min']:>10} "
                           f"{p['no_data_min']:>11} {mark}")
        out.append("✓ każdy port powyżej 97 %" if not r["below_threshold"] else
                   "✗ nie powyżej 97 %: " + ", ".join(f"{b['port']} ({b['month']}: {b['uptime_pct']})"
                                                     for b in r["below_threshold"]))
        for pid, eps in r["outages_in_reported_months"].items():
            for e in eps:
                out.append(f"  przestój {pid}: {e['start']} → {e['end']}, {e['duration_min']} min "
                           f"(wyłączone {e['excluded_min']})")
    else:
        w = r["window"]
        out.append(f"Dostępność informacyjna (nie metryka prawna), okno {w['start']} → {w['end']} ({w['minutes']} min)")
        out.append("  " + r["note"])
        for pid, p in r["ports"].items():
            out.append(f"  {pid}: operational {p['operational_share_pct']} % ({p['operational_min']} min), "
                       f"non-operational {p['non_operational_min']} min, bez danych {p['no_data_min']} min")
            a = p["availability_min"]
            out.append(f"    in use {a['in_use']}, reserved {a['reserved']}, not in use {a['not_in_use']}, "
                       f"nieokreślone {a['unspecified']} min")
            for k, v in p["non_operational_by_cause_min"].items():
                out.append(f"    przyczyna {k}: {v} min")
    out.append("Wybory narzędzia, nie reguły (choice of the tool, not the rule):")
    out += [f"  - [{c['code']}] {c['text']}" for c in r["tool_choices"]]
    out += [f"  ⚠ {w}" for w in r["warnings"]]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Dostępność portów ładowania: NEVI (23 CFR 680) albo informacyjnie "
                                             "(AFIR/OCPP, bez progu). Bez sieci.")
    ap.add_argument("data", help="przedziały stanu portów (JSON albo CSV)")
    ap.add_argument("--mode", choices=("nevi", "info"), required=True)
    ap.add_argument("--month", help="NEVI: miesiąc raportu RRRR-MM (okno = 12 miesięcy kończących się nim)")
    ap.add_argument("--months", type=int, default=1, help="NEVI: liczba kolejnych miesięcy do policzenia (np. 3)")
    ap.add_argument("--tz", default="UTC", help="NEVI: strefa granic miesięcy (IANA), domyślnie UTC")
    ap.add_argument("--from", dest="start", help="info: początek okna (ISO)")
    ap.add_argument("--to", dest="end", help="info: koniec okna (ISO)")
    ap.add_argument("--gaps", choices=("outage", "error"), default="outage", help="minuty bez danych")
    ap.add_argument("--map", action="append", default=[], help="STATUS=up|outage (powtarzalne)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        ports = normalize(load(args.data), parse_map(args.map))
        if args.mode == "nevi":
            if not args.month:
                raise InputError("--mode nevi wymaga --month RRRR-MM")
            result = nevi(ports, args.month, args.months, args.tz, args.gaps)
        else:
            result = info(ports, args.start, args.end, args.gaps)
    except InputError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1) if args.json else describe(result))
    return 1 if result["mode"] == "nevi" and result["below_threshold"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
