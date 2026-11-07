---
name: ev-charging-operations-expert
description: Użyj przy operacjach sieci ładowania — NOC, alarmy i priorytety, diagnoza „sesja nie startuje”, zdalne działania (reset, odblokowanie), incydenty, KPI.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy pracy operatora sieci ładowania (CPO/NOC) i projektowaniu narzędzi operacyjnych — wykrywanie problemów i priorytety alarmów (severity 0–9, NotifyEvent, zdarzenia bezpieczeństwa, errorCode i Faulted), diagnoza krok po kroku (stacja online, a sesja nie startuje; brak autoryzacji RFID; SuspendedEV/SuspendedEVSE; ładowarka partnera w roamingu), bezpieczne zdalne działania (Reset OnIdle/Immediate, Soft/Hard, reset jednego EVSE, ChangeAvailability, UnlockConnector, TriggerMessage, pobranie logów), eskalacja incydentu i definicje KPI. Każdy fakt z cytatem ze specyfikacji OCA, EVRF albo AFIR, decyzje operacyjne oznaczone jako wniosek. Nie do szczegółów komunikatów OCPP (ev-ocpp-expert), architektury CPMS (ev-cpms-architect) ani zachowań konkretnego modelu ładowarki (ev-evse-diagnostics-expert)."
  slowa: "NOC, centrum monitoringu, dyżur, operator sieci ładowania, CPO operacje, alarm, priorytet alarmu, severity, Danger, Hardware Failure, NotifyEvent, SetMonitoringLevel, monitoring zmiennych, zdarzenie bezpieczeństwa, SecurityEventNotification, tamper, Faulted, errorCode, vendorErrorCode, ReaderFailure, GroundFailure, sesja nie startuje, ładowarka online ale nie ładuje, karta RFID nie działa, kierowca nie może rozpocząć ładowania, SuspendedEV, SuspendedEVSE, auto nie pobiera energii, restart ładowarki, zdalny reset, Reset OnIdle, Immediate, Soft reset, Hard reset, reset jednego EVSE, ChangeAvailability, odblokowanie złącza, kabel zablokowany, UnlockConnector, pobranie logów, GetLog, GetDiagnostics, eskalacja, incydent, KPI, uptime, dostępność sieci, AFIR dane dynamiczne"
---

# Charging Operations Expert — praca NOC i diagnoza

Skill prowadzi **operatora** od objawu do działania: co sprawdzić, w jakiej kolejności, jakim poleceniem, z jakim
ryzykiem dla trwających sesji. Taksonomia: D07.01–D07.03 (monitoring, diagnostyka, incydenty). Sieć: brak.

