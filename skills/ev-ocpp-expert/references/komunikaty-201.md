# OCPP 2.0.1 i 2.1 — komunikaty, enumy, Device Model

Źródła: `[201-P2]`, `[201-P3]`, `[201-CSV]`, `[21-P3]` (znaczniki jak w `SKILL.md`). CS = stacja (Charging Station).

## Spis treści
1. Komunikaty wg bloków funkcjonalnych
2. TransactionEvent
3. Statusy i odpowiedzi
4. Device Model — zmienne
5. TxStartPoint i TxStopPoint
6. Nowe akcje w 2.1

## 1. Komunikaty wg bloków funkcjonalnych
Bloki A–P: spis treści części 2 `[201-P2]`. Przypisanie komunikatu do bloku: tytuły przypadków użycia (np. G01 Status
Notification, G02 Heartbeat) `[201-P2]`. Kierunek: opisy PDU („…Request PDU sent by the Charging Station to the CSMS”)
i przypadki użycia `[201-P2]`. Komplet: 64 akcje `[201-P3]`.

| Blok | CS → CSMS | CSMS → CS |
|---|---|---|
| A Security | `SecurityEventNotification` (A04), `SignCertificate` (A02/A03) | `CertificateSigned` (A02/A03) |
| B Provisioning | `BootNotification` (B01–B03), `NotifyReport` | `GetBaseReport` (B07), `GetReport` (B08), `GetVariables` (B06), `SetVariables` (B05), `SetNetworkProfile` (B09), `Reset` (B11/B12) |
| C Authorization | `Authorize` | `ClearCache` (C11) |
| D Local Authorization List Management | — | `SendLocalList` (D01), `GetLocalListVersion` (D02) |
| E Transactions | `TransactionEvent` | `GetTransactionStatus` (E14) |
| F Remote Control | — | `RequestStartTransaction` (F01/F02), `RequestStopTransaction` (F03), `UnlockConnector` (F05), `TriggerMessage` (F06) |
| G Availability | `StatusNotification` (G01), `Heartbeat` (G02) | `ChangeAvailability` (G03/G04) |
| H Reservation | `ReservationStatusUpdate` (H04) | `ReserveNow` (H01), `CancelReservation` (H02) |
| I Tariff And Cost | — | `CostUpdated` |
| J Meter Values | `MeterValues` (J01) | — |
| K Smart Charging | `ReportChargingProfiles` (K09), `NotifyChargingLimit`, `ClearedChargingLimit` (K11–K13), `NotifyEVChargingNeeds` (K15), `NotifyEVChargingSchedule` | `SetChargingProfile` (K01), `GetCompositeSchedule` (K08), `GetChargingProfiles` (K09), `ClearChargingProfile` (K10) |
| L Firmware Management | `FirmwareStatusNotification`, `PublishFirmwareStatusNotification` | `UpdateFirmware` (L01/L02), `PublishFirmware` (L03), `UnpublishFirmware` (L04) |
| M Certificate Management | `Get15118EVCertificate` (M01/M02), `GetCertificateStatus` (M06) | `GetInstalledCertificateIds` (M03), `DeleteCertificate` (M04), `InstallCertificate` (M05) |
| N Diagnostics | `LogStatusNotification`, `NotifyMonitoringReport`, `NotifyEvent` (N07/N08), `NotifyCustomerInformation` | `GetLog` (N01), `GetMonitoringReport` (N02), `SetMonitoringBase` (N03), `SetVariableMonitoring` (N04), `SetMonitoringLevel` (N05), `ClearVariableMonitoring` (N06), `CustomerInformation` (N09/N10) |
| O Display Message | `NotifyDisplayMessages` | `SetDisplayMessage` (O01/O02), `GetDisplayMessages` (O03/O04), `ClearDisplayMessage` (O05) |
| P DataTransfer | `DataTransfer` (P02) | `DataTransfer` (P01) |

## 2. TransactionEvent
- Wymagane: `eventType`, `timestamp`, `triggerReason`, `seqNo`, `transactionInfo`, a w nim `transactionId`.
  **Identyfikator nadaje stacja** `[201-P3]`.
- Opcjonalne: `meterValue`, `offline`, `numberOfPhasesUsed`, `cableMaxCurrent`, `reservationId`, `evse`, `idToken`.
  W `transactionInfo` opcjonalne: `chargingState`, `timeSpentCharging`, `stoppedReason`, `remoteStartId` `[201-P3]`.
- `offline`: „Indication that this transaction event happened when the Charging Station was offline. Default = false” `[201-P2]`.
- `seqNo`: „Incremental sequence number, helps with determining if all messages of a transaction have been received” `[201-P2]`.
  Licznik prowadzony **per EVSE**. Na początku transakcji SHOULD wynosić 0, licznik ciągły jest dozwolony, a po każdym
  `TransactionEvent` SHALL rosnąć o 1. CSMS ma komplet, gdy otrzymał start (`a`), koniec (`o > a`) i każdy `n` z przedziału
  `[201-P2 E §1.3.2, §1.3.2.1]`.
