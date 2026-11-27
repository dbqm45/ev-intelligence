#!/usr/bin/env python3
"""Przeglądarka wiedzy EV Intelligence: jeden plik HTML do czytania offline (docs/UZYCIE.md, sekcja 7).

Tylko podgląd. Niczego nie zmienia w repozytorium i nie da się w niej edytować: treść zmienia się wyłącznie przez
pliki w `skills/`, `sources/` i `taxonomy/` oraz bramkę `tools/skill_check.py`.

Widoki: mapa pokrycia (taksonomia → skill → pliki, liczba cytatów, luki), skill, plik, źródło (metadane z rejestru
i wszystkie miejsca, które je cytują), normy niedostępne, wyszukiwanie. Znaczniki `[ID §…]` i odwołania do plików
stają się linkami. Teksty dokumentów źródłowych (`.cache/`) NIE trafiają do pliku — licencje (CC BY-ND, eMIP poufny).

  python3 tools/render_site.py                  # → site/ev-intelligence.html
  python3 tools/render_site.py --out plik.html
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ev_kb  # noqa: E402

DEFAULT_OUT = ROOT / "site" / "ev-intelligence.html"


# ───────────────────────────── Markdown → HTML (podzbiór używany w skillach) ─────────────────────────────

def _frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return ((yaml.safe_load(m.group(1)) or {}), m.group(2)) if m else ({}, text)


class Linker:
    """Zamienia znaczniki źródeł, odwołania do plików i nazwy skilli na linki wewnętrzne."""

    def __init__(self, sources: dict, skills: dict[str, list[str]]):
        self.sources = sources
        self.skills = skills

    def tag_link(self, tag: str) -> str | None:
        head, _ = ev_kb.split_tag(tag)
        if head in self.sources:
            return f'<a class="tag" href="#zrodlo--{html.escape(head)}" title="{html.escape(self.sources[head].title)}">[{html.escape(tag)}]</a>'
        return None

    def code(self, content: str, skill: str) -> str:
        raw = html.unescape(content)
        if raw.startswith("[") and raw.endswith("]"):
            link = self.tag_link(raw[1:-1])
            if link:
                return link
        m = re.fullmatch(r"(?:skills/(ev-[\w-]+)/)?references/([\w.-]+\.md)", raw)
        if m:
            sk = m.group(1) or skill
            if m.group(2) in self.skills.get(sk, []):
                return f'<a class="file" href="#plik--{sk}--{m.group(2)}"><code>{content}</code></a>'
        m = re.fullmatch(r"([\w.-]+\.md)", raw)
        if m and m.group(1) != "SKILL.md":
            own = [s for s, fs in self.skills.items() if m.group(1) in fs]
            sk = skill if skill in own else (own[0] if len(own) == 1 else None)
            if sk:
                return f'<a class="file" href="#plik--{sk}--{m.group(1)}"><code>{content}</code></a>'
        m = re.fullmatch(r"(ev-[\w-]+)(?:\s*\(`?([\w.-]+\.md)`?\))?", raw)
        if m and m.group(1) in self.skills:
            return f'<a class="skill" href="#skill--{m.group(1)}"><code>{content}</code></a>'
        m = re.fullmatch(r"sources/([\w.-]+\.yaml)", raw)
        if m:
            return f'<a href="#zrodla"><code>{content}</code></a>'
        return f"<code>{content}</code>"

    def inline(self, text: str, skill: str) -> str:
        out, pos = [], 0
        for m in re.finditer(r"`([^`]+)`", text):
            out.append(self._plain(text[pos:m.start()], skill))
            out.append(self.code(html.escape(m.group(1)), skill))
            pos = m.end()
        out.append(self._plain(text[pos:], skill))
        return "".join(out)

    def _plain(self, text: str, skill: str) -> str:
        t = html.escape(text)
        t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: self._md_link(m, skill), t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)

        def bare(m: re.Match) -> str:
            return self.tag_link(html.unescape(m.group(1))) or m.group(0)
        return re.sub(r"\[([A-Z0-9][\w.-]*(?: [^\]]+)?)\](?!\()", bare, t)

    def _md_link(self, m: re.Match, skill: str) -> str:
        label, url = m.group(1), html.unescape(m.group(2))
        if re.match(r"https?://", url):
            return f'<a href="{html.escape(url)}" rel="noopener noreferrer" target="_blank">{label}</a>'
        name = url.split("#")[0].rsplit("/", 1)[-1]
        if name in self.skills.get(skill, []):
            return f'<a class="file" href="#plik--{skill}--{name}">{label}</a>'
        return label


def md_to_html(text: str, linker: Linker, skill: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    para: list[str] = []

    def flush() -> None:
        if para:
            out.append("<p>" + linker.inline(" ".join(para), skill) + "</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            flush()
            lvl = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{lvl}>{linker.inline(m.group(2), skill)}</h{lvl}>")
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]  # noqa: E731
            head = cells(ln)
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            t = ["<div class='tbl'><table><thead><tr>" + "".join(f"<th>{linker.inline(c, skill)}</th>" for c in head) + "</tr></thead><tbody>"]
            t += ["<tr>" + "".join(f"<td>{linker.inline(c, skill)}</td>" for c in r) + "</tr>" for r in rows]
            out.append("".join(t) + "</tbody></table></div>")
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
        if m:
            flush()
            ordered = m.group(2)[0].isdigit()
            items: list[str] = []
            while i < len(lines):
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if mm:
                    depth = len(mm.group(1)) // 2
                    items.append(("  " * depth) + mm.group(3))
                    i += 1
                elif lines[i].startswith("  ") and lines[i].strip() and items:
                    items[-1] += " " + lines[i].strip()
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            body = "".join(f"<li class='d{(len(x) - len(x.lstrip(' '))) // 2}'>{linker.inline(x.strip(), skill)}</li>" for x in items)
            out.append(f"<{tag}>{body}</{tag}>")
            continue
        if ln.startswith(">"):
            flush()
            out.append("<blockquote>" + linker.inline(ln.lstrip("> "), skill) + "</blockquote>")
            i += 1
            continue
        if not ln.strip() or ln.strip().startswith("<!--"):
            flush()
            i += 1
            continue
        para.append(ln.strip())
        i += 1
    flush()
    return "\n".join(out)


# ───────────────────────────── dane ─────────────────────────────

def build_data(root: Path = ROOT) -> dict:
    sources = ev_kb.load_sources(root)
    tax = yaml.safe_load((root / "taxonomy" / "taxonomy.yaml").read_text(encoding="utf-8"))
    skill_files: dict[str, list[str]] = {}
    for p in sorted((root / "skills").glob("*/SKILL.md")):
        refs = sorted(f.name for f in (p.parent / "references").glob("*.md")) if (p.parent / "references").is_dir() else []
        skill_files[p.parent.name] = ["SKILL.md"] + refs
    linker = Linker(sources, skill_files)

    files, cites = [], defaultdict(list)
    skills = {}
    for name, names in skill_files.items():
        sk_tags = 0
        for fname in names:
            path = root / "skills" / name / (fname if fname == "SKILL.md" else f"references/{fname}")
            text = path.read_text(encoding="utf-8")
            fm, body = _frontmatter(text) if fname == "SKILL.md" else ({}, text)
            if fname == "SKILL.md":
                meta = fm.get("metadata") or {}
                skills[name] = {"description": fm.get("description", ""), "katalog": meta.get("katalog", ""),
                                "przeglad": str(meta.get("przeglad", "")), "files": names}
            tags = ev_kb.extract_tags(text, sources)
            sk_tags += len(tags)
            docs = sorted({ev_kb.split_tag(t)[0] for _, t in tags if ev_kb.split_tag(t)[0] in sources})
            for line, t in tags:
                head = ev_kb.split_tag(t)[0]
                if head in sources:
                    cites[head].append({"skill": name, "file": fname, "line": line, "tag": t})
            title = next((ln.lstrip("# ").strip() for ln in body.splitlines() if ln.startswith("# ")), fname)
            files.append({"skill": name, "file": fname, "title": title, "tags": len(tags), "docs": docs,
                          "html": md_to_html(body, linker, name), "text": re.sub(r"\s+", " ", body)})
        skills[name]["tags"] = sk_tags
        skills[name]["docs"] = sorted({d for f in files if f["skill"] == name for d in f["docs"]})

    domains = []
    for d in tax.get("domains", []):
        subs = []
        for s in d.get("subdomains", []) or []:
            owners = s["skills"] if "skills" in s else d.get("skills", [])
            subs.append({"id": s["id"], "name": s["name"], "priority": s.get("priority", ""),
                         "topics": s.get("topics", []), "skills": owners, "explicit": "skills" in s})
        domains.append({"id": d["id"], "name": d["name"], "priority": d.get("priority", ""),
                        "description": d.get("description", ""), "skills": d.get("skills", []), "subdomains": subs})

    src = {}
    for sid, s in sources.items():
        src[sid] = {"title": s.title, "url": s.url, "date": s.date, "licence": s.licence, "registry": s.registry,
                    "package": s.package, "sha256": s.sha256, "note": s.note, "cites": cites.get(sid, [])}
    unavailable = []
    data = yaml.safe_load((root / "sources" / "niedostepne.yaml").read_text(encoding="utf-8")) or {}
    for section in ("normy_platne", "niezarejestrowane"):
        for e in data.get(section, []) or []:
            unavailable.append({"name": str(e.get("norma") or e.get("dokument") or ""), "access": e.get("dostep", ""),
                                "topic": e.get("temat", ""), "cited_by": e.get("przywolana_przez", []) or [],
                                "skills": e.get("przywolana_w", []) or [], "note": e.get("uwaga", "")})
    skill_doc: dict[tuple[str, str], int] = defaultdict(int)
    for sid, cs in cites.items():
        for c in cs:
            skill_doc[(c["skill"], sid)] += 1
    skill_skill: dict[tuple[str, str], int] = defaultdict(int)
    for f in files:
        for other in skill_files:
            if other != f["skill"]:
                n = len(re.findall(r"(?<![\w-])" + re.escape(other) + r"(?![\w-])", f["text"]))
                if n:
                    skill_skill[(f["skill"], other)] += n
    graph = {"skill_doc": [[s, d, n] for (s, d), n in sorted(skill_doc.items())],
             "skill_skill": [[a, b, n] for (a, b), n in sorted(skill_skill.items())]}
    version = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").exists() else ""
    return {"version": version, "taxonomy_version": str((tax.get("taxonomy") or {}).get("version", "")),
            "domains": domains, "skills": skills, "files": files, "sources": src, "unavailable": unavailable,
            "graph": graph}


# ───────────────────────────── strona ─────────────────────────────

# ───────────────────────────── strona (statyczny HTML; JavaScript tylko do wyszukiwania i grafu) ─────────────────────────────

def _e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _a_skill(s: str) -> str:
    return f'<a href="#skill--{_e(s)}">{_e(s)}</a>'


def _a_file(s: str, f: str, label: str | None = None) -> str:
    return f'<a href="#plik--{_e(s)}--{_e(f)}">{_e(label or f)}</a>'


def _a_src(i: str) -> str:
    return f'<a href="#zrodlo--{_e(i)}">{_e(i)}</a>'


def view_mapa(d: dict) -> str:
    n_sub = sum(len(x["subdomains"]) for x in d["domains"])
    gaps = sum(1 for x in d["domains"] for s in x["subdomains"] if not s["skills"])
    h = [f'<h1>Mapa pokrycia</h1><p class="muted">{len(d["domains"])} domen · {n_sub} poddomen · '
         f'<span class="gap">{gaps} luk</span> (poddomena bez skilla) · {len(d["skills"])} skilli · {len(d["sources"])} '
         'dokumentów źródłowych. Właściciel poddomeny pochodzi z taksonomii; to nie znaczy, że każdy jej temat jest już '
         'opisany.</p>']
    for dom in d["domains"]:
        g = sum(1 for s in dom["subdomains"] if not s["skills"])
        h.append(f'<details class="card" open><summary>{_e(dom["id"])} {_e(dom["name"])} <span class="muted">· '
                 f'{_e(dom["priority"])} · {len(dom["subdomains"])} poddomen</span>'
                 + (f' <span class="gap">· {g} luk</span>' if g else "") + '</summary>'
                 f'<p class="muted">{_e(dom["description"])}</p><div class="tbl"><table><thead><tr><th>Poddomena</th>'
                 '<th>Skill</th><th>Tematy</th></tr></thead><tbody>')
        for s in dom["subdomains"]:
            sk = "<br>".join(f'{_a_skill(x)} <span class="muted" title="znaczniki źródeł w całym skillu">(skill: '
                             f'{d["skills"].get(x, {}).get("tags", 0)} cyt.)</span>' for x in s["skills"]) \
                or '<span class="gap">luka: brak skilla</span>'
            h.append(f'<tr><td>{_e(s["id"])} {_e(s["name"])}</td><td>{sk}</td><td class="muted">'
                     f'{"; ".join(_e(x) for x in s["topics"])}</td></tr>')
        h.append("</tbody></table></div></details>")
    return "".join(h)


def view_start(d: dict) -> str:
    n_sub = sum(len(x["subdomains"]) for x in d["domains"])
    gaps = sum(1 for x in d["domains"] for s in x["subdomains"] if not s["skills"])
    n_tags = sum(s["tags"] for s in d["skills"].values())
    h = [f'<h1>Wiedza o ładowaniu pojazdów elektrycznych</h1><div class="card"><p><b>{len(d["skills"])} skilli · '
         f'{len(d["files"])} plików · {n_tags} znaczników źródeł · {len(d["sources"])} dokumentów oficjalnych · '
         f'{len(d["unavailable"])} norm niedostępnych</b></p><p>Każdy fakt ma znacznik źródła, np. '
         '<code>[OCPI230 §10.3.1]</code>; kliknięcie pokazuje dokument z rejestru i wszystkie miejsca, które go cytują. '
         '<b>Wniosek</b> w treści oznacza rekomendację wyprowadzoną z faktów, nie cytat.</p><p>'
         '<a href="#mapa">Mapa pokrycia</a> — domeny i poddomeny z luk&shy;ami · <a href="#graf">Graf</a> — które skille '
         'opierają się na których dokumentach · <a href="#zrodla">Źródła</a> · <a href="#niedostepne">Niedostępne</a>'
         '</p></div><h2>Pokrycie domen</h2><div class="tbl"><table><thead><tr><th>Domena</th><th>Skille</th>'
         f'<th>Poddomeny</th><th>Luki</th></tr></thead><tbody>']
    for dom in d["domains"]:
        g = sum(1 for s in dom["subdomains"] if not s["skills"])
        h.append(f'<tr><td>{_e(dom["id"])} {_e(dom["name"])}</td><td>' + ", ".join(_a_skill(x) for x in dom["skills"])
                 + f'</td><td>{len(dom["subdomains"])}</td><td>' + (f'<span class="gap">{g}</span>' if g else "0")
                 + "</td></tr>")
    h.append(f'</tbody></table></div><p class="muted">Razem {n_sub} poddomen, {gaps} bez skilla.</p><h2>Skille</h2>')
    return "".join(h) + view_skille(d).replace("<h1>Skille</h1>", "", 1)


def view_skille(d: dict) -> str:
    h = ["<h1>Skille</h1>"]
    for n, s in d["skills"].items():
        h.append(f'<div class="card"><h3>{_a_skill(n)}</h3><p>{_e(s["description"])}</p><p class="muted">'
                 f'{len(s["files"])} plików · {s["tags"]} znaczników · {len(s["docs"])} dokumentów · przegląd '
                 f'{_e(s["przeglad"])}</p></div>')
    return "".join(h)


def view_skill(d: dict, n: str) -> str:
    s = d["skills"][n]
    files = {(f["skill"], f["file"]): f for f in d["files"]}
    h = [f'<h1>{_e(n)}</h1><p>{_e(s["description"])}</p><p class="muted">{_e(s["katalog"])}</p><h2>Pliki</h2><ul>']
    for f in s["files"]:
        x = files[(n, f)]
        h.append(f'<li>{_a_file(n, f)} <span class="muted">— {_e(x["title"])} · {x["tags"]} znaczników</span></li>')
    h.append('</ul><h2>Dokumenty, na których się opiera</h2><p>'
             + " ".join(f'<a class="pill" href="#zrodlo--{_e(x)}">{_e(x)}</a>' for x in s["docs"]) + "</p>")
    subs = [x for dom in d["domains"] for x in dom["subdomains"] if n in x["skills"]]
    h.append("<h2>Poddomeny taksonomii</h2><ul>" + "".join(f'<li>{_e(x["id"])} {_e(x["name"])}</li>' for x in subs)
             + "</ul>")
    return "".join(h)


def view_file(f: dict) -> str:
    return (f'<p class="muted">{_a_skill(f["skill"])} / {_e(f["file"])} · {f["tags"]} znaczników · źródła: '
            + ", ".join(_a_src(x) for x in f["docs"]) + f'</p><article>{f["html"]}</article>')


def view_zrodla(d: dict) -> str:
    by = defaultdict(list)
    for i, s in d["sources"].items():
        by[s["registry"]].append((i, s))
    h = ['<h1>Dokumenty źródłowe</h1><p class="muted">Rejestr <code>sources/*.yaml</code>: adres, data pobrania, '
         'SHA-256, licencja. Teksty dokumentów nie są częścią przeglądarki.</p>']
    for r, items in by.items():
        h.append(f'<h2>{_e(r)}</h2><div class="tbl"><table><thead><tr><th>ID</th><th>Dokument</th><th>Cytowań</th>'
                 '</tr></thead><tbody>')
        for i, s in items:
            c = len(s["cites"])
            h.append(f'<tr><td>{_a_src(i)}</td><td>{_e(s["title"])}</td><td>{c or "<span class=warn>0</span>"}</td></tr>')
        h.append("</tbody></table></div>")
    return "".join(h)


def view_zrodlo(i: str, s: dict) -> str:
    url = f'<a href="{_e(s["url"])}" target="_blank" rel="noopener noreferrer">{_e(s["url"])}</a>' if s["url"] else "—"
    h = [f'<h1>{_e(i)}</h1><div class="card"><p><b>{_e(s["title"])}</b></p><p>URL: {url}</p><p>Pobrano: '
         f'{_e(s["date"])} · rejestr <code>sources/{_e(s["registry"])}</code>'
         + (f' · pakiet {_e(s["package"])}' if s["package"] else "") + f'</p><p>Licencja: {_e(s["licence"]) or "—"}</p>'
         f'<p class="muted">SHA-256: <code>{_e(s["sha256"]) or "—"}</code></p>'
         + (f'<p class="muted">{_e(s["note"])}</p>' if s["note"] else "") + f'</div><h2>Cytowany w ({len(s["cites"])})</h2>']
    by = defaultdict(list)
    for c in s["cites"]:
        by[(c["skill"], c["file"])].append(c)
    for (sk, f), cs in by.items():
        h.append(f'<details class="card"><summary>{_a_file(sk, f, sk + "/" + f)} <span class="muted">· {len(cs)}</span>'
                 "</summary><ul>" + "".join(f'<li><code>[{_e(c["tag"])}]</code> <span class="muted">linia {c["line"]}'
                                            "</span></li>" for c in cs) + "</ul></details>")
    return "".join(h)


def view_niedostepne(d: dict) -> str:
    h = ['<h1>Normy i dokumenty niedostępne</h1><p class="muted">Wpisy z <code>sources/niedostepne.yaml</code>. To nie '
         'są źródła: baza nie opisuje ich treści i mówi o tym w pierwszym zdaniu odpowiedzi.</p><div class="tbl"><table>'
         '<thead><tr><th>Dokument</th><th>Dostęp</th><th>Temat</th><th>Przywołany przez</th><th>W skillach</th></tr>'
         '</thead><tbody>']
    for u in d["unavailable"]:
        note = f'<br><span class="muted">{_e(u["note"])}</span>' if u["note"] else ""
        h.append(f'<tr><td>{_e(u["name"])}{note}</td><td>{_e(u["access"])}</td><td>{_e(u["topic"])}</td><td>'
                 + "<br>".join(_e(x) for x in u["cited_by"]) + "</td><td>"
                 + "<br>".join(_a_skill(x) if x in d["skills"] else _e(x) for x in u["skills"]) + "</td></tr>")
    return "".join(h) + "</tbody></table></div>"


VIEW_GRAF = """<h1>Graf zależności</h1><p class="muted">Skille (duże koła na okręgu) i dokumenty źródłowe (kolor = rejestr,
wielkość = liczba cytowań). Dokument ustawia się bliżej skilli, które go cytują; grubość krawędzi to liczba cytowań. Najedź
na węzeł, żeby zobaczyć jego połączenia; kliknij, aby otworzyć; przeciągaj węzły i tło, kółkiem myszy przybliżaj.</p>
<p class="js-off gap">Graf wymaga JavaScript. Otwórz plik w zwykłej przeglądarce (Chrome, Firefox, Safari, Edge), a nie
w podglądzie pliku.</p>
<p><label><input type="checkbox" id="gss"> krawędzie skill–skill</label> · <label>min. cytowań <input type="number"
id="gmin" value="1" min="1" style="width:4em"></label> · <span id="ginfo" class="muted"></span></p>
<canvas id="gc" style="width:100%;height:72vh;border:1px solid var(--line);border-radius:8px;background:var(--card);
touch-action:none"></canvas><div id="glegend" class="muted" style="margin-top:6px"></div>"""

