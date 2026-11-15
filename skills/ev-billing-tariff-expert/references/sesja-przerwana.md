# Przerwana sesja: od zdarzenia na stacji do rachunku

Zakres: co się dzieje, gdy ładowanie kończy się inaczej niż zwykłym zatrzymaniem przez kierowcę, i co z tego trafia do
wyceny, CDR i płatności. Plik łączy fakty z kilku warstw. Szczegóły komunikatów OCPP opisuje skill `ev-ocpp-expert`
(`komunikaty-16.md`, `komunikaty-201.md`, `wzorce.md`), a statusy złączy skill `ev-cpms-architect`.

Spis:
1. Scenariusze przerwania
2. Co dostaje wycena
3. Sesja i CDR w OCPI
4. Płatność ad hoc po przerwaniu (OCPP 2.1 i OCPI Payments)
5. Lista kontrolna przeglądu story i kodu
6. Czego źródła nie określają

## 1. Scenariusze przerwania
| Scenariusz | OCPP 1.6 | OCPP 2.0.1 / 2.1 |
|---|---|---|
| kabel odłączony od pojazdu | `StopTransactionOnEVSideDisconnect = true`: transakcja SHALL zostać zatrzymana, ponowne podłączenie wymaga nowej transakcji; `false`: transakcja trwa, po ponownym podłączeniu energia znów płynie, a złącze zostaje zablokowane do okazania identyfikatora `[16 §4.10]`. Stacja SHOULD wysłać `StatusNotification` `Finishing` (przy `true`) albo `SuspendedEV` (przy `false`) z „EV side disconnected” w `info` `[16 §4.9]` | koniec transakcji wyznacza `TxStopPoint` `[201-P2 §2.6.6]`; `TxCtrlr.StopTxOnEVSideDisconnect = true` → stacja SHALL zdeautoryzować transakcję `[201-CSV]`; powód `stoppedReason = EVDisconnected` `[201-P3]` |
| utrata zasilania albo restart stacji | powody `PowerLoss` („Complete loss of power”) i `Reboot` `[16 §7.36]`; wznowienia transakcji nie opisuje | 2.0.1: te same powody `[201-P3]`, wznowienia nie opisuje. 2.1: E17 — w ciągu `TxResumptionTimeout` transakcja SHALL zostać wznowiona `[21-P2 E17.FR.10]` i stacja wysyła `TransactionEvent(Updated)` z `triggerReason = TxResumed` (ta sama transakcja) `[21-P2 E17]`, po nim kończy się z `triggerReason = AbnormalCondition` i `stoppedReason = PowerLoss` albo `Reboot` `[21-P2 E17]` |
| utrata łączności stacja ↔ CSMS | ładowanie trwa; komunikaty transakcyjne MUST być kolejkowane i dostarczone chronologicznie `[16 §3.7]` | kolejka i ponawianie, po wyczerpaniu prób komunikat jest porzucany `[201-P2 E13]`; `offline = true` w zdarzeniu z czasu offline, kompletność po `seqNo` `[201-P2 E §1.3.2]` |
| pojazd przestaje pobierać energię | — | stan `SuspendedEV`: EVSE oferuje energię, pojazd jej nie pobiera `[201-P2 §3.16]`; czas bez ładowania trafia do `total_parking_time` w CDR `[OCPI230 §10.3.1]` |
| awaria lub zatrzymanie awaryjne | powód `EmergencyStop` `[16 §7.36]` | `stoppedReason` m.in. `EmergencyStop`, `GroundFault`, `OvercurrentFault`, `PowerQuality` `[201-P3]` |
| kierowca nie podłączył kabla na czas | — | `triggerReason = EVConnectTimeout` `[201-P2 §3.82]`; w 2.1 przy płatności ad hoc koszt 0 i anulowanie blokady `[21-P2 C20.FR.02]` |

**2.1, wznowienie po restarcie (E17):** stacja SHALL zapisać stan transakcji w pamięci trwałej (co najmniej `seqNo`,
`idToken`, `evse`, `transactionInfo`) `[21-P2 E17.FR.01]`. Licznik czasu startuje od wykrytego wyłączenia, a sposób
ustalenia chwili wyłączenia zależy od implementacji `[21-P2 E17.FR.02]`. Przy `TxAllowEnergyTransferResumption =
false` transakcja, która ładowała, wraca w stanie `SuspendedEVSE` albo `EVConnected` `[21-P2 E17.FR.12]`.

## 2. Co dostaje wycena
- Wartości z `SampledDataCtrlr.TxEndedMeasurands` są próbkowane co `TxEndedInterval` od startu transakcji i wysyłane
  tylko w `TransactionEvent(Ended)` `[201-P2 J §2.1]`. Odczyt końcowy ma kontekst `Transaction.End` („Value taken at end
  of transaction”) `[201-P2 §3.66]`.
- Komunikaty `MeterValues` nigdy nie przenoszą danych transakcji w 2.0.1 („Transaction related MeterValues are never
  transmitted in MeterValuesRequest”) `[201-P2 J §2.1]`.
- `step_size` liczy się raz na sesję z sumy zużycia `[OCPI230 §10.3.1]`. Przerwana sesja to zwykła sesja o krótszym
  zużyciu, bez osobnych reguł w OCPI.

