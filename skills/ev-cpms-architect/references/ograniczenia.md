# Ograniczenia dla modułów CPMS (z cytatami)

Znaczniki: `sources/oca-ocpp.yaml`, `sources/evrf-ocpi.yaml`, `sources/eu-afir.yaml`. Każdy punkt to wymóg albo zalecenie
źródła (MUST/SHALL/SHOULD/MAY jak w oryginale). Decyzje projektowe → **Wniosek**.

## Spis treści
1. Warstwa połączeń OCPP-J
2. Onboarding i provisioning
3. Topologie
4. Sesje i transakcje
5. Stacje zewnętrzne (OCPI)
6. Wymagania AFIR dla stacji publicznych
7. Bezpieczeństwo i separacja

## 1. Warstwa połączeń OCPP-J
- CSMS jest serwerem WebSocket, stacja klientem. Stacja SHALL utrzymywać połączenie otwarte cały czas `[201-P4 §3.1]`.
- URL połączenia = endpoint OCPP-J + `/` + identyfikator stacji (percent-encoding). Identyfikator: `identifierString`,
  bez znaku `:`, maks. 48 znaków. Zalecane jest, by CSMS nie polegał tylko na URL, lecz sprawdzał tożsamość względem danych
  uwierzytelniających `[201-P4 §3.1.1]`.
- Podprotokół wybiera serwer spośród zaproponowanych. W 1.6 przy braku zgody serwer MUST zakończyć handshake bez nagłówka
  i zamknąć połączenie. Nieznany identyfikator → SHOULD HTTP 404 `[J16 §3.2]`.
- Jedno niezakończone CALL naraz na połączenie OCPP-J; CSMS może równolegle pisać do innych stacji `[201-P4 §4.1.1]`.
- Ponowne łączenie: stacja SHALL stosować rosnące opóźnienie z losowym rozrzutem (`RetryBackOffWaitMinimum`,
  `RetryBackOffRandomRange`, `RetryBackOffRepeatTimes`), „to prevent an overload of the CSMS when all Charging Stations
  reconnect after a restart of the CSMS” `[201-P4 §5.4]`.
- Po ponownym połączeniu stacja SHOULD NOT wysyłać `BootNotification`, chyba że zmieniły się jego dane `[201-P4 §5.4]`.
- Ping WebSocket może zastąpić większość Heartbeatów, ale sprawdza łączność tylko na odcinku (point-to-point), a Heartbeat
  od końca do końca. Co najmniej jeden Heartbeat dziennie zaleca się dla synchronizacji zegara `[201-P4 §5.3]`.
- Mały bufor TLS: stacja z ograniczonymi zasobami SHOULD negocjować mniejszy fragment TLS. Rozszerzenie bywa
  nieobsługiwane przez zarządzane terminatory TLS w chmurze `[201-P4 §5.2]`.

**Wniosek:**
- stan „połączona / rozłączona” jest atrybutem sesji WebSocket po uwierzytelnieniu, a nie wynikiem Boot;
- kolejka poleceń jest per stacja (z uwagi na jedno CALL naraz);
- odtwarzanie stanu po ponownym połączeniu robisz przez `TriggerMessage` z limitem równoległości.

## 2. Onboarding i provisioning (2.0.1, blok B)
- Stacja SHALL wysłać `BootNotification` po każdym (re)starcie `[201-P2 B01.FR.03]`. Po `Accepted` SHALL wysłać
  `StatusNotification` dla każdego złącza `[201-P2 B01.FR.05]`. Dla 1.6 to samo wprowadza errata `[16E §3.22]`.
- `Pending`:
  - CSMS MAY pobierać dane (B06–B08) i zmieniać konfigurację (`SetVariables`) `[201-P2 B02.FR.01]`;
  - stacja SHALL NOT wysyłać CALL poza `BootNotification`, chyba że poleci jej to CSMS `[201-P2 B02.FR.02]`;
  - kanał SHALL NOT zostać zamknięty `[201-P2 B02.FR.06]`;
  - `RequestStart/StopTransaction` → stacja SHALL odpowiedzieć `Rejected` `[201-P2 B02.FR.05]`;
  - operator MAY skonfigurować stację, by przyjmowała transakcje i kolejkowała `TransactionEvent` `[201-P2 B02.FR.03]`.
