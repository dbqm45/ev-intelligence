# OCPP 1.6J — komunikaty, statusy, konfiguracja

Źródła: `[16]`, `[16E]`, `[S16]`, `[SWP4]` (znaczniki jak w `SKILL.md`). CP = stacja (Charge Point),
CS = Central System.

## Spis treści
1. Komunikaty wg profili i kierunku
2. Statusy i kody błędów złącza (z tabelą przejść)
3. Odpowiedzi poleceń, `BootNotification` `Pending`/`Rejected`, `StopTransaction`
4. Pomiary (MeterValues)
5. Klucze konfiguracji

## 1. Komunikaty wg profili i kierunku
Kierunek: rozdział 4 „Operations Initiated by Charge Point” i rozdział 5 „Operations Initiated by Central System” `[16]`.
Profil: tabela w §3.3 `[16]` **po korekcie errata**. W edycji 2 kolumny tabeli są pomieszane („the columns have
been mixed in edition 2”): nagłówki REMOTE TRIGGER / RESERVATION / SMART CHARGING należy czytać jako RESERVATION /
SMART CHARGING / REMOTE TRIGGER `[16E §3.2]`. Errata zmienia też status §3.3 z „informative” na „normative” `[16E §3.3]`.

| Profil | CP → CS | CS → CP |
|---|---|---|
| Core (wymagany) | `Authorize`, `BootNotification`, `DataTransfer`, `Heartbeat`, `MeterValues`, `StartTransaction`, `StatusNotification`, `StopTransaction` | `ChangeAvailability`, `ChangeConfiguration`, `ClearCache`, `DataTransfer`, `GetConfiguration`, `RemoteStartTransaction`, `RemoteStopTransaction`, `Reset`, `UnlockConnector` |
| Firmware Management | `DiagnosticsStatusNotification`, `FirmwareStatusNotification` | `GetDiagnostics`, `UpdateFirmware` |
| Local Auth List Management | — | `GetLocalListVersion`, `SendLocalList` |
| Reservation | — | `CancelReservation`, `ReserveNow` |
| Smart Charging | — | `ClearChargingProfile`, `GetCompositeSchedule`, `SetChargingProfile` |
| Remote Trigger | — | `TriggerMessage` |
| Dodatek bezpieczeństwa `[SWP4]` | `LogStatusNotification`, `SecurityEventNotification`, `SignCertificate`, `SignedFirmwareStatusNotification` | `CertificateSigned`, `DeleteCertificate`, `ExtendedTriggerMessage`, `GetInstalledCertificateIds`, `GetLog`, `InstallCertificate`, `SignedUpdateFirmware` |

„Implementation of the Core profile is required. Other profiles are optional.” `[16 §3.3]`. Obsługiwane profile stacja
zgłasza kluczem `SupportedFeatureProfiles` `[16 §3.3]`. Kierunki komunikatów dodatku: opisy PDU i przypadków użycia `[SWP4]`.

## 2. Statusy i kody błędów złącza (`StatusNotification`)
- Pola wymagane: `connectorId`, `errorCode`, `status`. Opcjonalne: `info`, `timestamp`, `vendorId`, `vendorErrorCode` `[S16]`.
- `status`: `Available`, `Preparing`, `Charging`, `SuspendedEVSE`, `SuspendedEV`, `Finishing`, `Reserved`,
  `Unavailable`, `Faulted` `[S16]`.
- `errorCode`: `ConnectorLockFailure`, `EVCommunicationError`, `GroundFailure`, `HighTemperature`, `InternalError`,
  `LocalListConflict`, `NoError`, `OtherError`, `OverCurrentFailure`, `PowerMeterFailure`, `PowerSwitchFailure`,
  `ReaderFailure`, `ResetFailure`, `UnderVoltage`, `OverVoltage`, `WeakSignal` `[S16]`.
- `connectorId = 0`: w poleceniach CS cała stacja, w raportach CP główny kontroler stacji. Złącza numeruje się od 1
  bez przerw `[16 §3.8]`.
- Po zmianie stanu CP SHALL wysłać `StatusNotification`, „taking into account some minimum status duration” `[16E §3.19]`.
- Po `BootNotification` z `Accepted` CP SHALL wysłać `StatusNotification` dla `connectorId 0` i wszystkich złączy `[16E §3.22]`.
- Dozwolone jest przejście `Preparing` → `Finishing` (B6) po upływie czasu bez okazania `idTag` przy wpiętym kablu `[16E §3.20]`.

