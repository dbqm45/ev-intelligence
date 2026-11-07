---
name: ev-ocpp-expert
description: Użyj przy OCPP 1.6J, 2.0.1 i 2.1 między ładowarką a CSMS — komunikaty, statusy, transakcje, zdalny start, Heartbeat, konfiguracja, różnice wersji.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy pytaniach i decyzjach projektowych dotyczących protokołu OCPP (1.6J, 2.0.1, 2.1) między stacją ładowania a CSMS/CPMS — kiedy wolno użyć komunikatu, jakie odpowiedzi i statusy są możliwe, timeouty i ponawianie, cykl BootNotification i Heartbeat, transakcje 1.6 vs TransactionEvent, zdalny start i stop, konfiguracja (klucze 1.6, Device Model 2.x), kody błędów RPC, profile bezpieczeństwa, różnice wersji, nowe komunikaty 2.1. Każdy fakt z cytatem ze specyfikacji OCA. Nie do wyboru domen i skilli dla zadania przekrojowego (ev-domain-expert), roamingu OCPI (ev-ocpi-roaming-expert) ani zachowań konkretnego modelu ładowarki odbiegających od standardu (ev-evse-diagnostics-expert)."
  slowa: "OCPP, OCPP 1.6, OCPP 1.6J, OCPP 2.0.1, OCPP 2.1, IEC 63584, CSMS, Central System, CALL, CALLRESULT, CALLERROR, BootNotification, Heartbeat, HeartbeatInterval, StatusNotification, StartTransaction, StopTransaction, TransactionEvent, seqNo, triggerReason, transactionId, RemoteStartTransaction, RequestStartTransaction, remoteStartId, RemoteStopTransaction, MeterValues, measurand, Authorize, idTag, idToken, ChangeConfiguration, GetConfiguration, SetVariables, GetVariables, Device Model, ConnectionTimeOut, EVConnectionTimeOut, AuthorizeRemoteTxRequests, AuthorizeRemoteStart, TxStartPoint, TriggerMessage, Security Whitepaper, profil bezpieczeństwa, zdalny start nie działa, sesja nie startuje po poleceniu, ładowarka przestała wysyłać Heartbeat, wykrywanie offline, różnice 1.6 i 2.0.1, migracja na 2.0.1, ramka OCPP, errata OCPP"
---

# OCPP Expert — stacja ładowania ↔ CSMS

Skill odpowiada na pytania o **protokół OCPP**: co wolno wysłać, co może wrócić, jak obsłużyć brak odpowiedzi
i czym różnią się wersje. Jak zbudować z tego moduł CPMS (kolejki, baza, UI), to temat `ev-cpms-architect`
(domena D05, jeszcze nieopracowana). Tu podajesz **ograniczenia protokołu**, które ten projekt musi spełnić.
Taksonomia: D01.01. Sieć: brak.

**Zasada źródeł.** Każdy fakt pochodzi z dokumentów OCA wymienionych w `sources/oca-ocpp.yaml` i ma znacznik
`[dokument §sekcja]`, np. `[16 §4.6]`. Zdania oznaczone **wniosek** to rekomendacje wyprowadzone z cytowanych
wymagań, a nie tekst normy. Czego nie ma w tych dokumentach, tego nie podajesz z pamięci: piszesz, że źródło tego nie
określa.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „errata OCPP 1.6
§3.18 `[16E §3.18]`”, „specyfikacja OCPI 2.3.0 §4.4 `[OCPI230 §4.4]`”, „AFIR art. 5 ust. 10”, „rozporządzenie
wykonawcze 2025/655 art. 2 `[AFIR-655 art. 2]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/wersje-i-status.md` | wersje, edycje, IEC 63584, licencja, podprotokół WebSocket, zgodność wersji |
| `references/ramki-i-bledy.md` | ramki RPC, kody CALLERROR, jedno CALL naraz, timeout |
| `references/komunikaty-16.md` | katalog 1.6 z kierunkiem, statusy, kody błędów złącza, klucze konfiguracji |
| `references/komunikaty-201.md` | katalog 2.0.1 wg bloków, `TransactionEvent`, zmienne Device Model, nowe akcje 2.1 |
| `references/wzorce.md` | zdalny start, wykrywanie offline, komunikaty transakcyjne i kolejka, odpowiedniki 1.6 ↔ 2.0.1 |

## Procedura
1. **Ustal wersję i edycję.** Podprotokół WebSocket (`ocpp1.6`, `ocpp2.0.1`, `ocpp2.1`) `[J16 §3.1.2]`
   `[201-P4 §3.1.2]` `[21-P4 §3.1.2]` albo rejestr urządzeń. Wersja nieznana → odpowiedz dla 1.6J i 2.0.1 osobno.
   Słowników nie mieszasz: 2.0.1 nie jest zgodne wstecz z 1.6 `[201-P0 rozdz. 2]`.
