#!/usr/bin/env python3
"""Composite schedule of one EVSE / connector from OCPP charging profiles (1.6, 2.0.1, 2.1), as GetCompositeSchedule
should report it, with every point the specification leaves open reported instead of guessed.

  python3 composite_schedule.py <profiles.json> --ocpp 1.6|2.0.1|2.1 --evse N --start <ISO> --duration <s>
      [--unit A|W] [--supply AC|DC] [--voltage 230] [--transaction-id ID] [--charging-start <ISO>]
      [--local-limit X] [--priority-charging] [--assume-utc] [--json]

<profiles.json>: a list (or {"profiles": [...]}) of installed profiles as messages: 1.6 SetChargingProfile.req
{connectorId, csChargingProfiles} [16 §6.43]; 2.x SetChargingProfileRequest {evseId, chargingProfile}
[201-P2 §1.51.1]; 2.x ReportChargingProfilesRequest {evseId, chargingLimitSource, chargingProfile: [...]}
[201-P2 §1.43.1] [21-P2 §1.63.1] (the only way to give ChargingStationExternalConstraints and LocalGeneration, which
CSMS must not send [201-P2 K01.FR.22] [201-E §2.15] [21-E §2.16.2]). An OCPP-J CALL [2, id, action, payload] is
unwrapped. --start = moment GetCompositeSchedule is received, --duration = its `duration` [201-P2 K08.FR.02]
[16E §3.29]. Exit code: 0 — complete schedule; 1 — schedule with gaps (no number) or depending on a point the
specification does not define (see `undefined`); 2 — input error or input the tool refuses. Standard library only.
Network: none.

Rules (2.0.1 text; 2.1 identical unless marked; 1.6 differences marked "1.6"):
- Purposes: Max (2.x ChargingStationMaxProfile, 1.6 ChargePointMaxProfile), TxDefaultProfile, TxProfile; 2.x also
  ChargingStationExternalConstraints [201-P2 K §3.2] [16 §3.13.1]; 2.1 also PriorityCharging and LocalGeneration
  [21-P2 K §3.2]. A profile of another version's purpose is an input error.
- Applicable to EVSE n: profiles on n and on EVSE 0 ("a charging profile for EVSE #0 is considered to be active on all
  EVSEs") [201-P2 K §3.4]. Max only on EVSE 0, TxProfile only on EVSE > 0 [201-P2 K §3.2] [201-P2 K01.FR.16]
  [16 §3.13.1]. 1.6: a TxDefaultProfile on the connector replaces the connector-0 TxDefaultProfile only for that
  connector [16 §3.13.1]; same stackLevel → replaced; different stackLevels: not specified → both kept + `undefined`.
- Validity: validFrom inclusive, validTo exclusive [201-P2 K01.FR.36] [201-P2 K01.FR.37]; absent = valid since receipt
  / until replaced [201-P2 §2.10] [16 §7.8] (the tool assumes the profile was received before the window).
- Schedule start: Absolute = startSchedule; Recurring = startSchedule + whole 24 h / 7 days [201-P2 §3.68]
  [16 §7.37] [16E §3.79]; Relative = moment the EVSE is ready to deliver energy (--charging-start): 2.0.1 RECOMMENDED
  [201-P2 K01.FR.42], 2.1 SHALL [21-P2 K01.FR.42], 1.6 "situation-specific start point ... determined by the charge
  point" [16 §7.9] / "relative to start of charging" [16 §7.13]. 1.6 Absolute/Recurring without startSchedule are
  relative to start of charging [16 §7.13] (warning); in 2.x startSchedule is required [201-P2 K01.FR.40].
  Before startSchedule the schedule does not limit [201-P2 K01.FR.30].
- Periods: first startPeriod 0, increasing [201-P2 K01.FR.31] [201-P2 K01.FR.35] [16 §5.16.4] [16 §7.14]; a period lasts
  until the next one or until `duration` [201-P2 K01.FR.12]; periods at or past `duration` are not executed
  [201-P2 K01.FR.11]; no duration = last period continues [201-P2 §2.12] [16 §7.13]. Recurring: periods/duration
  longer than the recurrence are not executed [16 §5.16.4]; 2.x has no such sentence — the tool applies the same cut
  (Wniosek from "restarts every 24 hours" [201-P2 §3.68]) and warns.
- Leading schedule per purpose: the schedule that has a period defined at that time and belongs to the valid profile
  with the highest stackLevel [201-P2 K §3.5] [201-P2 K01.FR.17]. 1.6: "the prevailing charging profile SHALL be the
  charging profile with the highest stackLevel among the profiles that are valid" [16 §3.13.2]; falling back to a lower
  stackLevel is written only for Recurring after `duration` [16 §5.16.4] [16E §3.43]; after `duration` of a
  non-recurring profile (Wniosek from [16E §3.7]: only a highest profile *without* duration never falls back) and
  before startSchedule (Wniosek from "no period of default charging behaviour" [16 §5.16.4]) the tool falls back the
  same way and warns.
- TxProfile overrules TxDefaultProfile [201-P2 K §3.5] [16 §3.13.1]. TxProfile valid but without a period: after its
  duration → fall back to TxDefaultProfile [201-P2 K02.FR.08] (a requirement, which takes precedence over the narrative
  of K §3.5 [201-P2 §2.1.2]); before its startSchedule → not defined (K §3.5: TxDefault not taken into account;
  K01.FR.30: TxProfile does not limit yet) → `undefined`; 1.6 has no rule for either → `undefined`.
  TxProfile counts only with --transaction-id (none without a transaction [201-P2 K01.FR.09] [16 §3.13.1]); 2.x matches
  transactionId [201-P2 K01.FR.04], 1.6 transactionId is optional [16 §7.8]. Without a transaction: computed as if a
  transaction used the TxDefaultProfile [201-P2 K08.FR.06]; 1.6 does not say → `undefined`.
- 2.1 PriorityCharging, when activated (--priority-charging; activation is a station state, not a profile field),
  overrules TxDefaultProfile / TxProfile [21-P2 K §3.6]; it has no duration [21-P2 K01.FR.70].
- Composite: per interval the lowest limit of the leading Max, ExternalConstraints and Tx/TxDefault (or Priority)
  schedules [201-P2 K §3.5] [201-P2 K08.FR.04] [16 §3.13.3]; 2.1: the leading LocalGeneration limit is added on top
  [21-P2 K §3.6] [21-P2 K08.FR.04] (example: 5000 W TxDefault + 2000 W LocalGeneration = 7000 W [21-P2 K27]).
  The Max limit is for all EVSEs combined [201-P2 K §3.5] [16 §3.13.3]: for one EVSE it is an upper bound; the
  station's share between EVSEs and its local limits are not known to the tool (the reported schedule is "only
  indicative") [201-P2 K08] [16 §5.7]. --local-limit (in the output unit) takes part in the minimum.
- No applicable profile: the station "falls back to the local limit of the Charging Station" [201-P2 K02.FR.08]; the
  test cases expect "Local limit of Charging Station" [201-P6] (TC_K_09_CS, TC_K_22_CS, TC_K_23_CS); without profiles
  the transaction runs "as if no constraints apply" [201-P2 K06.FR.02] [16 §3.13.6]. OCPP gives no number: without
  --local-limit the interval has limit null (exit 1). No default current is assumed.
- Units: A = per phase, W = total; AC current per phase = W / (line voltage × numberPhases), nominal voltage of the
  area, numberPhases of the ChargingSchedulePeriod, default 3 [201-P2 K01.FR.49] [201-P2 K01.FR.50]
  [201-P2 K01.FR.51] [16 §7.12]. The composite takes "the different chargingRateUnits into account"
  [201-P2 K §3.5]. A→W is the inverse of that formula (Wniosek). The tool converts only with --supply AC and
  --voltage; DC has no conversion rule → mixing units on DC is refused. Output unit: --unit ("can be used to force a
  power or current profile" [201-P2 §1.20.1] [16 §6.21]); without it, when profiles use different units, the
  specification does not say which unit the station reports → input error.
- numberPhases of a composite period: the lowest of the applicable periods [201-P2 K §3.7]; 1.6 has no rule → omitted
  with a warning when the values differ. DC: numberPhases should be omitted [201-P2 §2.11] → ignored. Conflicting
  phaseToUse → no composite possible [201-P2 K §3.7] → input error.
- `limit` accepts at most one digit fraction [201-P2 §2.11] [16 §7.14]; the tool does not round converted values
  (direction not specified) and warns.
- Input checks (CSMS-side rules; a violating profile would be rejected, so it is an input error): K01.FR.03, .06, .16,
  .19, .31, .35, .38, .39, .40, .41, .60 and duplicated TxDefaultProfile on EVSE 0 / EVSE n [201-P2 K01.FR.52]
  [201-P2 K01.FR.53]; 1.6 same stackLevel and purpose [16 §3.13.2]; same id twice [201-P2 K01.FR.05]. Time values per
  RFC 3339 with offset [201-P2 §2.1.4] (1.6: ISO 8601 [16 §3.15]); without offset only with --assume-utc. The
  2.0.1 / 2.1 examples write "2020-01-09T17:00:00" without offset [201-P2 K §3.6.1].
Refused (exit 2): EVSE 0 (total expected grid consumption [201-P2 K08.FR.03] [16 §5.7] needs the load of all EVSEs);
several chargingSchedules (ISO 15118 choice) [201-P2 K01.FR.34]; 2.1 Dynamic kind, operationMode other than
ChargingOnly (or ExternalLimits for LocalGeneration with a limit), setpoint*, dischargeLimit*, limit_L2/L3 [21-P2 K08.FR.09],
v2x*, evseSleep, limitAtSoC, useLocalTime, dynUpdate*, negative limit [21-P2 §2.18] [21-P2 §2.19] [21-P2 §2.17];
randomizedDelay > 0 (allowed only as 0 for TxDefaultProfile without transaction [21-P2 K08.FR.06] [21-P2 K01.FR.95]).
maxOfflineDuration is ignored with a warning (online calculation).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from decimal import Decimal
from pathlib import Path

VERSIONS = ("1.6", "2.0.1", "2.1")
GROUPS = {
    "1.6": {"ChargePointMaxProfile": "Max", "TxDefaultProfile": "TxDefault", "TxProfile": "Tx"},
    "2.0.1": {"ChargingStationMaxProfile": "Max", "ChargingStationExternalConstraints": "External",
              "TxDefaultProfile": "TxDefault", "TxProfile": "Tx"},
}
GROUPS["2.1"] = {**GROUPS["2.0.1"], "PriorityCharging": "Priority", "LocalGeneration": "LocalGen"}
REPORT_ONLY = {"ChargingStationExternalConstraints": "[201-P2 K01.FR.22] [201-E §2.15]",
               "LocalGeneration": "[21-E §2.16.2]"}
KINDS = ("Absolute", "Recurring", "Relative")
RECUR = {"Daily": 86400, "Weekly": 7 * 86400}
UNSUPPORTED_PERIOD = ("setpoint", "setpoint_L2", "setpoint_L3", "setpointReactive", "setpointReactive_L2",
                      "setpointReactive_L3", "dischargeLimit", "dischargeLimit_L2", "dischargeLimit_L3", "limit_L2",
                      "limit_L3", "v2xBaseline", "v2xFreqWattCurve", "v2xSignalWattCurve")
TENTH = Decimal("0.1")


class InputError(Exception):
    pass


def _iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class _Clock:
    """Parses time values; a value without offset is an error unless --assume-utc [201-P2 §2.1.4]."""

    def __init__(self, assume_utc: bool):
        self.assume_utc, self.naive = assume_utc, False

    def ts(self, v, what: str) -> dt.datetime:
        try:
            t = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        except ValueError as e:
            raise InputError(f"{what}: zła data/czas {v!r}") from e
        if t.tzinfo is None:
            if not self.assume_utc:
                raise InputError(f"{what}: {v!r} bez strefy (RFC 3339 wymaga przesunięcia) — dodaj 'Z' albo "
                                 "użyj --assume-utc")
            self.naive = True
            t = t.replace(tzinfo=dt.timezone.utc)
        return t


def _num(x) -> Decimal:
    if isinstance(x, bool) or not isinstance(x, (int, float, str)):
        raise InputError(f"zła liczba: {x!r}")
    try:
        return Decimal(str(x))
    except ArithmeticError as e:
        raise InputError(f"zła liczba: {x!r}") from e


def _out(x: Decimal | None):
    if x is None:
        return None
    v = float(round(x, 6))
    return int(v) if v == int(v) else v


class Profile:
    def __init__(self, raw: dict, evse: int, source: str, ver: str, ctx: "Ctx"):
        self.raw, self.evse, self.source, self.ver = raw, evse, source, ver
        idk = "chargingProfileId" if ver == "1.6" else "id"
        self.id = raw.get(idk)
        self.name = f"{raw.get('chargingProfilePurpose')}#{self.id}"
        self.purpose = raw.get("chargingProfilePurpose")
        self.group = GROUPS[ver].get(self.purpose)
        self.kind = raw.get("chargingProfileKind")
        self.level = raw.get("stackLevel")
        self.tx_id = raw.get("transactionId")
        self.valid_from = ctx.clock.ts(raw["validFrom"], f"{self.name}.validFrom") if raw.get("validFrom") else None
        self.valid_to = ctx.clock.ts(raw["validTo"], f"{self.name}.validTo") if raw.get("validTo") else None
        sch = raw.get("chargingSchedule")
        if ver != "1.6":
            if not isinstance(sch, list) or not sch:
                raise InputError(f"{self.name}: chargingSchedule ma być listą 1..3 [201-P2 §2.10]")
            if len(sch) > 1:
                raise InputError(f"{self.name}: kilka chargingSchedule (wybór harmonogramu w ISO 15118, K01.FR.34) — "
                                 "narzędzie nie wie, który wybrał pojazd")
            sch = sch[0]
        if not isinstance(sch, dict):
            raise InputError(f"{self.name}: brak chargingSchedule")
        self.sch = sch
        self.unit = sch.get("chargingRateUnit")
        self.duration = sch.get("duration")
        self.start_schedule = ctx.clock.ts(sch["startSchedule"], f"{self.name}.startSchedule") \
            if sch.get("startSchedule") else None
        self.periods = sch.get("chargingSchedulePeriod") or []
        self.recur = RECUR.get(raw.get("recurrencyKind")) if self.kind == "Recurring" else None
        self.anchor: dt.datetime | None = None
        self.cut_warned = False

    # --- schedule geometry -------------------------------------------------------------------------------------
    def valid(self, t: dt.datetime) -> bool:
        return not ((self.valid_from and t < self.valid_from) or (self.valid_to and t >= self.valid_to))

    def cycle_start(self, t: dt.datetime) -> dt.datetime:
        if not self.recur or t < self.anchor:
            return self.anchor
        k = math.floor((t - self.anchor).total_seconds() / self.recur)
        return self.anchor + dt.timedelta(seconds=k * self.recur)

    def state(self, t: dt.datetime):
        """('ok', period) | ('before', None) | ('after', None) at time t (validity checked separately)."""
        s = self.cycle_start(t)
        if t < s:
            return "before", None
        off = (t - s).total_seconds()
        if self.duration is not None and off >= self.duration:
            return "after", None
        if self.recur and off >= self.recur:
            return "after", None
        return "ok", [p for p in self.periods if p["startPeriod"] <= off][-1]

    def breakpoints(self, ws: dt.datetime, we: dt.datetime) -> set:
        pts = {x for x in (self.valid_from, self.valid_to) if x}
        starts = [self.anchor]
        if self.recur:
            k0 = max(0, math.floor((ws - self.anchor).total_seconds() / self.recur) - 1)
            k1 = math.floor((we - self.anchor).total_seconds() / self.recur) + 1
            starts = [self.anchor + dt.timedelta(seconds=k * self.recur) for k in range(k0, k1 + 1)]
        for s in starts:
            pts.update(s + dt.timedelta(seconds=p["startPeriod"]) for p in self.periods)
            if self.duration is not None:
                pts.add(s + dt.timedelta(seconds=self.duration))
            if self.recur:
                pts.add(s + dt.timedelta(seconds=self.recur))
        return {x for x in pts if ws < x < we}


class Ctx:
    def __init__(self, args):
        self.ver = args.ocpp
        self.clock = _Clock(args.assume_utc)
        self.warnings: list[str] = []
        self.undefined: list[str] = []
        self.ignored: list[dict] = []

    def warn(self, msg: str):
        if msg not in self.warnings:
            self.warnings.append(msg)

    def undef(self, msg: str):
        if msg not in self.undefined:
            self.undefined.append(msg)


# --- input ------------------------------------------------------------------------------------------------------
def _messages(data, ver: str):
    """Yields (evseId, profile dict, source) from the input messages."""
    if isinstance(data, dict) and "profiles" in data:
        data = data["profiles"]
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise InputError("wejście: lista komunikatów albo {\"profiles\": [...]}")
    for i, item in enumerate(data):
        if isinstance(item, list) and len(item) == 4 and item[0] == 2:      # OCPP-J CALL
            item = item[3]
        if not isinstance(item, dict):
            raise InputError(f"element {i}: oczekiwany obiekt komunikatu")
        if ver == "1.6":
            if "csChargingProfiles" not in item or "connectorId" not in item:
                raise InputError(f"element {i}: dla 1.6 podaj SetChargingProfile.req {{connectorId, "
                                 "csChargingProfiles}} [16 §6.43]")
            yield item["connectorId"], item["csChargingProfiles"], "SetChargingProfile"
            continue
        if "chargingProfile" not in item or "evseId" not in item:
            raise InputError(f"element {i}: dla {ver} podaj SetChargingProfileRequest {{evseId, chargingProfile}} albo "
                             "ReportChargingProfilesRequest {evseId, chargingLimitSource, chargingProfile: [...]}")
        cp = item["chargingProfile"]
        if isinstance(cp, list):
            for p in cp:
                yield item["evseId"], p, f"ReportChargingProfiles({item.get('chargingLimitSource')})"
        else:
            yield item["evseId"], cp, "SetChargingProfile"


def _validate(p: Profile, ctx: Ctx, args) -> None:
    ver, n = ctx.ver, p.name
    errs = []
    if p.group is None:
        known = ", ".join(GROUPS[ver])
        errs.append(f"cel {p.purpose!r} nie istnieje w OCPP {ver} (dozwolone: {known})")
    if p.purpose in REPORT_ONLY and p.source == "SetChargingProfile":
        errs.append(f"{p.purpose} nie może przyjść od CSMS w SetChargingProfileRequest {REPORT_ONLY[p.purpose]}; "
                    "podaj go jako ReportChargingProfilesRequest")
    if ver == "2.1" and p.kind == "Dynamic":
        errs.append("chargingProfileKind Dynamic (wartości zmieniane na bieżąco) — narzędzie tego nie liczy")
    elif p.kind not in KINDS:
        errs.append(f"nieznany chargingProfileKind {p.kind!r}")
    if not isinstance(p.level, int) or isinstance(p.level, bool) or p.level < 0:
        errs.append(f"stackLevel {p.level!r} — liczba całkowita ≥ 0 [201-P2 §2.10] [16 §7.8]")
    if p.unit not in ("A", "W"):
        errs.append(f"chargingRateUnit {p.unit!r} — dozwolone A albo W")
    if not isinstance(p.evse, int) or isinstance(p.evse, bool) or p.evse < 0:
        errs.append(f"evseId/connectorId {p.evse!r}")
    if p.duration is not None and (not isinstance(p.duration, int) or p.duration < 0):
        errs.append(f"duration {p.duration!r}")
    # periods
    if not p.periods:
        errs.append("brak chargingSchedulePeriod")
    else:
        starts = [x.get("startPeriod") for x in p.periods]
        if any(not isinstance(s, int) or isinstance(s, bool) for s in starts):
            errs.append("startPeriod musi być liczbą całkowitą")
        else:
            if starts[0] != 0:
                errs.append(f"pierwszy startPeriod musi być 0 (jest {starts[0]}) [201-P2 K01.FR.31] [16 §5.16.4]")
            if any(b <= a for a, b in zip(starts, starts[1:])):
                errs.append("startPeriod muszą rosnąć [201-P2 K01.FR.35] [16 §7.14]")
    for x in p.periods:
        if ver == "2.1":
            mode = x.get("operationMode")
            allowed = (None, "ChargingOnly", "ExternalLimits") if p.purpose == "LocalGeneration" else (None, "ChargingOnly")
            if mode not in allowed:
                errs.append(f"operationMode {mode!r} (V2X / setpointy) — narzędzie liczy tylko ChargingOnly")
            bad = [k for k in UNSUPPORTED_PERIOD if k in x]
            if bad:
                errs.append(f"pola okresu {', '.join(bad)} — narzędzie ich nie liczy (m.in. [21-P2 K08.FR.08], "
                            "[21-P2 K08.FR.09])")
            if x.get("evseSleep"):
                errs.append("evseSleep = true — nie liczony")
        if "limit" not in x:
            errs.append("okres bez limit (2.1: dozwolone tylko w trybach z setpointem [21-P2 §2.18])")
            continue
        lim = _num(x["limit"])
        if lim < 0:
            errs.append(f"limit ujemny ({x['limit']}) — w 2.1 tylko dla zgodności wstecz jako rozładowanie "
                        "[21-P2 §2.18]; narzędzie go nie liczy")
        if lim % TENTH:
            ctx.warn(f"{n}: limit {x['limit']} ma więcej niż jedną cyfrę po przecinku [201-P2 §2.11] [16 §7.14]")
        ph = x.get("numberPhases")
        if ph is not None and (not isinstance(ph, int) or isinstance(ph, bool) or not 0 <= ph <= 3):
            errs.append(f"numberPhases {ph!r}")
        if ver != "1.6" and x.get("phaseToUse") is not None and ph != 1:
            errs.append("phaseToUse tylko przy numberPhases = 1 [201-P2 K01.FR.19]")
        if ver == "1.6" and "phaseToUse" in x:
            errs.append("phaseToUse nie istnieje w 1.6 [16 §7.14]")
    # kind / startSchedule / recurrency
    if ver == "1.6":
        if p.kind == "Recurring" and p.raw.get("recurrencyKind") not in RECUR:
            errs.append("Recurring bez recurrencyKind Daily/Weekly — 1.6 nie podaje okresu powtarzania [16 §7.37]")
        if p.kind == "Relative" and p.start_schedule:
            errs.append("Relative ze startSchedule — 1.6 nie określa, od którego punktu liczyć [16 §7.13]")
        if p.group == "Max" and p.evse != 0:
            errs.append("ChargePointMaxProfile tylko na connectorId 0 [16 §3.13.1]")
        if p.group == "Tx" and p.evse == 0:
            errs.append("TxProfile tylko na connectorId > 0 [16 §3.13.1]")
    else:
        if p.kind in ("Absolute", "Recurring") and not p.start_schedule:
            errs.append(f"{p.kind} wymaga startSchedule [201-P2 K01.FR.40]")
        if p.kind == "Relative" and p.start_schedule:
            errs.append("Relative nie może mieć startSchedule [201-P2 K01.FR.41]")
        rk = p.raw.get("recurrencyKind")
        if (p.kind == "Recurring") != (rk is not None) or (rk is not None and rk not in RECUR):
            errs.append("recurrencyKind tylko i zawsze przy Recurring (Daily/Weekly) [201-P2 K01.FR.60]")
        if p.group == "Max" and p.kind == "Relative":
            errs.append("ChargingStationMaxProfile nie może być Relative [201-P2 K01.FR.38]")
        if p.group == "Max" and p.evse != 0:
            errs.append("ChargingStationMaxProfile tylko na evseId 0 [201-P2 K §3.2]")
        if p.group == "Tx" and p.evse == 0:
            errs.append("TxProfile tylko na evseId > 0 [201-P2 K01.FR.16]")
        if p.group == "Tx" and not p.tx_id:
            errs.append("TxProfile bez transactionId [201-P2 K01.FR.03]")
        if p.group != "Tx" and p.tx_id:
            errs.append("transactionId tylko przy TxProfile [201-P2 §2.10]")
    if ver == "2.1":
        if p.group == "Priority" and p.duration is not None:
            errs.append("PriorityCharging nie może mieć duration [21-P2 K01.FR.70]")
        for k in ("dynUpdateInterval", "dynUpdateTime"):
            if k in p.raw:
                errs.append(f"{k} (profil dynamiczny) — nie liczony")
        if p.sch.get("useLocalTime"):
            errs.append("useLocalTime = true — wymaga czasu lokalnego stacji; narzędzie tego nie liczy")
        if "limitAtSoC" in p.sch:
            errs.append("limitAtSoC — zależy od SoC pojazdu; nie liczony")
        rd = p.sch.get("randomizedDelay", 0) or 0
        if rd:
            if p.purpose not in ("TxProfile", "TxDefaultProfile") and p.source == "SetChargingProfile":
                errs.append("randomizedDelay > 0 tylko dla TxProfile/TxDefaultProfile [21-P2 K01.FR.95]")
            elif p.purpose == "TxDefaultProfile" and not args.transaction_id:
                ctx.warn(f"{n}: randomizedDelay pominięty — bez transakcji liczy się z randomizedDelay = 0 "
                         "[21-P2 K08.FR.06]")
            else:
                errs.append("randomizedDelay > 0 przesuwa okresy losowo — wyniku nie da się wyliczyć")
        if "maxOfflineDuration" in p.raw or "invalidAfterOfflineDuration" in p.raw:
            ctx.warn(f"{n}: maxOfflineDuration / invalidAfterOfflineDuration pominięte — obliczenie dla stacji online")
    if errs:
        raise InputError(f"{n} (EVSE {p.evse}): " + "; ".join(errs))


def _overlap(a: Profile, b: Profile) -> bool:
    lo = max(a.valid_from or dt.datetime.min.replace(tzinfo=dt.timezone.utc),
             b.valid_from or dt.datetime.min.replace(tzinfo=dt.timezone.utc))
    hi = min(a.valid_to or dt.datetime.max.replace(tzinfo=dt.timezone.utc),
             b.valid_to or dt.datetime.max.replace(tzinfo=dt.timezone.utc))
    return lo < hi


def _check_installed(profiles: list[Profile], ver: str) -> None:
    seen = {}
    for p in profiles:
        if p.id in seen:
            raise InputError(f"profil id {p.id} podany dwa razy — drugi zastąpiłby pierwszy [201-P2 K01.FR.05] "
                             "[16 §5.16.3]; podaj stan po zastąpieniu")
        seen[p.id] = p
    for i, a in enumerate(profiles):
        for b in profiles[i + 1:]:
            if a.level != b.level or a.purpose != b.purpose:
                continue
            if ver == "1.6":
                if a.evse == b.evse:
                    raise InputError(f"{a.name} i {b.name}: ten sam stackLevel i cel na connectorId {a.evse} — w 1.6 "
                                     "nowszy zastępuje starszy [16 §3.13.2]")
            elif a.group == "Tx":
                if a.tx_id == b.tx_id:
                    raise InputError(f"{a.name} i {b.name}: ten sam stackLevel i transactionId [201-P2 K01.FR.39]")
            elif a.evse == b.evse and _overlap(a, b):
                raise InputError(f"{a.name} i {b.name}: ten sam stackLevel, cel i evseId przy nakładającej się "
                                 "ważności [201-P2 K01.FR.06]")
            elif a.group == "TxDefault" and 0 in (a.evse, b.evse) and a.evse != b.evse:
                raise InputError(f"{a.name} i {b.name}: TxDefaultProfile o tym samym stackLevel na EVSE 0 i na EVSE "
                                 f"{max(a.evse, b.evse)} — stacja odrzuca [201-P2 K01.FR.52] [201-P2 K01.FR.53]")


# --- calculation ------------------------------------------------------------------------------------------------
def _applicable(profiles: list[Profile], ctx: Ctx, args) -> list[Profile]:
    out = []
    for p in profiles:
        if p.evse not in (0, args.evse):
            continue
        if p.group == "Tx":
            if not args.transaction_id:
                ctx.ignored.append({"profile": p.name, "reason": "TxProfile bez transakcji (--transaction-id) — "
                                    "stacja go nie przyjmuje [201-P2 K01.FR.09] [16 §3.13.1]"})
                continue
            if p.tx_id is not None and str(p.tx_id) != str(args.transaction_id):
                ctx.ignored.append({"profile": p.name, "reason": f"inna transakcja ({p.tx_id})"})
                continue
        if p.group == "Priority" and not args.priority_charging:
            ctx.ignored.append({"profile": p.name, "reason": "PriorityCharging nieaktywny (--priority-charging) "
                                "[21-P2 K §3.6]"})
            continue
        out.append(p)
    if ctx.ver == "1.6":
        own = [p for p in out if p.group == "TxDefault" and p.evse == args.evse]
        if own:
            keep = []
            levels = {p.level for p in own}
            for p in out:
                if p.group == "TxDefault" and p.evse == 0:
                    if p.level in levels:
                        ctx.ignored.append({"profile": p.name, "reason": "zastąpiony dla tego złącza przez "
                                            "TxDefaultProfile ze złącza [16 §3.13.1]"})
                        continue
                    ctx.undef(f"{p.name} (złącze 0) i TxDefaultProfile złącza {args.evse} mają różne stackLevel: 1.6 "
                              "mówi tylko, że profil złącza zastępuje profil ze złącza 0 [16 §3.13.1]; narzędzie "
                              "zostawia oba w stosie")
                keep.append(p)
            out = keep
    if args.priority_charging and not any(p.group == "Priority" for p in out):
        raise InputError("--priority-charging bez profilu PriorityCharging dla tego EVSE [21-P2 K §3.6]")
    return out


def _resolve_anchor(p: Profile, ctx: Ctx, args, charging_start):
    if p.kind == "Relative" or (ctx.ver == "1.6" and not p.start_schedule):
        if charging_start is None:
            raise InputError(f"{p.name}: harmonogram liczony od startu ładowania — podaj --charging-start")
        if ctx.ver == "1.6" and p.kind != "Relative":
            ctx.warn(f"{p.name}: {p.kind} bez startSchedule — w 1.6 liczony od startu ładowania [16 §7.13]")
        elif ctx.ver == "1.6":
            ctx.warn("1.6 Relative: punkt startu ustala stacja („determined by the charge point”) [16 §7.9]")
        elif ctx.ver == "2.0.1":
            ctx.warn("2.0.1 Relative: start od gotowości do dostarczania energii jest tylko RECOMMENDED "
                     "[201-P2 K01.FR.42]")
        p.anchor = charging_start
    else:
        p.anchor = p.start_schedule
    if p.recur and (p.duration or 0) > p.recur or p.recur and p.periods[-1]["startPeriod"] >= p.recur:
        src = "[16 §5.16.4]" if ctx.ver == "1.6" else "(Wniosek z [201-P2 §3.68]; 2.x nie ma osobnej reguły)"
        ctx.warn(f"{p.name}: okresy/duration dłuższe niż powtarzanie — reszta nie jest wykonywana {src}")


def _leading(group: list[Profile], t: dt.datetime, ctx: Ctx):
    """Leading schedule of one purpose at t [201-P2 K §3.5]; 1.6 fallbacks get warnings."""
    cands = sorted((p for p in group if p.valid(t)), key=lambda p: -p.level)
    for p in cands:
        st, per = p.state(t)
        if st == "ok":
            return p, per
        if ctx.ver == "1.6":
            if st == "after" and p.recur:
                ctx.warn(f"1.6 {p.name}: po duration powrót do niższego stackLevel [16 §5.16.4] [16E §3.43]")
            elif st == "after":
                ctx.warn(f"1.6 {p.name}: po duration profilu nie-Recurring powrót do niższego stackLevel — Wniosek "
                         "z [16E §3.7], nie zapisany wprost")
            else:
                ctx.warn(f"1.6 {p.name}: przed startSchedule powrót do niższego stackLevel — Wniosek z [16 §5.16.4] "
                         "(„period of default charging behaviour”)")
    return None, None


def _phases(per: dict, supply: str | None):
    if supply == "DC":
        return None
    ph = per.get("numberPhases")
    if ph is None and supply == "AC":
        return 3                                   # [201-P2 K01.FR.49] [16 §7.12]
    return ph


def _convert(v: Decimal, unit_from: str, unit_to: str, phases, args) -> Decimal:
    if unit_from == unit_to:
        return v
    ph = Decimal(phases if phases else 3)
    volt = Decimal(str(args.voltage))
    return v / (volt * ph) if unit_from == "W" else v * volt * ph


def options(**kw) -> argparse.Namespace:
    """Arguments of compute() with the CLI defaults (for use as a library and in tests)."""
    base = {"ocpp": None, "evse": None, "start": None, "duration": None, "unit": None, "supply": None,
            "voltage": None, "transaction_id": None, "charging_start": None, "local_limit": None,
            "priority_charging": False, "assume_utc": False}
    unknown = set(kw) - set(base)
    if unknown:
        raise TypeError(f"nieznane opcje: {sorted(unknown)}")
    return argparse.Namespace(**{**base, **kw})


def compute(data, args) -> dict:
    """Composite schedule for args (argparse.Namespace, see options())."""
    ctx = Ctx(args)
    if args.ocpp not in VERSIONS:
        raise InputError(f"--ocpp: {VERSIONS}")
    if args.evse == 0:
        raise InputError("EVSE / connectorId 0: stacja raportuje łączny oczekiwany pobór z sieci [201-P2 K08.FR.03] "
                         "[16 §5.7]; to zależy od obciążenia wszystkich EVSE, którego profile nie opisują — narzędzie "
                         "liczy tylko EVSE > 0")
    if args.duration <= 0:
        raise InputError("--duration > 0")
    ws = ctx.clock.ts(args.start, "--start")
    we = ws + dt.timedelta(seconds=args.duration)
    cs = ctx.clock.ts(args.charging_start, "--charging-start") if args.charging_start else None

    profiles = []
    for e, p, src in _messages(data, ctx.ver):
        if not isinstance(p, dict):
            raise InputError(f"profil ładowania ma być obiektem, jest {type(p).__name__}")
        profiles.append(Profile(p, e, src, ctx.ver, ctx))
    for p in profiles:
        _validate(p, ctx, args)
    _check_installed(profiles, ctx.ver)
    if args.transaction_id is None and args.ocpp == "1.6":
        if any(p.group == "TxDefault" and p.evse in (0, args.evse) for p in profiles):
            ctx.undef("1.6 bez transakcji: specyfikacja nie mówi, czy GetCompositeSchedule uwzględnia "
                      "TxDefaultProfile (2.0.1 tak: K08.FR.06 [201-P2 K08.FR.06]); narzędzie go uwzględnia")
    app = _applicable(profiles, ctx, args)
    for p in app:
        _resolve_anchor(p, ctx, args, cs)

    units = {p.unit for p in app}
    unit = args.unit or (units.pop() if len(units) == 1 else None)
    if unit is None:
        if not app:
            raise InputError("brak profili dla tego EVSE — podaj --unit")
        raise InputError("profile w A i w W, a bez --unit specyfikacja nie mówi, w jakiej jednostce stacja odpowie "
                         "[201-P2 §1.20.1] [16 §6.21] — podaj --unit")
    if any(p.unit != unit for p in app):
        if args.supply != "AC" or not args.voltage:
            raise InputError("przeliczenie A↔W: specyfikacja podaje wzór tylko dla AC (prąd fazy = W / (napięcie "
                             "× numberPhases)) [201-P2 K01.FR.50] [16 §7.12] — podaj --supply AC i --voltage; dla DC "
                             "reguły nie ma, więc jednostek nie da się łączyć")
        ctx.warn(f"przeliczenie A↔W przy {args.voltage} V (napięcie nominalne, nie zmierzone) [201-P2 K01.FR.50]")
    if args.supply == "DC" and any(x.get("numberPhases") is not None for p in app for x in p.periods):
        ctx.warn("DC: numberPhases pominięte [201-P2 §2.11] (2.0.1 MAY zignorować [201-P2 K01.FR.44]; 2.1 SHOULD "
                 "odrzucić [21-P2 K01.FR.44])")
    local = _num(args.local_limit) if args.local_limit is not None else None

    by_group: dict[str, list[Profile]] = {}
    for p in app:
        by_group.setdefault(p.group, []).append(p)
    cuts = sorted({ws}.union(*(p.breakpoints(ws, we) for p in app)))

    segs = []
    for t in cuts:
        seg = _segment(t, by_group, ctx, args, unit, local)
        seg["startPeriod"] = int((t - ws).total_seconds())
        prev = segs[-1] if segs else None
        key = ("limit", "numberPhases", "phaseToUse", "status", "reason")
        if prev and all(prev.get(k) == seg.get(k) for k in key):
            continue
        segs.append(seg)
    for s in segs:
        if s["limit"] is not None and Decimal(str(s["limit"])) % TENTH:
            ctx.warn("limit w wyniku ma więcej niż jedną cyfrę po przecinku; pole przyjmuje najwyżej jedną "
                     "[201-P2 §2.11] [16 §7.14], a kierunku zaokrąglenia OCPP nie podaje")
    if ctx.clock.naive:
        ctx.warn("czasy bez strefy przyjęte jako UTC (--assume-utc)")

    complete = all(s["limit"] is not None for s in segs)
    periods = [{k: v for k, v in (("startPeriod", s["startPeriod"]), ("limit", s["limit"]),
                                  ("numberPhases", s.get("numberPhases")), ("phaseToUse", s.get("phaseToUse")))
                if v is not None} for s in segs]
    response = None
    if complete:
        if ctx.ver == "1.6":
            response = {"status": "Accepted", "connectorId": args.evse, "scheduleStart": _iso(ws),
                        "chargingSchedule": {"duration": args.duration, "chargingRateUnit": unit,
                                             "chargingSchedulePeriod": periods}}
        else:
            response = {"status": "Accepted", "schedule": {"evseId": args.evse, "duration": args.duration,
                                                           "scheduleStart": _iso(ws), "chargingRateUnit": unit,
                                                           "chargingSchedulePeriod": periods}}
    return {"ocpp": ctx.ver, "evse": args.evse, "scheduleStart": _iso(ws), "duration": args.duration,
            "chargingRateUnit": unit, "periods": segs, "complete": complete, "response": response,
            "undefined": ctx.undefined, "ignored": ctx.ignored, "warnings": ctx.warnings}


def _segment(t, by_group, ctx: Ctx, args, unit, local) -> dict:
    leaders = []                                         # (profile, period) taking part in the minimum
    reason = None
    for g in ("Max", "External"):
        p, per = _leading(by_group.get(g, []), t, ctx)
        if p:
            leaders.append((p, per))
    tx = None
    if "Priority" in by_group:
        tx = _leading(by_group["Priority"], t, ctx)
        tx = tx if tx[0] else None
    if tx is None:
        txp = _leading(by_group.get("Tx", []), t, ctx)
        if txp[0]:
            tx = txp
        else:
            valid_tx = [p for p in by_group.get("Tx", []) if p.valid(t)]
            tdef = _leading(by_group.get("TxDefault", []), t, ctx)
            if valid_tx and tdef[0]:
                if ctx.ver == "1.6":
                    reason = (f"1.6: {valid_tx[0].name} ważny, ale bez okresu w tej chwili — 1.6 nie mówi, czy wtedy "
                              f"działa {tdef[0].name} [16 §3.13.1] [16 §5.16.4]")
                elif any(p.state(t)[0] == "before" for p in valid_tx):
                    reason = (f"{valid_tx[0].name} ważny, ale przed startSchedule: K §3.5 każe pominąć "
                              f"TxDefaultProfile, gdy TxProfile jest ważny [201-P2 K §3.5], a K01.FR.30 mówi tylko, "
                              f"że TxProfile jeszcze nie ogranicza [201-P2 K01.FR.30]; co obowiązuje, nie jest określone")
                else:
                    ctx.warn(f"{valid_tx[0].name} po duration: powrót do TxDefaultProfile [201-P2 K02.FR.08]")
                    tx = tdef
            elif tdef[0]:
                tx = tdef
    if tx:
        leaders.append(tx)
    if reason:
        ctx.undef(f"{_iso(t)}: {reason}")
        return {"limit": None, "status": "NIEOKRESLONE", "reason": reason, "sources": []}

    vals = [(_convert(_num(per["limit"]), p.unit, unit, _phases(per, args.supply), args), p.name)
            for p, per in leaders]
    if local is not None:
        vals.append((local, "limit lokalny (--local-limit)"))
    lg = _leading(by_group.get("LocalGen", []), t, ctx)
    if not vals:
        reason = ("brak profilu: stacja stosuje własny limit lokalny [201-P2 K02.FR.08] [201-P2 K06.FR.02]; OCPP nie "
                  "podaje wartości — podaj --local-limit")
        return {"limit": None, "status": "BRAK_PROFILU", "reason": reason, "sources": []}
    limit, src = min(vals, key=lambda v: v[0])
    sources = [src]
    if lg[0]:
        limit += _convert(_num(lg[1]["limit"]), lg[0].unit, unit, _phases(lg[1], args.supply), args)
        sources.append(f"+ {lg[0].name} [21-P2 K §3.6]")
        leaders.append(lg)
    seg = {"limit": _out(limit), "status": "OK", "reason": None, "sources": sources}
    # numberPhases / phaseToUse [201-P2 K §3.7]
    phs = {_phases(per, args.supply) for _, per in leaders} - {None}
    if phs:
        if ctx.ver == "1.6" and len(phs) > 1:
            ctx.warn(f"{_iso(t)}: różne numberPhases w profilach {sorted(phs)} — 1.6 nie mówi, które podać; pominięte")
        else:
            seg["numberPhases"] = min(phs)
    ptu = {per.get("phaseToUse") for _, per in leaders} - {None}
    if len(ptu) > 1:
        raise InputError(f"{_iso(t)}: sprzeczne phaseToUse {sorted(ptu)} — nie da się złożyć okresu [201-P2 K §3.7]")
    if ptu and seg.get("numberPhases") == 1:
        seg["phaseToUse"] = ptu.pop()
    return seg


# --- CLI --------------------------------------------------------------------------------------------------------
def describe(r: dict) -> str:
    out = [f"Composite schedule OCPP {r['ocpp']}, EVSE {r['evse']}, od {r['scheduleStart']} przez {r['duration']} s "
           f"({r['chargingRateUnit']}):"]
    for s in r["periods"]:
        lim = "—" if s["limit"] is None else s["limit"]
        ph = f"  fazy {s['numberPhases']}" if s.get("numberPhases") else ""
        why = ", ".join(s["sources"]) if s["status"] == "OK" else f"{s['status']}: {s['reason']}"
        out.append(f"  +{s['startPeriod']:>7} s  {lim:>10} {r['chargingRateUnit']}{ph}  ← {why}")
    out += [f"  ? nieokreślone: {u}" for u in r["undefined"]]
    out += [f"  · pominięty {x['profile']}: {x['reason']}" for x in r["ignored"]]
    out += [f"  ⚠ {w}" for w in r["warnings"]]
    if not r["complete"]:
        out.append("✗ harmonogram niepełny: okresy bez liczby (patrz wyżej)")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Composite schedule OCPP 1.6 / 2.0.1 / 2.1 z profili ładowania (bez sieci).")
    ap.add_argument("profiles", help="JSON z komunikatami SetChargingProfile / ReportChargingProfiles")
    ap.add_argument("--ocpp", required=True, choices=VERSIONS)
    ap.add_argument("--evse", "--connector", dest="evse", type=int, required=True, help="evseId / connectorId > 0")
    ap.add_argument("--start", required=True, help="chwila otrzymania GetCompositeSchedule (RFC 3339)")
    ap.add_argument("--duration", type=int, required=True, help="duration z GetCompositeSchedule (s)")
    ap.add_argument("--unit", choices=("A", "W"), help="chargingRateUnit z żądania")
    ap.add_argument("--supply", choices=("AC", "DC"), help="rodzaj EVSE (potrzebny do przeliczeń i faz)")
    ap.add_argument("--voltage", type=float, help="napięcie nominalne obszaru do przeliczenia A↔W (AC)")
    ap.add_argument("--transaction-id", help="transakcja trwa na tym EVSE (dla TxProfile)")
    ap.add_argument("--charging-start", help="chwila gotowości do dostarczania energii (profile Relative)")
    ap.add_argument("--local-limit", type=float, help="limit lokalny stacji w jednostce wyniku (OCPP go nie podaje)")
    ap.add_argument("--priority-charging", action="store_true", help="2.1: PriorityCharging aktywny")
    ap.add_argument("--assume-utc", action="store_true", help="czasy bez strefy traktuj jako UTC")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        try:
            data = json.loads(Path(args.profiles).read_text(encoding="utf-8"))
        except OSError as e:
            raise InputError(f"nie można odczytać {args.profiles}: {e.strerror}") from e
        except json.JSONDecodeError as e:
            raise InputError(f"{args.profiles}: zły JSON ({e.msg}, linia {e.lineno})") from e
        r = compute(data, args)
    except (InputError, KeyError, TypeError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1) if args.json else describe(r))
    return 0 if r["complete"] and not r["undefined"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