### Przejścia statusów (tabela `[16 §4.9]`, tylko `connectorId > 0`)
Kod przejścia = litera stanu wyjściowego + numer stanu docelowego (1 `Available`, 2 `Preparing`, 3 `Charging`,
4 `SuspendedEV`, 5 `SuspendedEVSE`, 6 `Finishing`, 7 `Reserved`, 8 `Unavailable`, 9 `Faulted`) `[16 §4.9]`.

| Z \ do | Dozwolone przejścia |
|---|---|
| A `Available` | A2, A3, A4, A5, A7, A8, A9 |
| B `Preparing` | B1, B3, B4, B5, B6, B9 |
| C `Charging` | C1, C4, C5, C6, C8, C9 |
| D `SuspendedEV` | D1, D3, D5, D6, D8, D9 |
| E `SuspendedEVSE` | E1, E3, E4, E6, E8, E9 |
| F `Finishing` | F1, F2, F8, F9 |
| G `Reserved` | G1, G2, G8, G9 |
| H `Unavailable` | H1, H2, H3, H4, H5, H9 |
| I `Faulted` | I1–I8 („Fault is resolved and status returns to the pre-fault state”) |

Wybrane zdarzenia z tabeli opisów `[16 §4.9]`:
- A2: rozpoczęcie użycia, np. wpięcie wtyku, okazanie `idTag`, przycisk start, odbiór `RemoteStartTransaction.req`;
  A3–A5: stacja bez środka autoryzacji (od razu ładowanie, EV nie ładuje, EVSE nie pozwala);
- B1: koniec zamierzonego użycia, m.in. upływ `ConnectionTimeOut` `[16E §3.21]`; B6: `idTag` nie okazany w czasie;
- C4 / D3: ładowanie zatrzymane / wznowione na żądanie EV (np. otwarcie / zamknięcie S2); C5 / D5: wstrzymanie przez
  EVSE (np. ograniczenie smart charging albo transakcja unieważniona przez `AuthorizationStatus` w
  `StartTransaction.conf`);
- C6: transakcja zatrzymana przez użytkownika albo `RemoteStopTransaction`, potrzebna dalsza akcja (odpięcie kabla);
- C8 / D8 / E8 / F8 / G8: koniec przy zaplanowanej zmianie na `Unavailable`;
- F2: ponowne użycie (wpięcie, ponowne `idTag`) tworzy **nową** transakcję; G1: rezerwacja wygasła albo
  `CancelReservation`; G2: okazano identyfikator rezerwacji.

Reguły obok tabeli:
- Oficjalna tabela pisze stan `Preparing` z literówką „Prepairing” `[16 §4.9]`; w schemacie wartość to `Preparing` `[S16]`.
- Wstrzymanie jednocześnie przez EV i EVSE → `SuspendedEVSE` SHALL mieć pierwszeństwo przed `SuspendedEV` `[16 §4.9]`.
- `Unavailable` ustawiony przez `ChangeAvailability` MUST przetrwać restart; stacja MAY używać `Unavailable` także
  wewnętrznie (np. aktualizacja firmware, oczekiwanie na pierwsze `Accepted`) `[16 §4.9]`.
- Przy starcie transakcji status zwykle przechodzi `Preparing` → `Charging`, możliwe z krótkim `SuspendedEV` lub
  `SuspendedEVSE` po drodze, „possibly within a couple of seconds” `[16 §4.9]`.
- Stacja MAY nie wysłać `StatusNotification` dla stanu krótszego niż `MinimumStatusDuration`; producent MAY mieć własne
  minimalne opóźnienie, do którego ta wartość się dodaje, a `0` go nie wyłącza `[16 §4.9]`.
- `status` inny niż `Faulted` z kodem błędu to ostrzeżenie (ładowanie możliwe); `EVCommunicationError` SHALL wystąpić
  tylko przy `Preparing`, `SuspendedEV`, `SuspendedEVSE`, `Finishing` `[16 §4.9]`.
