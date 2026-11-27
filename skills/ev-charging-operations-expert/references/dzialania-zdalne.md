# Zdalne działania — skutki dla trwających sesji

Znaczniki jak w `SKILL.md`. Przed każdym działaniem zmieniającym stan sprawdzasz trwające transakcje na stacji.

## Spis treści
1. Reset
2. ChangeAvailability
3. UnlockConnector
4. TriggerMessage i logi
5. Odpowiedzi poleceń — co znaczą
6. Pola poleceń serwisowych (logi, firmware)

## Reset
| Wersja | Wariant | Skutek | Źródło |
|---|---|---|---|
| 1.6 | każdy | przed resetem stacja SHALL wysłać `StopTransaction` dla każdej trwającej transakcji (brak resetu pojedynczego złącza) | `[16 §5.14]` |
| 1.6 | Soft | SHALL zakończyć transakcje łagodnie, potem restart oprogramowania | `[16 §5.14]` |
| 1.6 | Hard | restart całego sprzętu, bez obowiązku łagodnego zakończenia; „last resort”, informacje w kolejce mogą przepaść | `[16 §5.14]` |
| 2.0.1 | `OnIdle` + trwająca transakcja | odpowiedź `Scheduled`; reset po zakończeniu transakcji | `[201-P2 B12.FR.01]` |
| 2.0.1 | `Immediate` + trwająca transakcja | odpowiedź `Accepted`; stacja SHALL spróbować zakończyć transakcje (`Ended`, `triggerReason = ResetCommand`) | `[201-P2 B12.FR.02, B12.FR.04]` |
| 2.0.1 | z `evseId` | reset tylko wskazanego EVSE | `[201-P2 B11.FR.08]` |
Stan niedostępności ustawiony przez CSMS przetrwa restart: 2.0.1 `[201-P2 B11.FR.02]`; 1.6 „Persistent states” `[16 §5.14]`.
2.0.1, dalsze reguły: stacja, która w tej chwili nie może wykonać resetu → `Rejected` `[201-P2 B11.FR.06]`; reset
zaplanowany na później → `Scheduled` `[201-P2 B11.FR.07]`; reset jednego EVSE bez wsparcia stacji → `Rejected`
`[201-P2 B11.FR.09]` (wsparcie sygnalizuje `AllowReset` = true na EVSE `[201-P2 B11.FR.10]`). Rezerwacja wraca po
restarcie `[201-P2 B11.FR.05]`. `OnIdle` czeka także na inne zadania, np. aktualizację firmware lub wysyłanie logu
`[201-P2 B11]`. Po `Immediate` niedostarczone `TransactionEvent` stacja kolejkuje i wysyła po restarcie
`[201-P2 B12.FR.05]`. 1.6: jeśli `StopTransaction.conf` nie przyjdzie, stacja SHALL kolejkować `StopTransaction.req`
`[16E §3.36]`.

**Wniosek:**
- 2.0.1: najpierw reset jednego EVSE (`evseId`) albo `OnIdle`. `Immediate` stosujesz tylko przy zagrożeniu lub awarii
  całej stacji;
- 1.6: reset zawsze kończy wszystkie sesje stacji, więc przy innych aktywnych sesjach czekasz albo uzgadniasz to z klientami;
- hard reset stosujesz dopiero po soft.

## ChangeAvailability
- 1.6: przy trwającej transakcji odpowiedź `Scheduled`, zmiana po jej zakończeniu. `connectorId = 0` dotyczy stacji i
  wszystkich złączy. Po zmianie stacja SHALL wysłać `StatusNotification` `[16 §5.2]`.
- 2.0.1: odpowiedzi `Accepted` / `Rejected` / `Scheduled` `[201-P3]`. Status `Unavailable` może zmienić się od razu albo
  być zaplanowany, a po wejściu w życie SHALL przyjść `StatusNotification` `[201-P2 §3.23]`.
- 2.0.1, szczegóły `[201-P2 G03]` `[201-P2 G04]`:
  - prośba o stan, który już obowiązuje → `Accepted` `[201-P2 G03.FR.03]`;
  - brak pola `evse` → zmiana dotyczy całej stacji `[201-P2 G04.FR.01]`;
  - EVSE lub stacja `Inoperative` → wszystkie złącza poza `Faulted` przechodzą w `Unavailable`; `Operative` przywraca ich
    poprzedni status `[201-P2 G03.FR.06–07]` `[201-P2 G04.FR.07–08]`;
  - stany stacji, EVSE i złącza są osobne: złącze wyłączone osobno zostaje wyłączone po włączeniu EVSE (NOTE 1)
    `[201-P2 G03]`;
  - stan przetrwa restart i zanik zasilania `[201-P2 G03.FR.08]` `[201-P2 G04.FR.09]`.