VIEW_SZUKAJ = """<h1>Wyszukiwanie</h1><p class="js-off gap">Wyszukiwanie wymaga JavaScript. Otwórz plik w zwykłej
przeglądarce, a nie w podglądzie pliku.</p><div id="wyniki"></div>"""

CSS = """
:root{--bg:#fbfbfa;--fg:#1d1f22;--muted:#666b73;--line:#e3e4e6;--card:#fff;--accent:#1f6feb;--tag:#7a3e9d;--gap:#b42318;--ok:#1a7f37;--warn:#9a6700}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121416;--fg:#e6e7e9;--muted:#9aa0a8;--line:#2a2e33;--card:#1a1d21;--accent:#6aa6ff;--tag:#c792ea;--gap:#ff7b72;--ok:#56d364;--warn:#e3b341}}
:root[data-theme=dark]{--bg:#121416;--fg:#e6e7e9;--muted:#9aa0a8;--line:#2a2e33;--card:#1a1d21;--accent:#6aa6ff;--tag:#c792ea;--gap:#ff7b72;--ok:#56d364;--warn:#e3b341}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:16px;align-items:center;flex-wrap:wrap;z-index:2}
header b{font-size:16px}nav a{margin-right:12px}input[type=search]{flex:1;min-width:180px;max-width:420px;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
main{max-width:1100px;margin:0 auto;padding:16px}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
a.tag{color:var(--tag);font-size:.92em;white-space:nowrap}code{font:.9em ui-monospace,Menlo,Consolas,monospace;background:var(--card);border:1px solid var(--line);border-radius:4px;padding:0 3px}
pre{background:var(--card);border:1px solid var(--line);padding:10px;overflow:auto}.tbl{overflow-x:auto}table{border-collapse:collapse;margin:8px 0;width:100%}
th,td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}th{background:var(--card)}
.muted{color:var(--muted)}.gap{color:var(--gap);font-weight:600}.ok{color:var(--ok)}.warn{color:var(--warn)}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:10px 0}
details>summary{cursor:pointer;font-weight:600}li.d1{margin-left:1.2em}li.d2{margin-left:2.4em}.pill{display:inline-block;border:1px solid var(--line);border-radius:10px;padding:0 7px;font-size:.85em;margin:1px 2px}
mark{background:#ffe58f;color:#000}.hit{margin:6px 0;padding:6px 0;border-bottom:1px solid var(--line)}
button{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:5px 10px;cursor:pointer}
main>section{display:none;scroll-margin-top:70px}main>section:target{display:block}
main>#start{display:block}main>section:target~#start{display:none}
html.js .js-off{display:none}html:not(.js) .js-on{display:none}
"""