- `eventType`: `Started`, `Updated`, `Ended` `[201-P3]`.
- `chargingState`: `Charging`, `EVConnected`, `SuspendedEV`, `SuspendedEVSE`, `Idle` `[201-P3]`.
- `triggerReason`: `Authorized`, `CablePluggedIn`, `ChargingRateChanged`, `ChargingStateChanged`, `Deauthorized`,
  `EnergyLimitReached`, `EVCommunicationLost`, `EVConnectTimeout`, `MeterValueClock`, `MeterValuePeriodic`,
  `TimeLimitReached`, `Trigger`, `UnlockCommand`, `StopAuthorized`, `EVDeparted`, `EVDetected`, `RemoteStop`,
  `RemoteStart`, `AbnormalCondition`, `SignedDataReceived`, `ResetCommand` `[201-P3]`.
  Uwaga: część wymagań (np. F02.FR.07/08) pisze „EVConnectionTimeout”, ale wartość enum to `EVConnectTimeout`
  `[201-P2 §3.82]`. Errata 2.1 w przypadku testowym wymaga „triggerReason must be EVConnectTimeout” `[21-E]`.
- `stoppedReason`: `DeAuthorized`, `EmergencyStop`, `EnergyLimitReached`, `EVDisconnected`, `GroundFault`,
  `ImmediateReset`, `Local`, `LocalOutOfCredit`, `MasterPass`, `Other`, `OvercurrentFault`, `PowerLoss`,
  `PowerQuality`, `Reboot`, `Remote`, `SOCLimitReached`, `StoppedByEV`, `TimeLimitReached`, `Timeout` `[201-P3]`.
- Odpowiedź (`TransactionEventResponse`): wszystkie pola opcjonalne: `totalCost`, `chargingPriority`, `idTokenInfo`,
  `updatedPersonalMessage` `[201-P3]`.

## 3. Statusy i odpowiedzi (wartości ze schematów `[201-P3]`)
| Element | Wartości |
|---|---|
| `StatusNotification` (wymagane `timestamp`, `connectorStatus`, `evseId`, `connectorId`) | `Available`, `Occupied`, `Reserved`, `Unavailable`, `Faulted` |
| `BootNotification.reason` | `ApplicationReset`, `FirmwareUpdate`, `LocalReset`, `PowerUp`, `RemoteReset`, `ScheduledReset`, `Triggered`, `Unknown`, `Watchdog` |
| `BootNotificationResponse` (wymagane `currentTime`, `interval`, `status`) | `Accepted`, `Pending`, `Rejected` |
| `RequestStartTransaction` (wymagane `remoteStartId`, `idToken`; opcjonalne `evseId`, `groupIdToken`, `chargingProfile`) | odpowiedź `Accepted` / `Rejected`; opcjonalnie `statusInfo`, `transactionId` |
| `idToken.type` | `Central`, `eMAID`, `ISO14443`, `ISO15693`, `KeyCode`, `Local`, `MacAddress`, `NoAuthorization` |
| `AuthorizationStatus` | `Accepted`, `Blocked`, `ConcurrentTx`, `Expired`, `Invalid`, `NoCredit`, `NotAllowedTypeEVSE`, `NotAtThisLocation`, `NotAtThisTime`, `Unknown` |
| `Reset.type` | `Immediate`, `OnIdle` |
| `ChangeAvailability` | `Operative` / `Inoperative` → `Accepted`, `Rejected`, `Scheduled` |
| `UnlockConnector` | `Unlocked`, `UnlockFailed`, `OngoingAuthorizedTransaction`, `UnknownConnector` |
| `TriggerMessage.requestedMessage` | `BootNotification`, `LogStatusNotification`, `FirmwareStatusNotification`, `Heartbeat`, `MeterValues`, `SignChargingStationCertificate`, `SignV2GCertificate`, `StatusNotification`, `TransactionEvent`, `SignCombinedCertificate`, `PublishFirmwareStatusNotification` |
| `GetVariables` (wynik) | `Accepted`, `Rejected`, `UnknownComponent`, `UnknownVariable`, `NotSupportedAttributeType` |
| `SetVariables` (wynik) | j.w. oraz `RebootRequired` |
| `GetBaseReport` | `ConfigurationInventory`, `FullInventory`, `SummaryInventory` |
| Atrybut zmiennej / mutowalność | `Actual`, `Target`, `MinSet`, `MaxSet` / `ReadOnly`, `WriteOnly`, `ReadWrite` |

`RequestStartTransactionResponse.transactionId`: „When the transaction was already started by the Charging Station before
the RequestStartTransactionRequest was received, for example: cable plugged in first” `[201-P2]`; wymaganie F01.FR.13
`[201-P2]`.