**Wniosek:** wyłączenie EVSE do serwisu robisz przez `ChangeAvailability(Inoperative)`, a nie reset. Status trafia do
danych AFIR jako non-operational (`references/alarmy.md`). Po serwisie włączasz ten sam poziom (złącze, EVSE, stacja),
który wyłączałeś, bo włączenie wyższego poziomu nie włącza wyłączonego osobno złącza.

## UnlockConnector
- Cel: pomoc kierowcy, gdy nie może wyjąć kabla. Polecenie SHOULD NOT służyć do zdalnego zatrzymania transakcji `[16 §5.18]`.
- **Różnica wersji:**
  - 1.6: przy trwającej transakcji na złączu stacja SHALL ją najpierw zakończyć `[16 §5.18]`;
  - 2.0.1: przy autoryzowanej transakcji stacja SHALL NOT odblokowywać ani zatrzymywać, odpowiada
    `OngoingAuthorizedTransaction` `[201-P2 F05.FR.02]`.
- Roaming: `UNLOCK_CONNECTOR` tylko od operatora lub eMSP, nigdy bezpośrednio od kierowcy `[OCPI230 §13.4.3]`.
- Polecenie dotyczy tylko blokady wtyku na złączu, nie drzwiczek dostępowych `[16 §5.18]` `[201-P2 F05]`.
- 2.0.1: stacja SHALL próbować odblokować także bez wykrytego kabla i zwrócić wynik próby `[201-P2 F05.FR.06]`.
- Partner OCPI widzi możliwość zdalnego odblokowania w `capabilities` EVSE (`UNLOCK_CAPABLE`) `[OCPI230 §8.4.3]`.

## TriggerMessage i logi
- `TriggerMessage` pobiera bieżący stan: 1.6 `BootNotification`, `DiagnosticsStatusNotification`,
  `FirmwareStatusNotification`, `Heartbeat`, `MeterValues`, `StatusNotification`; 2.0.1 m.in. `StatusNotification`,
  `TransactionEvent`, `MeterValues`, `LogStatusNotification` `[S16]` `[201-P3]`.
- 1.6: po `BootNotification` `Accepted` CSMS SHALL NOT żądać nowego `BootNotification` przez `TriggerMessage`, dopóki
  stacja sama go nie wyśle `[16E §3.40]`. Stacja jest RECOMMENDED odrzucić taki `TriggerMessage` `[16E §3.35]`; w 2.0.1
  SHALL odpowiedzieć `Rejected` `[201-P2 F06.FR.17]`.
- Mechanizm nie służy do pobierania historii: wyzwolone komunikaty niosą tylko bieżące dane `[16 §5.17]`
  `[201-P2 F06.FR.09]`. 1.6: `StartTransaction` i `StopTransaction` są wyłączone z mechanizmu, bo opisują przejście,
  nie stan `[16 §5.17]`.
- **Różnica wersji przy `StatusNotification`:**
  - 1.6: brak `connectorId` = status stacji i każdego złącza; `connectorId` 0 = status stacji `[16 §5.17]`;
  - 2.0.1: CSMS SHALL podać `connectorId`, a bez niego stacja MAY odpowiedzieć `Rejected` `[201-P2 F06.FR.12–13]`.
- Komunikat oznaczony `Accepted`: 1.6 SHOULD go wysłać `[16 §5.17]`, 2.0.1 SHALL `[201-P2 F06.FR.10]`. Komunikat
  wysłany w międzyczasie z normalnej pracy MAY uchodzić za spełnienie żądania (obie wersje).
- `MeterValues`: najnowsze odczyty dla `MeterValuesSampledData` (1.6, SHALL wg erraty `[16E §3.46]`) albo
  `AlignedDataMeasurands` (2.0.1 `[201-P2 F06.FR.06]`). `TransactionEvent`: `triggerReason = Trigger`, co najmniej
  `chargingState` i odczyty `SampledDataTxUpdatedMeasurands` `[201-P2 F06.FR.07]`.
- Logi: 1.6 `GetDiagnostics` `[16 §5.9]`, dodatek bezpieczeństwa `GetLog` `[SWP4]`; 2.0.1 `GetLog` (`DiagnosticsLog`,
  `SecurityLog`) `[201-P2 N01]`.

