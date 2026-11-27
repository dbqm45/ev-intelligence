# Alarmy, priorytety, KPI

Znaczniki jak w `SKILL.md`.

## Spis treści
1. Poziomy ważności OCPP 2.0.1
2. Mechanizmy zdarzeń
3. Zdarzenia bezpieczeństwa
4. Kody błędów złącza 1.6
5. KPI

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
  `Faulted`; przy awarii stacji lub EVSE status SHALL być `Faulted` `[201-P2 B01]`. `Faulted` = zgłoszony błąd i brak
  możliwości dostarczenia energii `[201-P2 §3.23]`.
- Pola zdarzenia (`EventDataType`): `eventId`, `timestamp`, `trigger`, `cause` (id zdarzenia-przyczyny), `actualValue`,
  `techCode` i `techInfo` (kod i opis z komponentu), `cleared` („return to normal”), `transactionId`,
  `variableMonitoringId`, `eventNotificationType`, `component`, `variable` `[201-P2 §2.22]`.
- Zamknięcie alarmu progowego: powrót wartości w granice → `NotifyEvent` z `cleared` = true `[201-P2 N07.FR.02]`, także
  po restarcie `[201-P2 N07.FR.14]`. Usunięcie monitora przy przekroczonym progu → stacja SHALL NOT wysłać `cleared`
  `[201-P2 N07.FR.12]`.
- Offline: stacja kolejkuje tylko zdarzenia o ważności ≤ `OfflineMonitoringEventQueuingSeverity` i dostarcza je po
  powrocie `[201-P2 N07.FR.04]`. Zdarzenia o ważności większej niż `SetMonitoringLevel` nie są wysyłane wcale
  `[201-P2 N07.FR.15]`.
- Przyczyna: stacja MAY wpisać w `cause` `eventId` zdarzenia, które wywołało bieżące `[201-P2 N07.FR.05]`.
- Blokada złącza (2.0.1): nieudane zablokowanie → stacja SHALL NOT rozpocząć ładowania i SHALL wysłać `NotifyEvent`
  dla `ConnectorPlugRetentionLock`, `Problem` = true `[201-P2 G05.FR.01–02]`. Wymaga komponentu w Device Model i poziomu
  monitorowania, który to zdarzenie przepuszcza `[201-P2 G05]`.
- 1.6: błąd przy statusie innym niż `Faulted` to ostrzeżenie (ładowanie możliwe). `EVCommunicationError` tylko przy
  `Preparing`, `SuspendedEV`, `SuspendedEVSE`, `Finishing`. Po powrocie z offline stacja MAY zgłosić błąd z czasu
  offline. Status krótszy niż `MinimumStatusDuration` MAY nie zostać wysłany `[16 §4.9]`.

**Wniosek:**
- alarm z `NotifyEvent` otwierasz po (`component`, `variable`, `evse`) i zamykasz zdarzeniem `cleared`. Po usunięciu
  lub zmianie monitora zamykasz go w CSMS sam, bo `cleared` nie przyjdzie;
- `cause` służy do grupowania: zdarzenia z przyczyną podpinasz pod zdarzenie nadrzędne zamiast budzić dyżurnego wiele
  razy;
- po powrocie stacji z offline brak zdarzeń o niskiej ważności nie znaczy, że ich nie było. Konfigurację
  `OfflineMonitoringEventQueuingSeverity` ustalasz razem z progami dyżuru;
- priorytety alarmów w 2.0.1 opierasz na dwóch źródłach: ważności zdarzeń (`NotifyEvent`, skala 0–9) i
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
Firmware 2.0.1: stan „Invalid Certificate” → stacja SHALL wysłać `InvalidFirmwareSigningCertificate`, stan
„Invalid Signature” → `InvalidFirmwareSignature` `[201-P2 L01.FR.02–03]`.

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
- „Availability of data” w AFIR to „the existence of data in a digital machine-readable format” `[AFIR art. 2 pkt 9]`,
  a „accessibility of data” to możliwość pobrania danych w każdej chwili `[AFIR art. 2 pkt 1]`. Obie definicje
  dotyczą danych, nie dostępności ładowarki. Pole „Availability” w danych dynamicznych opisuje zajętość (in use /
  reserved / not in use), a nie sprawność `[AFIR-655 Annex, tabela F]`.
- Polska: ustawa o elektromobilności wymaga przekazywania do EIPA dostępności punktu „natychmiast po zmianie stanu”
  i cen w ciągu godziny `[PL-EMOB art. 42 ust. 6]`. Progu uptime ustawa nie zawiera (wystąpienia „dostępności” w tekście
  dotyczą tylko danych do EIPA, przeszukane 2026-11-27).
- Dane wejściowe KPI z OCPP:
  - łączność: CSMS SHALL zakładać dostępność stacji po każdej odebranej wiadomości `[201-P2 G02.FR.04]`;
    w 1.6 SHOULD `[16 §4.6]`;
  - Inoperative = `Unavailable`, `Faulted` `[201-P2 §3.23]` `[16 §7.7]`;
  - `Unavailable` bywa ustawiany przez stację sama (firmware, przed `Accepted`) `[201-P2 G01]` `[16 §4.9]`, a gdy
    czeka na instalację firmware, SHALL tak ustawić nieużywane EVSE `[201-P2 L01.FR.07]`;
  - po restarcie stan ustawiony przez `ChangeAvailability` wraca `[201-P2 B11.FR.02]` `[201-P2 G03.FR.08]`.
- **Wniosek:** w KPI dzielisz czas „non-operational” według przyczyny (offline, `Faulted`, `Unavailable` operatora,
  `Unavailable` firmware). Definicja AFIR obejmuje i problem techniczny, i prace konserwacyjne, więc do NAP idą wszystkie
  te stany jako non-operational. Wyłączenia z KPI dopuszcza tylko umowa SLA, nie AFIR.
- **Wniosek:** KPI dostępności definiujesz w umowie (SLA). Licznik opierasz na tych samych zdarzeniach statusu, które
  idą do NAP, żeby raport KPI i dane publiczne były spójne. Wymogi spoza UE (np. USA) to domena D12.06, nieopracowana.