def render(data: dict) -> str:
    sections = [("graf", VIEW_GRAF), ("skille", view_skille(data)),
                ("zrodla", view_zrodla(data)), ("niedostepne", view_niedostepne(data)), ("szukaj", VIEW_SZUKAJ)]
    sections += [(f"skill--{n}", view_skill(data, n)) for n in data["skills"]]
    sections += [(f'plik--{f["skill"]}--{f["file"]}', view_file(f)) for f in data["files"]]
    sections += [(f"zrodlo--{i}", view_zrodlo(i, s)) for i, s in data["sources"].items()]
    sections.append(("mapa", view_mapa(data)))
    sections.append(("start", view_start(data)))    # ostatnia: widoczna domyślnie, ukrywana przez „:target ~ #start”
    body = "\n".join(f'<section id="{_e(i)}">{h}</section>' for i, h in sections)
    js_data = {"version": data["version"], "skills": {n: {"tags": s["tags"]} for n, s in data["skills"].items()},
               "sources": {i: {"title": s["title"], "registry": s["registry"], "cites": len(s["cites"])}
                           for i, s in data["sources"].items()},
               "files": [{"skill": f["skill"], "file": f["file"], "title": f["title"], "text": f["text"]}
                         for f in data["files"]],
               "graph": data["graph"]}
    blob = json.dumps(js_data, ensure_ascii=False).replace("</", "<\\/")
    return PAGE.replace("__CSS__", CSS).replace("__BODY__", body).replace("__DATA__", blob) \
        .replace("__VER__", _e(f'wiedza {data["version"]} · taksonomia {data["taxonomy_version"]} · tylko podgląd')) \
        .replace("__GRAPH__", GRAPH_JS)


