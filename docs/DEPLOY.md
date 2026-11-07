# Wdrożenie serwera MCP `ev-intelligence`

Cel: jeden publiczny adres HTTPS, który podłączasz raz jako konektor w claude.ai. Wiedza jest wtedy dostępna w
claude.ai, aplikacjach mobilnych, Claude Desktop, Cowork i w Claude Code zalogowanym kontem claude.ai, także w
trybie Talos (opis klientów: `docs/EV-KB-MCP.md`).

```
claude.ai / Claude Code ──HTTPS──▶ Caddy :443 (certyfikat automatyczny) ──HTTP──▶ ev-kb :8765 (kontener, tylko odczyt)
   (z chmury Anthropic)                                                          token + walidacja Host/Origin
```

## Pliki
| Plik | Rola |
|---|---|
| `deploy/Dockerfile` | obraz serwera: Python 3.13.18-slim przypięty skrótem, użytkownik bez uprawnień (UID 10001), healthcheck `/healthz` |
| `deploy/requirements.lock` | przypięte `mcp==2.3.0`, `PyYAML==6.0.3` |
| `deploy/compose.yaml` | serwer + Caddy 2.10.2; kontener serwera tylko do odczytu, bez capabilities, `no-new-privileges` |
| `deploy/Caddyfile` | reverse proxy z HTTPS dla `EV_KB_DOMAIN` |
| `deploy/env.example` | wzór `deploy/.env` (domena, token, wersja wiedzy) |
| `.dockerignore` | do obrazu nie trafiają `.git`, `.cache` (kopie dokumentów), `.work`, `evals`, `docs`, `tests`, `deploy/.env` |

## Wymagania
- Maszyna z Dockerem i Docker Compose, dostępna z internetu. Konektor łączy się z infrastruktury Anthropic, więc
  serwer w sieci prywatnej, za VPN albo za firewallem się nie połączy.
- Domena z rekordem DNS A/AAAA wskazującym na maszynę. Caddy wystawia certyfikat publiczny tylko dla nazwy, która nie
  jest localhost ani adresem IP.
- Otwarte porty 80 i 443. Port 80 jest potrzebny do wyzwania HTTP ACME przy wydawaniu certyfikatu.
- Trwały wolumen na dane Caddy (`caddy_data` w compose), bo tam są certyfikaty i klucze.

## Uruchomienie
```bash
git clone https://github.com/dbqm45/ev-intelligence.git && cd ev-intelligence/deploy
```
Repozytorium jest prywatne, więc klon wymaga uwierzytelnienia na maszynie, np. klucza wdrożeniowego (deploy key) tylko do odczytu.
```bash
cp env.example .env
```
Uzupełnij `.env`: `EV_KB_DOMAIN`, `EV_KB_TOKEN` i `EV_KB_VERSION`. Token wygeneruj tak:
```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```
Wersję wiedzy weź z repozytorium:
```bash
git rev-parse --short=12 HEAD
```
Start:
```bash
docker compose up -d --build
```
Kontrola:
```bash
docker compose ps
```
```bash
curl -s https://<twoja-domena>/healthz
```
Spodziewany wynik: `ok`, usługa `ev-kb` ze statusem `healthy`. Żądanie do `/mcp` bez tokenu dostaje 401.

## Podłączenie w claude.ai
**Customize > Connectors > Add custom connector**, a potem jedna z dwóch metod:
- adres `https://<domena>/<token>/mcp`, uwierzytelnienie „No sign-in”. Działa na każdym planie;
- adres `https://<domena>/mcp`, „No sign-in” i nagłówek `authorization` z wartością `Bearer <token>`. Tylko gdy
  dialog ma sekcję **Request headers**, która jest w becie dla części organizacji.

Potem w Claude Code (zalogowanym kontem claude.ai) konektor pojawia się w `/mcp`. Szczegóły i źródła:
`docs/EV-KB-MCP.md`.

## Aktualizacja wiedzy
```bash
cd ev-intelligence && git pull
```
```bash
cd deploy && sed -i "s/^EV_KB_VERSION=.*/EV_KB_VERSION=$(git rev-parse --short=12 HEAD)/" .env && docker compose up -d --build
```
Klienci dostają nową wersję od razu. Wersja (commit) jest w instrukcjach serwera.

