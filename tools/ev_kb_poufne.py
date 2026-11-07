#!/usr/bin/env python3
"""Źródła poufne wewnętrznie: sprawdzenie bez przekazywania treści.

Dotyczy dokumentów, które mamy legalnie, ale których licencja zakazuje ujawniania treści (np. eMIP, licencja Gireve,
rozdz. 1.4 Confidentiality). Zasady (decyzja właściciela projektu, 2026-11-07):

- Rejestr: `sources/poufne/*.yaml` (poza `sources/*.yaml`, więc tych dokumentów nie da się cytować znacznikiem).
- Tekst: tylko lokalnie w `.cache/ev-kb-poufne/` albo w katalogu z EV_KB_POUFNE (poza gitem i obrazem kontenera).
- Wynik sprawdzenia to wyłącznie werdykt dla każdego terminu: WYSTEPUJE / NIE_WYSTEPUJE / BRAK_TEKSTU, z informacją
  o poufności i linkiem do strony, z której pytający może pobrać dokument. Bez fragmentów, numerów sekcji i liczby
  wystąpień.
- Limity chronią przed odtwarzaniem treści serią pytań: najwyżej MAX_TERMS terminów w wywołaniu i RATE_PER_MIN na minutę.

Użycie:
  python3 tools/ev_kb_poufne.py list
  python3 tools/ev_kb_poufne.py index PLIK...
  python3 tools/ev_kb_poufne.py sprawdz [--zrodlo emip] TERMIN...
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ev_kb  # noqa: E402
import yaml  # noqa: E402

ROOT = ev_kb.ROOT
MAX_TERMS = 10
RATE_PER_MIN = 30
TERM_RE = re.compile(r"^[\w.\-/ ]{3,80}$", re.UNICODE)
NOTICE = ("Źródło poufne wewnętrznie: {tytul}. Licencja ({licencja}) zakazuje ujawniania treści, dlatego narzędzie "
          "podaje tylko werdykt, bez fragmentów i numerów sekcji. Szczegóły w dokumencie u wydawcy: {dostep}. "
          "Napisz to w odpowiedzi i nie uzupełniaj treści z pamięci.")


def poufne_dir(root: Path = ROOT) -> Path:
    return Path(os.environ.get("EV_KB_POUFNE") or root / ".cache" / "ev-kb-poufne")


def load_confidential(root: Path = ROOT) -> list[dict]:
    out = []
    for path in sorted((root / "sources" / "poufne").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for d in data.get("documents", []) or []:
            out.append({"id": str(d["id"]), "title": str(d.get("title", "")), "url": str(d.get("url", "")),
                        "sha256": str(d.get("sha256", "")), "licence": str(data.get("licence", "")),
                        "access": str(data.get("access_url", "")), "source": str(data.get("source", "")),
                        "keys": [str(k).lower() for k in data.get("klucze", []) or []], "registry": path.name})
    return out


def cmd_index(files: list[str], root: Path = ROOT) -> list[dict]:
    docs = {d["sha256"]: d for d in load_confidential(root) if d["sha256"]}
    target = poufne_dir(root)
    target.mkdir(parents=True, exist_ok=True)
    res = []
    for name in files:
        p = Path(name)
        if not p.is_file():
            res.append({"file": name, "status": "BRAK_PLIKU"})
            continue
        digest = ev_kb.sha256_file(p)
        d = docs.get(digest)
        if not d:
            res.append({"file": name, "status": "SPOZA_REJESTRU"})
            continue
        (target / f"{d['id']}.txt").write_text(ev_kb.to_text(p), encoding="utf-8")
        res.append({"file": name, "id": d["id"], "status": "OK"})
    return res


class _RateLimiter:
    def __init__(self, per_min: int) -> None:
        self.per_min, self.events, self.lock = per_min, [], threading.Lock()

    def take(self, n: int) -> bool:
        now = time.monotonic()
        with self.lock:
            self.events = [t for t in self.events if now - t < 60]
            if len(self.events) + n > self.per_min:
                return False
            self.events.extend([now] * n)
            return True


LIMITER = _RateLimiter(RATE_PER_MIN)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def verify(terms: list[str], source: str = "", root: Path = ROOT, limiter: _RateLimiter | None = LIMITER) -> dict:
    """Werdykt dla każdego terminu w dokumentach poufnych danego źródła (np. "emip"). Bez treści dokumentów."""
    docs = load_confidential(root)
    src = _norm(source)
    if src:
        docs = [d for d in docs if src == d["source"].lower() or src in d["keys"] or src == d["id"].lower()]
    if not docs:
        return {"status": "NIEZNANE_ZRODLO", "known": sorted({d["source"] for d in load_confidential(root)})}
    terms = [t for t in (str(x).strip() for x in terms) if t]
    if not terms or len(terms) > MAX_TERMS:
        return {"status": "ZLE_ZAPYTANIE", "detail": f"Podaj od 1 do {MAX_TERMS} terminów."}
    bad = [t for t in terms if not TERM_RE.match(t)]
    if bad:
        return {"status": "ZLE_ZAPYTANIE", "detail": "Termin: 3–80 znaków, litery, cyfry, spacja, . - _ /", "terms": bad}
    if limiter is not None and not limiter.take(len(terms)):
        return {"status": "LIMIT", "detail": f"Najwyżej {RATE_PER_MIN} terminów na minutę."}
    texts = {}
    for d in docs:
        p = poufne_dir(root) / f"{d['id']}.txt"
        texts[d["id"]] = _norm(p.read_text(encoding="utf-8")) if p.is_file() else None
    results = {}
    for t in terms:
        pat = re.compile(r"(?<![\w])" + re.escape(_norm(t)) + r"(?![\w])")
        if all(v is None for v in texts.values()):
            results[t] = "BRAK_TEKSTU"
        else:
            results[t] = "WYSTEPUJE" if any(v is not None and pat.search(v) for v in texts.values()) else "NIE_WYSTEPUJE"
    first = docs[0]
    return {"status": "OK", "source": first["source"], "results": results,
            "documents": [{"id": d["id"], "title": d["title"], "sha256": d["sha256"]} for d in docs],
            "notice": NOTICE.format(tytul=", ".join(d["title"] for d in docs), licencja=first["licence"],
                                    dostep=first["access"])}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("index")
    p.add_argument("files", nargs="+")
    p = sub.add_parser("sprawdz")
    p.add_argument("--zrodlo", default="")
    p.add_argument("terms", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        res = [{k: d[k] for k in ("id", "source", "title", "sha256", "access")} for d in load_confidential()]
    elif a.cmd == "index":
        res = cmd_index(a.files)
    else:
        res = verify(a.terms, a.zrodlo, limiter=None)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
