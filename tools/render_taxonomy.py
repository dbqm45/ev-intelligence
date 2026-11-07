#!/usr/bin/env python3
"""Validate taxonomy/taxonomy.yaml and render taxonomy/TAXONOMY-TREE.md.

Usage:
    python3 tools/render_taxonomy.py          # validate + write TAXONOMY-TREE.md
    python3 tools/render_taxonomy.py --check  # validate + fail if TAXONOMY-TREE.md is stale
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "taxonomy" / "taxonomy.yaml"
OUT = ROOT / "taxonomy" / "TAXONOMY-TREE.md"

PRIORITIES = {"mvp", "p2", "p3"}
PRIORITY_LABEL = {"mvp": "MVP", "p2": "P2", "p3": "P3"}
DOMAIN_ID = re.compile(r"^D\d{2}$")
SUB_ID = re.compile(r"^D\d{2}\.\d{2}$")
KEY = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    skills = set((data.get("skills") or {}).keys())
    domains = data.get("domains") or []
    domain_ids = {d.get("id") for d in domains}
    seen_ids: set[str] = set()
    seen_keys: set[str] = set()

    for d in domains:
        did = d.get("id", "?")
        for field in ("id", "key", "name", "name_en", "description", "priority", "subdomains"):
            if field not in d:
                errors.append(f"{did}: missing field '{field}'")
        if not DOMAIN_ID.match(str(did)):
            errors.append(f"{did}: invalid domain id")
        if did in seen_ids:
            errors.append(f"{did}: duplicate id")
        seen_ids.add(did)
        if not KEY.match(str(d.get("key", ""))) or d.get("key") in seen_keys:
            errors.append(f"{did}: invalid or duplicate key '{d.get('key')}'")
        seen_keys.add(d.get("key"))
        if d.get("priority") not in PRIORITIES:
            errors.append(f"{did}: invalid priority '{d.get('priority')}'")
        for s in d.get("skills", []):
            if s not in skills:
                errors.append(f"{did}: unknown skill '{s}'")
        for dep in d.get("depends_on", []):
            if dep not in domain_ids:
                errors.append(f"{did}: depends_on unknown domain '{dep}'")
            if dep == did:
                errors.append(f"{did}: depends on itself")

        sub_keys: set[str] = set()
        for s in d.get("subdomains", []):
            sid = s.get("id", "?")
            for field in ("id", "key", "name", "priority", "topics"):
                if field not in s:
                    errors.append(f"{sid}: missing field '{field}'")
            if not SUB_ID.match(str(sid)) or not str(sid).startswith(f"{did}."):
                errors.append(f"{sid}: invalid subdomain id for domain {did}")
            if sid in seen_ids:
                errors.append(f"{sid}: duplicate id")
            seen_ids.add(sid)
            if not KEY.match(str(s.get("key", ""))) or s.get("key") in sub_keys:
                errors.append(f"{sid}: invalid or duplicate key '{s.get('key')}'")
            sub_keys.add(s.get("key"))
            if s.get("priority") not in PRIORITIES:
                errors.append(f"{sid}: invalid priority '{s.get('priority')}'")
            if not s.get("topics"):
                errors.append(f"{sid}: no topics")
    return errors


def render(data: dict) -> str:
    meta = data["taxonomy"]
    domains = data["domains"]
    skills = data.get("skills", {})
    n_sub = sum(len(d["subdomains"]) for d in domains)
    n_topics = sum(len(s["topics"]) for d in domains for s in d["subdomains"])

    lines = [
        "<!-- AUTO-GENERATED from taxonomy/taxonomy.yaml by tools/render_taxonomy.py — do not edit by hand. -->",
        "",
        f"# EV Knowledge Taxonomy — drzewo (v{meta['version']}, {meta['status']}, {meta['date']})",
        "",
        f"**Domeny: {len(domains)} · poddomeny: {n_sub} · tematy: {n_topics}.** "
        "Legenda: `MVP` = Etap 1, `P2` = Etap 4, `P3` = później; ⚠️ = wersje/numery do weryfikacji w źródle pierwotnym.",
        "",
        "## Spis domen",
        "",
        "| ID | Domena | Priorytet | Poddomeny | Skille | Zależy od |",
        "|----|--------|-----------|-----------|--------|-----------|",
    ]
    for d in domains:
        anchor = f"{d['id'].lower()}--{d['key']}"
        sk = ", ".join(f"`{s}`" for s in d.get("skills", []))
        deps = ", ".join(d.get("depends_on", [])) or "—"
        cross = " *(przekrojowa)*" if d.get("cross_cutting") else ""
        lines.append(
            f"| {d['id']} | [{d['name']}](#{anchor}){cross} | {PRIORITY_LABEL[d['priority']]} "
            f"| {len(d['subdomains'])} | {sk} | {deps} |"
        )
    lines.append("")

    for d in domains:
        lines += [
            f"## {d['id']} · {d['key']}",
            "",
            f"**{d['name']}** — *{d['name_en']}* · priorytet **{PRIORITY_LABEL[d['priority']]}** · "
            f"katalog `knowledge/{d['key']}/`",
            "",
            d["description"],
            "",
        ]
        for s in d["subdomains"]:
            flag = " ⚠️" if s.get("verify") else ""
            lines.append(
                f"### {s['id']} {s['name']} `{PRIORITY_LABEL[s['priority']]}`{flag}"
            )
            lines.append("")
            lines.append(f"`knowledge/{d['key']}/{s['key']}/`")
            lines.append("")
            lines += [f"- {t}" for t in s["topics"]]
            lines.append("")

    lines += ["## Rejestr skilli", "", "| Skill | Nazwa | Etap | Domeny |", "|-------|-------|------|--------|"]
    for key, info in skills.items():
        used = ", ".join(d["id"] for d in domains if key in d.get("skills", []))
        lines.append(f"| `{key}` | {info['name']} | {PRIORITY_LABEL.get(info.get('stage'), info.get('stage'))} | {used} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("Taxonomy validation failed:", *errors, sep="\n  ")
        return 1
    output = render(data)
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != output:
            print(f"{OUT.relative_to(ROOT)} is stale — run: python3 tools/render_taxonomy.py")
            return 1
        print("Taxonomy OK, tree up to date.")
        return 0
    OUT.write_text(output, encoding="utf-8")
    print(f"Taxonomy OK — wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
