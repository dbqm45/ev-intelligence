# Drzewo diagnozy — od objawu do przyczyny

Znaczniki jak w `SKILL.md`. Każda gałąź wskazuje mechanizm opisany w specyfikacji. Kolejność gałęzi to **Wniosek**:
najpierw tanie odczyty bez skutków ubocznych, potem polecenia zmieniające stan.

## Spis treści
1. Stacja online, sesja nie startuje (1.6J)
2. Te same objawy w 2.0.1
3. Sesja trwa, energia nie płynie
4. Stacja „offline”
5. Stacja partnera (roaming)
6. Kabel nie daje się wyjąć albo nie blokuje się
7. Logi lub firmware „wiszą”

## 1. Stacja online, sesja nie startuje (1.6J)
| Krok | Sprawdź | Interpretacja | Źródło |
|---|---|---|---|
| 1 | Status złącza i `errorCode` | `Unavailable` / `Faulted` → stacja nie przyjmie sesji (Inoperative). `ReaderFailure` → czytnik RFID. `ConnectorLockFailure` → blokada złącza | `[16 §7.6–7.7]` |
| 2 | Czy przyszło `Authorize.req` | brak → problem przed CSMS (czytnik, autoryzacja lokalna: `LocalPreAuthorize`, `LocalAuthorizeOffline`, cache, lista lokalna) | `[16 §9.1]` `[16 §7.6]` |
| 3 | `idTagInfo.status` | `Blocked`, `Expired`, `Invalid` („unknown”), `ConcurrentTx` („already involved in another transaction”) | `[16 §7.2]` |
| 4 | Zdalny start: `AuthorizeRemoteTxRequests` | `true` → stacja najpierw autoryzuje `idTag`, transakcja dopiero po autoryzacji | `[16 §5.11]` |
| 5 | `Preparing` bez `StartTransaction` | czeka na kabel; po `ConnectionTimeOut` wraca do stanu wyjściowego (B1) albo do `Finishing` (B6, kabel wpięty, brak `idTag`) | `[16 §9.1.6]` `[16E §3.20–3.21]` |
| 6 | `StartTransaction.conf` z `idTagInfo` ≠ `Accepted` | zależnie od `StopTransactionOnInvalidId` stacja zatrzyma transakcję; `MaxEnergyOnInvalidId` ogranicza energię po unieważnieniu | `[16 §9.1.24]` `[16 §9.1.14]` |
| 7 | Logi | `GetDiagnostics` → `DiagnosticsStatusNotification`; Security Whitepaper: `GetLog` | `[16 §5.9]` `[SWP4]` |

**Wniosek:** restart dopiero, gdy kroki 1–7 nie wskazały przyczyny. Patrz `dzialania-zdalne.md`.

## 2. Te same objawy w 2.0.1
- Stacja w `Pending` odrzuca `RequestStartTransaction` statusem `Rejected` `[201-P2 B02.FR.05]`.
- EVSE w `Unavailable` albo `Faulted` → `RequestStartTransaction` SHALL dostać `Rejected` `[201-P2 F01.FR.23]`.
  `Unavailable` może pochodzić z `ChangeAvailability` (trwały po restarcie) albo z decyzji stacji, np. w czasie
  aktualizacji firmware `[201-P2 G03.FR.08]` `[201-P2 G01]` `[201-P2 L01.FR.07]`.
- Złącze `Reserved`, a kierowca bez pasującego `IdToken`: status się nie zmienia i sesja nie rusza
  `[201-P2 G01.FR.09]`.
- Statusy złącza: Inoperative = `Unavailable`, `Faulted` `[201-P2 §3.23]`. Autoryzacja ma szerszy zbiór wartości (np.
  `NoCredit`, `NotAtThisLocation`, `NotAtThisTime`, `NotAllowedTypeEVSE`) `[201-P3]`.
- Moment startu transakcji zależy od `TxStartPoint` (np. `EVConnected`, `Authorized`, `PowerPathClosed`)
  `[201-P2 §2.6.6.1]`. Zdalny start bez kabla kończy się po `EVConnectionTimeOut` (`stoppedReason = Timeout`)
  `[201-P2 F02.FR.07]`.
