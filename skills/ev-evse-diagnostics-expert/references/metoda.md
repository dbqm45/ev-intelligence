# Metoda: czy stacja odbiega od OCPP

Znaczniki jak w `SKILL.md`. Metoda jest **wnioskiem**: kolejność i kryteria wynikają z tego, co oferują dokumenty OCA.

## Spis treści
1. Dowody
2. Walidacja ramek
3. Certyfikat i PICS
4. Rozstrzyganie niespójności dokumentów
5. Odtworzenie przypadkiem testowym
6. Werdykt i poziom pewności

## 1. Dowody (minimum)
- Surowe ramki z obu kierunków, ze znacznikiem czasu i identyfikatorem stacji. Bez przeformatowania: walidujemy dokładnie
  to, co przyszło.
- Identyfikacja z `BootNotification`: 1.6 `chargePointVendor`, `chargePointModel`, `chargePointSerialNumber`,
  `firmwareVersion` `[S16]`; 2.0.1 `chargingStation.vendorName`, `model`, `serialNumber`, `firmwareVersion` `[201-P3]`.
- Wersja protokołu: wynegocjowany podprotokół (`ocpp1.6`, `ocpp2.0.1`, `ocpp2.1`) `[J16 §3.1.2]` `[201-P4 §3.1.2]`.
- Konfiguracja w chwili zdarzenia: `GetConfiguration` (1.6) albo `GetBaseReport` / `GetVariables` (2.0.1).
- Logi stacji: `GetDiagnostics` / `GetLog` (`DiagnosticsLog`, `SecurityLog`) `[16 §5.9]` `[201-P2 N01]`.

## 2. Walidacja ramek (`scripts/ocpp_frame_check.py`)
- Sprawdza:
  - strukturę ramki i dozwolony typ (2/3/4; w 2.1 także 5 i 6) `[J16 §4.1.3]` `[21-P4 §4.1.3]`;
  - payload CALL wobec schematu akcji i payload CALLRESULT wobec schematu odpowiedzi (para po `messageId`);
  - kod CALLERROR wobec listy wersji `[J16 §4.2.3]` `[201-P4 §4.3]`.
- Nazwy plików schematów: 1.6 `<Akcja>.json` / `<Akcja>Response.json`; 2.0.1 i 2.1 `<Akcja>Request.json` /
  `<Akcja>Response.json` (pakiety OCA).
- Ograniczenia: skrypt nie sprawdza sekwencji (np. czy `StatusNotification` przyszedł po Boot), czasów ani reguł z
  tekstu wymagań. To robisz ręcznie (sekcja 4) albo przypadkiem testowym (sekcja 5).
- Sprawdzenie na danych OCA (2026-11-07): przykładowe ramki z OCPP-J 2.0.1 przechodzą. Przykład `BootNotification.conf`
  z OCPP-J 1.6 §4.2.2 nie przechodzi (`heartbeatInterval` zamiast `interval`), zgodnie z erratą 1.6 §4.6.

## 3. Certyfikat i PICS
- Certyfikacja 2.0.1 `[OCA-CERT]` `[201-P5 §2]`:
  - **Core** obowiązkowy: boot, autoryzacja, konfiguracja, transakcje, zdalne sterowanie, podstawowe bezpieczeństwo;
  - opcjonalne: **Advanced Security** (TLS z uwierzytelnieniem klienta), **Smart Charging** (wszystkie typy profili, ze
    stosem), **ISO 15118 Support** (smart charging i Plug & Charge).
- Lista certyfikowanych produktów `[OCA-LIST]`:
  - wersja OCPP, typ produktu (m.in. Charging Station, CSMS, Charging Station Software Stack);
  - typ certyfikatu (Full, Subset, Core, Security, Family);
  - profile S (Advanced Security), L (Local Authorization List Management), C (Smart Charging), D (Advanced Device
    Management), R (Reservation), U (Advanced User Interface), I (ISO 15118 Support);
  - wersja oprogramowania i data rejestracji.
  Osobno: „Withdrawn certificates” i strona weryfikacji certyfikatu.
- PICS (Protocol Implementation Conformance Statement) dla stacji, wersja 3.0.5 `[PICS-CS]`. Producent opisuje w nim
  cechy sprzętu, wybrane profile, zaimplementowane funkcje opcjonalne i ustawienia własne. Z tego wynika lista
  przypadków testowych do zaliczenia. Część 5 zawiera listy funkcji opcjonalnych i testów per profil `[201-P5 §3–4]`.
- **Wniosek:** porównujesz trzy rzeczy: certyfikat (co zbadało laboratorium, dla której wersji oprogramowania), PICS
  (co producent deklaruje) i obserwację u siebie (wersja firmware w `BootNotification`). Różna wersja firmware niż
  certyfikowana oznacza, że certyfikat nie rozstrzyga sprawy.

## 4. Rozstrzyganie niespójności dokumentów
Kolejność (Wniosek, wyprowadzony z charakteru dokumentów):
1. errata do danej wersji (najnowsza);
2. schemat JSON (wiąże format ramek);
3. tekst wymagań (SHALL/SHOULD/MAY);
4. przykłady i diagramy (ilustracyjne).
Przykłady niespójności znalezione przy budowie bazy:
- przykład OCPP-J 1.6 §4.2.2 (`heartbeatInterval`) wobec schematu 1.6 i erraty 1.6 §4.6 (`interval`);
- 2.0.1: tekst wymagania F02.FR.07 pisze `EVConnectionTimeout`, a enum `TriggerReasonEnumType` ma `EVConnectTimeout`
  `[201-P2 F02.FR.07, §3.82]`;
- 1.6 §3.3: kolumny tabeli profili pomieszane w edycji 2, korekta w erracie §3.2 `[16E §3.2]`;
- 2.0.1 §3.22: `sType3` opisany jako „Type 2 socket a.k.a. Scame” `[201-P2 §3.22]`.

## 5. Odtworzenie przypadkiem testowym
- Część 6 OCPP 2.0.1 zawiera przypadki `TC_<blok>_<nr>_CS` i `TC_<blok>_<nr>_CSMS` (675 identyfikatorów w Ed4),
  np. `TC_F_02_CS` (tytuł w dokumencie: `Remote start transaction - Remote start first - AuthorizeRemoteStart`)
  `[201-P6]`.
- **Wniosek:** wybierasz przypadek najbliższy objawowi, odtwarzasz go na stacji (z symulatorem CSMS albo własnym CSMS) i
  porównujesz kroki z ramkami z logu. Zgodność kroków przy innym wyniku wskazuje na konfigurację, niezgodność na
  implementację.

## 6. Werdykt i poziom pewności
| Werdykt | Kiedy |
|---|---|
| zgodne | ramki i sekwencja zgodne z wymaganiem i schematem |
| niezgodne | wskazane wymaganie (dokument §) lub błąd schematu, dowód w logu |
| nierozstrzygnięte | brak dowodów, wymaganie niejednoznaczne albo niespójne dokumenty |
Poziom pewności wpisu w rejestrze: `observed` (dowód + odtworzenie albo wielokrotne wystąpienie), `hypothesis`
(pojedyncze zgłoszenie bez dowodu), `confirmed-by-vendor` (potwierdzenie pisemne producenta, z odnośnikiem).
