# Wzorce protokołowe: zdalny start, wykrywanie offline, komunikaty transakcyjne

Źródła: znaczniki jak w `SKILL.md`. Zdania **Wniosek** to rekomendacje projektowe wyprowadzone z cytowanych wymagań.

## Spis treści
1. Zdalny start — 1.6J
2. Zdalny start — 2.0.1
3. Wykrywanie utraty łączności
4. Komunikaty transakcyjne, kolejka offline, ponawianie
5. Odpowiedniki konfiguracji 1.6 ↔ 2.0.1

## 1. Zdalny start — 1.6J
Fakty:
- Stacja odpowiada statusem, czy „has accepted the request and will attempt to start a transaction” `[16 §5.11]`
  (brzmienie po errata `[16E §3.32]`).
- `AuthorizeRemoteTxRequests = true`: stacja zachowuje się jak przy akcji lokalnej, najpierw autoryzuje `idTag` (lista
  lokalna, cache, `Authorize.req`) i startuje transakcję dopiero po autoryzacji. `false`: startuje od razu, a CS sprawdza
  `idTag` przy obsłudze `StartTransaction.req` `[16 §5.11]`.
- Bez `connectorId` stacja sama wybiera złącze i MAY odrzucić takie polecenie `[16 §5.11]`.
- `chargingProfile` w poleceniu: cel SHALL być `TxProfile` `[16 §5.11]`, a `transactionId` w tym profilu SHALL NOT być
  ustawiony `[16E §3.41]`.
- Brak podłączenia kabla: po `ConnectionTimeOut` liczonym od początku `Preparing` transakcja jest anulowana
  `[16 §9.1.6]` `[16E §3.21]`.
- Polecenie nie zawiera identyfikatora, który wróciłby w `StartTransaction` (pola: `idTag`, `connectorId`,
  `chargingProfile`) `[S16]`.

**Wniosek:**
- korelację robisz po (stacja, `connectorId`, `idTag`) i oknie czasu `ConnectionTimeOut`;
- nie ponawiasz polecenia, dopóki `StatusNotification` nie potwierdzi stanu złącza (np. `Available`);
- spóźniony `StartTransaction` przyjmujesz (kolejka offline, sekcja 4).

## 2. Zdalny start — 2.0.1
Fakty:
- `RequestStartTransactionRequest` wymaga `remoteStartId` i `idToken` `[201-P3]`. `remoteStartId` to „Id given by the
  server to this start request. The Charging Station will return this in the TransactionEventRequest” `[201-P2]`.
- Gdy transakcja powstała w wyniku polecenia, stacja SHALL umieścić `remoteStartId` w pierwszym `TransactionEvent` tej
  transakcji `[201-P2 F02.FR.01]`.
- Gdy transakcja już istniała, ale nie była autoryzowana (np. najpierw kabel), stacja SHALL zwrócić jej `transactionId`
  w odpowiedzi `[201-P2 F01.FR.13]` i SHALL dodać `remoteStartId` do następnego `TransactionEvent` `[201-P2 F01.FR.25]`.
- `AuthorizeRemoteStart = true` → stacja najpierw autoryzuje `IdToken` jak przy akcji lokalnej `[201-P2 F02.FR.09]`
  `[201-CSV]`.
- Kabel niepodłączony przed `EVConnectionTimeOut`:
  - `TxStopPoint` bez `ParkingBayOccupancy` → stacja SHALL zakończyć transakcję (`eventType = Ended`,
    `stoppedReason = Timeout`) `[201-P2 F02.FR.07]`;
  - `TxStopPoint` z `ParkingBayOccupancy` → stacja SHALL zdeautoryzować transakcję, a ta kończy się, gdy kierowca
    opuści miejsce `[201-P2 F02.FR.08]`.
  W obu przypadkach wartość `triggerReason` na łączu to `EVConnectTimeout` `[201-P2 §3.82]`.
- `RequestStartTransaction` z `IdTokenType` `NoAuthorization` jest dozwolony. Przy lokalnym zatrzymaniu taką transakcję
  może zakończyć każdy `[201-P2 F02 Remark]`.

**Wniosek:** korelacja po `remoteStartId` jest jednoznaczna. Po timeoucie odpowiedzi stan sprawdzasz przez
`GetTransactionStatus` (E14) albo `TriggerMessage` (`TransactionEvent` / `StatusNotification`) przed ponowieniem.

## 3. Wykrywanie utraty łączności
Fakty 1.6J:
- „With JSON over WebSocket, sending heartbeats is not mandatory. However, for time synchronization it is advised to at
  least send one heartbeat per 24 hour.” `[16 §4.6]`
- Stacja MAY pominąć Heartbeat, gdy w interwale wysłała inny PDU; CS SHOULD uznać dostępność po każdym PDU `[16 §4.6]`.
- `HeartbeatInterval` = interwał **bezczynności** („no OCPP exchanges”) `[16 §9.1.10]`. Odpowiedź `BootNotification`
  zawiera `interval` (wymagany) `[S16]`.
- `WebSocketPingInterval`: ping/pong WebSocket po stronie klienta albo serwera `[16 §9.1.34]`.

Fakty 2.0.1:
- Stacja SHALL dostosować interwał do wartości z `BootNotificationResponse(Accepted)` (G02.FR.01) i SHALL wysyłać
  `HeartbeatRequest` po skonfigurowanym czasie (G02.FR.02) `[201-P2]`.