- Diagnostyka: `GetLog` (`DiagnosticsLog`, `SecurityLog`) → `LogStatusNotification` `[201-P2 N01]` `[201-P3]`.
  Zdarzenia z monitorów → `NotifyEvent` `[201-P2 N07–N08]`.

## 3. Sesja trwa, energia nie płynie
- 1.6 `SuspendedEVSE`: EVSE nie oferuje energii, „e.g. due to a smart charging restriction, local supply power constraints,
  or as the result of StartTransaction.conf indicating that charging is not allowed” `[16 §7.7]`.
- 1.6 `SuspendedEV`: EVSE oferuje energię, ale pojazd jej nie pobiera `[16 §7.7]`.
- `EVCommunicationError` (np. problem Mode 3): stacja SHOULD przejść do `SuspendedEVSE`, a nie `Faulted` `[16 §7.6]`.
- 2.0.1: `chargingState` w `TransactionEvent`: `SuspendedEV`, `SuspendedEVSE`, `EVConnected`, `Charging`, `Idle` `[201-P3]`.

**Wniosek:** przy `SuspendedEVSE` sprawdzasz aktywne profile ładowania (`GetCompositeSchedule`) i limity zewnętrzne
(EMS/DSO, `[201-P1 §8.5–8.6]`). Przy `SuspendedEV` z definicji EVSE oferuje energię, a pojazd jej nie pobiera.
Reset stacji tego nie zmienia, więc najpierw kierujesz klienta do sprawdzenia stanu i ustawień pojazdu.

## 4. Stacja „offline”
- Łączność wyznacza CSMS: każda ramka od stacji świadczy o dostępności `[201-P2 G02.FR.04]` `[16 §4.6]`.
- Stacja po zerwaniu łączy się ponownie z rosnącym opóźnieniem i losowym rozrzutem `[201-P4 §5.4]`.
- Kontroler lokalny: utrata stacja–LC → LC SHALL zamknąć połączenie tej stacji do CSMS `[201-P4 §6.3]`.
- Brak Heartbeatu: CSMS „concludes that the Charging Station is Offline” `[201-P2 G02]`. Progu czasu nie określa żadne
  źródło; interwał stacja bierze z `BootNotificationResponse` `[201-P2 G02.FR.01]`.
- Po powrocie (1.6): stacja SHOULD wysłać bieżący status, jeśli się zmienił, MAY zgłosić błędy z czasu offline, a
  historii bez błędów SHOULD NOT wysyłać `[16 §4.9]`. 2.0.1: zdarzenia monitorów z czasu offline dochodzą tylko do
  ważności `OfflineMonitoringEventQueuingSeverity` `[201-P2 N07.FR.04]`.

**Wniosek:** wiele stacji offline jednocześnie → najpierw CSMS, sieć, APN lub kontroler lokalny, a nie pojedyncze stacje.
Po powrocie stanu nie oczekujesz `BootNotification`. Po `Accepted` CSMS w 1.6 SHALL NOT wywoływać nowego
`BootNotification` przez `TriggerMessage` `[16E §3.40]`. Statusy pobierasz `TriggerMessage(StatusNotification)`.

## 5. Stacja partnera (roaming)
- Działać może tylko CPO partnera. Ty widzisz status EVSE, sesje i wyniki komend `[OCPI230 §8, §9, §13]`.
- `CommandResult`: `EVSE_OCCUPIED`, `EVSE_INOPERATIVE`, `TIMEOUT`, `FAILED`, `REJECTED`… `[OCPI230 §13.4.2]`.
  `ACCEPTED` nie gwarantuje sesji (Figure 28) `[OCPI230 §13.1]`.
- Autoryzacja tokenu: whitelist i real-time; kod 2004 „Unknown Token” `[OCPI230 §12.4.5]` `[OCPI230 §5.2]`.

**Wniosek:** zgłoszenie do partnera zawiera `country_code` / `party_id`, `location_id` / `evse_uid`, czas, wynik komendy
i `X-Correlation-ID` żądania `[OCPI230 §4.2]`.

