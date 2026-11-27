# Model statusów i dostępności — stacje własne i roamingowe

Znaczniki: `sources/*.yaml`. Fakty (definicje) są cytowane, a model docelowy jest **wnioskiem**.

## Spis treści
1. Definicje w źródłach
2. Co jest oficjalnie zmapowane, a co nie
3. Model docelowy — Wniosek
4. Jak stacja raportuje status (wejście modelu)
5. Publikacja: OCPI, AFIR, EIPA

## 1. Definicje w źródłach
| Źródło | Poziom | Wartości | Operative / Inoperative |
|---|---|---|---|
| OCPP 1.6 `ChargePointStatus` `[16 §7.7]` | złącze; `connectorId` 0 = kontroler stacji (tylko Available / Unavailable / Faulted) | `Available`, `Preparing`, `Charging`, `SuspendedEVSE`, `SuspendedEV`, `Finishing`, `Reserved`, `Unavailable`, `Faulted` (+ `errorCode`) | Inoperative: `Unavailable`, `Faulted`; pozostałe Operative |
| OCPP 2.0.1 `ConnectorStatusEnumType` `[201-P2 §3.23]` | złącze EVSE | `Available`, `Occupied`, `Reserved`, `Unavailable`, `Faulted` (+ `chargingState` w `TransactionEvent`) | Inoperative: `Unavailable`, `Faulted`; Operative: `Available`, `Reserved`, `Occupied` |
| OCPI 2.3.0 `Status` `[OCPI230 §8.4.26]` | EVSE | `AVAILABLE`, `BLOCKED`, `CHARGING`, `INOPERATIVE`, `OUTOFORDER`, `PLANNED`, `REMOVED`, `RESERVED`, `UNKNOWN` | — |
| AFIR dane dynamiczne `[AFIR art. 20 ust. 2 lit. f]` `[AFIR-655 Annex, tabela F]` | punkt ładowania | Operational status: operational / non-operational; Availability: in use / reserved / not in use | non-operational: „cannot be used due to a technical problem or maintenance works” |

Kluczowe opisy:
- OCPP `Unavailable`: wynik `ChangeAvailability` albo decyzji stacji. `Faulted`: zgłoszony błąd, brak możliwości dostarczenia
  energii `[201-P2 §3.23]` `[16 §7.7]`.
- OCPI `INOPERATIVE`: „not yet active, or temporarily not available for use, but not broken or defect”. `OUTOFORDER`:
  „some part/components may be broken/defect”. `UNKNOWN`: „No status information available (also used when offline)”
  `[OCPI230 §8.4.26]`.
- AFIR Operational: „it can be used in normal conditions during the opening time that is accessible to the public”.
  In use: „it is occupied”. Reserved: „it is booked by an end user” `[AFIR-655 Annex, tabela F]`.

## 2. Co jest oficjalnie zmapowane, a co nie
- **OCPI 2.3.0 → AFIR: zmapowane przez EVRF** `[OCPI-NAP §3.3.1.1]`:
  - Operational status: `INOPERATIVE`, `OUTOFORDER`, `PLANNED`, `REMOVED`, `UNKNOWN` → non-operational, reszta → operational;
  - Availability: `CHARGING`/`BLOCKED` → in use, `RESERVED` → reserved, `AVAILABLE` → not in use.
  EVRF zauważa, że w 2.3.0 jedno pole `status` niesie obie informacje, a OCPI 3.0 je rozdziela `[OCPI-NAP §4.3.1.1]`.
- **OCPP → OCPI: brak oficjalnego mapowania.** Specyfikacja OCPI podaje tylko obejście dla OCPP 1.x z wieloma złączami
  na EVSE (wirtualne EVSE na złącze) `[OCPI230 §8.1.3]`.
- **„Offline” nie jest statusem OCPP.** To stan wyznaczany przez CSMS z reguł łączności `[16 §4.6]` `[201-P2 G02]`
  `[201-P4 §5.3]`.

## 3. Model docelowy — Wniosek
Trzy niezależne wymiary na poziomie EVSE (jednostka „jeden pojazd naraz”, zgodnie z definicjami OCPP, OCPI i AFIR):