2. **Nazwy komunikatów, pól i wartości enum** bierzesz z tabel w `references/` (wyciąg ze schematów OCA). Wartości spoza
   tabeli → piszesz, że schemat danej wersji jej nie ma.
3. **Rozdziel trzy warstwy odpowiedzi:**
   - transport (WebSocket, ping, zerwanie);
   - RPC (`CALLRESULT` / `CALLERROR`, timeout);
   - biznes (`status`, potem zdarzenia, które potwierdzają skutek).
   Przykład: `Accepted` na zdalny start znaczy, że stacja „has accepted the request and will attempt to start
   a transaction” `[16E §3.32]` `[201-P2 F02 Remark]`, a nie, że ładowanie ruszyło.
4. **Wskaż konfigurację, od której zależy zachowanie** (klucz 1.6 i zmienna 2.x, `references/wzorce.md`).
   Wartości nie zakładaj: odczytaj ją (`GetConfiguration` / `GetVariables`).
5. **Brak odpowiedzi to wynik nieznany.** Timeout CALL jest zależny od implementacji `[J16 §4.1.1]`
   `[201-P4 §4.1.1]`. **Wniosek:** stan sprawdzasz przed ponowieniem (`TriggerMessage`, w 2.0.1 także
   `GetTransactionStatus`); poleceń ze skutkiem (start, reset, odblokowanie) nie ponawiasz w ciemno.
6. **Norma czy praktyka.** Wymóg z dokumentu OCA → piszesz „SHALL/SHOULD/MAY” tak jak w źródle. Zachowanie konkretnej
   stacji → D21 (`ev-evse-diagnostics-expert`), z modelem i wersją firmware.
7. **Zakończ kryteriami akceptacji:** jakie ramki i w jakiej kolejności zobaczy CSMS oraz przypadki brzegowe
   (timeout, duplikat, offline, odrzucony komunikat transakcyjny).

## Najważniejsze różnice 1.6J ↔ 2.0.1
| Temat | 1.6J | 2.0.1 |
|---|---|---|
| Transakcja | `StartTransaction` / `StopTransaction` (+ `MeterValues`) `[S16]` | `TransactionEvent`: `Started` / `Updated` / `Ended`, wymagany `seqNo` `[201-P3]` |
| Kto nadaje `transactionId` | CSMS: pole wymagane w `StartTransactionResponse` `[S16]` | stacja: wymagane `transactionInfo.transactionId` `[201-P3]` |
| Zdalny start | `RemoteStartTransaction(idTag, [connectorId], [chargingProfile])` `[16 §5.11]` — bez identyfikatora polecenia | `RequestStartTransaction` z wymaganym `remoteStartId`, który stacja odsyła w `TransactionEvent` `[201-P2 F01.FR.25, F02.FR.01]` |
| Status złącza | 9 stanów + `errorCode` `[S16]` | 5 stanów: `Available`, `Occupied`, `Reserved`, `Unavailable`, `Faulted`; stan ładowania w `chargingState` `[201-P3]` |
| Konfiguracja | klucze, `GetConfiguration` / `ChangeConfiguration` `[16 §9]` | Device Model: `GetVariables` / `SetVariables` `[201-P2 B05–B07]` |
| Heartbeat | przy JSON „not mandatory”; zalecany co najmniej raz na 24 h dla zegara `[16 §4.6]` | `HeartbeatInterval` = czas bezczynności „no OCPP exchanges” `[201-CSV]` |
| Bezpieczeństwo | dodatek: Security Whitepaper ed. 4, profile 1–3, 11 akcji `[SWP4]` | profile 1–3 w standardzie; bez zabezpieczeń „NOT considered a valid OCPP 2.0.1 implementation” `[201-P2 A §1.3]` |

## Przykład
**Pytanie:** „`RemoteStartTransaction` na 1.6J zwraca `Accepted`, ale po 2 minutach nie ma `StartTransaction`.
Co z tym zrobić w CSMS?”

1. `Accepted` oznacza przyjęcie polecenia i próbę startu, a nie start `[16 §5.11]` `[16E §3.32]`.
2. Przyczyny przewidziane w specyfikacji:
   - przy `AuthorizeRemoteTxRequests = true` stacja najpierw autoryzuje `idTag` (lista lokalna, cache albo
     `Authorize`), a transakcja startuje „only after authorization was obtained” `[16 §5.11]`;
   - kierowca nie podłączył kabla: po `ConnectionTimeOut`, liczonym od początku stanu `Preparing`, stacja anuluje
     rozpoczętą transakcję i wraca do stanu wyjściowego, „probably: Available” `[16 §9.1.6]` `[16E §3.21]`.