- Odłączenie kabla po stronie EV w trakcie transakcji: przy `StopTransactionOnEVSideDisconnect = false` stacja SHOULD
  zgłosić `SuspendedEV`, a przy `true` `Finishing`, w obu przypadkach z `errorCode = NoError` i powodem w `info`
  („EV side disconnected”) `[16 §4.9]`.
- Status `connectorId 0` nie jest bezpośrednio związany ze statusami złączy `[16 §4.9]`.

**Wniosek:** przejście spoza tabeli (np. `Available` → `Finishing`) w logu stacji to kandydat na odchylenie
modelu albo zgubione `StatusNotification` (`MinimumStatusDuration`, opóźnienie producenta). Rozstrzyga to
`ev-evse-diagnostics-expert` na podstawie logu i wersji firmware.
- Wiele złączy na jednym EVSE (np. Type 2 i CCS ze wspólnym modułem mocy): OCPP 1.x zakłada, że każde złącze ładuje
  niezależnie. Zalecenie OCA (TWG): każde złącze jak osobne EVSE, a blokadę wzajemną zgłaszać statusami
  `StatusNotification` `[OCA-AN-MC §4]`:
  - początek autoryzacji → wszystkie złącza EVSE `Preparing`;
  - gdy wiadomo, które złącze jest używane → pozostałe `Unavailable`;
  - koniec transakcji i odłączenie → wszystkie `Available`;
  - uszkodzone jedno złącze → tylko ono `Faulted`; uszkodzone EVSE → wszystkie `Faulted`.

  Integracja z OCPI (złącza jako osobne EVSE): skill `ev-integration-architect`.

## 3. Odpowiedzi poleceń (wartości ze schematów `[S16]`)
| Odpowiedź / pole | Wartości |
|---|---|
| `BootNotification` (wymagane `status`, `currentTime`, `interval`) | `Accepted`, `Pending`, `Rejected` |
| `idTagInfo.status` (`Authorize`, `StartTransaction`, `StopTransaction`) | `Accepted`, `Blocked`, `Expired`, `Invalid`, `ConcurrentTx` |
| `RemoteStartTransaction`, `RemoteStopTransaction`, `Reset`, `ClearCache`, `CancelReservation`, `GetCompositeSchedule` | `Accepted`, `Rejected` |
| `ChangeAvailability` (`type`: `Inoperative`, `Operative`) | `Accepted`, `Rejected`, `Scheduled` |
| `ChangeConfiguration` | `Accepted`, `Rejected`, `RebootRequired`, `NotSupported` |
| `ReserveNow` | `Accepted`, `Faulted`, `Occupied`, `Rejected`, `Unavailable` |
| `SendLocalList` (`updateType`: `Differential`, `Full`) | `Accepted`, `Failed`, `NotSupported`, `VersionMismatch` |
| `SetChargingProfile` | `Accepted`, `Rejected`, `NotSupported` |
| `ClearChargingProfile` | `Accepted`, `Unknown` |
| `UnlockConnector` | `Unlocked`, `UnlockFailed`, `NotSupported` |
| `DataTransfer` | `Accepted`, `Rejected`, `UnknownMessageId`, `UnknownVendorId` |
| `TriggerMessage.requestedMessage` | `BootNotification`, `DiagnosticsStatusNotification`, `FirmwareStatusNotification`, `Heartbeat`, `MeterValues`, `StatusNotification` |
| `TriggerMessage` (odpowiedź) | `Accepted`, `Rejected`, `NotImplemented` |
| `StopTransaction.reason` | `EmergencyStop`, `EVDisconnected`, `HardReset`, `Local`, `Other`, `PowerLoss`, `Reboot`, `Remote`, `SoftReset`, `UnlockCommand`, `DeAuthorized` |
| `FirmwareStatusNotification` | `Downloaded`, `DownloadFailed`, `Downloading`, `Idle`, `InstallationFailed`, `Installing`, `Installed` |
| `Reset.type` | `Hard`, `Soft` |

- `StartTransactionResponse` wymaga `idTagInfo` i `transactionId`: identyfikator nadaje CS `[S16]`.
- `RemoteStartTransaction`: wymagany tylko `idTag`; `connectorId` i `chargingProfile` opcjonalne `[S16]` `[16 §5.11]`.
- `TriggerMessage(BootNotification)`: wartość istnieje w schemacie, ale po wysłaniu `BootNotification.conf` ze statusem
  `Accepted` CS SHALL NOT żądać nowego `BootNotification`, dopóki stacja sama go nie wyśle (errata 1.6 §3.40
  `[16E §3.40]`). Stan złączy odświeżasz przez `TriggerMessage(StatusNotification)`.
