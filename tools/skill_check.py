#!/usr/bin/env python3
"""Bramka jakości skilli EV Intelligence — bez modelu, bez sieci i bez zewnętrznych repozytoriów (docs/SKILLS-WORKFLOW.md).

Kroki:
  taxonomy   — tools/render_taxonomy.py --check (TAXONOMY.md i pochodne zgodne z taxonomy.yaml)
  registry   — każdy skills/<nazwa> jest w taxonomy.yaml → skills, ma prefiks ev- i plik scenariuszy
  unit tests — python3 -m unittest discover tests
  citations  — tools/ev_kb.py check skills knowledge (znaczniki [ID §…] w rejestrze; sekcje w lokalnych kopiach)
  structure  — reguły SKILL.md: frontmatter, opis, katalog z granicami, obowiązkowe akapity i sekcje, references
  scenarios  — format evals/skill_evals/<nazwa>.json: ≥2 trigger ze sprawdzeniami, ≥1 no-trigger z sąsiadem
  routing    — (ostrzeżenia) czy ev_kb route wskazuje skill dla jego scenariuszy trigger

Wynik: linia RESULT: PASS|FAIL; odcisk treści każdego skilla zapisuje evals/skill-gate.json.

  python3 tools/skill_check.py [--skills a,b] [--strict-routing]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ev_kb  # noqa: E402

SKILLS = ROOT / "skills"
EVALS = ROOT / "evals" / "skill_evals"
GATE_OUT = ROOT / "evals" / "skill-gate.json"
TAXONOMY = ROOT / "taxonomy" / "taxonomy.yaml"
PREFIX = "ev-"
DESC_MAX = 170
PARAGRAPHS = ("**Zasada źródeł.**", "**Źródła niedostępne.**", "**Cytowanie w odpowiedzi.**")
SECTIONS = ("## Procedura", "## Przykład", "## Pułapki", "## Źródła")
ROUTE_TOP = 3


def frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def check_structure(name: str) -> list[str]:
    path = SKILLS / name / "SKILL.md"
    fm, body = frontmatter(path.read_text(encoding="utf-8"))
    p = []
    if not fm:
        return [f"{name}: brak frontmattera YAML"]
    if fm.get("name") != name:
        p.append(f"{name}: name w frontmatterze ({fm.get('name')}) ≠ nazwa katalogu")
    desc = str(fm.get("description") or "")
    if not desc.startswith("Użyj"):
        p.append(f"{name}: description zaczyna się od „Użyj …”")
    if len(desc) > DESC_MAX:
        p.append(f"{name}: description ma {len(desc)} znaków (najwyżej {DESC_MAX})")
    meta = fm.get("metadata") or {}
    katalog = str(meta.get("katalog") or "")
    if not katalog.startswith("Użyj"):
        p.append(f"{name}: metadata.katalog zaczyna się od „Użyj …”")
    if "Nie do" not in katalog:
        p.append(f"{name}: metadata.katalog bez granic („Nie do …”)")
    if not str(meta.get("slowa") or "").strip():
        p.append(f"{name}: brak metadata.slowa")
    try:
        dt.date.fromisoformat(str(meta.get("przeglad")))
    except ValueError:
        p.append(f"{name}: metadata.przeglad to nie data RRRR-MM-DD")
    for para in PARAGRAPHS:
        if para not in body:
            p.append(f"{name}: brak akapitu {para}")
    for sec in SECTIONS:
        if not re.search(r"^" + re.escape(sec) + r"\b", body, re.M):
            p.append(f"{name}: brak sekcji „{sec}”")
    refs_dir = SKILLS / name / "references"
    listed = set(re.findall(r"`references/([^`]+\.md)`", body))
    actual = {f.name for f in refs_dir.glob("*.md")} if refs_dir.is_dir() else set()
    for f in sorted(listed - actual):
        p.append(f"{name}: SKILL.md wymienia references/{f}, którego nie ma")
    for f in sorted(actual - listed):
        p.append(f"{name}: references/{f} nie jest wymieniony w SKILL.md")
    return p


def check_scenarios(name: str, names: set[str]) -> list[str]:
    path = EVALS / f"{name}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{name}: scenariusze nieczytelne ({exc})"]
    p = []
    if data.get("skill") != name:
        p.append(f"{name}: pole skill w scenariuszach ≠ {name}")
    sc = data.get("scenarios") or []
    ids = [s.get("id") for s in sc]
    if len(ids) != len(set(ids)):
        p.append(f"{name}: powtórzone id scenariuszy")
    trig = [s for s in sc if s.get("expect") == "trigger"]
    notrig = [s for s in sc if s.get("expect") == "no-trigger"]
    if len(trig) < 2:
        p.append(f"{name}: mniej niż 2 scenariusze trigger")
    if not notrig:
        p.append(f"{name}: brak scenariusza no-trigger")
    for s in sc:
        sid = s.get("id", "?")
        if s.get("expect") not in ("trigger", "no-trigger"):
            p.append(f"{name}/{sid}: expect to trigger albo no-trigger")
        if not str(s.get("prompt") or "").strip():
            p.append(f"{name}/{sid}: pusty prompt")
        if s.get("expect") == "trigger":
            checks = s.get("checks") or {}
            if not checks.get("all"):
                p.append(f"{name}/{sid}: trigger bez checks.all")
            for group in checks.get("all", []) or []:
                for rx in group if isinstance(group, list) else [group]:
                    try:
                        re.compile(rx)
                    except re.error as exc:
                        p.append(f"{name}/{sid}: zły regex „{rx}” ({exc})")
            for rx in checks.get("none", []) or []:
                try:
                    re.compile(rx)
                except re.error as exc:
                    p.append(f"{name}/{sid}: zły regex „{rx}” ({exc})")
        if s.get("expect") == "no-trigger":
            nb = s.get("neighbor")
            if not nb:
                p.append(f"{name}/{sid}: no-trigger bez neighbor")
            elif nb.startswith(PREFIX) and nb not in names:
                p.append(f"{name}/{sid}: neighbor {nb} nie istnieje")   # sąsiad spoza ev- to skill zewnętrzny
    return p


def check_routing(name: str) -> list[str]:
    data = json.loads((EVALS / f"{name}.json").read_text(encoding="utf-8"))
    warn = []
    for s in data.get("scenarios", []):
        ranked = [r["skill"] for r in ev_kb.cmd_route(s.get("prompt", ""), 20, ROOT)["skills"]]
        if s.get("expect") == "trigger" and name not in ranked[:ROUTE_TOP]:
            warn.append(f"{name}/{s.get('id')}: route nie daje skilla w top {ROUTE_TOP} ({', '.join(ranked[:ROUTE_TOP])})")
        nb = s.get("neighbor")
        if (s.get("expect") == "no-trigger" and nb and nb.startswith(PREFIX) and name in ranked
                and (nb not in ranked or ranked.index(name) < ranked.index(nb))):
            warn.append(f"{name}/{s.get('id')}: route stawia {name} przed sąsiadem {nb}")
    return warn


def fingerprint(name: str) -> str:
    h = hashlib.sha256()
    for f in sorted((SKILLS / name).rglob("*")):
        if f.is_file():
            h.update(f.relative_to(SKILLS).as_posix().encode())
            h.update(f.read_bytes())
    scen = EVALS / f"{name}.json"
    if scen.exists():
        h.update(scen.read_bytes())
    return h.hexdigest()[:16]


def run(label: str, cmd: list[str]) -> bool:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(f"{'✓' if r.returncode == 0 else '✗'} {label}")
    if r.returncode:
        out = (r.stdout + r.stderr).strip().splitlines()
        print("    " + "\n    ".join(out[-40:]))
    return r.returncode == 0


def report(label: str, problems: list[str], fatal: bool = True) -> bool:
    mark = "✓" if not problems else ("✗" if fatal else "⚠")
    print(f"{mark} {label}" + (f" — {len(problems)}" if problems else ""))
    for x in problems:
        print(f"    {x}")
    return not problems or not fatal


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills", default="", help="nazwy skilli po przecinku (domyślnie wszystkie)")
    ap.add_argument("--strict-routing", action="store_true", help="ostrzeżenia routingu traktuj jako błędy")
    a = ap.parse_args(argv)
    all_names = sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))
    names = [s.strip() for s in a.skills.split(",") if s.strip()] or all_names
    unknown = [n for n in names if n not in all_names]
    if unknown:
        print(f"✗ nieznane skille: {', '.join(unknown)}")
        return 1

    ok = run("taxonomy (render_taxonomy --check)", [sys.executable, "tools/render_taxonomy.py", "--check"])
    registry = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8")).get("skills") or {}
    reg = [f"{n}: brak w taxonomy.yaml → skills" for n in names if n not in registry]
    reg += [f"{n}: nazwa bez prefiksu {PREFIX}" for n in names if not n.startswith(PREFIX)]
    reg += [f"{n}: brak evals/skill_evals/{n}.json" for n in names if not (EVALS / f"{n}.json").exists()]
    ok &= report("registry (taxonomy ↔ skills ↔ scenarios)", reg)
    ok &= run("unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"])
    ok &= run("citations (ev_kb check skills knowledge)", [sys.executable, "tools/ev_kb.py", "check", "skills", "knowledge"])
    ok &= report("structure (SKILL.md)", [x for n in names for x in check_structure(n)])
    ok &= report("scenarios", [x for n in names if (EVALS / f"{n}.json").exists()
                               for x in check_scenarios(n, set(all_names))])
    ok &= report("routing (ev_kb route)", [x for n in names if (EVALS / f"{n}.json").exists()
                                          for x in check_routing(n)], fatal=a.strict_routing)
    if ok:
        prev = json.loads(GATE_OUT.read_text(encoding="utf-8")) if GATE_OUT.exists() else {}
        today = dt.date.today().isoformat()
        for n in names:
            fp = fingerprint(n)
            if (prev.get(n) or {}).get("fingerprint") != fp:
                prev[n] = {"fingerprint": fp, "offline": today}
        GATE_OUT.write_text(json.dumps(prev, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