3. Stan złącza pobierz przez `TriggerMessage` (`StatusNotification`) `[S16]`. Po zmianie stanu stacja i tak
   SHALL wysłać `StatusNotification` (z uwzględnieniem minimalnego czasu trwania stanu) `[16E §3.19]`.
4. **Wniosek:** nie ponawiaj startu automatycznie. W 1.6 polecenie nie ma identyfikatora `[16 §5.11]`, więc dwa
   starty na tym samym złączu i `idTag` są nierozróżnialne. Ponów dopiero, gdy złącze wróciło do `Available`.
5. **Wniosek, kryteria dla CSMS:**
   - sesja „oczekuje na start” z terminem `ConnectionTimeOut` plus margines;
   - po terminie stan „nie rozpoczęto” z ostatnim `StatusNotification`;
   - spóźniony `StartTransaction` nadal przyjmujesz: komunikaty transakcyjne są kolejkowane offline `[16 §3.7]`.
6. W 2.0.1: `RequestStartTransaction` z `remoteStartId`, timeout `TxCtrlr.EVConnectionTimeOut`. Bez kabla stacja
   kończy transakcję zdarzeniem `Ended` ze `stoppedReason = Timeout` `[201-P2 F02.FR.07]`. Na łączu
   `triggerReason = EVConnectTimeout` (wartość enum) `[201-P3]` `[201-P2 §3.82 TriggerReasonEnumType]`
   (szczegóły i warunek `TxStopPoint`: `references/wzorce.md`).

## Pułapki
- `Accepted` traktowane jako dowód skutku (start, reset, `UnlockConnector`, profil ładowania).
- Odrzucanie komunikatów transakcyjnych przez CALLERROR: stacja ponawia z rosnącym odstępem
  (`TransactionMessageAttempts`, `TransactionMessageRetryInterval`), a po limicie **porzuca** komunikat `[16 §3.7.1]`;
  w 2.0.1 tak samo przy `MessageAttemptsTransactionEvent` `[201-P2 E13]`. Skutek to utrata danych sesji.
- Brak `transactionId` w 1.6 (nie dotarł `StartTransaction.conf`): stacja wysyła komunikaty transakcji
  z `transactionId = -1`, a CSMS SHALL odpowiadać, jakby identyfikator był ważny `[16E §3.18]`.
- `TriggerMessage(BootNotification)` do zaakceptowanej stacji 1.6: CSMS SHALL NOT żądać nowego `BootNotification`, dopóki
  stacja sama go nie wyśle (errata 1.6 §3.40 `[16E §3.40]`). Stan pobierasz `TriggerMessage(StatusNotification)`.
- Wykrywanie offline wyłącznie po `Heartbeat`: przy 1.6J heartbeat nie jest obowiązkowy, a stacja MAY go pominąć, gdy
  wysłała inny komunikat; CSMS SHOULD uznać dostępność po każdym PDU `[16 §4.6]`.
- `meterStart` jest w **Wh** `[16 §6.45 StartTransaction.req]`. `unit` w `SampledValue` domyślnie `Wh` dla measurandów
  typu energia `[16 §7.43 SampledValue]`.
- `connectorId = 0` w 1.6: w poleceniach CSMS cała stacja, w raportach stacji jej główny kontroler `[16 §3.8]`.
- Kody błędów RPC: 1.6 pozostaje przy `FormationViolation` i `OccurenceConstraintViolation` (errata: „Do not fix”)
  `[J16E §5.1–5.2]`; 2.0.1 używa `FormatViolation` i `OccurrenceConstraintViolation` `[201-P4 §4.3]`.
- `seqNo` w 2.0.1 to licznik **per EVSE**; zerowanie na starcie transakcji jest zaleceniem (SHOULD), licznik ciągły jest
  dozwolony, a po każdym `TransactionEvent` SHALL rosnąć o 1 `[201-P2 E §1.3.2, §1.3.2.1]`.

## Źródła
Wszystkie dokumenty i sumy kontrolne: `sources/oca-ocpp.yaml` (pobrane ze strony OCA 2026-11-07). Znaczniki:
- `16` — OCPP 1.6 edition 2 (2017-09-28); `16E` — errata 1.6 (2025-04);
- `J16` — OCPP-J 1.6; `J16E` — errata OCPP-J 1.6 (2025-04-30);
- `S16` — schematy JSON 1.6; `SWP4` — Security Whitepaper 1.6-J ed. 4 (2026-02-05);
- `201-P0/P2/P3/P4/CSV/E` — OCPP 2.0.1 Edition 4 (2025-12-03): części 0, 2, schematy, część 4, załączniki CSV v1.5,
  errata 2026-09;
- `21-P0/P3/P4/E` — OCPP 2.1 Edition 2 (2025-12-03), schematy „Edition 1” (2025-01-23), errata 2026-09;
- `OCA-N1`, `OCA-N2` — komunikaty OCA z 2025-09-02 i 2025-12-09.