## 4. Device Model — zmienne (cytaty z `[201-CSV]`, plik `dm_components_vars.csv`)
| Zmienna | Wymagana | Typ / jedn. | Opis |
|---|---|---|---|
| `OCPPCommCtrlr.HeartbeatInterval` | nie | integer, s | „Interval of inactivity (no OCPP exchanges) with CSMS after which the Charging Station should send HeartbeatRequest.” |
| `OCPPCommCtrlr.OfflineThreshold` | tak | integer, s | „When the offline period of a Charging Station exceeds the OfflineThreshold it is recommended to send a StatusNotificationRequest for all its Connectors.” |
| `OCPPCommCtrlr.MessageTimeout[Default]` | tak | integer, s | „specifies after which time a message times out. It is configured in the network connection profile.” |
| `OCPPCommCtrlr.MessageAttempts[TransactionEvent]` | tak | integer | ile razy stacja próbuje wysłać `TransactionEventRequest`, którego CSMS nie przetworzył |
| `OCPPCommCtrlr.MessageAttemptInterval[TransactionEvent]` | tak | integer | jak długo czekać przed ponownym wysłaniem takiego komunikatu |
| `OCPPCommCtrlr.QueueAllMessages` | nie | boolean | gdy `true`, stacja kolejkuje wszystkie komunikaty do czasu dostarczenia |
| `OCPPCommCtrlr.WebSocketPingInterval` | nie | integer, s | 0 wyłącza ping po stronie klienta; wartości dodatnie to sekundy między pingami |
| `AuthCtrlr.AuthorizeRemoteStart` | tak | boolean | czy `RequestStartTransactionRequest` jest autoryzowany wcześniej jak akcja lokalna |
| `AuthCtrlr.LocalPreAuthorize` | tak | boolean | start dla lokalnie autoryzowanych identyfikatorów bez czekania na `AuthorizeResponse` (online) |
| `AuthCtrlr.LocalAuthorizeOffline` | tak | boolean | start dla lokalnie autoryzowanych identyfikatorów offline |
| `TxCtrlr.EVConnectionTimeOut` | tak | integer, s | czas od „rozpoczęcia” transakcji do jej anulowania, gdy kierowca nie podłączy kabla |
| `TxCtrlr.TxStartPoint` / `TxStopPoint` | tak | MemberList | kiedy stacja rozpoczyna / kończy transakcję |
| `TxCtrlr.StopTxOnEVSideDisconnect` | tak | boolean | `true` → stacja SHALL zdeautoryzować transakcję po odłączeniu kabla od EV |
| `SampledDataCtrlr.TxUpdatedInterval` | tak | integer, s | interwał próbkowania danych wysyłanych w `TransactionEvent(Updated)` |
| `SecurityCtrlr.SecurityProfile` | tak | integer | profil bezpieczeństwa używany przez stację |

Załączniki mogą być aktualizowane bez nowego wydania OCPP (nowe opcjonalne komponenty i zmienne): ReadMe pakietu `[201-CSV]`.

## 5. TxStartPoint i TxStopPoint `[201-P2 §2.6.6]`
Wartości: `ParkingBayOccupancy`, `EVConnected`, `Authorized`, `DataSigned`, `PowerPathClosed`, `EnergyTransfer`.
- `PowerPathClosed` to logiczne AND `EVConnected` i `Authorized`; „Despite its name, this event is not related to the
  state of the power relay”.
- Przy `EnergyTransfer` istnieje krótka luka między początkiem przepływu energii a startem transakcji, która może
  zniekształcić odczyt licznika. OCA zaleca wtedy `PowerPathClosed`.
- `DataSigned`: start przy otrzymaniu podpisanej wartości licznika (gdy przepisy wymagają jej do rozliczenia).
  Jako `TxStopPoint` nie ma znaczenia.
- Dla `TxStopPoint` każdą wartość czyta się z przedrostkiem „Not” (koniec zdarzenia).
Od tych zmiennych zależy, kiedy przyjdzie `TransactionEvent(Started)` i `Ended`. Przypadki użycia E01 i E06 opisują
warianty `[201-P2]`.

## 6. Nowe akcje w 2.1
27 akcji obecnych w schematach 2.1 i nieobecnych w 2.0.1 (porównanie `[201-P3]`, `[21-P3]`):
- energia i DER: `AFRRSignal`, `SetDERControl`, `GetDERControl`, `ClearDERControl`, `ReportDERControl`, `NotifyDERAlarm`,
  `NotifyDERStartStop`, `NotifyAllowedEnergyTransfer`, `UpdateDynamicSchedule`, `PullDynamicScheduleUpdate`,
  `NotifyPriorityCharging`, `UsePriorityCharging`;
- taryfy i płatności: `SetDefaultTariff`, `GetTariffs`, `ClearTariffs`, `ChangeTransactionTariff`, `NotifySettlement`,
  `NotifyWebPaymentStarted`, `VatNumberValidation`;
- strumienie zdarzeń: `OpenPeriodicEventStream`, `ClosePeriodicEventStream`, `GetPeriodicEventStream`,
  `AdjustPeriodicEventStream`, `NotifyPeriodicEventStream`;
- inne: `BatterySwap`, `RequestBatterySwap`, `GetCertificateChainStatus`.
`NotifyPeriodicEventStream` ma w pakiecie jeden plik schematu (bez pary Request/Response) `[21-P3]`.
Pogrupowanie powyżej to opis po nazwach akcji, a nie podział z dokumentu. Kierunki i bloki funkcjonalne 2.1 sprawdzasz
w części 2 specyfikacji 2.1 przed użyciem.
