#!/usr/bin/env python3
"""Serwer MCP „ev-intelligence”: wiedza EV z kontrolą źródeł dla dowolnego klienta Claude.

Cienka nakładka na tools/ev_kb.py (te same funkcje, te same wyniki). Protokół obsługuje oficjalny Python SDK MCP
(pakiet `mcp`, wersja 2.x, klasa MCPServer).

Transporty:
  stdio            klient uruchamia serwer jako proces (Claude Code, Claude Desktop):
                   python3 tools/ev_kb_mcp.py
  streamable-http  serwer pod adresem URL (dla klientów, które łączą się przez sieć):
                   python3 tools/ev_kb_mcp.py --transport http [--host 127.0.0.1] [--port 8765]
                   Domyślnie tylko localhost. Inny adres wymaga EV_KB_TOKEN (≥ 32 znaki): każde żądanie musi mieć
                   nagłówek `Authorization: Bearer <token>` albo adres `/<token>/mcp`.
                   Szczegóły i licencje: docs/EV-KB-MCP.md.

Zmienne: EV_KB_TOKEN (token HTTP), PORT, EV_KB_ROOT (katalog repozytorium z wiedzą; domyślnie to repozytorium), EV_KB_DOCS (kopie dokumentów).
"""
from __future__ import annotations

import argparse
import hmac
import os
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ev_kb  # noqa: E402

try:
    from mcp.server.mcpserver import MCPServer
    from mcp.types import ToolAnnotations
except ImportError:  # pragma: no cover
    sys.stderr.write("Brak pakietu `mcp` w wersji 2.x (pip install 'mcp>=2,<3').\n")
    raise

ROOT = Path(os.environ.get("EV_KB_ROOT") or ev_kb.ROOT).resolve()
READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)

INSTRUCTIONS = """EV Intelligence: wiedza o ładowaniu pojazdów elektrycznych (OCPP, OCPI, CPMS, operacje, sprzęt, taryfy,
AFIR) z cytatami ze źródeł oficjalnych (OCA, EVRoaming Foundation, EUR-Lex).

Zasady:
1. Nic z pamięci modelu. Fakty o protokołach, normach i regulacjach bierz z tych narzędzi i podawaj ze znacznikiem
   [ID §sekcja] oraz nazwą dokumentu słowami (np. „specyfikacja OCPI 2.3.0 §10.3.1 [OCPI230 §10.3.1]”).
2. Kolejność: ev_route (które skille i domeny), potem ev_skill (procedura, pułapki, references), ev_search (konkretny
   fakt), ev_cite (źródło i fragment tekstu), ev_check (kontrola znaczników w gotowym tekście).
3. Rekomendacje wyprowadzone z faktów oznaczaj słowem „Wniosek”.
4. Gdy baza czegoś nie obejmuje (brak trafień, skill nieopracowany), powiedz to wprost. Nie uzupełniaj z pamięci.
"""

server = MCPServer(
    name="ev-intelligence",
    title="EV Intelligence",
    description="Wiedza EV (OCPP, OCPI, CPMS, AFIR, taryfy) z kontrolą źródeł oficjalnych",
    instructions=INSTRUCTIONS,
    version="0.1.0",
)


def _docs() -> Path:
    return ev_kb.docs_dir(None, ROOT)


@server.tool(title="Dobór skilli i domen", annotations=READ_ONLY)
def ev_route(task: str, limit: int = 5) -> dict[str, Any]:
    """Które skille EV Intelligence i które poddomeny taksonomii dotyczą zadania. Zwraca też skille zaplanowane,
    ale jeszcze nieopracowane (wtedy baza tej wiedzy nie ma). Wywołaj na początku zadania z branży EV."""
    return ev_kb.cmd_route(task, max(1, min(limit, 20)), ROOT)


@server.tool(title="Treść skilla", annotations=READ_ONLY)
def ev_skill(name: str | None = None, file: str | None = None) -> dict[str, Any]:
    """Bez argumentów: lista skilli z opisami i plikami references. Z `name`: treść SKILL.md (procedura, przykład,
    pułapki). Z `name` i `file`: plik z references/ (np. "taryfy-ocpi.md")."""
    if not name:
        return {"skills": ev_kb.list_skills(ROOT)}
    return ev_kb.read_skill(name, file, ROOT)