## Odpowiedzi poleceń — co znaczą
| Polecenie | 1.6 | 2.0.1 |
|---|---|---|
| `Reset` | `Accepted`, `Rejected` `[16 §7.41]` | `Accepted`, `Rejected`, `Scheduled` `[201-P2 §3.75]` |
| `ChangeAvailability` | `Accepted`, `Rejected`, `Scheduled` (po zakończeniu transakcji) `[16 §7.3]` | to samo `[201-P2 §3.10]` |
| `UnlockConnector` | `Unlocked`, `UnlockFailed`, `NotSupported` (brak blokady albo nieznane złącze) `[16 §7.46]` `[16E §3.87]` | `Unlocked`, `UnlockFailed`, `OngoingAuthorizedTransaction`, `UnknownConnector`; brak blokady → CALLERROR `NotSupported` `[201-P2 §3.83]` `[201-P2 F05.FR.07]` |
| `TriggerMessage` | `Accepted`, `Rejected`, `NotImplemented` `[16 §7.44]` | to samo `[201-P2 §3.81]` `[201-P2 F06.FR.08]` |

`Accepted` przy `Reset` znaczy „Command will be executed” `[16 §7.41]`, a przy `TriggerMessage` „Requested message
will be sent” `[201-P2 §3.81]`. Wynik działania potwierdza dopiero następny komunikat stacji (Boot, status, żądany
komunikat).

**Wniosek:** w narzędziu NOC zapisujesz polecenie jako „wysłane → odpowiedź → potwierdzone”. `Scheduled` to stan
oczekujący, a nie błąd: zamykasz go dopiero po `StatusNotification` albo Boot.

## Pola poleceń serwisowych (logi, firmware)
| Polecenie | Pola | Źródło |
|---|---|---|
| 1.6 `GetDiagnostics` | `location` (katalog docelowy, wymagane), `retries`, `retryInterval` [s], `startTime`, `stopTime`; odpowiedź: `fileName` (brak = brak danych) | `[16 §6.25]` `[16 §6.26]` |
| 1.6 `UpdateFirmware` | `location` (URI pliku), `retrieveDate` (wymagane), `retries`, `retryInterval`; odpowiedź bez pól | `[16 §6.55]` `[16 §6.56]` |
| 2.0.1 `GetLog` | `logType` (`DiagnosticsLog` / `SecurityLog`), `requestId`, `retries` (0 = bez ponowień), `retryInterval`, `log.remoteLocation`, `log.oldestTimestamp`, `log.latestTimestamp` | `[201-P2 §1.24.1]` `[201-P2 §2.29]` |
| 2.0.1 `UpdateFirmware` | `requestId`, `retries`, `retryInterval`, `firmware.location`, `firmware.retrieveDateTime`, `installDateTime`, `signingCertificate`, `signature` | `[201-P2 §1.64.1]` `[201-P2 §2.24]` |

- Odpowiedź `GetLog`: `Accepted`, `Rejected`, `AcceptedCanceled` (anulowano trwające wysyłanie) `[201-P2 §3.49]`. Nowy
  `GetLog` w czasie wysyłania → stacja SHOULD anulować poprzedni `[201-P2 N01.FR.12]`.
- Odpowiedź `UpdateFirmware`: `Accepted`, `Rejected`, `AcceptedCanceled`, `InvalidCertificate`, `RevokedCertificate`
  `[201-P2 §3.86]`. CSMS SHALL dołączyć certyfikat podpisu firmware `[201-P2 L01.FR.11]`.
- `Accepted` nie oznacza sukcesu: stacja dopiero zaczyna wysyłać log albo aktualizować firmware `[201-P2 §3.49]`
  `[201-P2 §3.86]`. Postęp raportują `LogStatusNotification` / `FirmwareStatusNotification` z tym samym `requestId`
  `[201-P2 N01.FR.07]` `[201-P2 L01.FR.10]`.
- Firmware a sesje: gdy instalacja (albo aktywacja wymagająca restartu) w trakcie transakcji nie jest możliwa, stacja
  czeka na koniec transakcji, a nieużywane EVSE ustawia do instalacji na `Unavailable`, chyba że
  `AllowNewSessionsPendingFirmwareUpdate` = true `[201-P2 L01.FR.06–07]` `[201-P2 L01.FR.33]`. W 1.6 errata zaleca to samo `[16E §3.49]`.
- Hasło do serwera logów: przy basic auth CSMS jest RECOMMENDED wymagać innego hasła niż do połączenia OCPP, bo
  serwer logów może być systemem zewnętrznym `[201-P2 N01.FR.17]`.

**Wniosek:**
- `installDateTime` ustawiasz na okno małego ruchu: gdy nadejdzie czas instalacji, a trwają transakcje, wolne EVSE są
  niedostępne do ich zakończenia (i idą do danych AFIR jako non-operational);
- URL do logów i firmware ma osobne poświadczenia, nie hasło OCPP stacji.