| Wymiar | Wartości | Źródło wartości dla stacji własnej | Dla stacji partnera (OCPI) |
|---|---|---|---|
| Łączność | online / offline / nieznana | CSMS: sesja WebSocket + reguła braku kontaktu | `UNKNOWN` → nieznana |
| Operacyjność | operative / inoperative (wyłączona) / faulted (awaria) / planned / removed | OCPP: `Unavailable` → inoperative, `Faulted` → faulted; planned/removed z cyklu życia zasobu | `INOPERATIVE`, `OUTOFORDER`, `PLANNED`, `REMOVED` |
| Zajętość | wolna / zarezerwowana / w użyciu / zablokowana | 1.6: `Available` / `Reserved` / stany sesji; 2.0.1: `Available` / `Reserved` / `Occupied` | `AVAILABLE`, `RESERVED`, `CHARGING`, `BLOCKED` |

Agregacja do OCPI (Wniosek, każda pozycja uzasadniona definicjami z sekcji 1):
1. offline albo nieznana → `UNKNOWN` (definicja OCPI obejmuje offline);
2. removed → `REMOVED`, planned → `PLANNED` (cykl życia; OCPI wymaga `REMOVED` zamiast kasowania `[OCPI230 §8.1]`);
3. faulted → `OUTOFORDER` (uszkodzenie) — inoperative → `INOPERATIVE` (niedostępne, „not broken”);
4. zarezerwowana → `RESERVED`; w użyciu → `CHARGING`; zablokowana fizycznie → `BLOCKED`; wolna → `AVAILABLE`.

Agregacja do AFIR: przez tabelę EVRF z sekcji 2 (z OCPI) albo bezpośrednio z wymiarów:
- non-operational = offline, nieznana, inoperative, faulted, planned, removed;
- availability z wymiaru zajętości.

Decyzje do podjęcia przez produkt (źródła ich nie rozstrzygają):
- czy 1.6 `Preparing` (np. pojazd zajmuje miejsce, brak transakcji `[16 §7.7]`) i `Finishing` publikować jako `CHARGING`
  czy `BLOCKED`;
- próg czasu, po którym brak kontaktu oznacza offline. Ograniczenie: dane dynamiczne AFIR SHALL być aktualizowane
  najpóźniej 1 minutę po zmianie `[AFIR-655 art. 2]`;
- agregacja wielu złączy jednego EVSE (1.6: status per złącze; OCPI: status per EVSE). Źródło przenosi to zadanie na
  CSMS, ale nie podaje reguły (sekcja 4).

## 4. Jak stacja raportuje status (wejście modelu)
**OCPP 1.6:**
- Przy zmianie stanu stacja SHALL wysłać `StatusNotification`, „taking into account some minimum status duration”
  `[16E §3.19]`. **Rozbieżność:** tekst 1.6 mówi „MAY send” `[16 §4.9]`. Rozstrzygnięcie: obowiązuje errata OCA (SHALL).
- `MinimumStatusDuration`: stacja MAY pominąć status trwający krócej. Minimum producenta działa niezależnie, wartość
  klucza dodaje się do niego, a 0 go nie wyłącza. Wysoka wartość opóźnia wszystkie `StatusNotification` `[16 §4.9]`.
- Błąd zgłoszony przy statusie innym niż `Faulted` to ostrzeżenie, bo ładowanie jest nadal możliwe.
  `EVCommunicationError` tylko przy `Preparing`, `SuspendedEV`, `SuspendedEVSE`, `Finishing`, jako ostrzeżenie `[16 §4.9]`.
- Po powrocie z offline stacja SHOULD wysłać bieżący status, jeśli się zmienił, i MAY zgłosić błąd z czasu offline.
  Historycznych zmian bez błędu SHOULD NOT wysyłać. Kolejność MUST odpowiadać kolejności zdarzeń `[16 §4.9]`.
- Po `BootNotification` `Accepted` stacja SHALL wysłać status `connectorId` 0 i wszystkich złączy `[16E §3.22]`.

**OCPP 2.0.1 i 2.1:**
- Zamiast `StatusNotification` stacja może wysłać `NotifyEvent` (`component` = `Connector`, `variable` =
  `AvailabilityState`, `trigger` = `Delta`) `[201-P2 G01]`. W 2.1 `NotifyEvent` jest metodą preferowaną, a
  `StatusNotification` jest „deprecated and will be removed in a future release” `[21-P2 G01]`.
- Stacja, EVSE i złącze mają osobne stany. Wyłączenie EVSE ustawia `Unavailable` na wszystkich złączach poza `Faulted`,
  a włączenie przywraca ich poprzedni status `[201-P2 G03.FR.06–07]`; to samo dla całej stacji `[201-P2 G04.FR.07–08]`.
  Złącze wyłączone osobno zostaje `Inoperative` po ponownym włączeniu EVSE (NOTE 1) `[201-P2 G03]`.