## Bezpieczeństwo
- **Token** to jedyne zabezpieczenie dostępu. Przy metodzie z tokenem w adresie URL konektora jest hasłem.
  - Zmiana tokenu: nowy token w `.env`, potem `docker compose up -d`, potem ponowne dodanie konektora z nowym adresem
    (w claude.ai konektora nie da się edytować, trzeba go usunąć i dodać ponownie).
- **Logi:** serwer przy ustawionym tokenie nie zapisuje logów dostępu. Caddy zapisuje logi dostępu tylko z dyrektywą
  `log`, której `Caddyfile` nie ma. Sprawdzone na Caddy 2.10.2: w logach nie ma adresów żądań ani tokenu.
- **Host i Origin:** serwer przyjmuje tylko `Host` równy `EV_KB_DOMAIN` (inny dostaje 421). Nagłówek `Origin`, jeśli
  jest, musi być `https://<domena>`, inaczej 403. Żądanie bez `Origin` przechodzi. Gdyby konektor dostawał 403
  „Invalid Origin header”, log kontenera pokazuje odrzuconą wartość; dodaj ją do `EV_KB_ALLOWED_ORIGINS`.
- **Uprawnienia:** narzędzia tylko czytają. Kontener ma system plików tylko do odczytu i działa bez capabilities.
- OAuth (osobne konta użytkowników) nie jest zaimplementowany.

## Licencje: kopie dokumentów źródłowych
Domyślnie obraz **nie zawiera** dokumentów źródłowych. `ev_cite` podaje wtedy metadane z rejestru (URL, data, SHA-256)
bez fragmentu tekstu (`BRAK_TEKSTU`), a reszta narzędzi działa normalnie. Odblokowanie wolumenu `/docs` w
`compose.yaml` sprawia, że serwer zwraca dosłowne fragmenty dokumentów. Przed tym trzeba zdecydować o licencjach:
dokumenty OCA i EVRF mają według rejestru CC BY-ND 4.0, a zasady EUR-Lex są oznaczone „[niesprawdzone]”.

Teksty źródeł poufnych (np. eMIP) montuje się osobnym wolumenem `/poufne` (`EV_KB_POUFNE`). Serwer zwraca z nich tylko
werdykt `ev_confidential_check`, nigdy treść; zasady w `docs/EV-KB-MCP.md`, „Źródła poufne wewnętrznie”.

## Koszt
Zależy od wybranego dostawcy maszyny i domeny; nie jest tu szacowany. Serwer jest lekki: obraz ma ok. 240 MB i nie
potrzebuje bazy danych.

## Budowa za proxy z inspekcją TLS
Jeśli pip w trakcie budowy nie ufa certyfikatowi proxy (sieć firmowa), podaj CA jako sekret budowy. Weryfikacja TLS
zostaje włączona, a certyfikat nie trafia do obrazu:
```bash
docker build --secret id=pip_ca,src=/ścieżka/ca.crt -f deploy/Dockerfile -t ev-intelligence-mcp .
```

## Co sprawdzono (2026-11-07, lokalnie)
- Obraz zbudowany; kontener `healthy`, UID 10001, `--read-only`, `--cap-drop ALL`.
- Compose z Caddy na `localhost` (lokalne CA Caddy):
  - HTTPS przez proxy;
  - token w ścieżce i nagłówek `Bearer` → 200; brak tokenu → 401; obcy `Origin` → 403; obcy `Host` → 421;
  - klient oficjalnego SDK MCP wywołał narzędzia przez Caddy;
  - token nie pojawił się w żadnym logu.
- **Nie sprawdzono:** certyfikatu publicznego dla prawdziwej domeny i połączenia z konektora w claude.ai, bo wymaga to
  maszyny z publicznym adresem.

Źródła: dokumentacja Caddy `https://caddyserver.com/docs/automatic-https` (wymagania nazwy, wyzwanie HTTP na porcie 80,
trwały katalog danych) i `https://caddyserver.com/docs/caddyfile/directives/log` (logi dostępu tylko po
skonfigurowaniu), sprawdzona 2026-11-07, także w repozytorium źródłowym `caddyserver/website`. Konektory i MCP: źródła w `docs/EV-KB-MCP.md`.