- `Rejected`:
  - stacja SHALL NOT wysyłać komunikatów do końca interwału `[201-P2 B03.FR.02]`;
  - CSMS SHALL NOT inicjować komunikatów `[201-P2 B03.FR.03]`;
  - inne komunikaty niż Boot dostają `CALLERROR: SecurityError` `[201-P2 B03.FR.07–08]`.
- `interval = 0` przy statusie innym niż `Accepted` → stacja sama wybiera odstęp, unikając zalewania CSMS
  `[201-P2 B02.FR.07]` `[201-P2 B03.FR.05]`.

**Wniosek:** `Pending` jest naturalnym stanem procesu onboardingu: `GetBaseReport`, konfiguracja, weryfikacja, a dopiero
potem `Accepted`. Stacja nieznana albo zablokowana dostaje `Rejected`.

## 3. Topologie `[201-P1 rozdz. 8]` `[201-P4 rozdz. 6]`
- „OCPP has no knowledge of the topology of the Charging Station network” `[201-P1 rozdz. 8]`.
- Local Proxy tylko routuje. Dla stacji „jest” CSMS, a dla CSMS „jest” stacją `[201-P1 §8.2]`.
- Local Controller może sam wysyłać polecenia (np. lokalny smart charging). Ma własną tożsamość stacji (bez EVSE),
  a CSMS „will possess the logic to deal with the Local Controller”. Topologię grupy konfiguruje się ręcznie albo wywodzi
  z adresów IP i `BootNotification`, zależnie od implementacji CSMS `[201-P1 §8.3]`.
- Kontroler otwiera do CSMS osobny WebSocket per stacja, z tym samym identyfikatorem `[201-P4 §6.2]`. Utrata połączenia
  LC–CSMS → LC SHALL zamknąć połączenia stacji (chyba że sam obsługuje żądania i przekazuje transakcyjne później).
  Utrata stacja–LC → LC SHALL zamknąć jej połączenie do CSMS `[201-P4 §6.3]`. Identyfikatory komunikatów LC SHALL NOT
  kolidować z identyfikatorami CSMS `[201-P4 §6.4]`.
- Stacje bez OCPP za kontrolerem: LC jako jedna stacja z wieloma EVSE albo jako wiele stacji `[201-P1 §8.4]`.
- DSO: sygnały spoza OCPP (np. OpenADR, OSCP) do CSMS, który ogranicza ładowanie profilami `[201-P1 §8.5]`.
- EMS równolegle z CSMS: EMS narzuca limit zewnętrzny, który stacja raportuje przez OCPP `[201-P1 §8.6]`.

## 4. Sesje i transakcje
- 2.0.1: `transactionId` generuje stacja i MUST być unikalny na tej stacji; format zależy od implementacji (np. licznik,
  UUID). W 1.x identyfikator nadawał CSMS `[201-P1 §7.3]`.
- Numeracja: EVSE od 1 bez luk, złącza od 1 na każdym EVSE. `evseId` 0 to cała stacja (polecenia CSMS) albo jej główny
  kontroler (raporty stacji) `[201-P1 §7.1–7.2]`. W 1.6 analogicznie `connectorId` `[16 §3.8]`.
- Komunikaty transakcyjne offline są kolejkowane i dostarczane chronologicznie. Odrzucane przez CSMS są ponawiane
  ograniczoną liczbę razy, a potem porzucane `[16 §3.7–3.7.1]` `[201-P2 E13]`. W 1.6 przy braku `transactionId` stacja
  wysyła `-1`, a CSMS SHALL przyjąć `[16E §3.18]`. W 2.0.1 kompletność transakcji sprawdza się po `seqNo` per EVSE
  `[201-P2 E §1.3.2]`.
Szczegóły: skill `ev-ocpp-expert` (wzorce komunikatów transakcyjnych).

**Wniosek:** klucz transakcji w CSMS to (stacja, `transactionId`) dla 2.0.1 i (stacja, `transactionId` nadany przez CSMS)
dla 1.6, z osobną ścieżką dla `-1`. Rozliczenie dopiero po kompletnym ciągu zdarzeń albo z flagą „dane niepełne”.

## 5. Stacje zewnętrzne (OCPI)
- Partner widzi Location/EVSE/Connector, statusy i taryfy. Steruje tylko pięcioma komendami (asynchronicznie, z
  `timeout`) `[OCPI230 §13]`.
