# OCPP 1.6J — komunikaty, statusy, konfiguracja

Źródła: `[16]`, `[16E]`, `[S16]`, `[SWP4]` (znaczniki jak w `SKILL.md`). CP = stacja (Charge Point),
CS = Central System.

## Spis treści
1. Komunikaty wg profili i kierunku
2. Statusy i kody błędów złącza
3. Odpowiedzi poleceń
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