## 6. Kabel nie daje się wyjąć albo nie blokuje się
| Objaw | Mechanizm | Źródło |
|---|---|---|
| Kierowca nie może wyjąć kabla po sesji | `UnlockConnector`: ponowna próba odblokowania; dotyczy tylko blokady wtyku, nie drzwiczek | `[16 §5.18]` `[201-P2 F05]` |
| 2.0.1: `OngoingAuthorizedTransaction` | na złączu trwa autoryzowana transakcja; najpierw ją kończysz | `[201-P2 F05.FR.02]` |
| `UnlockFailed` | stacja próbowała i wykryła, że złącze nadal jest zablokowane albo mechanizm zawiódł | `[16 §7.46]` `[16E §3.87]` |
| 1.6: `NotSupported` | brak blokady albo nieznany `connectorId` (errata) | `[16E §3.87]` |
| 2.0.1: `UnknownConnector` / CALLERROR `NotSupported` | nieznane złącze / brak blokady lub blokada ręczna | `[201-P2 F05.FR.03]` `[201-P2 F05.FR.07]` |
| Ładowanie nie startuje po wpięciu kabla (2.0.1) | nieudane zablokowanie: stacja SHALL NOT ładować i zgłasza `ConnectorPlugRetentionLock` `Problem` = true | `[201-P2 G05.FR.01–02]` |
| Ładowanie nie startuje po wpięciu kabla (1.6) | `errorCode` `ConnectorLockFailure` | `[16 §7.6]` |

**Wniosek:** `UnlockFailed` powtórzone po kolejnej próbie to sprawa serwisu na miejscu. Z odpowiedzi `Unlocked` nie
wynika, że kabel został wyjęty: potwierdza to dopiero zmiana statusu złącza na `Available` `[201-P2 G01.FR.04]`.

## 7. Logi lub firmware „wiszą”
- Statusy bieżące pobierasz `TriggerMessage`: `DiagnosticsStatusNotification` / `LogStatusNotification`,
  `FirmwareStatusNotification`. `Idle` oznacza brak trwającego zadania i SHALL występować tylko w odpowiedzi na
  `TriggerMessage` `[16 §7.24]` `[16 §7.25]` `[201-P2 F06.FR.14–16]`.
- 1.6: w czasie wysyłania pliku diagnostyki stacja MUST wysyłać `DiagnosticsStatusNotification` `[16E §3.31]`.
  Wartości: `Uploading`, `Uploaded`, `UploadFailed` `[16 §7.24]`.
- 2.0.1 log: `Uploading`, `Uploaded`, błędy `UploadFailure`, `BadMessage`, `PermissionDenied`, `NotSupportedOperation`.
  Status błędu zaleca się wysłać dopiero po wyczerpaniu ponowień `[201-P2 N01.FR.10]` `[201-P2 §3.87]`. Każde
  powiadomienie ma `requestId` z `GetLog` `[201-P2 N01.FR.07]`.
- 2.0.1 firmware: stany pośrednie (np. `DownloadScheduled`, `DownloadPaused`, `InstallScheduled`, `InstallRebooting`) i
  końcowe: `Installed` (sukces), `DownloadFailed`, `InstallationFailed`, `InstallVerificationFailed`,
  `InvalidSignature` (porażka) `[201-P2 §3.33]`. Pobieranie odłożone z powodu ładowania albo `retrieveDateTime` w
  przyszłości → `DownloadScheduled` `[201-P2 L01.FR.13]`. Instalacja czeka na koniec transakcji, a nieużywane EVSE
  są w tym czasie `Unavailable`, chyba że `AllowNewSessionsPendingFirmwareUpdate` = true `[201-P2 L01.FR.06–07]`.

**Wniosek:** firmware „zawieszony” w stanie pośrednim przy trwającej sesji może być oczekiwaniem przewidzianym w
specyfikacji (`L01.FR.06`, `L01.FR.13`), a nie awarią. Po zakończeniu sesji sprawdzasz, czy przyszedł stan końcowy. Dopiero jego brak eskalujesz.