GRAPH_JS = r"""function initGraf(){
  const cv=document.getElementById('gc'),ctx=cv.getContext('2d'),css=getComputedStyle(document.documentElement),col=v=>css.getPropertyValue(v).trim();
  const PAL=['#1f77b4','#d62728','#2ca02c','#9467bd','#ff7f0e','#17becf','#8c564b','#e377c2','#bcbd22','#7f7f7f','#393b79','#637939'];
  const regs=[...new Set(Object.values(D.sources).map(s=>s.registry))].sort(),rc=r=>PAL[regs.indexOf(r)%PAL.length];
  $('#glegend').innerHTML=regs.map(r=>`<span class="pill"><span style="color:${rc(r)}">●</span> ${esc(r)}</span>`).join(' ')+' <span class="pill"><span style="color:'+col('--accent')+'">●</span> skill</span>';
  let nodes,links,byId;
  function build(){
    const min=Math.max(1,+$('#gmin').value||1),ss=$('#gss').checked,keep=new Set();
    links=D.graph.skill_doc.filter(l=>l[2]>=min).map(([a,b,n])=>({a:'s:'+a,b:'d:'+b,n,t:'sd'}));
    if(ss)links=links.concat(D.graph.skill_skill.map(([a,b,n])=>({a:'s:'+a,b:'s:'+b,n,t:'ss'})));
    links.forEach(l=>{keep.add(l.a);keep.add(l.b)});Object.keys(D.skills).forEach(s=>keep.add('s:'+s));
    const old=byId||{};byId={};nodes=[];
    for(const id of keep){const sk=id.startsWith('s:'),key=id.slice(2),o=old[id];
      const w=sk?D.skills[key].tags:D.sources[key].cites.length;
      const n={id,key,sk,label:key,r:sk?9+Math.sqrt(w)/2.2:3+Math.sqrt(w)/1.6,color:sk?col('--accent'):rc(D.sources[key].registry),
        x:o?o.x:(Math.random()-.5)*600,y:o?o.y:(Math.random()-.5)*600,vx:0,vy:0};nodes.push(n);byId[id]=n}
    links.forEach(l=>{l.s=byId[l.a];l.d=byId[l.b]});
    const sks=nodes.filter(n=>n.sk).sort((a,b)=>a.key.localeCompare(b.key)),R=320;
    sks.forEach((n,i)=>{const a=2*Math.PI*i/sks.length-Math.PI/2;n.fx=R*Math.cos(a);n.fy=R*Math.sin(a);if(!old[n.id]){n.x=n.fx;n.y=n.fy}});
    $('#ginfo').textContent=`${nodes.filter(n=>n.sk).length} skilli · ${nodes.filter(n=>!n.sk).length} dokumentów · ${links.length} krawędzi`;
    alpha=1}
  let alpha=1,view={x:0,y:0,k:1},hover=null,drag=null,moved=false,raf;
  function tick(){
    const N=nodes.length;
    for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){const a=nodes[i],b=nodes[j];let dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy+.01;
      const f=(a.sk&&b.sk?9000:a.sk||b.sk?1800:500)/d2,d=Math.sqrt(d2);dx/=d;dy/=d;a.vx-=f*dx;a.vy-=f*dy;b.vx+=f*dx;b.vy+=f*dy}
    for(const l of links){const a=l.s,b=l.d;let dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)+.01;
      const want=l.t==='ss'?260:120,k=(l.t==='ss'?.004:.012)*Math.min(3,1+Math.log(l.n));const f=(d-want)*k;a.vx+=f*dx/d;a.vy+=f*dy/d;b.vx-=f*dx/d;b.vy-=f*dy/d}
    for(const n of nodes){if(n===drag)continue;if(n.sk){n.x+=(n.fx-n.x)*.2;n.y+=(n.fy-n.y)*.2;n.vx=n.vy=0;continue}
      n.vx-=n.x*.002;n.vy-=n.y*.002;n.x+=n.vx*alpha;n.y+=n.vy*alpha;n.vx*=.6;n.vy*=.6}
    alpha=Math.max(.02,alpha*.985)}
  function draw(){
    const dpr=devicePixelRatio||1,w=cv.clientWidth,h=cv.clientHeight;if(cv.width!==w*dpr){cv.width=w*dpr;cv.height=h*dpr}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);ctx.translate(w/2+view.x,h/2+view.y);ctx.scale(view.k,view.k);
    const nb=new Set();if(hover){nb.add(hover);links.forEach(l=>{if(l.s===hover)nb.add(l.d);if(l.d===hover)nb.add(l.s)})}
    for(const l of links){const on=!hover||l.s===hover||l.d===hover;ctx.globalAlpha=on?(hover?.8:.35):.06;ctx.strokeStyle=l.t==='ss'?col('--muted'):l.d.color;
      ctx.lineWidth=(l.t==='ss'?1:Math.min(5,.6+Math.log(1+l.n)))/view.k;ctx.setLineDash(l.t==='ss'?[6/view.k,4/view.k]:[]);ctx.beginPath();ctx.moveTo(l.s.x,l.s.y);ctx.lineTo(l.d.x,l.d.y);ctx.stroke()}
    ctx.setLineDash([]);
    for(const n of nodes){ctx.globalAlpha=!hover||nb.has(n)?1:.15;ctx.fillStyle=n.color;ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,7);ctx.fill();
      if(n.sk||nb.has(n)&&hover||view.k>1.6){ctx.font=`${n.sk?'600 ':''}${(n.sk?13:11)/view.k}px system-ui`;const tw=ctx.measureText(n.label).width,left=n.sk&&n.x<0;
        const tx=left?n.x-n.r-4/view.k-tw:n.x+n.r+4/view.k,ty=n.y+4/view.k;ctx.lineWidth=3/view.k;ctx.strokeStyle=col('--card');ctx.strokeText(n.label,tx,ty);ctx.fillStyle=col('--fg');ctx.fillText(n.label,tx,ty)}}
    ctx.globalAlpha=1;
    if(hover){const t=hover.sk?`${hover.key}: ${D.skills[hover.key].tags} znaczników`:`${hover.key}: ${D.sources[hover.key].title} · ${D.sources[hover.key].cites.length} cytowań`;
      ctx.setTransform(dpr,0,0,dpr,0,0);ctx.font='12px system-ui';const tw=ctx.measureText(t).width;ctx.fillStyle=col('--bg');ctx.fillRect(8,8,Math.min(tw+12,w-16),22);ctx.fillStyle=col('--fg');ctx.fillText(t,14,23)}}
  function loop(){tick();draw();raf=requestAnimationFrame(loop)}
  const pt=e=>{const r=cv.getBoundingClientRect();return{x:(e.clientX-r.left-cv.clientWidth/2-view.x)/view.k,y:(e.clientY-r.top-cv.clientHeight/2-view.y)/view.k}};
  const at=p=>{let best=null,bd=1e9;for(const n of nodes){const d=Math.hypot(n.x-p.x,n.y-p.y);if(d<n.r+4/view.k&&d<bd){best=n;bd=d}}return best};
  let pan=null;
  cv.onpointerdown=e=>{cv.setPointerCapture(e.pointerId);moved=false;const n=at(pt(e));if(n){drag=n}else pan={x:e.clientX-view.x,y:e.clientY-view.y}};
  cv.onpointermove=e=>{const p=pt(e);if(drag){drag.x=p.x;drag.y=p.y;moved=true;alpha=Math.max(alpha,.3)}else if(pan){view.x=e.clientX-pan.x;view.y=e.clientY-pan.y;moved=true}else{hover=at(p);cv.style.cursor=hover?'pointer':'grab'}};
  cv.onpointerup=e=>{if(drag&&drag.sk&&moved){drag.fx=drag.x;drag.fy=drag.y}if(drag&&!moved)location.hash=drag.sk?'#skill--'+drag.key:'#zrodlo--'+drag.key;drag=null;pan=null};
  cv.onwheel=e=>{e.preventDefault();const k=Math.min(6,Math.max(.2,view.k*(e.deltaY<0?1.12:1/1.12)));view.k=k};
  view.k=Math.min(1,Math.min(cv.clientWidth,cv.clientHeight)/(2*320+220));
  $('#gss').onchange=build;$('#gmin').onchange=build;build();loop();G.stop=()=>{cancelAnimationFrame(raf);G.stop=null}}
"""

