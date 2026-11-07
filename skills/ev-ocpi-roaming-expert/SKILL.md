---
name: ev-ocpi-roaming-expert
description: Użyj przy roamingu OCPI 2.2.1 i 2.3.0 między CPO, eMSP i hubem — rejestracja credentials, Locations, Sessions, CDR, taryfy, tokeny, komendy, routing.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy pytaniach i decyzjach projektowych dotyczących OCPI (2.2.1, 2.3.0; status 3.0) między platformami CPO, eMSP, hubem, NSP, NAP, SCSP i PTP — wersje i role, rejestracja i tokeny credentials A/B/C, nagłówek Authorization (Base64), push i pull, paginacja, nagłówki routingu przez hub, X-Request-ID i X-Correlation-ID, kody statusu OCPI, zachowanie offline, Locations/EVSE/Connector i statusy, Sessions, CDR i credit CDR, taryfy i step_size, tokeny i whitelist, autoryzacja real-time, asynchroniczne komendy START_SESSION, STOP_SESSION, RESERVE_NOW, UNLOCK_CONNECTOR. Każdy fakt z cytatem ze specyfikacji EVRoaming Foundation. Nie do protokołu ładowarka–CSMS (ev-ocpp-expert), doboru domen dla zadania przekrojowego (ev-domain-expert) ani OICP/Hubject i eMIP (domeny D01.03–D01.04, jeszcze nieopracowane)."
  slowa: "OCPI, OCPI 2.2.1, OCPI 2.3.0, OCPI 3.0, roaming, EVRoaming Foundation, CPO, eMSP, MSP, hub, roaming hub, NSP, NAP, SCSP, platforma, credentials, CREDENTIALS_TOKEN_A, token B, token C, rejestracja partnera, onboarding roamingu, 401 OCPI, versions endpoint, Authorization Token, Base64, push, pull, paginacja, X-Total-Count, X-Limit, Link, date_from, OCPI-to-party-id, OCPI-from-country-code, routing, X-Request-ID, X-Correlation-ID, status_code 1000, 2001, 2003, 3001, 4001, Locations, EVSE, Connector, status EVSE, UNKNOWN, OUTOFORDER, INOPERATIVE, REMOVED, Sessions, SessionStatus, CDR, credit CDR, credit_reference_id, Tariffs, step_size, PriceComponent, TariffDimensionType, Tokens, whitelist, real-time authorization, ALLOWED_OFFLINE, Commands, START_SESSION, CommandResponse, CommandResult, response_url, timeout komendy, sesja roamingowa nie startuje, synchronizacja po awarii, ładowarki roamingowe, country_code party_id"
---

# OCPI / Roaming Expert — CPO ↔ eMSP ↔ hub

Skill odpowiada na pytania o **protokół OCPI**: role, rejestrację, transport, moduły i ich cykl życia. Projekt modułu
CPMS dla ładowarek roamingowych to `ev-cpms-architect` (D05.05, jeszcze nieopracowany). Tu podajesz **ograniczenia
protokołu**. Taksonomia: D01.02, D06. Sieć: brak.

**Zasada źródeł.** Fakty pochodzą z dokumentów EVRoaming Foundation w `sources/evrf-ocpi.yaml`. Znacznik
`[OCPI230 §x]` wskazuje sekcję OCPI 2.3.0 (2025-02-21). Kluczowe zdania mają identyczne brzmienie
w `[OCPI221]` (porównanie ciągów; numery sekcji: tabela w `references/transport.md`). Inne fakty dla 2.2.1
sprawdzasz w `[OCPI221]` przed cytowaniem. **Wniosek** to rekomendacja wyprowadzona
z cytowanych wymagań. Czego dokumenty nie określają, nie podajesz z pamięci.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „errata OCPP 1.6
§3.18 `[16E §3.18]`”, „specyfikacja OCPI 2.3.0 §4.4 `[OCPI230 §4.4]`”, „AFIR art. 5 ust. 10”, „rozporządzenie
wykonawcze 2025/655 art. 2 `[AFIR-655 art. 2]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/wersje-i-role.md` | status wersji (2.2.1, 2.3.0, 3.0), role i typowe moduły per rola, topologie, rozszerzenia EVRF |
| `references/transport.md` | Authorization i Base64, push/pull, paginacja, routing przez hub, ID żądań, kody statusu, offline |
| `references/moduly.md` | Credentials A/B/C, Locations i statusy EVSE, Sessions, CDR i credit CDR, Tariffs i `step_size`, Tokens, Commands |

## Procedura
1. **Ustal wersję po obu stronach i rolę każdej platformy.** Wspólną wersję wybiera się w module Versions podczas
   rejestracji `[OCPI230 §7.1.1]`. Platforma może pełnić wiele ról (CPO, eMSP, hub, NSP, NAP, SCSP, PTP)
   `[OCPI230 §2.3]`.
2. **Ustal właściciela danych i kierunek.** Kto jest Senderem, a kto Receiverem w danym module, i czy działa push,
   pull, czy oba. Pull jest wymagany, push opcjonalny `[OCPI230 §4.1.3]`. Typowe role: `references/wersje-i-role.md`.
3. **Ustal topologię.** Połączenie peer-to-peer czy przez hub. Przez hub moduły funkcjonalne niosą nagłówki routingu,
   a moduły konfiguracyjne (Credentials, Versions, Hub Client Info) ich nie mają `[OCPI230 §4.1.9.2]`.
4. **Nazwy obiektów, pól i wartości enum** bierzesz z `references/`. Wartość spoza nich → piszesz, że w cytowanej sekcji
   jej nie ma.
