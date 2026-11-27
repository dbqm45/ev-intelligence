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
            return f'<a class="tag" href="#/zrodlo/{html.escape(head)}" title="{html.escape(self.sources[head].title)}">[{html.escape(tag)}]</a>'
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
                return f'<a class="file" href="#/plik/{sk}/{m.group(2)}"><code>{content}</code></a>'
        m = re.fullmatch(r"(ev-[\w-]+)(?:\s*\(`?([\w.-]+\.md)`?\))?", raw)
        if m and m.group(1) in self.skills:
            return f'<a class="skill" href="#/skill/{m.group(1)}"><code>{content}</code></a>'
        m = re.fullmatch(r"sources/([\w.-]+\.yaml)", raw)
        if m:
            return f'<a href="#/rejestr/{m.group(1)}"><code>{content}</code></a>'
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
            return f'<a class="file" href="#/plik/{skill}/{name}">{label}</a>'
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
    version = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").exists() else ""
    return {"version": version, "taxonomy_version": str((tax.get("taxonomy") or {}).get("version", "")),
            "domains": domains, "skills": skills, "files": files, "sources": src, "unavailable": unavailable}


# ───────────────────────────── strona ─────────────────────────────

PAGE = r"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>EV Intelligence</title>
<style>
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
mark{background:#ffe58f;color:#000}button{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:5px 10px;cursor:pointer}.hit{margin:6px 0;padding:6px 0;border-bottom:1px solid var(--line)}
</style></head><body>
<header><b>EV Intelligence</b><span class="muted" id="ver"></span>
<nav><a href="#/mapa">Mapa</a><a href="#/skille">Skille</a><a href="#/zrodla">Źródła</a><a href="#/niedostepne">Niedostępne</a></nav>
<input type="search" id="q" placeholder="Szukaj w treści skilli…" aria-label="Szukaj">
<button id="theme" title="Przełącz jasny i ciemny motyw">Motyw</button></header>
<main id="app"></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const $=s=>document.querySelector(s), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
$('#ver').textContent=`wiedza ${D.version} · taksonomia ${D.taxonomy_version} · tylko podgląd`;
try{const t=localStorage.getItem('evkb-theme');if(t)document.documentElement.dataset.theme=t}catch(e){}
$('#theme').onclick=()=>{const r=document.documentElement,n=r.dataset.theme==='dark'?'light':'dark';r.dataset.theme=n;try{localStorage.setItem('evkb-theme',n)}catch(e){}};
const skillLink=s=>`<a href="#/skill/${esc(s)}">${esc(s)}</a>`;
const fileOf=(s,f)=>D.files.find(x=>x.skill===s&&x.file===f);
function mapa(){
  let nSub=0,gaps=0;D.domains.forEach(d=>d.subdomains.forEach(s=>{nSub++;if(!s.skills.length)gaps++}));
  let h=`<h1>Mapa pokrycia</h1><p class="muted">${D.domains.length} domen · ${nSub} poddomen · <span class="gap">${gaps} luk</span> (poddomena bez skilla) · ${Object.keys(D.skills).length} skilli · ${Object.keys(D.sources).length} dokumentów źródłowych. Właściciel poddomeny pochodzi z taksonomii; to nie znaczy, że każdy jej temat jest już opisany.</p>`;
  for(const d of D.domains){
    const g=d.subdomains.filter(s=>!s.skills.length).length;
    h+=`<details class="card"><summary>${esc(d.id)} ${esc(d.name)} <span class="muted">· ${esc(d.priority)} · ${d.subdomains.length} poddomen</span>${g?` <span class="gap">· ${g} luk</span>`:''}</summary><p class="muted">${esc(d.description)}</p><div class="tbl"><table><thead><tr><th>Poddomena</th><th>Skill</th><th>Tematy</th></tr></thead><tbody>`;
    for(const s of d.subdomains){
      const sk=s.skills.length?s.skills.map(x=>`${skillLink(x)} <span class="muted" title="znaczniki źródeł w całym skillu">(skill: ${D.skills[x]?D.skills[x].tags:0} cyt.)</span>`).join('<br>'):'<span class="gap">luka: brak skilla</span>';
      h+=`<tr><td>${esc(s.id)} ${esc(s.name)}</td><td>${sk}</td><td class="muted">${s.topics.map(esc).join('; ')}</td></tr>`}
    h+='</tbody></table></div></details>'}
  return h}
function skille(){
  let h='<h1>Skille</h1>';
  for(const [n,s] of Object.entries(D.skills))h+=`<div class="card"><h3>${skillLink(n)}</h3><p>${esc(s.description)}</p><p class="muted">${s.files.length} plików · ${s.tags} znaczników · ${s.docs.length} dokumentów · przegląd ${esc(s.przeglad)}</p></div>`;
  return h}
function skill(n){
  const s=D.skills[n];if(!s)return '<p>Nie ma takiego skilla.</p>';
  let h=`<h1>${esc(n)}</h1><p>${esc(s.description)}</p><p class="muted">${esc(s.katalog)}</p><h2>Pliki</h2><ul>`;
  for(const f of s.files){const x=fileOf(n,f);h+=`<li><a href="#/plik/${esc(n)}/${esc(f)}">${esc(f)}</a> <span class="muted">— ${esc(x.title)} · ${x.tags} znaczników</span></li>`}
  h+='</ul><h2>Dokumenty, na których się opiera</h2><p>'+s.docs.map(d=>`<a class="pill" href="#/zrodlo/${esc(d)}">${esc(d)}</a>`).join(' ')+'</p>';
  const sub=[];D.domains.forEach(d=>d.subdomains.forEach(x=>{if(x.skills.includes(n))sub.push(x)}));
  h+='<h2>Poddomeny taksonomii</h2><ul>'+sub.map(x=>`<li>${esc(x.id)} ${esc(x.name)}</li>`).join('')+'</ul>';return h}
function plik(n,f){
  const x=fileOf(n,f);if(!x)return '<p>Nie ma takiego pliku.</p>';
  return `<p class="muted"><a href="#/skill/${esc(n)}">${esc(n)}</a> / ${esc(f)} · ${x.tags} znaczników · źródła: ${x.docs.map(d=>`<a href="#/zrodlo/${esc(d)}">${esc(d)}</a>`).join(', ')}</p><article>${x.html}</article>`}
function zrodla(){
  const byReg={};for(const [id,s] of Object.entries(D.sources))(byReg[s.registry]=byReg[s.registry]||[]).push([id,s]);
  let h='<h1>Dokumenty źródłowe</h1><p class="muted">Rejestr <code>sources/*.yaml</code>: adres, data pobrania, SHA-256, licencja. Teksty dokumentów nie są częścią przeglądarki.</p>';
  for(const [r,list] of Object.entries(byReg)){h+=`<h2 id="r-${esc(r)}">${esc(r)}</h2><div class="tbl"><table><thead><tr><th>ID</th><th>Dokument</th><th>Cytowań</th></tr></thead><tbody>`;
    for(const [id,s] of list)h+=`<tr><td><a href="#/zrodlo/${esc(id)}">${esc(id)}</a></td><td>${esc(s.title)}</td><td>${s.cites.length||'<span class="warn">0</span>'}</td></tr>`;
    h+='</tbody></table></div>'}
  return h}
function zrodlo(id){
  const s=D.sources[id];if(!s)return '<p>Nie ma takiego dokumentu w rejestrze.</p>';
  let h=`<h1>${esc(id)}</h1><div class="card"><p><b>${esc(s.title)}</b></p><p>URL: ${s.url?`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.url)}</a>`:'—'}</p><p>Pobrano: ${esc(s.date)} · rejestr <code>sources/${esc(s.registry)}</code>${s.package?` · pakiet ${esc(s.package)}`:''}</p><p>Licencja: ${esc(s.licence)||'—'}</p><p class="muted">SHA-256: <code>${esc(s.sha256)||'—'}</code></p>${s.note?`<p class="muted">${esc(s.note)}</p>`:''}</div><h2>Cytowany w (${s.cites.length})</h2>`;
  const by={};s.cites.forEach(c=>(by[c.skill+'/'+c.file]=by[c.skill+'/'+c.file]||[]).push(c));
  for(const [k,cs] of Object.entries(by)){const [sk,f]=k.split('/');h+=`<details class="card"><summary><a href="#/plik/${esc(sk)}/${esc(f)}">${esc(k)}</a> <span class="muted">· ${cs.length}</span></summary><ul>${cs.map(c=>`<li><code>[${esc(c.tag)}]</code> <span class="muted">linia ${c.line}</span></li>`).join('')}</ul></details>`}
  return h}