- Zmiana na stan, w którym obiekt już jest → `Accepted` `[201-P2 G03.FR.03]`. Trwająca transakcja → `Scheduled`
  `[201-P2 G03.FR.05]`. Stan ustawiony przez `ChangeAvailability` przetrwa restart i zanik zasilania
  `[201-P2 G03.FR.08]` (1.6: `[16 §4.9]`).
- `Reserved` i podłączenie pojazdu bez pasującego `IdToken`: status SHALL NOT się zmienić `[201-P2 G01.FR.09]`.
- Wiele złączy na EVSE: po wpięciu kabla stacja SHOULD NOT raportować pozostałych złączy, choć nie da się ich już użyć
  `[201-P2 G01.FR.08]`. CSMS „has to take care of the status of the other connectors when presenting availability
  information to another system or user” `[201-P2 G01]`.

**`Unavailable` nie zawsze pochodzi od CSMS:**
- stacja MAY używać go wewnętrznie, np. przy aktualizacji firmware albo przed `Accepted` `[16 §4.9]` `[201-P2 G01]`;
- gdy firmware nie da się instalować w trakcie transakcji, stacja SHALL ustawić nieużywane EVSE na `Unavailable` do
  końca instalacji, chyba że `AllowNewSessionsPendingFirmwareUpdate` = true `[201-P2 L01.FR.07]`. W 1.6 to zalecenie
  erraty `[16E §3.49]`.

**Łączność:**
- CSMS SHALL zakładać dostępność stacji po każdej odebranej wiadomości `[201-P2 G02.FR.04]`; w 1.6 SHOULD `[16 §4.6]`;
- przy braku Heartbeatu CSMS „concludes that the Charging Station is Offline” (failure postcondition) `[201-P2 G02]`;
- interwał Heartbeatu stacja bierze z `BootNotificationResponse` `[201-P2 G02.FR.01]`. Progu czasu offline żadne
  źródło nie podaje.

**Wniosek:**
- każde zdarzenie statusu zapisujesz z czasem stacji, czasem odbioru i flagą „po powrocie z offline”. Brak zmian z czasu
  offline nie dowodzi, że ich nie było (1.6: historii SHOULD NOT wysyłać);
- krótkie stany przejściowe mogą nie dotrzeć wcale (`MinimumStatusDuration`), więc ciąg statusów nie jest pełnym zapisem
  sesji. Granice sesji bierzesz z komunikatów transakcyjnych;
- `Unavailable` zapisujesz z przyczyną (polecenie operatora, firmware, decyzja stacji). Sam status jej nie niesie;
- EVSE jest „w użyciu”, gdy którekolwiek jego złącze jest zajęte, bo stacja nie raportuje pozostałych złączy;
- dla 2.0.1 i 2.1 parser przyjmuje `NotifyEvent(AvailabilityState)` i `StatusNotification` jako to samo zdarzenie.

## 5. Publikacja: OCPI, AFIR, EIPA
- OCPI `status_schedule` (planowane okresy statusu) jest „purely informational”. Przy faktycznej zmianie CPO musi
  wysłać aktualizację pola `status` `[OCPI230 §8.4.27]`. Usunięcie EVSE: `REMOVED` i PUT/PATCH, bez kasowania
  `[OCPI230 §8.1]`.
- AFIR: status operacyjny i dostępność są na poziomie punktu ładowania, cena ad hoc na poziomie stacji. Dostępność to
  możliwość użycia „at present time and, when technically possible, at a specific future time”
  `[AFIR-655 Annex, tabela F]`. Punkt ładowania ładuje jeden pojazd naraz, choć może mieć kilka złączy
  `[AFIR art. 2 pkt 48]`.
- Polska (EIPA): rejestr zawiera informacje o dostępności punktów ładowania `[PL-EMOB art. 42 ust. 3]`. Operator
  przekazuje ją usługą sieciową „natychmiast po zmianie stanu dostępności tego punktu, w czasie wynikającym ze sposobu
  działania usługi sieciowej”, a ceny w ciągu godziny od zmiany `[PL-EMOB art. 42 ust. 6]`. Wartości statusu określa
  specyfikacja usługi publikowana w BIP UDT `[PL-EMOB art. 42 ust. 9]`. Tu jej nie opracowano.

**Wniosek:** jeden wyliczony stan EVSE zasila trzy kanały (OCPI, API do NAP, EIPA). Każdy kanał mapujesz osobno, bo
słowniki i terminy są różne (1 minuta w AFIR, „natychmiast” w EIPA).
