#!/usr/bin/env python3
"""ev_kb — dostęp do wiedzy EV Intelligence z kontrolą źródeł.

Polecenia:
  route  <zadanie>        domeny taksonomii i skille pasujące do zadania
  search <pytanie>        fragmenty skilli i knowledge/ razem ze znacznikami źródeł
  cite   <znacznik>       dokument z rejestru sources/*.yaml (URL, data, SHA-256, licencja) i tekst sekcji z lokalnej kopii
  check  [plik|-]         sprawdza znaczniki `[ID §…]`: czy dokument jest w rejestrze i czy sekcja istnieje w tekście
  skill  [nazwa [plik]]   lista skilli albo treść SKILL.md / pliku z references/
  index  <pliki…>         dodaje lokalne kopie dokumentów do pamięci podręcznej; dopasowanie wyłącznie po SHA-256

Teksty dokumentów nie są w repozytorium (licencje, rozmiar). Pamięć podręczna: --docs, zmienna EV_KB_DOCS albo
.cache/ev-kb/ w katalogu repozytorium. `index` przyjmuje plik tylko wtedy, gdy jego SHA-256 jest w rejestrze.

Wynik: tekst albo JSON (--json). Kod wyjścia `check`: 1, gdy jest nieznany dokument albo nieznaleziona sekcja
(z --require-text także brak lokalnej kopii); w pozostałych przypadkach 0.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# ───────────────────────────── rejestr źródeł ─────────────────────────────


@dataclass
class Source:
    id: str
    title: str = ""
    url: str = ""
    sha256: str = ""
    sha_kind: str = ""          # "file" albo "html"
    date: str = ""
    licence: str = ""
    registry: str = ""
    package: str = ""
    file: str = ""
    note: str = ""


def _walk(node, out: list, ctx: dict, registry: str) -> None:
    if isinstance(node, dict):
        if "id" in node and isinstance(node["id"], (str, int)) and ("title" in node or "file" in node or "url" in node):
            sha, kind = "", ""
            if node.get("sha256"):
                sha, kind = str(node["sha256"]), "file"
            elif node.get("sha256_html"):
                sha, kind = str(node["sha256_html"]), "html"
            is_package = "documents" in node
            if not is_package:
                out.append(Source(
                    id=str(node["id"]), title=str(node.get("title", "")), url=str(node.get("url") or ctx.get("url", "")),
                    sha256=sha, sha_kind=kind, date=str(node.get("date") or node.get("retrieved") or ctx.get("retrieved", "")),
                    licence=str(ctx.get("licence", "")), registry=registry, package=str(ctx.get("package", "")),
                    file=str(node.get("file", "")), note=str(node.get("note", "")).strip()))
            if is_package:
                sub = dict(ctx, url=node.get("url", ""), package=str(node["id"]))
                _walk(node["documents"], out, sub, registry)
            return
        for k, v in node.items():
            if k in ("licence", "retrieved", "owner", "source_class"):
                continue
            _walk(v, out, ctx, registry)
    elif isinstance(node, list):
        for item in node:
            _walk(item, out, ctx, registry)


def load_sources(root: Path = ROOT) -> dict[str, Source]:
    sources: dict[str, Source] = {}
    for path in sorted((root / "sources").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        ctx = {"licence": data.get("licence", ""), "retrieved": data.get("retrieved", "")}
        found: list[Source] = []
        _walk(data, found, ctx, path.name)
        for s in found:
            if s.id in sources:
                raise SystemExit(f"Zduplikowany identyfikator źródła {s.id} ({sources[s.id].registry}, {path.name})")
            sources[s.id] = s
    return sources


# ───────────────────────────── pamięć podręczna tekstów ─────────────────────────────


def docs_dir(arg: str | None, root: Path = ROOT) -> Path:
    return Path(arg or os.environ.get("EV_KB_DOCS") or root / ".cache" / "ev-kb")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def html_to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h[1-6]|table)>", "\n", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(raw)
    lines = [re.sub(r"[ \t\xa0]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln) + "\n"


def to_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        if not shutil.which("pdftotext"):
            raise RuntimeError("brak programu pdftotext (poppler-utils)")
        res = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, check=True)
        return res.stdout.decode("utf-8", errors="replace")
    if suffix in (".html", ".htm"):
        return html_to_text(path.read_text(encoding="utf-8", errors="replace"))
    return path.read_text(encoding="utf-8", errors="replace")


def cmd_index(files: list[str], ddir: Path, sources: dict[str, Source]) -> list[dict]:
    by_sha = {s.sha256: s for s in sources.values() if s.sha256}
    ddir.mkdir(parents=True, exist_ok=True)
    results = []
    for name in files:
        path = Path(name)
        if not path.is_file():
            results.append({"file": name, "status": "BRAK_PLIKU"})
            continue
        digest = sha256_file(path)
        src = by_sha.get(digest)
        if not src:
            results.append({"file": name, "sha256": digest, "status": "SPOZA_REJESTRU"})
            continue
        try:
            text = to_text(path)
        except (RuntimeError, subprocess.CalledProcessError) as exc:
            results.append({"file": name, "id": src.id, "status": "BLAD", "detail": str(exc)})
            continue
        (ddir / f"{src.id}.txt").write_text(text, encoding="utf-8")
        (ddir / f"{src.id}.json").write_text(json.dumps({"id": src.id, "sha256": digest, "file": path.name}), encoding="utf-8")
        results.append({"file": name, "id": src.id, "status": "OK"})
    return results


def load_text(doc_id: str, ddir: Path) -> str | None:
    path = ddir / f"{doc_id}.txt"
    return path.read_text(encoding="utf-8") if path.is_file() else None


# ───────────────────────────── znaczniki i lokalizacja sekcji ─────────────────────────────

TAG_BACKTICK = re.compile(r"`\[([^\]`\n]+)\]`")
TAG_BARE = re.compile(r"(?<![`\w])\[([^\]\[\n]+)\](?!\()")
ID_LIKE = re.compile(r"^[A-Z0-9][A-Z0-9-]+$")
ROMAN = r"[IVXLC]+"


@dataclass
class PartResult:
    part: str
    status: str             # OK | NIE_ZNALEZIONO | NIESPRAWDZONE | BRAK_TEKSTU
    line: int | None = None
    excerpt: str = ""


@dataclass
class TagResult:
    tag: str
    doc_id: str
    status: str             # OK | NIEZNANY_DOKUMENT | NIE_ZNALEZIONO | BRAK_TEKSTU | NIESPRAWDZONE
    where: str = ""
    parts: list[PartResult] = field(default_factory=list)


def split_tag(tag: str) -> tuple[str, str]:
    tag = tag.strip()
    head, _, rest = tag.partition(" ")
    return head, rest.strip()


TOC_LINE = re.compile(r"(\.\s){3,}|\.{4,}")


def _find_line(text_lines: list[str], pattern: re.Pattern, start: int = 0, stop: int | None = None) -> int | None:
    """Pierwsza pasująca linia poza spisem treści (linie z kropkami prowadzącymi są pomijane)."""
    stop = len(text_lines) if stop is None else stop
    for i in range(start, stop):
        if pattern.search(text_lines[i]) and not TOC_LINE.search(text_lines[i]):
            return i
    return None


def _excerpt(lines: list[str], i: int, n: int = 4) -> str:
    out = [re.sub(r"\s+", " ", ln).strip() for ln in lines[i:i + 12]]
    return "\n".join([ln for ln in out if ln][:n])


def _section_pattern(num: str) -> re.Pattern:
    """Nagłówek „10.3.1. Tytuł”; rozdział najwyższego poziomu także jako „Chapter 2.” (dokumenty OCA)."""
    alt = r"|^\s*Chapter\s+" + re.escape(num) + r"\b" if "." not in num else ""
    return re.compile(r"^\s*" + re.escape(num) + r"\.?(\s|$)" + alt)


def locate(rest: str, text: str) -> list[PartResult]:
    """Rozbija lokalizator (np. '§10.3.1, §11.4.2', 'art. 5 ust. 4', 'I03.FR.04') i szuka każdej części."""
    lines = text.splitlines()
    results: list[PartResult] = []
    if not rest:
        return results
    for raw in [p.strip() for p in rest.split(",") if p.strip()]:
        part = raw
        found: int | None = None
        checked = False
        # Artykuł i ustęp (akty UE): art. 5 ust. 4 lit. f
        m = re.match(r"^art\.\s*(\d+)(?:\s+ust\.\s*(\d+)(?:\s*[–-]\s*(\d+))?)?", part)
        if m:
            checked = True
            a = _find_line(lines, re.compile(r"^\s*Article\s+" + m.group(1) + r"\s*$"))
            if a is not None:
                found = a
                if m.group(2):
                    nxt = _find_line(lines, re.compile(r"^\s*Article\s+\d+\s*$"), a + 1)
                    paras = [m.group(2)] + ([m.group(3)] if m.group(3) else [])
                    for p in paras:
                        u = _find_line(lines, re.compile(r"^\s*" + p + r"\.\s*"), a + 1, nxt)
                        if u is None:
                            found = None
                            break
                        found = u
        # Aneks: Annex II [pkt 1.2]; „Annex” bez numeru (akt z jednym załącznikiem)
        if not checked:
            m = re.match(r"^(?:Annex|aneks)(?:\s+(" + ROMAN + r"))?\b", part, re.I)
            if m:
                checked = True
                num = r"\s+" + m.group(1) if m.group(1) else ""
                found = _find_line(lines, re.compile(r"^\s*ANNEX" + num + r"\s*$"))
        # Rozdział: rozdz. 8 → „Chapter 8.”
        if not checked:
            m = re.match(r"^rozdz\.\s*(\d+)(?:\s|$)", part)
            if m:
                checked = True
                found = _find_line(lines, re.compile(r"^\s*Chapter\s+" + m.group(1) + r"\b"))
        # Część i punkt wytycznych: cz. 2 pkt 6 → „Part 2:”, potem „6. …”
        if not checked:
            m = re.match(r"^cz\.\s*(\d+)(?:\s+pkt\s*(\d+))?", part)
            if m:
                checked = True
                found = _find_line(lines, re.compile(r"^\s*Part\s+" + m.group(1) + r"\b"))
                if found is not None and m.group(2):
                    nxt = _find_line(lines, re.compile(r"^\s*Part\s+\d+\b"), found + 1)
                    found = _find_line(lines, re.compile(r"^" + m.group(2) + r"\.\s+\S"), found + 1, nxt)
        # Blok OCPP 2.x: „I” → „I. Tariff And Cost”
        if not checked:
            m = re.match(r"^([A-P])$", part)
            if m:
                checked = True
                found = _find_line(lines, re.compile(r"^" + m.group(1) + r"\.\s+[A-Z]"))
        # Nazwany fragment: Preface
        if not checked and part in ("Preface",):
            checked = True
            found = _find_line(lines, re.compile(r"^\s*" + part + r"\s*$"))
        # Wymaganie OCPP 2.x: I03.FR.04, F02.FR.07; przypadek użycia: E13, F02
        if not checked:
            m = re.search(r"\b([A-Z]\d{2}\.FR\.\d{2})\b", part) or \
                re.match(r"^([A-Z]\d{2})(?:\s*[–-]\s*([A-Z]\d{2}))?(?:\s|$)", part)
            if m:
                checked = True
                for uc in [g for g in m.groups() if g]:
                    found = _find_line(lines, re.compile(r"(?<![\w.])" + re.escape(uc) + r"(?![\w])"))
                    if found is None:
                        break
        # Sekcja numerowana: §10.3.1, §8.4.5–8.4.6, App. §3.1.17, E §1.3.2
        if not checked:
            m = re.search(r"§\s*(\d+(?:\.\d+)*)(?:\s*[–-]\s*(\d+(?:\.\d+)*))?", part)
            if m:
                checked = True
                nums = [m.group(1)] + ([m.group(2)] if m.group(2) else [])
                for num in nums:
                    found = _find_line(lines, _section_pattern(num))
                    if found is None:
                        break
        if not checked:
            results.append(PartResult(part=raw, status="NIESPRAWDZONE"))
        elif found is None:
            results.append(PartResult(part=raw, status="NIE_ZNALEZIONO"))
        else:
            results.append(PartResult(part=raw, status="OK", line=found + 1, excerpt=_excerpt(lines, found)))
    return results


def check_tag(tag: str, sources: dict[str, Source], ddir: Path, texts: dict) -> TagResult:
    doc_id, rest = split_tag(tag)
    if doc_id not in sources:
        return TagResult(tag=tag, doc_id=doc_id, status="NIEZNANY_DOKUMENT")
    if not rest:
        return TagResult(tag=tag, doc_id=doc_id, status="OK")
    if doc_id not in texts:
        texts[doc_id] = load_text(doc_id, ddir)
    text = texts[doc_id]
    if text is None:
        return TagResult(tag=tag, doc_id=doc_id, status="BRAK_TEKSTU",
                         parts=[PartResult(part=p.strip(), status="BRAK_TEKSTU") for p in rest.split(",") if p.strip()])
    parts = locate(rest, text)
    statuses = {p.status for p in parts}
    if "NIE_ZNALEZIONO" in statuses:
        status = "NIE_ZNALEZIONO"
    elif statuses == {"NIESPRAWDZONE"}:
        status = "NIESPRAWDZONE"
    else:
        status = "OK"
    return TagResult(tag=tag, doc_id=doc_id, status=status, parts=parts)


def extract_tags(text: str, sources: dict[str, Source]) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for n, line in enumerate(text.splitlines(), 1):
        spans = []
        for m in TAG_BACKTICK.finditer(line):
            head, _ = split_tag(m.group(1))
            if ID_LIKE.match(head) or head in sources:
                found.append((n, m.group(1).strip()))
                spans.append(m.span())
        for m in TAG_BARE.finditer(line):
            if any(a <= m.start() < b for a, b in spans):
                continue
            head, _ = split_tag(m.group(1))
            if head in sources:
                found.append((n, m.group(1).strip()))
    return found


# ───────────────────────────── wyszukiwanie i routing ─────────────────────────────

WORD = re.compile(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ][\w.\-ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]*")
STOP = {"jak", "czy", "jest", "się", "dla", "przy", "oraz", "albo", "który", "która", "które", "the", "and", "for",
        "with", "what", "how", "jaki", "jaka", "jakie", "nie", "tak", "też", "ile", "kiedy", "gdy", "aby", "żeby"}


def terms(text: str) -> list[str]:
    out = []
    for w in WORD.findall(text.lower()):
        w = w.strip(".-")
        if len(w) >= 3 and w not in STOP:
            out.append(w)
    return out


def _stem(w: str) -> str:
    return w if len(w) <= 5 or not w.isalpha() else w[:max(5, len(w) - 3)]


def score(query_terms: list[str], text: str) -> int:
    low = text.lower()
    s = 0
    for t in set(query_terms):
        if t in low:
            s += 3
        elif _stem(t) != t and _stem(t) in low:
            s += 1
    return s


def blocks(path: Path) -> list[tuple[int, str]]:
    """Akapity i wypunktowania (z kontynuacjami) jako jednostki wyszukiwania; zwraca (pierwsza linia, tekst)."""
    out, cur, start, heading = [], [], 0, ""
    lines = path.read_text(encoding="utf-8").splitlines()
    skip = 0
    if lines and lines[0] == "---":                      # frontmatter skilla to opis, nie fakty
        skip = next((i for i in range(1, len(lines)) if lines[i] == "---"), 0) + 1
    for n, line in enumerate(lines, 1):
        if n <= skip:
            continue
        if line.startswith("#"):
            if cur:
                out.append((start, heading + "\n" + "\n".join(cur)))
            cur, heading = [], line.lstrip("# ").strip()
            continue
        new_item = bool(re.match(r"^\s{0,1}(- |\d+\. |\|)", line)) or not line.strip()
        if new_item and cur:
            out.append((start, heading + "\n" + "\n".join(cur)))
            cur = []
        if line.strip():
            if not cur:
                start = n
            cur.append(line)
    if cur:
        out.append((start, heading + "\n" + "\n".join(cur)))
    return out


def corpus(root: Path = ROOT) -> list[Path]:
    files = sorted((root / "skills").glob("*/SKILL.md")) + sorted((root / "skills").glob("*/references/*.md"))
    files += sorted(p for p in (root / "knowledge").rglob("*") if p.suffix in (".md", ".yaml") and p.is_file())
    return [p for p in files if "taksonomia-" not in p.name]


def cmd_search(query: str, limit: int, sources: dict[str, Source], root: Path = ROOT) -> list[dict]:
    q = terms(query)
    hits = []
    for path in corpus(root):
        for line, text in blocks(path):
            s = score(q, text)
            if s:
                body = text.split("\n", 1)[1] if "\n" in text else text
                s += 1 if TAG_BACKTICK.search(body) else 0
                hits.append({"score": s, "file": str(path.relative_to(root)), "line": line,
                             "section": text.split("\n", 1)[0], "text": body.strip(),
                             "tags": sorted({t for _, t in extract_tags(body, sources)})})
    hits.sort(key=lambda h: (-h["score"], h["file"], h["line"]))
    return hits[:limit]


def _frontmatter(path: Path) -> dict:
    txt = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def cmd_route(task: str, limit: int, root: Path = ROOT) -> dict:
    q = terms(task)
    tax = yaml.safe_load((root / "taxonomy" / "taxonomy.yaml").read_text(encoding="utf-8"))
    domains = []
    for d in tax.get("domains", []):
        for sd in d.get("subdomains", []) or [{}]:
            blob = " ".join(str(x) for x in [d.get("name"), d.get("name_en"), d.get("description"), d.get("key"),
                                               sd.get("name"), sd.get("key")] + list(sd.get("topics", []) or []))
            s = score(q, blob)
            if s:
                domains.append({"score": s, "domain": d["id"], "domain_name": d.get("name"),
                                "subdomain": sd.get("id"), "subdomain_name": sd.get("name"),
                                "priority": sd.get("priority") or d.get("priority"),
                                "skills": d.get("skills", [])})
    domains.sort(key=lambda x: (-x["score"], x["subdomain"] or x["domain"]))
    skills = []
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        fm = _frontmatter(path)
        meta = fm.get("metadata", {}) or {}
        blob = " ".join([str(fm.get("description", "")), str(meta.get("slowa", ""))])
        s = score(q, blob)
        if s:
            skills.append({"score": s, "skill": fm.get("name"), "description": fm.get("description")})
    skills.sort(key=lambda x: (-x["score"], x["skill"]))
    built = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    for d in domains:
        d["skills_missing"] = [s for s in d["skills"] if s not in built]
    return {"skills": skills[:limit], "domains": domains[:limit]}


# ───────────────────────────── treść skilli ─────────────────────────────


def list_skills(root: Path = ROOT) -> list[dict]:
    out = []
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        fm = _frontmatter(path)
        refs = sorted(p.name for p in (path.parent / "references").glob("*.md")) if (path.parent / "references").is_dir() else []
        out.append({"skill": fm.get("name", path.parent.name), "description": fm.get("description", ""), "references": refs})
    return out


def read_skill(name: str, file: str | None = None, root: Path = ROOT) -> dict:
    """SKILL.md albo plik z references/; nazwy sprawdzane wobec listy plików (bez ścieżek z zewnątrz)."""
    skills = {s["skill"]: s for s in list_skills(root)}
    if name not in skills:
        return {"error": f"nieznany skill: {name}", "skills": sorted(skills)}
    base = root / "skills" / name
    if not file or file == "SKILL.md":
        path = base / "SKILL.md"
    else:
        fname = Path(file).name
        if fname not in skills[name]["references"]:
            return {"error": f"brak pliku {file} w {name}/references", "references": skills[name]["references"]}
        path = base / "references" / fname
    return {"skill": name, "file": str(path.relative_to(root)), "references": skills[name]["references"],
            "content": path.read_text(encoding="utf-8")}


# ───────────────────────────── CLI ─────────────────────────────


def _print_check(results: list[tuple[str, int, TagResult]], verbose: bool) -> None:
    counts: dict[str, int] = {}
    for where, line, r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
        if r.status in ("NIEZNANY_DOKUMENT", "NIE_ZNALEZIONO") or verbose:
            bad = [p.part for p in r.parts if p.status == "NIE_ZNALEZIONO"]
            extra = f" (brak: {', '.join(bad)})" if bad else ""
            print(f"{r.status:18} {where}:{line}  [{r.tag}]{extra}")
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
    print(f"Znaczniki: {len(results)} ({summary})" if results else "Znaczniki: 0")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--docs", help="katalog pamięci podręcznej tekstów (domyślnie EV_KB_DOCS albo .cache/ev-kb)")
    ap.add_argument("--json", action="store_true", help="wynik jako JSON")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("route"); p.add_argument("task", nargs="+"); p.add_argument("--limit", type=int, default=5)
    p = sub.add_parser("search"); p.add_argument("query", nargs="+"); p.add_argument("--limit", type=int, default=5)
    p = sub.add_parser("cite"); p.add_argument("tag", nargs="+")
    p = sub.add_parser("check"); p.add_argument("paths", nargs="*", default=["-"])
    p.add_argument("--require-text", action="store_true", help="brak lokalnej kopii dokumentu to błąd")
    p.add_argument("-v", "--verbose", action="store_true", help="pokaż także znaczniki poprawne")
    p = sub.add_parser("index"); p.add_argument("files", nargs="+")
    p = sub.add_parser("skill"); p.add_argument("name", nargs="?"); p.add_argument("file", nargs="?")
    args = ap.parse_args(argv)

    sources = load_sources()
    ddir = docs_dir(args.docs)
    out = lambda obj: print(json.dumps(obj, ensure_ascii=False, indent=2))  # noqa: E731

    if args.cmd == "route":
        res = cmd_route(" ".join(args.task), args.limit)
        if args.json:
            out(res)
        else:
            print("Skille:")
            for s in res["skills"] or [{"skill": "—", "description": "brak dopasowania", "score": 0}]:
                print(f"  {s['skill']}  ({s['score']})  {s['description']}")
            print("Domeny:")
            for d in res["domains"]:
                miss = f"; nieopracowane: {', '.join(d['skills_missing'])}" if d["skills_missing"] else ""
                print(f"  {d['subdomain'] or d['domain']} {d['domain_name']} / {d['subdomain_name']} "
                      f"[{d['priority']}] → {', '.join(d['skills']) or 'brak skilla'}{miss}")
        return 0

    if args.cmd == "search":
        res = cmd_search(" ".join(args.query), args.limit, sources)
        if args.json:
            out(res)
        else:
            for h in res:
                print(f"── {h['file']}:{h['line']}  ({h['section']}; trafność {h['score']})")
                print(h["text"])
                print()
            if not res:
                print("Brak trafień. Baza może tego nie obejmować — nie uzupełniaj z pamięci (CLAUDE.md).")
        return 0

    if args.cmd == "cite":
        tag = " ".join(args.tag).strip().strip("`").strip("[]")
        doc_id, _ = split_tag(tag)
        src = sources.get(doc_id)
        if not src:
            msg = {"tag": tag, "status": "NIEZNANY_DOKUMENT"}
            out(msg) if args.json else print(f"NIEZNANY_DOKUMENT: {doc_id} nie ma w sources/*.yaml")
            return 1
        r = check_tag(tag, sources, ddir, {})
        if args.json:
            out({"source": asdict(src), "result": asdict(r)})
        else:
            print(f"{src.id}: {src.title}")
            print(f"  rejestr: sources/{src.registry}" + (f" (pakiet {src.package})" if src.package else ""))
            for k in ("url", "file", "date", "licence"):  # date: data dokumentu albo pobrania
                if getattr(src, k):
                    print(f"  {k}: {getattr(src, k)}")
            if src.sha256:
                print(f"  sha256{'' if src.sha_kind == 'file' else ' (html)'}: {src.sha256}")
            if src.note:
                print(f"  uwaga: {src.note}")
            print(f"  wynik: {r.status}")
            for p in r.parts:
                print(f"  · {p.part}: {p.status}" + (f" (linia {p.line})" if p.line else ""))
                if p.excerpt:
                    print("    " + p.excerpt.replace("\n", "\n    "))
        return 0 if r.status not in ("NIE_ZNALEZIONO",) else 1

    if args.cmd == "check":
        texts: dict = {}
        results: list[tuple[str, int, TagResult]] = []
        paths: list[Path | str] = []
        for p in args.paths:
            if p == "-":
                paths.append("-")
            elif Path(p).is_dir():
                paths += sorted(x for x in Path(p).rglob("*.md"))
            else:
                paths.append(Path(p))
        for p in paths:
            text = sys.stdin.read() if p == "-" else Path(p).read_text(encoding="utf-8")
            where = "stdin" if p == "-" else str(p)
            for line, tag in extract_tags(text, sources):
                results.append((where, line, check_tag(tag, sources, ddir, texts)))
        failing = {"NIEZNANY_DOKUMENT", "NIE_ZNALEZIONO"} | ({"BRAK_TEKSTU"} if args.require_text else set())
        rc = 1 if any(r.status in failing for _, _, r in results) else 0
        if args.json:
            out({"ok": rc == 0, "results": [dict(asdict(r), where=w, line=n) for w, n, r in results]})
        else:
            _print_check(results, args.verbose)
            print("Werdykt: OK" if rc == 0 else "Werdykt: BŁĘDY")
        return rc

    if args.cmd == "skill":
        res = read_skill(args.name, args.file) if args.name else list_skills()
        if args.json:
            out(res)
        elif isinstance(res, list):
            for x in res:
                print(f"{x['skill']}: {x['description']}" + (f"\n  references: {', '.join(x['references'])}" if x["references"] else ""))
        elif "error" in res:
            print(res["error"])
            return 1
        else:
            print(res["content"])
        return 0

    if args.cmd == "index":
        res = cmd_index(args.files, ddir, sources)
        if args.json:
            out(res)
        else:
            for r in res:
                print(f"{r['status']:15} {r.get('id', '—'):10} {r['file']}" + (f"  {r['detail']}" if r.get("detail") else ""))
            print(f"Katalog: {ddir}")
        return 0 if all(r["status"] == "OK" for r in res) else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