- Brak informacji o statusie, także offline, to `UNKNOWN` `[OCPI230 §8.4.26]`.
- Synchronizacja po przerwie: pull, bez kolejkowania `[OCPI230 §4.4]`. Sesje: PUT, potem PATCH, stan końcowy `COMPLETED`
  `[OCPI230 §9.1.1]`. CDR niezmienny, korekta przez credit CDR `[OCPI230 §10.1.1]`.
- Obiekty partnera rozróżnia się po `country_code` + `party_id` z CredentialsRoles `[OCPI230 §4.1.5]`.

**Wniosek:** stacje zewnętrzne trzymasz w tym samym modelu Location/EVSE/Connector z atrybutem źródła (własna / partner
`country_code`+`party_id`) i ograniczonym zestawem dozwolonych operacji. UI i API nie oferują dla nich operacji OCPP.

## 6. Wymagania AFIR dla stacji publicznych
- Ad hoc: możliwość ładowania ad hoc na publicznych punktach. Od 13.04.2024 płatność powszechnie używanym instrumentem
  (czytnik kart, urządzenie zbliżeniowe; dla < 50 kW także np. kod QR). Od 01.01.2027 punkty ≥ 50 kW na TEN-T i w
  bezpiecznych parkingach, także starsze, muszą mieć (a) czytnik kart albo (b) urządzenie zbliżeniowe `[AFIR art. 5 ust. 1]`.
- Ceny ≥ 50 kW: cena ad hoc oparta na kWh, opcjonalnie opłata za zajętość za minutę; pokazane przed rozpoczęciem sesji.
  < 50 kW: składniki w kolejności kWh, minuta, sesja, inne `[AFIR art. 5 ust. 4]`. MSP pokazuje przed sesją wszystkie
  składniki ceny, w tym koszty e-roamingu `[AFIR art. 5 ust. 5]`.
- Do 14.10.2024 wszystkie publiczne punkty „digitally-connected”, czyli monitorowane i sterowane zdalnie, m.in. start/stop
  i pomiar `[AFIR art. 5 ust. 7]` `[AFIR art. 2]`. Zbudowane po 13.04.2024 lub odnowione po 14.10.2024 zdolne do smart
  recharging `[AFIR art. 5 ust. 8]`.
- Dane statyczne i dynamiczne bezpłatnie przez API zgłoszone do NAP `[AFIR art. 20 ust. 2–3]`. Lista danych po zmianie
  aktem M2 (2025/671). Dynamiczne to: status operacyjny, dostępność, cena ad hoc `[AFIR art. 20 ust. 2 lit. f]`.
- Częstotliwość: statyczne przy zmianie, najpóźniej 24 h po niej; **dynamiczne najpóźniej 1 minutę po zmianie**
  `[AFIR-655 art. 2]`. Jakość: kompletność, poprawność, spójność, terminowość, niezawodność, mechanizmy kontroli jakości
  „at source” `[AFIR-655 art. 3]`. Format zgodny z załącznikiem, a od 14.04.2026 także model DATEX II, co najmniej
  CEN/TS 16157-10:2022 `[AFIR-655 art. 1]`.
- API może prowadzić podmiot zewnętrzny w imieniu operatora; nie zdejmuje to z operatora obowiązku jakości
  `[AFIR-655 art. 3 ust. 3]`.

**Wniosek:**
- status EVSE w CPMS musi być wyliczany na bieżąco (zdarzeniowo), żeby publikacja do NAP mieściła się w 1 minucie;
- detekcja offline i jej próg wpływają bezpośrednio na zgodność z AFIR;
- mapowanie na dane AFIR: `references/model-statusow.md`.

## 7. Bezpieczeństwo i separacja
- OCPP nie przewiduje ról ani kontroli dostępu na stacji; zalecana jest kontrola dostępu w CSMS `[201-P2 A §1.2]`.
- 2.0.1 bez zabezpieczeń „NOT considered a valid OCPP 2.0.1 implementation” `[201-P2 A §1.3]`.
- OCPI: token credentials identyfikuje stronę. Dostęp do obiektów spoza CredentialsRoles → dozwolone HTTP 404
  `[OCPI230 §4.1.2]` `[OCPI230 §4.1.5.1]`.

**Wniosek:** każdy obiekt (stacja, Location, sesja, CDR, token) ma właściciela-tenanta. Uprawnienia operatorów egzekwuje
CSMS, zwłaszcza dla poleceń masowych.
