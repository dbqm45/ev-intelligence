# Serwer MCP `ev-intelligence`: wiedza EV w dowolnym kliencie Claude

`tools/ev_kb_mcp.py` udostępnia funkcje `tools/ev_kb.py` (opis: `docs/EV-KB.md`) jako serwer MCP. Protokół obsługuje
oficjalny Python SDK MCP (`mcp` 2.x, klasa `MCPServer`). Wymagania: Python ≥ 3.10, `pip install -r
tools/requirements-mcp.txt`.

## Narzędzia
Wszystkie tylko czytają (`readOnlyHint: true`, `openWorldHint: false`). Wynik jest strukturalny (JSON).

| Narzędzie | Do czego |
|---|---|
| `ev_route(task)` | które skille i poddomeny dotyczą zadania; skille zaplanowane, ale nieopracowane |
| `ev_skill(name?, file?)` | lista skilli albo treść `SKILL.md` / pliku z `references/`. Dzięki temu klient **bez zainstalowanych skilli** dostaje procedury i pułapki |
| `ev_search(query)` | fragmenty wiedzy ze znacznikami źródeł; pusta lista = baza tego nie obejmuje |
| `ev_cite(tag)` | dokument z rejestru (URL, data, SHA-256, licencja) i fragment sekcji z lokalnej kopii |
| `ev_check(text)` | kontrola znaczników `[ID §…]` w tekście, np. w opisie PR albo w odpowiedzi modelu |
| `ev_confidential_check(terms, source)` | źródła poufne wewnętrznie (np. `emip`): tylko werdykt WYSTEPUJE / NIE_WYSTEPUJE dla do 10 nazw komunikatów, pól lub wartości, z informacją o poufności i linkiem do wydawcy; bez treści (opis niżej) |

**Jedno połączenie zamiast instalowania skilli.** Skille nie są instalowane w kliencie. Serwer czyta je z
repozytorium, więc po `git pull` na serwerze każdy klient ma od razu aktualną wiedzę i nie trzeba śledzić, co gdzie
dodano. Elementy, które zastępują zainstalowane skille:
- **instrukcje serwera** zawierają katalog wszystkich skilli z ich opisami, budowany automatycznie przy starcie.
  Claude Code przy wyszukiwaniu narzędzi ładuje na start tylko nazwy narzędzi i instrukcje serwera, które według
  dokumentacji działają podobnie do opisów skilli. Limit to 4096 znaków; przy przekroczeniu katalog skraca się do nazw;
- **prompty MCP**: każdy skill jest promptem z argumentem `task`. W Claude Code to komenda
  `/ev-intelligence:<skill>` (albo `/mcp__ev-intelligence__<skill>`), która wstawia treść `SKILL.md` do rozmowy;
- **wersja wiedzy** (commit repozytorium) w instrukcjach, żeby odpowiedź dało się przypisać do wersji bazy.

Serwer przekazuje klientowi instrukcje (pole `instructions` przy inicjalizacji): nic z pamięci, znaczniki ze słowną
nazwą dokumentu, „Wniosek” przy rekomendacjach, jawne luki.

## Gdzie działa i jak podłączyć
Stan dokumentacji na 2026-11-07. Źródła na końcu.

| Klient | Sposób | Wymaga |
|---|---|---|
| Claude Code (lokalnie) | stdio | klon repozytorium, Python i `mcp` |
| claude.ai (przeglądarka), aplikacje mobilne, Claude Desktop, Cowork | **konektor po URL** | serwer HTTP dostępny publicznie przez HTTPS |
| Claude Code zalogowany kontem claude.ai | ten sam konektor, pojawia się automatycznie | jak wyżej |

**Wniosek:** jeden zdalny serwer z konektorem w claude.ai obejmuje wszystkie klienty. Stdio jest wygodne do pracy nad
samą bazą i nie wymaga hostingu.

### Claude Code: stdio
Składnia z dokumentacji Claude Code: opcje Claude przed `--`, polecenie serwera po `--`.

```bash
claude mcp add --transport stdio ev-intelligence -- python3 /ścieżka/do/ev-intelligence/tools/ev_kb_mcp.py
```

Dla całego zespołu w danym projekcie: `--scope project` (wpis w `.mcp.json` w katalogu projektu). Dla wszystkich
projektów: `--scope user`.

### Konektor w claude.ai: serwer zdalny
Gotowe pliki wdrożenia (Docker, Caddy z HTTPS) i procedura: `docs/DEPLOY.md`. Za reverse proxy ustaw
`EV_KB_ALLOWED_HOSTS` na domenę, bo SDK sprawdza nagłówek `Host`. Compose robi to sam.

1. Uruchom serwer HTTP pod publicznym adresem HTTPS:
   ```bash
   EV_KB_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" \
     python3 tools/ev_kb_mcp.py --transport http --host 0.0.0.0 --port 8765
   ```
   Poza localhost serwer nie wystartuje bez `EV_KB_TOKEN` (co najmniej 32 znaki). Tryb bezstanowy z odpowiedziami JSON
   (`stateless_http`, `json_response`), więc można uruchomić kilka instancji za load balancerem.
2. Połączenie przychodzi **z infrastruktury Anthropic, nie z Twojego komputera**. Serwer musi być osiągalny z
   publicznego internetu. Serwer w sieci firmowej, za VPN albo za firewallem się nie połączy.