PAGE = r"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>EV Intelligence</title><style>__CSS__</style>
<script>document.documentElement.classList.add('js')</script></head><body>
<header><b>EV Intelligence</b><span class="muted">__VER__</span>
<nav><a href="#start">Start</a><a href="#mapa">Mapa</a><a href="#graf">Graf</a><a href="#skille">Skille</a><a href="#zrodla">Źródła</a><a href="#niedostepne">Niedostępne</a></nav>
<input class="js-on" type="search" id="q" placeholder="Szukaj w treści skilli…" aria-label="Szukaj">
<button class="js-on" id="theme" title="Przełącz jasny i ciemny motyw">Motyw</button></header>
<main>
__BODY__
</main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
D.sources=Object.fromEntries(Object.entries(D.sources).map(([k,v])=>[k,Object.assign({},v,{cites:{length:v.cites}})]));
try{const t=localStorage.getItem('evkb-theme');if(t)document.documentElement.dataset.theme=t}catch(e){}
$('#theme').onclick=()=>{const r=document.documentElement,n=r.dataset.theme==='dark'?'light':'dark';r.dataset.theme=n;try{localStorage.setItem('evkb-theme',n)}catch(e){}};
function szukaj(q){
  q=q.trim();const out=$('#wyniki');if(q.length<2){out.innerHTML='<p class="muted">Wpisz co najmniej 2 znaki.</p>';return}
  const words=q.toLowerCase().split(/\s+/).filter(Boolean),hits=[];
  for(const f of D.files){const low=f.text.toLowerCase();if(words.every(w=>low.includes(w))){const i=low.indexOf(words[0]);hits.push([f,f.text.slice(Math.max(0,i-90),i+200)])}}
  const re=new RegExp('('+words.map(w=>w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|')+')','gi');
  out.innerHTML=`<p class="muted">${esc(q)}: ${hits.length} plików</p>`+hits.map(([f,snip])=>`<div class="hit"><a href="#plik--${esc(f.skill)}--${esc(f.file)}">${esc(f.skill)} / ${esc(f.file)}</a> <span class="muted">— ${esc(f.title)}</span><br><span class="muted">…${esc(snip).replace(re,'<mark>$1</mark>')}…</span></div>`).join('')}
let tm;$('#q').addEventListener('input',e=>{clearTimeout(tm);tm=setTimeout(()=>{szukaj(e.target.value);if(location.hash!=='#szukaj')location.hash='#szukaj'},250)});
const G={};
__GRAPH__
function onHash(){if(location.hash==='#graf'){if(!G.stop)initGraf()}else if(G.stop)G.stop();window.scrollTo(0,0)}
addEventListener('hashchange',onHash);onHash();
</script></body></html>
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="plik wynikowy HTML")
    a = ap.parse_args(argv)
    data = build_data(ROOT)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data), encoding="utf-8")
    n_tags = sum(s["tags"] for s in data["skills"].values())
    print(f"✓ {out} — {len(data['skills'])} skilli, {len(data['files'])} plików, {n_tags} znaczników, "
          f"{len(data['sources'])} dokumentów, {len(data['unavailable'])} wpisów niedostępnych")
    return 0


if __name__ == "__main__":
    sys.exit(main())