@server.tool(title="Szukaj w wiedzy", annotations=READ_ONLY)
def ev_search(query: str, limit: int = 5) -> dict[str, Any]:
    """Fragmenty skilli i knowledge/ pasujące do pytania, każdy z plikiem, linią i znacznikami źródeł.
    Pusta lista oznacza, że baza tego nie obejmuje."""
    sources = ev_kb.load_sources(ROOT)
    hits = ev_kb.cmd_search(query, max(1, min(limit, 20)), sources, ROOT)
    return {"hits": hits, "note": "" if hits else "Brak trafień: baza tego nie obejmuje. Nie uzupełniaj z pamięci."}


@server.tool(title="Źródło znacznika", annotations=READ_ONLY)
def ev_cite(tag: str) -> dict[str, Any]:
    """Rozwija znacznik, np. "[OCPI230 §10.3.1]" albo "AFIR art. 5 ust. 4": dokument z rejestru (tytuł, URL, data,
    SHA-256, licencja) i, gdy jest lokalna kopia, początek wskazanej sekcji."""
    sources = ev_kb.load_sources(ROOT)
    tag = tag.strip().strip("`").strip("[]")
    doc_id, _ = ev_kb.split_tag(tag)
    if doc_id not in sources:
        return {"tag": tag, "status": "NIEZNANY_DOKUMENT", "known_ids": sorted(sources)}
    r = ev_kb.check_tag(tag, sources, _docs(), {})
    return {"source": ev_kb.asdict(sources[doc_id]), "result": ev_kb.asdict(r)}


@server.tool(title="Kontrola znaczników", annotations=READ_ONLY)
def ev_check(text: str, require_text: bool = False) -> dict[str, Any]:
    """Sprawdza wszystkie znaczniki `[ID §…]` w tekście (np. opis PR, odpowiedź, dokument): czy dokument jest w
    rejestrze i czy sekcja istnieje w jego tekście. ok=false przy nieznanym dokumencie albo nieznalezionej sekcji."""
    sources = ev_kb.load_sources(ROOT)
    texts: dict = {}
    results = []
    for line, tag in ev_kb.extract_tags(text, sources):
        r = ev_kb.check_tag(tag, sources, _docs(), texts)
        results.append(dict(ev_kb.asdict(r), line=line))
    failing = {"NIEZNANY_DOKUMENT", "NIE_ZNALEZIONO"} | ({"BRAK_TEKSTU"} if require_text else set())
    return {"ok": not any(r["status"] in failing for r in results), "count": len(results), "results": results}


class BearerAuth:
    """ASGI: żądanie przechodzi, gdy ma nagłówek `Authorization: Bearer <token>` albo ścieżkę `/<token>/mcp`.

    Druga forma jest dla konektorów bez obsługi nagłówków (claude.ai: „No sign-in”). Porównanie stałoczasowe.
    """

    def __init__(self, app, token: str):
        self.app, self.token = app, token.encode()
        self.expected = b"Bearer " + self.token

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            got = dict(scope.get("headers") or []).get(b"authorization", b"")
            path = scope.get("path", "")
            parts = path.split("/", 2)                    # ["", "<token>", "mcp…"]
            if hmac.compare_digest(got, self.expected):
                pass
            elif len(parts) == 3 and hmac.compare_digest(parts[1].encode(), self.token):
                scope = dict(scope, path="/" + parts[2], raw_path=("/" + parts[2]).encode())
            else:
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"content-type", b"text/plain; charset=utf-8"), (b"www-authenticate", b"Bearer")]})
                await send({"type": "http.response.body", "body": "Brak lub zły token.\n".encode()})
                return
        await self.app(scope, receive, send)


def http_app(token: str | None):
    """Aplikacja Streamable HTTP (bezstanowa, odpowiedzi JSON) z opcjonalnym tokenem."""
    app = server.streamable_http_app(stateless_http=True, json_response=True)
    return BearerAuth(app, token) if token else app


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Serwer MCP ev-intelligence")
    ap.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8765")))
    a = ap.parse_args(argv)
    if a.transport == "stdio":
        server.run("stdio")
        return 0
    token = os.environ.get("EV_KB_TOKEN") or None
    local = a.host in ("127.0.0.1", "localhost", "::1")
    if not local and (not token or len(token) < 32):
        sys.stderr.write("Odmowa: adres inny niż localhost wymaga EV_KB_TOKEN (co najmniej 32 znaki).\n")
        return 2
    import uvicorn
    # access_log=False: przy tokenie w ścieżce adres zawiera sekret
    uvicorn.run(http_app(token), host=a.host, port=a.port, log_level="info", access_log=not token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