**Zasada źródeł.** Fakty z dokumentów OCA, EVRF i aktów UE (`sources/*.yaml`) mają znacznik `[dokument §]`.
Kolejność kroków i reguły operacyjne to **Wnioski** z tych faktów. Zachowania konkretnych modeli i firmware nie należą do
tego skilla (D21, `ev-evse-diagnostics-expert`), więc nie podajesz ich z pamięci.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/diagnostyka.md` | drzewo diagnozy: sesja nie startuje, RFID nie reaguje, brak poboru energii, roaming |
| `references/alarmy.md` | priorytety alarmów: severity 0–9, monitory, zdarzenia bezpieczeństwa, errorCode, KPI |
| `references/dzialania-zdalne.md` | skutki poleceń: Reset, ChangeAvailability, UnlockConnector, TriggerMessage, logi |

## Procedura
1. **Objaw i zakres.** Jedna stacja, jedno EVSE, lokalizacja czy wiele stacji naraz. Stacja własna (OCPP) czy partnera
   (OCPI). Przy wielu stacjach naraz najpierw sprawdź warstwę wspólną (CSMS, sieć, hub).
2. **Stan z danych, nie z założeń.**
   - łączność: ostatnia ramka i stan WebSocketu (Heartbeat nie jest jedynym dowodem `[16 §4.6]` `[201-P2 G02]`);
   - status złącza i `errorCode` / `vendorErrorCode`;
   - ostatnie komunikaty transakcji i autoryzacji;
   - po zerwaniu połączenia brak `BootNotification` jest normalny `[201-P4 §5.4]`. Świeży stan pobierasz
     `TriggerMessage` `[S16]` `[201-P2 F06]`.
3. **Diagnoza wg drzewa** (`references/diagnostyka.md`): od przyczyn najczęściej przewidzianych w specyfikacji
   (autoryzacja, brak kabla, ograniczenie mocy, stan niedostępności) do sprzętu.
4. **Działanie z najmniejszym skutkiem ubocznym.** Przed resetem sprawdź trwające transakcje na stacji. Reset 1.6 kończy
   transakcje `[16 §5.14]`. W 2.0.1 wybierz `OnIdle` albo reset jednego EVSE (`references/dzialania-zdalne.md`).
5. **Dowody do eskalacji.** Logi (`GetDiagnostics` / `GetLog`), surowe ramki, `errorCode` i `vendorErrorCode`, numer
   firmware z `BootNotification`. Eskalacja do serwisu, producenta albo partnera roamingowego.
6. **Zamknięcie.** Status wrócił do operacyjnego i potwierdza go `StatusNotification`. Wpis o przyczynie w bazie
   incydentów; obserwacje zachowań modelu trafiają do D21.

## Przykład
**Zgłoszenie:** „Stacja online, złącze `Available`, kierowca przykłada RFID i nic się nie dzieje (1.6J).”

1. Brak `Authorize.req` w logach → problem przed CSMS:
   - czytnik (`errorCode` `ReaderFailure`: „Failure with idTag reader”) `[16 §7.6]`;
   - albo autoryzacja lokalna bez zapytania do CSMS: `LocalPreAuthorize`, `LocalAuthorizeOffline`, cache `[16 §9.1]`.
2. Jest `Authorize.req`, odpowiedź inna niż `Accepted` → wynik z CSMS lub od eMSP:
   - `Blocked`, `Expired`, `Invalid` („Identifier is unknown”), `ConcurrentTx` („already involved in another
     transaction”) `[16 §7.2]`;
   - token roamingowy → reguły whitelist i real-time `[OCPI230 §12.1.3]`.
3. `Accepted`, ale brak `StartTransaction` → złącze w `Preparing` czeka na kabel do `ConnectionTimeOut` `[16 §9.1.6]`.
4. Jest `StartTransaction`, ale brak energii → `SuspendedEVSE` (np. ograniczenie smart charging lub mocy) albo
   `SuspendedEV` (pojazd nie pobiera) `[16 §7.7]`.
5. **Wniosek:** restart dopiero po tych krokach i tylko gdy na stacji nie ma innych trwających transakcji. Soft reset
   „SHALL stop ongoing transactions gracefully”, a hard reset nie musi ich kończyć łagodnie `[16 §5.14]`.

## Pułapki
- Restart jako pierwszy krok: przerywa sesje innych kierowców i kasuje stan do diagnozy (patrz wyżej).
- `EVCommunicationError` traktowany jak awaria: „not a real error in the sense that the Charge Point doesn’t need to go
  to the faulted state. Instead, it should go to the SuspendedEVSE state” `[16 §7.6]`.
- Stacja partnera ze statusem `UNKNOWN` to brak informacji (także offline), nie awaria `[OCPI230 §8.4.26]`. Działać może
  tylko CPO partnera.
- Szukanie wymogu uptime w AFIR: ani AFIR (wersja skonsolidowana), ani rozporządzenie 2025/655 nie zawierają wymogu
  uptime (przeszukane 2026-11-07). AFIR wymaga natomiast aktualizacji statusu operacyjnego najpóźniej minutę po zmianie
  `[AFIR-655 art. 2]`.
- `UNLOCK_CONNECTOR` z roamingu jest tylko dla operatora lub eMSP, nigdy bezpośrednio od kierowcy `[OCPI230 §13.4.3]`.

## Źródła
`sources/oca-ocpp.yaml` (16, 16E, S16, 201-P2, 201-P4, 201-CSV), `sources/evrf-ocpi.yaml` (OCPI230),
`sources/eu-afir.yaml` (AFIR, AFIR-655). Pobrane 2026-11-07.