- „Whenever a message from a Charging Station has been received” → CSMS SHALL uznać jej dostępność (G02.FR.04). Zaleca
  się reset licznika Heartbeat po wysłaniu innego komunikatu (G02.FR.05) i Heartbeat co najmniej raz na 24 h dla
  synchronizacji zegara (G02.FR.07) `[201-P2]`.
- Po przekroczeniu `OfflineThreshold` zaleca się wysłanie `StatusNotification` dla wszystkich złączy `[201-CSV]`.
- Przy timeoucie żądania albo braku odpowiedzi na ping zaleca się, żeby stacja zerwała i odnowiła połączenie
  `[201-P2 rozdz. ogólny §3.2 Message Timeouts]`.

**Wniosek, reguła CSMS:**
- znacznik „ostatni kontakt” aktualizujesz przy **każdej** ramce i pongu, a nie tylko przy Heartbeat;
- alarm podnosisz po upływie kilku interwałów (`interval` z `BootNotification` + margines), osobno dla zerwanego
  WebSocketu (zdarzenie natychmiastowe) i dla „cichej” stacji;
- po ponownym połączeniu weryfikujesz stan przez `StatusNotification` (1.6: wymagane po Boot `[16E §3.22]`).

## 4. Komunikaty transakcyjne, kolejka offline, ponawianie
Fakty 1.6:
- Komunikaty transakcyjne to `StartTransaction`, `StopTransaction` oraz okresowe i zegarowe `MeterValues`. Offline
  stacja MUST je kolejkować; dostarcza je chronologicznie; nowe komunikaty transakcyjne czekają na opróżnienie kolejki
  `[16 §3.7]`.
- CS SHOULD przetwarzać komunikat historyczny „as any other” `[16 §3.7]`.
- Przy powtarzającym się „failure to process” stacja ponawia z odstępem `TransactionMessageRetryInterval` × liczba
  poprzednich prób, do `TransactionMessageAttempts`, potem SHOULD porzucić komunikat i przejść do następnego `[16 §3.7.1]`.
- Bez `transactionId` (nie dotarł `StartTransaction.conf`) stacja SHALL wysyłać komunikaty transakcji z
  `transactionId = -1`, a CS SHALL odpowiadać, jakby identyfikator był ważny `[16E §3.18]`.

Fakty 2.0.1:
- Gdy CSMS nie przyjmie komunikatu transakcyjnego albo nie odpowie w `MessageTimeout`, stacja SHALL ponawiać do
  `MessageAttemptsTransactionEvent`, czekając `MessageAttemptIntervalTransactionEvent` × liczba poprzednich wysyłek
  (E13.FR.02–03). Po wyczerpaniu prób komunikat jest porzucany (warunek końcowy E13) `[201-P2 E13]`.
- `TransactionEvent.offline = true` oznacza zdarzenie, które zaszło offline `[201-P2]`. `seqNo` pozwala ustalić
  kompletność transakcji `[201-P2 E §1.3.2]`.

**Wniosek:**
- CALLERROR na komunikat transakcyjny tylko przy realnym błędzie formatu. Problem biznesowy (nieznana transakcja)
  obsługujesz po przyjęciu: zapis, kwarantanna, alarm. Inaczej stacja po limicie prób porzuci dane;
- rozliczenie 2.0.1 rozpoczynasz po kompletnym ciągu `seqNo` albo z flagą „dane niepełne”.

## 5. Odpowiedniki konfiguracji 1.6 ↔ 2.0.1
W sprawdzonych dokumentach 2.0.1 Ed4 (części 0, 2, załączniki) **nie ma tabeli mapowania kluczy 1.6 na zmienne
2.0.1**. Poniższe pary łączy zbieżny opis w obu źródłach. To wniosek z porównania opisów, a nie mapowanie OCA.

| 1.6 `[16 §9]` | 2.0.1 `[201-CSV]` | Zbieżność opisu |
|---|---|---|
| `HeartbeatInterval` | `OCPPCommCtrlr.HeartbeatInterval` | ten sam opis („Interval of inactivity (no OCPP exchanges)…”) |
| `ConnectionTimeOut` | `TxCtrlr.EVConnectionTimeOut` | ten sam opis anulowania przy niepodłączonym kablu; w 1.6 liczony od `Preparing`, w 2.0.1 od „starting” transakcji |
| `AuthorizeRemoteTxRequests` | `AuthCtrlr.AuthorizeRemoteStart` | ten sam opis dla `RemoteStartTransaction` / `RequestStartTransaction` |
| `TransactionMessageAttempts`, `TransactionMessageRetryInterval` | `OCPPCommCtrlr.MessageAttempts[TransactionEvent]`, `MessageAttemptInterval[TransactionEvent]` | ten sam mechanizm ponawiania (`[16 §3.7.1]`, `[201-P2 E13]`) |
| `LocalPreAuthorize`, `LocalAuthorizeOffline` | `AuthCtrlr.LocalPreAuthorize`, `AuthCtrlr.LocalAuthorizeOffline` | te same nazwy i znaczenie |
| `WebSocketPingInterval` | `OCPPCommCtrlr.WebSocketPingInterval` | ten sam opis |
| `StopTransactionOnEVSideDisconnect` | `TxCtrlr.StopTxOnEVSideDisconnect` | **różne brzmienie**: 1.6 „SHALL administratively stop the transaction” `[16 §9.1.23]`, 2.0.1 „SHALL deauthorize the transaction” `[201-CSV]`; w 2.0.1 koniec transakcji wyznacza `TxStopPoint` („Defines when the Charging Station ends a transaction” `[201-CSV]`) |
