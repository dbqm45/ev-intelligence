#!/usr/bin/env python3
"""Check OCPP-J frames from a log against the official OCA JSON schemas.

  python3 ocpp_frame_check.py --version 1.6|2.0.1|2.1 --schemas <dir with OCA JSON schemas> <log file | ->

For every line containing an OCPP-J frame ([2,...] CALL, [3,...] CALLRESULT, [4,...] CALLERROR; in 2.1 also
[5,...] CALLRESULTERROR and [6,...] SEND) the script:
  - checks the frame structure and the message type number allowed for the version,
  - validates CALL / SEND payloads against <Action>.json (1.6) or <Action>Request.json (2.x),
  - pairs CALLRESULT with the earlier CALL by messageId and validates against <Action>Response.json,
  - checks CALLERROR error codes against the list of the version.

The schemas are NOT shipped (OCA licence CC BY-ND 4.0): download the official package (see sources/oca-ocpp.yaml) and
pass its directory; files are found recursively by name.
Output: first line "Werdykt: OK" or "Werdykt: BŁĘDY (…)", then one line per frame. Exit 0 = OK, 1 = errors, 2 = usage.
Requires the `jsonschema` package. Network: none.

Sources of the fixed lists: OCPP-J 1.6 §4.1.3 and §4.2.3; OCPP 2.0.1 Ed4 Part 4 §4.1.3 and §4.3; OCPP 2.1 Ed2 Part 4
§4.1.3 and §4.3.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ERROR_CODES = {
    "1.6": {"NotImplemented", "NotSupported", "InternalError", "ProtocolError", "SecurityError", "FormationViolation",
            "PropertyConstraintViolation", "OccurenceConstraintViolation", "TypeConstraintViolation", "GenericError"},
    "2.0.1": {"FormatViolation", "GenericError", "InternalError", "MessageTypeNotSupported", "NotImplemented",
              "NotSupported", "OccurrenceConstraintViolation", "PropertyConstraintViolation", "ProtocolError",
              "RpcFrameworkError", "SecurityError", "TypeConstraintViolation"},
}
ERROR_CODES["2.1"] = ERROR_CODES["2.0.1"]
MESSAGE_TYPES = {"1.6": {2, 3, 4}, "2.0.1": {2, 3, 4}, "2.1": {2, 3, 4, 5, 6}}
NAMES = {2: "CALL", 3: "CALLRESULT", 4: "CALLERROR", 5: "CALLRESULTERROR", 6: "SEND"}
FRAME_START = re.compile(r"\[\s*[2-6]\s*,")


def index_schemas(directory: Path) -> dict[str, Path]:
    return {p.name: p for p in directory.rglob("*.json")}


def schema_file(index: dict[str, Path], version: str, action: str, response: bool) -> Path | None:
    if response:
        return index.get(f"{action}Response.json")
    candidates = [f"{action}.json"] if version == "1.6" else [f"{action}Request.json", f"{action}.json"]
    for name in candidates:
        if name in index:
            return index[name]
    return None


def validate(path: Path, payload, cache: dict) -> list[str]:
    import jsonschema  # imported lazily so that --help works without it
    if path not in cache:
        schema = json.loads(path.read_text(encoding="utf-8"))
        cls = jsonschema.validators.validator_for(schema)
        cache[path] = cls(schema)
    errors = []
    for err in sorted(cache[path].iter_errors(payload), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{where}: {err.message}")
    return errors


def extract_frame(line: str):
    m = FRAME_START.search(line)
    if not m:
        return None
    try:
        frame, _ = json.JSONDecoder().raw_decode(line[m.start():])
    except json.JSONDecodeError as exc:
        return {"_error": f"niepoprawny JSON ramki: {exc.msg}"}
    return frame


def check_lines(lines, version: str, schemas: Path) -> list[dict]:
    index = index_schemas(Path(schemas))
    cache: dict = {}
    pending: dict[str, str] = {}
    results = []
    for no, line in enumerate(lines, 1):
        frame = extract_frame(line)
        if frame is None:
            continue
        res = {"line": no, "type": None, "action": None, "id": None, "errors": []}
        results.append(res)
        if isinstance(frame, dict):
            res["errors"].append(frame["_error"])
            continue
        if not isinstance(frame, list) or len(frame) < 3 or not isinstance(frame[1], str):
            res["errors"].append("ramka nie ma postaci [typ, \"messageId\", …]")
            continue
        mtype, mid = frame[0], frame[1]
        res["type"], res["id"] = NAMES.get(mtype, str(mtype)), mid
        if mtype not in MESSAGE_TYPES[version]:
            res["errors"].append(f"typ ramki {mtype} nie istnieje w OCPP-J {version}")
            continue
        if mtype in (2, 6):
            if len(frame) != 4 or not isinstance(frame[2], str):
                res["errors"].append(f"{NAMES[mtype]} musi mieć 4 elementy: [{mtype}, id, akcja, payload]")
                continue
            res["action"] = frame[2]
            if mtype == 2:
                pending[mid] = frame[2]
            path = schema_file(index, version, frame[2], response=False)
            if path is None:
                res["errors"].append(f"brak schematu dla akcji {frame[2]} w {version} (nieznana akcja?)")
            else:
                res["errors"] += validate(path, frame[3], cache)
        elif mtype == 3:
            if len(frame) != 3:
                res["errors"].append("CALLRESULT musi mieć 3 elementy: [3, id, payload]")
                continue
            action = pending.pop(mid, None)
            if action is None:
                res["errors"].append("brak wcześniejszego CALL o tym messageId — nie można dobrać schematu odpowiedzi")
                continue
            res["action"] = action
            path = schema_file(index, version, action, response=True)
            if path is None:
                res["errors"].append(f"brak schematu odpowiedzi dla {action}")
            else:
                res["errors"] += validate(path, frame[2], cache)
        else:  # 4 CALLERROR, 5 CALLRESULTERROR
            if len(frame) != 5:
                res["errors"].append(f"{NAMES[mtype]} musi mieć 5 elementów: [{mtype}, id, kod, opis, szczegóły]")
                continue
            res["action"] = pending.pop(mid, None) if mtype == 4 else None
            if frame[2] not in ERROR_CODES[version]:
                res["errors"].append(f"kod błędu {frame[2]!r} nie należy do listy OCPP-J {version}")
    for r in results:
        r["ok"] = not r["errors"]
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True, choices=sorted(MESSAGE_TYPES))
    ap.add_argument("--schemas", required=True, help="katalog ze schematami JSON OCA (przeszukiwany rekurencyjnie)")
    ap.add_argument("log", help="plik logu albo '-' dla stdin")
    a = ap.parse_args(argv)
    schemas = Path(a.schemas)
    if not schemas.is_dir() or not any(schemas.rglob("*.json")):
        print(f"Werdykt: BŁĄD UŻYCIA — brak schematów JSON w {schemas}")
        return 2
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        print("Werdykt: BŁĄD UŻYCIA — brak pakietu jsonschema (pip install jsonschema)")
        return 2
    lines = sys.stdin.read().splitlines() if a.log == "-" else Path(a.log).read_text(encoding="utf-8").splitlines()
    results = check_lines(lines, a.version, schemas)
    bad = [r for r in results if not r["ok"]]
    print("Werdykt: OK" if not bad else f"Werdykt: BŁĘDY ({len(bad)} z {len(results)} ramek)")
    for r in results:
        head = f"L{r['line']} {r['type'] or '?'} {r['action'] or '-'} id={r['id']}"
        print(f"{head}: OK" if r["ok"] else f"{head}: " + "; ".join(r["errors"]))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
