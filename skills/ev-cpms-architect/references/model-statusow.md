# Model statusów i dostępności — stacje własne i roamingowe

Znaczniki: `sources/*.yaml`. Fakty (definicje) są cytowane, a model docelowy jest **wnioskiem**.

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
- agregacja wielu złączy jednego EVSE (1.6: status per złącze; OCPI: status per EVSE).