- `BootNotification` `Pending`: kanał komunikacji „SHOULD NOT be closed by either the Charge Point or the Central
  System” `[16 §4.2]`.

### `BootNotification` — zasady przed akceptacją `[16 §4.2]`
- Stacja SHALL wysłać `BootNotification` przy każdym starcie i restarcie. Do odpowiedzi `Accepted` albo `Pending` SHALL
  NOT wysyłać innych żądań, także zbuforowanych sprzed restartu.
- Odpowiedź inna niż `Accepted`: `interval` to minimalny czas do kolejnego `BootNotification`; `0` → stacja sama
  dobiera odstęp, żeby nie zalewać CS. Wcześniej SHOULD NOT, chyba że na `TriggerMessage`.
- `Pending`: CS MAY odczytywać i zmieniać konfigurację, stacja SHOULD odpowiadać, ale SHALL NOT wysyłać własnych żądań
  bez `TriggerMessage`. W tym stanie CS nie może wysłać `RemoteStartTransaction` ani `RemoteStopTransaction`.
- `Rejected`: do upływu `interval` stacja SHALL NOT wysyłać żadnych komunikatów OCPP i SHALL NOT odpowiadać na żądania
  CS; CS SHOULD NOT ich inicjować. Obie strony MAY zamknąć kanał.
- Transakcje przed akceptacją: operator MAY je dopuścić, ale nie wiadomo, czy dotrą do CS. Bez zegara czasu
  rzeczywistego stacja może nie mieć poprawnej daty. Zwykle zaleca się odmowę ładowania stacji, która nigdy nie była
  `Accepted` `[16 §4.2.1]` `[16E §3.11]`.

### `StopTransaction` `[16 §4.10]` `[16 §6.49–6.50]`
- `StopTransaction.req`: wymagane `meterStop` (Wh), `timestamp`, `transactionId` (ten z `StartTransaction.conf`);
  opcjonalne `idTag` (stacja SHALL wysłać, gdy jest znany), `reason` (MAY pominąć tylko dla „Local”),
  `transactionData` (`MeterValue` „relevant for billing purposes”) `[16 §6.49]`.
- `StopTransaction.conf`: tylko opcjonalne `idTagInfo` (transakcja mogła się skończyć bez identyfikatora) `[16 §6.50]`.
- CS „cannot prevent a transaction from stopping”; może tylko potwierdzić i podać dane `idTag` do cache. Wyniki
  kontroli poprawności danych SHOULD NOT nigdy powstrzymać odpowiedzi `StopTransaction.conf` `[16 §4.10]`.
- Normalny koniec (kierowca okazał identyfikator): `reason` MAY być pominięty i SHOULD być przyjęty jako „Local”;
  w innych przypadkach SHOULD mieć właściwą wartość `[16 §4.10]`.

**Wniosek:** energia sesji w CSMS = `meterStop` − `meterStart` (oba w Wh `[16 §6.45]` `[16 §6.49]`); próbki z
`transactionData` służą do kontroli i wyceny, a odpowiedź `StopTransaction.conf` wysyłasz także wtedy, gdy kontrola
danych wykryła problem (problem obsługujesz po przyjęciu).

## 4. Pomiary (`MeterValues`, `SampledValue`) `[S16]`
- `measurand`: `Energy.Active.Export.Register`, `Energy.Active.Import.Register`, `Energy.Reactive.Export.Register`,
  `Energy.Reactive.Import.Register`, `Energy.Active.Export.Interval`, `Energy.Active.Import.Interval`,
  `Energy.Reactive.Export.Interval`, `Energy.Reactive.Import.Interval`, `Power.Active.Export`, `Power.Active.Import`,
  `Power.Offered`, `Power.Reactive.Export`, `Power.Reactive.Import`, `Power.Factor`, `Current.Import`, `Current.Export`,
  `Current.Offered`, `Voltage`, `Frequency`, `Temperature`, `SoC`, `RPM`.
- `context`: `Interruption.Begin`, `Interruption.End`, `Sample.Clock`, `Sample.Periodic`, `Transaction.Begin`,
  `Transaction.End`, `Trigger`, `Other`.
