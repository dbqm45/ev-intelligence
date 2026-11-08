# Alarmy, priorytety, KPI

Znaczniki jak w `SKILL.md`.

## 1. Poziomy ważności OCPP 2.0.1 `[201-P2 §1.54.1 SetMonitoringLevelRequest]`
Skala 0–9: 0 to najwyższa ważność, 9 najniższa. Stacja raportuje tylko zdarzenia o ważności ≤ ustawionego poziomu.
| Poziom | Nazwa | Opis (OCA) |
|---|---|---|
| 0 | Danger | lives are potentially in danger; action should be taken immediately |
| 1 | Hardware Failure | unable to continue regular operations due to Hardware issues; action is required |
| 2 | System Failure | unable to continue … due to software or minor hardware issues; action is required |
| 3 | Critical | critical error; action is required |
| 4 | Error | non-urgent error; action is required |
| 5 | Alert | alert event; default severity for any type of monitoring event |
| 6 | Warning | action may be required |
| 7 | Notice | unusual event; no immediate action is required |
| 8 | Informational | regular operational event; no action is required |
| 9 | Debug | useful to developers, not useful during operations |

**Wniosek:** 0–2 budzą dyżurnego natychmiast, 3–4 to praca w godzinach z SLA, 5–6 przegląd, 7–9 tylko zapis i analityka.
Granice dopasowujesz do umów SLA. Skala OCA określa tylko, czy „action is required”.

## 2. Mechanizmy zdarzeń
- Monitory zmiennych: `SetVariableMonitoring` (typy `UpperThreshold`, `LowerThreshold`, `Delta`, `Periodic`,
  `PeriodicClockAligned`), `SetMonitoringBase` (`All`, `FactoryDefault`, `HardWiredOnly`), `SetMonitoringLevel`,
  `GetMonitoringReport` / `NotifyMonitoringReport` `[201-P3]` `[201-P2 N02–N06]`.
- Zdarzenia: `NotifyEvent` z `trigger` `Alerting` / `Delta` / `Periodic` i typem `HardWiredNotification`,
  `HardWiredMonitor`, `PreconfiguredMonitor`, `CustomMonitor` `[201-P3]` `[201-P2 N07–N08]`.
- 1.6: brak monitorów; stan pochodzi ze `StatusNotification` (`status`, `errorCode`, `vendorErrorCode`) `[16 §7.6–7.7]`.
- 2.0.1, stan złącza: oprócz zdarzeń stacja raportuje stan `StatusNotification` (`connectorStatus`), także
  `Faulted`; przy awarii stacji lub EVSE status SHALL być `Faulted` `[201-P2 B01]` `[201-P2 G01]`.

**Wniosek:** priorytety alarmów w 2.0.1 opierasz na dwóch źródłach: ważności zdarzeń (`NotifyEvent`, skala 0–9) i
przejściu złącza w `Faulted` (`StatusNotification`). `Faulted` na publicznym punkcie traktujesz jak alarm wymagający
działania, a nie zdarzenie do przeglądu rano.

## 3. Zdarzenia bezpieczeństwa (`SecurityEventNotification`) `[201-CSV security_events.csv]`
Oznaczone przez OCA jako **Critical = Yes** (wybór): `FirmwareUpdated`, `SettingSystemTime`, `StartupOfTheDevice`,
`ResetOrReboot`, `SecurityLogWasCleared`, `MemoryExhaustion`, `TamperDetectionActivated`, `InvalidFirmwareSignature`,
`InvalidFirmwareSigningCertificate`, `InvalidCsmsCertificate`, `InvalidChargingStationCertificate`,
`DiscardedRenewedClientCertificate`, `InvalidTLSVersion`, `InvalidTLSCipherSuite`, `MaintenanceLoginAccepted`,
`MaintenanceLoginFailed`.
Critical = No: `FailedToAuthenticateAtCsms`, `CsmsFailedToAuthenticate`, `ReconfigurationOfSecurityParameters`,
`InvalidMessages`, `AttemptedReplayAttacks`.
Komunikat jest w 2.0.1 (blok A04) i w dodatku bezpieczeństwa 1.6 `[201-P2 A04]` `[SWP4]`.

**Wniosek:** `TamperDetectionActivated` i nieoczekiwane `MaintenanceLogin*` traktujesz jak incydent bezpieczeństwa
(eskalacja poza NOC). Szczegóły: domena D11.

## 4. Kody błędów złącza 1.6 `[16 §7.6]`
`ConnectorLockFailure`, `EVCommunicationError` (nie wymaga `Faulted`, a `SuspendedEVSE`), `GroundFailure`,
`HighTemperature`, `InternalError`, `LocalListConflict`, `NoError`, `OtherError` (szczegóły w `vendorErrorCode`),
`OverCurrentFailure`, `OverVoltage`, `PowerMeterFailure`, `PowerSwitchFailure`, `ReaderFailure`, `ResetFailure`,
`UnderVoltage`, `WeakSignal`. Znaczenie `vendorErrorCode` zależy od producenta (D21).

## 5. KPI
- AFIR (wersja skonsolidowana) i rozporządzenie 2025/655 **nie zawierają** wymogu uptime (przeszukane 2026-11-07).
  Wymagają aktualnych danych dynamicznych, w tym statusu operacyjnego i dostępności, najpóźniej minutę po zmianie
  `[AFIR art. 20 ust. 2 lit. f]` `[AFIR-655 art. 2]`.
- Definicje AFIR: non-operational = „cannot be used due to a technical problem or maintenance works”
  `[AFIR-655 Annex, tabela F]`.
- **Wniosek:** KPI dostępności definiujesz w umowie (SLA). Licznik opierasz na tych samych zdarzeniach statusu, które
  idą do NAP, żeby raport KPI i dane publiczne były spójne. Wymogi spoza UE (np. USA) to domena D12.06, nieopracowana.
