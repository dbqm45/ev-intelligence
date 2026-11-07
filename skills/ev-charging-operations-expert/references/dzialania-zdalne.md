# Zdalne działania — skutki dla trwających sesji

Znaczniki jak w `SKILL.md`. Przed każdym działaniem zmieniającym stan sprawdzasz trwające transakcje na stacji.

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
**Wniosek:** wyłączenie EVSE do serwisu robisz przez `ChangeAvailability(Inoperative)`, a nie reset. Status trafia do
danych AFIR jako non-operational (`references/alarmy.md`).

## UnlockConnector
- Cel: pomoc kierowcy, gdy nie może wyjąć kabla. Polecenie SHOULD NOT służyć do zdalnego zatrzymania transakcji `[16 §5.18]`.
- **Różnica wersji:**
  - 1.6: przy trwającej transakcji na złączu stacja SHALL ją najpierw zakończyć `[16 §5.18]`;
  - 2.0.1: przy autoryzowanej transakcji stacja SHALL NOT odblokowywać ani zatrzymywać, odpowiada
    `OngoingAuthorizedTransaction` `[201-P2 F05.FR.02]`.
- Roaming: `UNLOCK_CONNECTOR` tylko od operatora lub eMSP, nigdy bezpośrednio od kierowcy `[OCPI230 §13.4.3]`.

## TriggerMessage i logi
- `TriggerMessage` pobiera bieżący stan: 1.6 `BootNotification`, `DiagnosticsStatusNotification`,
  `FirmwareStatusNotification`, `Heartbeat`, `MeterValues`, `StatusNotification`; 2.0.1 m.in. `StatusNotification`,
  `TransactionEvent`, `MeterValues`, `LogStatusNotification` `[S16]` `[201-P3]`.
- 1.6: po `BootNotification` `Accepted` CSMS SHALL NOT żądać nowego `BootNotification` przez `TriggerMessage`, dopóki
  stacja sama go nie wyśle `[16E §3.40]`.
- Logi: 1.6 `GetDiagnostics` `[16 §5.9]`, dodatek bezpieczeństwa `GetLog` `[SWP4]`; 2.0.1 `GetLog` (`DiagnosticsLog`,
  `SecurityLog`) `[201-P2 N01]`.
