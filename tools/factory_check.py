#!/usr/bin/env python3
"""OPTIONAL interoperability check with the tf factory. Not required: the project gate is tools/skill_check.py.

Validate EV Intelligence skills with the quality gates of the tf factory — without adopting its layout.

The repository keeps its own structure (skills/<name>/, evals/skill_evals/<name>.json, taxonomy/). This script
assembles a throw-away workspace with the tf *core only* (no domain packs), registers the `ev-` skill prefix there,
copies our skills and scenarios in, and runs the factory's checks:

  1. taxonomy     — tools/render_taxonomy.py --check (local)
  2. registry     — every skills/<name> is listed in taxonomy.yaml → skills (local)
     unit tests   — python3 -m unittest discover tests (scripts shipped with skills)
     citations    — tools/ev_kb.py check skills knowledge (every `[ID §…]` tag is in sources/*.yaml; sections are
                    checked against local copies in .cache/ev-kb when present)
  3. build        — factory/build.py check (skill structure rules)
  4. scenarios    — .claude/tests/run_skill_evals.py --validate
  5. gate         — factory/skill_gate.py <skill> for each skill (free checks: structure, scenarios, hint routing,
                    hint regression across all skills, Polish lint, references, security audit)

Usage:
  python3 tools/factory_check.py [--tf PATH] [--skills a,b] [--fast] [--keep]
  python3 tools/factory_check.py --model haiku --budget 1 --yes   # + paid evaluation on a model (human consent only)

--tf defaults to $TF_DIR, then ../tf. Workspace: .work/factory (git-ignored). Gate results for our skills are copied to
evals/skill-gate.json.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
EVALS_DIR = ROOT / "evals" / "skill_evals"
GATE_OUT = ROOT / "evals" / "skill-gate.json"
TAXONOMY = ROOT / "taxonomy" / "taxonomy.yaml"
PREFIX = "ev-"
FACET = ('  - {prefix: ev-, order: 150, name: EV Intelligence, '
         'question: "jak działa branża ładowania EV — protokoły, CPMS, roaming, operacje, energia, regulacje"}\n')


def step(label: str, cmd: list[str], cwd: Path) -> bool:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{'✓' if ok else '✗'} {label}")
    out = (r.stdout + r.stderr).strip()
    if out and (not ok or os.environ.get("VERBOSE")):
        print("    " + "\n    ".join(out.splitlines()[-40:]))
    return ok


def find_tf(arg: str | None) -> Path:
    for cand in (arg, os.environ.get("TF_DIR"), str(ROOT.parent / "tf")):
        if cand and (Path(cand) / "core" / "factory" / "install.py").exists():
            return Path(cand).resolve()
    sys.exit("✗ tf factory not found — pass --tf PATH or set TF_DIR (clone: https://github.com/dbqm45/tf)")


def our_skills(selected: str) -> list[str]:
    names = sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md"))
    if selected:
        wanted = [s.strip() for s in selected.split(",") if s.strip()]
        missing = [s for s in wanted if s not in names]
        if missing:
            sys.exit(f"✗ unknown skills: {', '.join(missing)}")
        names = wanted
    return names


def check_registry(names: list[str]) -> bool:
    registry = (yaml.safe_load(TAXONOMY.read_text(encoding="utf-8")).get("skills") or {})
    problems = [f"{n}: not in taxonomy.yaml → skills" for n in names if n not in registry]
    problems += [f"{n}: name must start with '{PREFIX}'" for n in names if not n.startswith(PREFIX)]
    problems += [f"{n}: no scenarios at evals/skill_evals/{n}.json" for n in names
                 if not (EVALS_DIR / f"{n}.json").exists()]
    print(f"{'✓' if not problems else '✗'} registry (taxonomy ↔ skills ↔ scenarios)")
    for p in problems:
        print(f"    {p}")
    return not problems


def assemble(tf: Path, ws: Path, names: list[str]) -> None:
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    r = subprocess.run([sys.executable, str(tf / "core" / "factory" / "install.py"), str(ws), "--yes",
                        "--packs", "none", "--language", "pl"], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:] + r.stderr[-2000:])
        sys.exit("✗ tf install failed")
    cfg = ws / "factory" / "config.yaml"
    text = cfg.read_text(encoding="utf-8")
    text, n = re.subn(r"(?m)^facets:\n", lambda m: m.group(0) + FACET, text, count=1)
    if n != 1:
        sys.exit("✗ could not register the ev- facet in factory/config.yaml (factory format changed?)")
    cfg.write_text(text, encoding="utf-8")
    # skills reference repository files (taxonomy, knowledge) by repo-relative paths — make them resolvable
    for shared in ("taxonomy", "knowledge", "sources", "tests"):
        if (ROOT / shared).is_dir():
            shutil.copytree(ROOT / shared, ws / shared)
    for name in names:
        shutil.copytree(SKILLS_DIR / name, ws / ".claude" / "skills" / name)
        shutil.copy2(EVALS_DIR / f"{name}.json", ws / ".claude" / "tests" / "skill_evals" / f"{name}.json")
        holdout = EVALS_DIR / "holdout" / f"{name}.json"
        if holdout.exists():
            dst = ws / ".claude" / "tests" / "skill_evals" / "holdout"
            dst.mkdir(exist_ok=True)
            shutil.copy2(holdout, dst / holdout.name)
    # regenerate catalog, agents and the skill_hint index with our skills included
    subprocess.run([sys.executable, "factory/build.py"], cwd=ws, capture_output=True, text=True)


def save_gate(ws: Path, names: list[str]) -> None:
    src = ws / ".claude" / "skill-gate.json"
    if not src.exists():
        return
    data = json.loads(src.read_text(encoding="utf-8"))
    entries = data.get("skills", data) if isinstance(data, dict) else {}
    ours = {k: v for k, v in entries.items() if k in names} if isinstance(entries, dict) else {}
    previous = json.loads(GATE_OUT.read_text(encoding="utf-8")) if GATE_OUT.exists() else {}
    previous.update(ours)
    GATE_OUT.write_text(json.dumps(previous, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tf", help="path to a tf factory clone (default: $TF_DIR, ../tf)")
    ap.add_argument("--skills", default="", help="comma-separated skill names (default: all in skills/)")
    ap.add_argument("--out", default=str(ROOT / ".work" / "factory"), help="workspace directory")
    ap.add_argument("--fast", action="store_true", help="skip the all-skills hint regression in the gate")
    ap.add_argument("--keep", action="store_true", help="keep the workspace after the run")
    ap.add_argument("--model", default="", help="paid evaluation on models (haiku,sonnet,opus) — human consent only")
    ap.add_argument("--budget", default="1", help="USD limit for --model")
    ap.add_argument("--yes", action="store_true", help="with --model: confirm the cost")
    a = ap.parse_args()

    tf = find_tf(a.tf)
    names = our_skills(a.skills)
    ws = Path(a.out).resolve()
    print(f"tf: {tf} · skills: {', '.join(names) or '(none)'} · workspace: {ws}")

    ok = step("taxonomy (render_taxonomy --check)", [sys.executable, "tools/render_taxonomy.py", "--check"], ROOT)
    ok &= check_registry(names)
    if (ROOT / "tests").is_dir():
        ok &= step("unit tests (python3 -m unittest discover tests)",
                   [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], ROOT)
    ok &= step("citations (tools/ev_kb.py check skills knowledge)",
               [sys.executable, "tools/ev_kb.py", "check", "skills", "knowledge"], ROOT)
    if not names:
        print("No skills yet — only the taxonomy was checked.")
        return 0 if ok else 1

    assemble(tf, ws, names)
    ok &= step("build (factory/build.py check)", [sys.executable, "factory/build.py", "check"], ws)
    ok &= step("scenarios (run_skill_evals.py --validate)",
               [sys.executable, ".claude/tests/run_skill_evals.py", "--validate"], ws)
    for name in names:
        cmd = [sys.executable, "factory/skill_gate.py", name]
        if a.fast:
            cmd.append("--fast")
        if a.model:
            if not a.yes:
                sys.exit("✗ --model runs a paid evaluation — add --yes after the human agreed to the cost")
            cmd += ["--model", a.model, "--budget", a.budget, "--yes"]
        ok &= step(f"gate {name} (factory/skill_gate.py)", cmd, ws)
    save_gate(ws, names)
    if not a.keep:
        shutil.rmtree(ws, ignore_errors=True)
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