5. **Oddziel warstwy:** HTTP (401, 404, 400) → `status_code` OCPI (1xxx/2xxx/3xxx/4xxx) → wynik biznesowy
   (np. `CommandResult`, `SessionStatus`) `[OCPI230 §5]`.
6. **Awaria łączności:** OCPI nie kolejkuje komunikatów. Odbiorca po powrocie łączności robi GET (pull) z filtrem
   `date_from` `[OCPI230 §4.4]` `[OCPI230 §4.1.4.1]`.
7. **Zakończ kryteriami akceptacji:** jakie wywołania HTTP i jakie `status_code` w jakiej kolejności, oraz przypadki
   brzegowe (timeout komendy, brak `CommandResult`, credit CDR, zmiana `X-Total-Count` w trakcie paginacji).

## Przykład
**Pytanie:** „Jako eMSP wysłaliśmy `START_SESSION`, CPO zwrócił `ACCEPTED`, potem przyszedł `CommandResult` `ACCEPTED`,
a sesji nie ma.”

1. Komendy są **asynchroniczne**. `CommandResponse` w odpowiedzi HTTP mówi tylko, czy CPO może przekazać polecenie
   do stacji. Wynik ze stacji przychodzi później jako `CommandResult` na `response_url` `[OCPI230 §13.1]`.
2. `CommandResult` `ACCEPTED` oznacza „Command request accepted by the Charge Point” `[OCPI230 §13.4.2]`. Specyfikacja
   pokazuje dokładnie ten przypadek: `ACCEPTED`, a sesja nie powstaje, bo EV nie został podłączony przed upływem
   timeoutu (Figure 28) `[OCPI230 §13.1]`.
3. Stan sesji pochodzi z modułu Sessions (`PENDING`, `ACTIVE`, `COMPLETED`, `INVALID`, `RESERVATION`).
   `PENDING` „might never become an active session” `[OCPI230 §9.4.3]`.
4. `CommandResponse.timeout` (sekundy): gdy `CommandResult` nie przyjdzie w tym czasie, eMSP może założyć, że nie
   przyjdzie wcale. OCPI nie przewiduje ponowień `[OCPI230 §13.3.2]`.
5. **Wniosek, kryteria dla aplikacji eMSP:**
   - status „czekam na stację” do `CommandResult` albo `timeout`;
   - po `ACCEPTED` status „podłącz pojazd”, aż Session przejdzie w `ACTIVE`;
   - brak `ACTIVE` w rozsądnym czasie → komunikat „sesja nie rozpoczęła się” bez automatycznego ponowienia
     (ponowienie przy otwartym poprzednim poleceniu może dać dwie próby startu na stacji).
   Po stronie CPO szczegóły polecenia OCPP: `ev-ocpp-expert`.

## Pułapki
- Nagłówek `Authorization: Token <Base64(credentials token)>`. Wiele implementacji 2.1.1 i 2.2 nie koduje tokenu,
  a od 2.2-d2 kodowanie Base64 jest wymagane `[OCPI230 §4.1.2]`.
- `CREDENTIALS_TOKEN_A` działa tylko dla modułów Credentials i Versions. Inne moduły z tym tokenem → HTTP 401
  `[OCPI230 §4.1.2]`.
- Kolejkowanie nieudanych PUT/PATCH: „OCPI messages SHOULD NOT be queued” `[OCPI230 §4.4]`.
- Zmiana lub kasowanie wysłanego CDR: niedozwolone. Wysyłasz credit CDR z `credit = true`, `credit_reference_id`
  i ujemnym `total_cost`, potem nowy CDR z nowym `id` `[OCPI230 §10.1.1]`.
- Usuwanie EVSE: nie da się. Ustawiasz `status = REMOVED`. Location bez ważnego EVSE uznaje się za wygasłą
  `[OCPI230 §8.1]`.
- „Offline” w roamingu: status EVSE `UNKNOWN` to „No status information available (also used when offline)”, a nie awaria
  (`OUTOFORDER`) ani wyłączenie z użytku (`INOPERATIVE`) `[OCPI230 §8.4.26]`.
- Mapowania statusów OCPP → statusy EVSE OCPI **specyfikacja nie definiuje**. Dla OCPP 1.x z wieloma złączami na EVSE
  odsyła do noty aplikacyjnej OCA i opisuje obejście z „wirtualnym” EVSE na złącze `[OCPI230 §8.1.3]`.
- `step_size` zaokrągla zużycie w górę do wielokrotności kroku. EVRF zaleca `step_size = 1` przy przygotowaniu do 3.0,
  gdzie tego pola już nie ma `[OCPI230 §11.4.2]`.
- `UNLOCK_CONNECTOR` jest tylko dla operatora lub eMSP: „SHALL never be allowed to be sent directly by the EV-Driver”
  `[OCPI230 §13.4.3]`.
- Hub przekazując żądanie SHALL nadać nowy `X-Request-ID`, a `X-Correlation-ID` zostaje ten sam `[OCPI230 §4.2]`.

## Źródła
Dokumenty, adresy i sumy SHA-256: `sources/evrf-ocpi.yaml` (pobrane ze stron EVRF 2026-11-07).
- `OCPI230` — OCPI 2.3.0, document version 2.3.0, 2025-02-21;
- `OCPI221` — OCPI 2.2.1-d2 (wewnątrz: „2.2.1-d3-pre1, 2023-09-07”);
- `EVRF-DL` — strona „OCPI Downloads” (status wersji, 2026-11-07);
- `EVRF-V25` — „OCPI versions explained”, 19/08/2025.