- `format`: `Raw`, `SignedData`. `location`: `Cable`, `EV`, `Inlet`, `Outlet`, `Body`.
- `phase`: `L1`, `L2`, `L3`, `N`, `L1-N`, `L2-N`, `L3-N`, `L1-L2`, `L2-L3`, `L3-L1`.
- `unit`: `Wh`, `kWh`, `varh`, `kvarh`, `W`, `kW`, `VA`, `kVA`, `var`, `kvar`, `A`, `V`, `K`, `Celcius`, `Celsius`,
  `Fahrenheit`, `Percent`. Oficjalny schemat zawiera **obie** pisownie `Celcius` i `Celsius`. Domyślnie
  „Wh” dla measurandu typu energia `[16 §7.43]`.
- `meterStart` w `StartTransaction.req` jest w Wh `[16 §6.45]`.
- MeterValues zegarowe: `transactionId` to ID transakcji trwającej na złączu w chwili pomiaru; dla `connectorId 0`
  (licznik główny) zaleca się nie podawać `transactionId` `[16E §3.16]`.

## 5. Klucze konfiguracji
Pełne definicje (wymagany / opcjonalny, dostęp, typ, jednostka, opis): `[16 §9.1–9.4]`; dodatek bezpieczeństwa `[SWP4]`.
Aktualne wartości stacji zawsze odczytuj `GetConfiguration`.

| Obszar | Klucze `[16 §9]` |
|---|---|
| Łączność | `HeartbeatInterval`, `WebSocketPingInterval`, `ResetRetries` |
| Start transakcji | `ConnectionTimeOut`, `AuthorizeRemoteTxRequests`, `LocalPreAuthorize`, `LocalAuthorizeOffline`, `AllowOfflineTxForUnknownId`, `AuthorizationCacheEnabled`, `MaxEnergyOnInvalidId` |
| Koniec transakcji | `StopTransactionOnEVSideDisconnect`, `StopTransactionOnInvalidId`, `UnlockConnectorOnEVSideDisconnect` |
| Kolejka transakcji | `TransactionMessageAttempts`, `TransactionMessageRetryInterval` |
| Pomiary | `MeterValueSampleInterval`, `MeterValuesSampledData`, `ClockAlignedDataInterval`, `MeterValuesAlignedData`, `StopTxnSampledData`, `StopTxnAlignedData` |
| Statusy | `MinimumStatusDuration` |
| Opis stacji | `NumberOfConnectors`, `SupportedFeatureProfiles`, `GetConfigurationMaxKeys`, `ConnectorPhaseRotation` |
| Lista lokalna (§9.2) | `LocalAuthListEnabled`, `LocalAuthListMaxLength`, `SendLocalListMaxLength` |
| Rezerwacja (§9.3) | `ReserveConnectorZeroSupported` |
| Smart Charging (§9.4) | `ChargeProfileMaxStackLevel`, `ChargingScheduleAllowedChargingRateUnit`, `ChargingScheduleMaxPeriods`, … |

Definicje kluczowe (cytaty):
- `HeartbeatInterval` (wymagany, RW, s): „Interval of inactivity (no OCPP exchanges) with central system after which
  the Charge Point should send a Heartbeat.req PDU” `[16 §9.1.10]`.
- `ConnectionTimeOut` (wymagany, RW, s): „Interval from beginning of status: 'Preparing' until incipient Transaction is
  automatically canceled, due to failure of EV driver to (correctly) insert the charging cable connector(s)…” `[16 §9.1.6]`.
- `AuthorizeRemoteTxRequests` (wymagany, R lub RW): czy `RemoteStartTransaction.req` jest autoryzowany wcześniej jak
  akcja lokalna `[16 §9.1.3]`.
- `MinimumStatusDuration` (opcjonalny, RW, s): minimalny czas stabilnego stanu przed wysłaniem `StatusNotification` `[16 §9.1.20]`.
- `TransactionMessageAttempts` (wymagany, RW): ile razy stacja próbuje wysłać komunikat transakcyjny, którego CS nie
  przetworzył `[16 §9.1.31]`.
- `WebSocketPingInterval` (opcjonalny, RW, s): 0 wyłącza ping po stronie klienta; wartości dodatnie to sekundy między
  pingami `[16 §9.1.34]`.