**Wniosek:** przy przerwaniu offline rozliczasz dopiero po kompletnym ciągu `seqNo` albo oznaczasz sesję „dane
niepełne”. Przy transakcji porzuconej po limicie prób ostatni znany odczyt może nie być końcowy.

## 3. Sesja i CDR w OCPI
- Statusy sesji: `COMPLETED` (zakończona, bez dalszych zmian) i `INVALID` („declared invalid and will not be billed”)
  `[OCPI230 §9.4.3]`.
- CDR to „the only billing-relevant object”, wysyłany po zakończeniu sesji `[OCPI230 §10]`. Raz wysłanego nie wolno
  zmienić; korekta to Credit CDR z ujemnym `total_cost` i nowy CDR `[OCPI230 §10.1.1]`. Jak daleko wstecz, OCPI nie
  określa `[OCPI230 §10.1.1]`.
- CDR może powstać bez przesłanej energii, np. za samą rezerwację `[OCPI230 §9.1.4]`.

**Wniosek:** gdy dane z przerwanej sesji dotrą później (kolejka offline), nie wysyłasz CDR z niepełnych danych.
Wysłany zbyt wcześnie poprawisz już tylko przez Credit CDR.

## 4. Płatność ad hoc po przerwaniu (OCPP 2.1 i OCPI Payments)
Szczegóły i wymagania: `references/platnosc-ad-hoc.md`.
- Sesja bez kosztu (koniec przed energią, brak podłączenia na czas): koszt 0, zwolnienie blokady i
  `NotifySettlementRequest` ze `status = Canceled` `[21-P2 C20.FR.05]`.
- Sesja z kosztem: rozliczenie całkowitego kosztu po `Ended` `[21-P2 C21.FR.01]`. Odmowa albo błąd łączności przy
  rozliczeniu daje `Rejected` / `Failed` `[21-P2 C22.FR.01]` `[21-P2 C22.FR.02]`.

**OCPI 2.3.0, moduł Payments (terminal PTP w roamingu).** Sesję kończy pojazd albo stacja, `StopSession` od PTP po
osiągnięciu limitu preautoryzacji albo backend CPO `[OCPI230 §16.4]`. Potem CDR trafia do PTP, PTP pobiera kwotę u PSP
(capture), a gdy fakturę wystawia CPO, wysyła Financial Advice Confirmation z `capture_status_code` `[OCPI230 §16.4]`.

**Wniosek** (przypadki końca sesji z płatnością terminalem; reguły rozliczenia ustala CPO z PTP):
| Przypadek | Co wynika z faktów |
|---|---|
| sesja bez energii | CDR może powstać bez energii, np. za samą rezerwację `[OCPI230 §9.1.4]`; sesja `INVALID` nie jest rozliczana `[OCPI230 §9.4.3]`. Czy PTP robi wtedy capture zerowy, czy tylko zwalnia blokadę, OCPI nie określa |
| osiągnięty limit blokady | koszt nie powinien przekroczyć `preauthorize_amount`, bo PTP albo CPO zatrzymuje sesję przy limicie `[OCPI230 §16.4]` |
| capture nieudany albo częściowy | `FAILED` albo `PARTIAL_SUCCESS` `[OCPI230 §16.7.2]`; dalsza windykacja jest poza OCPI |
| brak CDR (stacja offline, dane z kolejki) | bez CDR nie ma kwoty do capture, więc blokada trwa. To trzyma środki kierowcy (PSD2 art. 75: `references/platnosc-ad-hoc.md` §7) |

## 5. Lista kontrolna przeglądu story i kodu
**Wniosek** (pytania wynikające z faktów powyżej):
1. Jaka jest wartość `StopTransactionOnEVSideDisconnect` / `TxStopPoint` i czy story zakłada to samo (koniec przy
   odłączeniu od pojazdu albo dalsze trwanie transakcji z zablokowanym złączem)?
2. Co robi system z transakcją bez `StopTransaction` / `Ended` po restarcie stacji (1.6, 2.0.1) i czy obsługuje
   `TxResumed` oraz koniec z `AbnormalCondition` (2.1)?
3. Czy rozliczenie czeka na komplet komunikatów z kolejki offline (`seqNo`) i czy obsługuje zdarzenia z
   `offline = true`?
4. Czy postój bez ładowania (`SuspendedEV`) jest wyceniany zgodnie z taryfą (`PARKING_TIME`) i pokazany kierowcy?
5. Czy sesja bez energii ma regułę: `INVALID` bez rachunku, CDR zerowy albo CDR z opłatą (np. rezerwacja)?
6. Przy płatności ad hoc: czy blokada jest zwalniana przy sesji bez kosztu i co się dzieje po `Failed`?

## 6. Czego źródła nie określają
- Czy kierowca płaci za przerwaną sesję i ile: to reguła biznesowa CPO i umowy z MSP, nie wymóg OCPI ani OCPP.
- Wznowienie transakcji po utracie zasilania w OCPP 1.6 i 2.0.1 (opisuje je dopiero OCPP 2.1 E17).
- Termin wysłania Credit CDR `[OCPI230 §10.1.1]`.