3. W claude.ai: **Customize > Connectors > Add custom connector**, adres serwera, potem uwierzytelnienie:
   - **nagłówek** (jeśli organizacja ma sekcję **Request headers**, obecnie w becie dla części organizacji):
     URL `https://<host>/mcp`, „No sign-in”, nagłówek `authorization` o wartości `Bearer <token>`. Claude wysyła
     wartość dokładnie tak, jak ją wpiszesz, więc słowo `Bearer` i spację trzeba wpisać;
   - **token w ścieżce** (gdy nie ma sekcji nagłówków): URL `https://<host>/<token>/mcp`, „No sign-in”. Serwer
     wyłącza wtedy logi dostępu, żeby adres z sekretem nie trafiał do logów. URL traktujesz jak hasło.
4. Na planie Free można dodać jeden własny konektor. W Team i Enterprise konektor dodaje właściciel organizacji, a
   członkowie się z nim łączą.

OAuth (logowanie każdej osoby osobno) nie jest zaimplementowany. Jest potrzebny, gdy dostęp mają mieć różne osoby z
osobnymi uprawnieniami.

## Źródła poufne wewnętrznie
Dotyczy dokumentów, które mamy legalnie, ale których licencja zakazuje ujawniania treści osobom trzecim (pierwszy
przypadek: eMIP, licencja Gireve, rozdz. 1.4). Decyzja właściciela projektu (2026-11-07): baza **nie przekazuje
wiedzy** z takich dokumentów, a tylko stwierdza zgodność albo jej brak i wskazuje, gdzie pobrać dokument.
- Rejestr: `sources/poufne/*.yaml`. Te dokumenty nie są w rejestrze cytowalnym, więc znacznik `[EMIP-PD …]` w skillu
  to błąd `check`.
- Tekst leży tylko w `.cache/ev-kb-poufne/` (albo w katalogu z `EV_KB_POUFNE`), poza gitem i obrazem kontenera.
  Indeksowanie: `python3 tools/ev_kb_poufne.py index PLIK…` (plik musi mieć SHA-256 z rejestru).
- `ev_confidential_check` zwraca tylko werdykt dla każdego terminu, bez fragmentów, numerów sekcji i liczby wystąpień.
  Limity: 10 terminów w wywołaniu, 30 na minutę na proces (ochrona przed odtwarzaniem treści serią pytań).
- Werdykt deterministyczny dotyczy tylko występowania nazw. Ocena zgodności całego opisu wymagałaby modelu po stronie
  serwera (klucz API, koszt), żeby treść nie trafiała do modelu pytającego. To decyzja na później.
- Ograniczenie: to interpretacja licencji, nie opinia prawna. Przy użyciu komercyjnym warto mieć pisemne potwierdzenie
  wydawcy.

## Decyzje przed uruchomieniem publicznym
- **Hosting:** gdzie działa serwer (np. mała maszyna albo kontener z HTTPS), kto za to płaci i kto go utrzymuje.
- **Licencje treści:** `ev_cite` zwraca dosłowne fragmenty dokumentów, jeśli serwer ma lokalne kopie (`.cache/ev-kb`).
  Dokumenty OCA i EVRF są na CC BY-ND 4.0 (według rejestru `sources/*.yaml`). Zasady ponownego wykorzystania EUR-Lex są
  w rejestrze oznaczone „[niesprawdzone]”. Bez kopii serwer podaje tylko metadane i treść skilli.
- **Wersja wiedzy:** serwer czyta repozytorium, z którego działa. Aktualizacja = `git pull` i restart.

## Testy
`tests/test_ev_kb_mcp.py`: klient SDK w procesie (lista narzędzi, adnotacje, instrukcje, wyniki, ochrona ścieżek w
`ev_skill`), blokada adresu publicznego bez tokenu, nagłówek i token w ścieżce. Ręcznie sprawdzone 2026-11-07: stdio
jako podproces, Streamable HTTP z klientem SDK, inicjalizacja surowym JSON-RPC z wersją protokołu 2025-06-18.

## Źródła (pobrane 2026-11-07)
- Specyfikacja MCP 2025-11-25, transporty: `github.com/modelcontextprotocol/modelcontextprotocol`,
  `docs/specification/2025-11-25/basic/transports.mdx` (stdio: wiadomości rozdzielane znakiem nowej linii, stdout tylko
  dla MCP; Streamable HTTP: walidacja `Origin`, na localhost nasłuch tylko na 127.0.0.1, zalecane uwierzytelnienie).
- Python SDK MCP 2.3.0 (pakiet `mcp`, licencja MIT): `MCPServer`, `run("stdio" | "streamable-http")`,
  `streamable_http_app(stateless_http, json_response)`.
- Claude Code, „Connect Claude Code to tools via MCP”: `https://code.claude.com/docs/en/mcp.md` (`claude mcp add`,
  zakresy local/project/user, konektory claude.ai widoczne w Claude Code, limity rozmiaru wyników, `readOnlyHint`).
- Claude Help Center, „Get started with custom connectors using remote MCP”:
  `https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp`
  (plany, połączenie z chmury Anthropic, wymóg dostępności publicznej).
- „Add a connector that isn't in the directory”: `https://claude.com/docs/connectors/custom/add-unlisted.md`
  (Customize > Connectors, „No sign-in”, Request headers w becie, wartość nagłówka wysyłana dosłownie, rozszerzenia
  MCPB dla Claude Desktop).
