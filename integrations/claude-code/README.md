# EV Intelligence w Claude Code

Serwer MCP `ev-intelligence` działa lokalnie na Twoim komputerze (stdio), tak jak `pdi`. Nie potrzebuje hostingu, domeny
ani tokenu: Claude Code sam uruchamia `tools/ev_kb_mcp.py` jako proces. Narzędzia (wszystkie tylko czytają):
`ev_route`, `ev_skill`, `ev_search`, `ev_cite`, `ev_check`, `ev_confidential_check`. Każdy skill jest też komendą
`/ev-intelligence:<skill>`. Opis narzędzi i serwera zdalnego: [docs/EV-KB-MCP.md](../../docs/EV-KB-MCP.md).

Działa w Claude Code i Claude Desktop na tym komputerze. W claude.ai w przeglądarce i w aplikacji mobilnej go nie ma,
bo te łączą się tylko z serwerem publicznym przez HTTPS (`docs/DEPLOY.md`).

## Instalacja krok po kroku (macOS / Linux)

**1. Zainstaluj uv** (jeśli `uv --version` już działa, pomiń):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh      # albo: brew install uv
```
Zamknij i otwórz terminal, sprawdź: `uv --version`.

**2. Sklonuj bazę:**
```bash
cd ~
git clone https://github.com/dbqm45/ev-intelligence.git
```

**3. Sprawdź, że serwer startuje** (uv sam pobierze Pythona i pakiety `mcp`, `PyYAML`):
```bash
cd ~/ev-intelligence
uv run --no-project --with-requirements tools/requirements-mcp.txt python3 tools/ev_kb.py route "jak liczona jest cena sesji"
```
Oczekiwany wynik: lista skilli, na górze `ev-billing-tariff-expert`.

**4. Zarejestruj serwer w Claude Code** (raz, dla wszystkich projektów):
```bash
claude mcp add --scope user ev-intelligence -- \
  uv run -q --no-project --with-requirements "$HOME/ev-intelligence/tools/requirements-mcp.txt" \
  python3 "$HOME/ev-intelligence/tools/ev_kb_mcp.py"
claude mcp list       # ev-intelligence powinien mieć status „Connected”
```

**5. Opcjonalnie dopisz [`CLAUDE-fragment.md`](CLAUDE-fragment.md) do `~/.claude/CLAUDE.md`.** Claude będzie wtedy sam
sięgał do bazy przy story, przeglądzie kodu i pytaniach o ładowanie, zamiast odpowiadać z pamięci.

**6. Próba:** uruchom `claude` w dowolnym projekcie, wpisz `/mcp`: `ev-intelligence` z 6 narzędziami. Zapytaj np.
„Co się dzieje w OCPP 2.0.1, gdy kierowca odłączy kabel w trakcie ładowania?”. Odpowiedź powinna mieć znaczniki
`[201-P2 …]` i nazwę skilla, z którego pochodzi.

Aktualizacja bazy: `git -C ~/ev-intelligence pull`. Restart Claude Code wczytuje nową wersję. Numer wersji wiedzy serwer
podaje w instrukcjach (`VERSION` i commit).

## Jak używać
Pełny przewodnik (tryby pracy, jak czytać znaczniki i „Wniosek”, dobre praktyki): [docs/UZYCIE.md](../../docs/UZYCIE.md).


**Pytanie, gdy coś dopiero rozważasz.** Pytasz normalnie, np. „jak liczona jest cena sesji przy taryfie OCPI z
`step_size`?”, „co stanie się z transakcją, gdy stacja straci połączenie z CSMS?”, „jakie wymogi AFIR dotyczą
płatności ad hoc?”. Claude wybiera skill (`ev_route`), czyta jego procedurę (`ev_skill`) i podaje fakty ze
znacznikami. Gdy baza czegoś nie obejmuje, mówi to wprost zamiast zgadywać.

**Przegląd story albo projektu.** Wklej story (albo wskaż plik) i poproś o sprawdzenie pod kątem protokołów, np.:
```
/ev-intelligence:ev-product-designer sprawdź to story: czego brakuje, co jest niezgodne z OCPI/AFIR, jakie przypadki brzegowe pominięto
```
Każdy skill ma sekcję **Pułapki** (typowe błędy i przeoczenia ze źródłami) i to na niej opiera się przegląd.

**Przegląd istniejącego kodu.** W repozytorium projektu:
```
/ev-intelligence:ev-ocpp-expert przejrzyj obsługę TransactionEvent w src/ocpp/ — co jest niezgodne z OCPP 2.0.1, co może nie działać, czego brakuje
```
Claude czyta kod sam, a wiedzę o protokole bierze z bazy. Wnioski, które nie są cytatem, oznacza słowem **Wniosek**.

Który skill do czego (pełna lista: `ev_skill` bez argumentów albo `/mcp`):

| Temat | Skill |
|---|---|
| komunikaty OCPP, przebieg sesji, statusy, autoryzacja | `ev-ocpp-expert` |
| cena, taryfy, CDR, koszt sesji, płatność ad hoc | `ev-billing-tariff-expert` |
| roaming, OCPI, OICP, OCHP | `ev-ocpi-roaming-expert` |
| architektura CSMS/CPMS, połączenia stacji | `ev-cpms-architect` |
| integracje między systemami, migracja stacji | `ev-integration-architect` |
| smart charging, limity mocy, V2G | `ev-energy-smart-charging-expert` |
| Plug & Charge, ISO 15118, certyfikaty | `ev-iso15118-pki-expert` |
| wymogi prawne PL i UE, AFIR, MID | `ev-compliance-expert` |
| story, aplikacja kierowcy, ekran ładowarki, dostępność | `ev-product-designer` |
| dyżur NOC, alarmy, incydenty | `ev-charging-operations-expert` |
| konkretny model ładowarki działa inaczej niż OCPP | `ev-evse-diagnostics-expert` |
| sprzęt, złącza, karta urządzenia | `ev-evse-hardware-expert` |
| ogólny obraz domeny, pojęcia | `ev-domain-expert` |

## Ograniczenia
- **Kopie dokumentów źródłowych.** Świeży klon nie ma tekstów norm (licencje, rozmiar; katalog `.cache/ev-kb/` jest poza
  gitem). Odpowiedzi i znaczniki działają bez nich. `ev_cite` podaje wtedy tylko metadane dokumentu (URL, wersja,
  licencja) bez fragmentu sekcji. Żeby mieć fragmenty: pobierz dokumenty z adresów w `sources/*.yaml` i dodaj je
  poleceniem `tools/ev_kb.py index` (`docs/EV-KB.md`, „Pliki źródłowe”).
- **Źródła poufne** (eMIP): `ev_confidential_check` działa tylko z lokalnym tekstem w `.cache/ev-kb-poufne/`. Bez niego
  zwraca dla każdego terminu `BRAK_TEKSTU`, a nie werdykt.
- **Zakres.** Tematy, których baza jeszcze nie obejmuje: `docs/DO-ZROBIENIA.md` („Tematy bez skilla w bazie”). Wyniki
  ostatnich pomiarów jakości: `docs/evals/`.