function niedostepne(){
  let h='<h1>Normy i dokumenty niedostępne</h1><p class="muted">Wpisy z <code>sources/niedostepne.yaml</code>. To nie są źródła: baza nie opisuje ich treści i mówi o tym w pierwszym zdaniu odpowiedzi.</p><div class="tbl"><table><thead><tr><th>Dokument</th><th>Dostęp</th><th>Temat</th><th>Przywołany przez</th><th>W skillach</th></tr></thead><tbody>';
  for(const u of D.unavailable)h+=`<tr><td>${esc(u.name)}${u.note?`<br><span class="muted">${esc(u.note)}</span>`:''}</td><td>${esc(u.access)}</td><td>${esc(u.topic)}</td><td>${u.cited_by.map(esc).join('<br>')}</td><td>${u.skills.map(skillLink).join('<br>')}</td></tr>`;
  return h+'</tbody></table></div>'}
function szukaj(q){
  q=q.trim();if(q.length<2)return '<p class="muted">Wpisz co najmniej 2 znaki.</p>';
  const words=q.toLowerCase().split(/\s+/).filter(Boolean),hits=[];
  for(const f of D.files){const low=f.text.toLowerCase();if(words.every(w=>low.includes(w))){const i=low.indexOf(words[0]);hits.push([f,f.text.slice(Math.max(0,i-90),i+200)])}}
  const re=new RegExp('('+words.map(w=>w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|')+')','gi');
  let h=`<h1>Wyniki: ${esc(q)}</h1><p class="muted">${hits.length} plików</p>`;
  for(const [f,snip] of hits)h+=`<div class="hit"><a href="#/plik/${esc(f.skill)}/${esc(f.file)}">${esc(f.skill)} / ${esc(f.file)}</a> <span class="muted">— ${esc(f.title)}</span><br><span class="muted">…${esc(snip).replace(re,'<mark>$1</mark>')}…</span></div>`;
  return h}
function route(){
  const p=decodeURIComponent(location.hash.replace(/^#\/?/,'')).split('/');let h;
  switch(p[0]){case 'skille':h=skille();break;case 'skill':h=skill(p[1]);break;case 'plik':h=plik(p[1],p[2]);break;
    case 'zrodla':h=zrodla();break;case 'zrodlo':h=zrodlo(p[1]);break;case 'rejestr':location.hash='#/zrodla';return;
    case 'niedostepne':h=niedostepne();break;case 'szukaj':h=szukaj(p.slice(1).join('/'));break;default:h=mapa()}
  $('#app').innerHTML=h;window.scrollTo(0,0)}
let tm;$('#q').addEventListener('input',e=>{clearTimeout(tm);tm=setTimeout(()=>{location.hash='#/szukaj/'+encodeURIComponent(e.target.value)},250)});
addEventListener('hashchange',route);route();
</script></body></html>
"""


def render(data: dict) -> str:
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return PAGE.replace("__DATA__", blob)


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
