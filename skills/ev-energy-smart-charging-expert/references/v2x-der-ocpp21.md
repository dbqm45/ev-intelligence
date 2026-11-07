# OCPP 2.1: przepływ dwukierunkowy (V2X, blok Q) i sterowanie DER (blok R)

Źródła: OCPP 2.1 Edition 2: część 2 `[21-P2]` (blok K: wymagania 2.1, blok Q, blok R, rozdz. 2.17 Device Model),
załączniki `[21-APP]`, errata 2026-09 `[21-E]`, część 0 `[21-P0]`. Wymagania z errat mają w nawiasie ich numer
sekcji erraty. Zdania **Wniosek** to rekomendacje.

## Spis treści
1. Zakres i pojęcia
2. Setpoint, limit, dischargeLimit
3. Tryby pracy (operationMode)
4. Reguły ogólne V2X (V2X.01–V2X.12)
5. Autoryzacja V2X i start sesji (Q01–Q02)
6. Sterowanie centralne i profile dynamiczne (Q03–Q04, Q07)
7. Sterowanie zewnętrzne, EMS (Q05–Q06)
8. Wsparcie częstotliwości lokalne: FCR i aFRR (Q08)
9. Lokalne równoważenie z budynkiem (Q09, po erratach)
10. Bezczynność (Q10)
11. Offline i powrót online (Q11–Q12, K01.FR.101–104)
12. DER: stacja jako rozproszone źródło (blok R)
13. Device Model
14. Rozbieżności i errata
15. Czego baza nie obejmuje

## 1. Zakres i pojęcia `[21-P2 Q §1]`
- Blok Q opisuje komunikację stacja–CSMS dla ładowania dwukierunkowego, gdy pojazd komunikuje się przez **CHAdeMO albo
  ISO 15118-20**.
- V2X obejmuje V2G (sieć), V2H (dom), V2B (budynek) i V2L (urządzenie). V2L nie wymaga OCPP, a V2H i V2B to
  szczególne przypadki V2G.
- Specyfikacja nie używa skrótu V2G w znaczeniu „pojazd–sieć”, bo w ISO 15118 oznacza on komunikację pojazd–stacja.
- Ładowanie dwukierunkowe rozszerza smart charging z bloku K; wszystkie wymagania bloku K obowiązują też dla V2X
  (V2X.01) `[21-P2 Q §2.5]`.

## 2. Setpoint, limit, dischargeLimit `[21-P2 Q §2.1]`
W okresie harmonogramu (`ChargingSchedulePeriodType`), w jednostce `chargingRateUnit` (W albo A):
- `setpoint`: wartość docelowa; dodatnia oznacza ładowanie, ujemna rozładowanie. Pojazd ma się do niej stosować jak
  najdokładniej (V2X.02);
- `limit`: maksymalne ładowanie, tylko wartości dodatnie;
- `dischargeLimit`: maksymalne rozładowanie, tylko wartości ujemne.

Reguły `[21-P2 Q §2.5]`:
- V2X.03: dodatni `setpoint` stacja ogranicza do `limit` (np. setpoint 2000 W, limit 1000 W → do pojazdu 1000 W);
- V2X.04: ujemny `setpoint` ogranicza do `dischargeLimit` (−2000 W przy −1000 W → −1000 W);
- V2X.05: `setpoint` poza zakresem od `dischargeLimit` do `limit` → `Rejected`, `InvalidSchedule`;
- V2X.06–V2X.10: warianty `_L2` i `_L3` dla poszczególnych faz tylko razem z polem bez przyrostka. CSMS ich nie podaje,
  gdy pojazd nie zgłosił danych dla faz L2/L3, ani w profilach innych niż `TxProfile`. Inaczej stacja odpowiada
  `Rejected`, `PhaseConflict`.

## 3. Tryby pracy `[21-P2 Q §2.2]`
`operationMode` jest ustawiany w okresie harmonogramu, więc różne okresy mogą mieć różne tryby. Zmiana trybu niezaplanowana
z góry wymaga nowego profilu `[21-P2 Q §2.3]`.

| Tryb | Kto ustala | `limit` | `dischargeLimit` | `setpoint` |
|---|---|---|---|---|
| `ChargingOnly` (domyślny, gdy brak pola) | CSMS | wymagany | — | — |
| `CentralSetpoint` | CSMS | opcja | opcja | wymagany |
| `CentralFrequency` | CSMS na podstawie częstotliwości | opcja | opcja | wymagany |
| `LocalFrequency` | stacja z krzywych częstotliwość–moc | — | — | liczony z krzywych |
| `ExternalSetpoint` | system zewnętrzny, np. EMS | opcja | opcja | z zewnątrz |
| `ExternalLimits` | system zewnętrzny | z zewnątrz | z zewnątrz | — |
| `LocalLoadBalancing` | stacja z pomiaru przyłącza | opcja (po erracie) | opcja (po erracie) | liczony z obciążenia |
| `Idle` | CSMS | — | — | — |

Tabela według erraty 2026-06 `[21-E §2.19]`, która dopuściła limity w `LocalLoadBalancing`. Pierwotna tabela w
`[21-P2 Q §2.2]` ich nie przewidywała.

- Dla `ChargingOnly` CSMS SHALL NOT wysyłać `dischargeLimit`, `setpoint` ani `setpointReactive` (Q02.FR.02)
  `[21-P2 Q02.FR.02]`.
- Miara `Power.Active.Residual`: odchyłka mocy zmierzonej od `setpoint`. Wartość dodatnia oznacza moc wyższą od
  zadanej, ujemna niższą `[21-P2 Q §2.4]`.

## 4. Reguły ogólne V2X `[21-P2 Q §2.5]` `[21-E §2.20]`
- V2X.01–V2X.10 jak w sekcji 2.
- V2X.11 (errata 2026-09): gdy w sesji dwukierunkowej ISO 15118-20 stacja wróci do sygnału Mode 3 PWM, a okres ma tryb
  inny niż `ChargingOnly`, stacja SHALL ustawić `dischargeLimit` i `setpoint` na 0, bo Mode 3 nie obsługuje
  rozładowania. V2X.12: stacja SHALL zgłosić to przez `NotifyEvent` dla `V2XChargingCtrlr`, zmienna `Problem` = true.

## 5. Autoryzacja V2X i start sesji
- Q01: stacja wysyła `Authorize` z EVCCID pojazdu. CSMS zwraca listę dozwolonych sposobów przesyłu energii
  `allowedEnergyTransfer` (Q01.FR.01), a stacja zgłasza wybrany sposób w `NotifyEVChargingNeedsRequest` razem z
  parametrami V2X (Q01.FR.03). Potem CSMS wysyła profil z trybem innym niż `ChargingOnly` `[21-P2 Q01]`.
- Errata 2026-09 zmienia Q01.FR.02: przy autoryzacji zewnętrznej (EIM) transakcja może się zacząć przed komunikacją ISO
  15118. EVCCID trafia więc do pierwszego `TransactionEvent` po jego otrzymaniu od pojazdu, a nie koniecznie do
  `Started` `[21-E §2.21]`.
- Odrzucony sposób przesyłu: CSMS odpowiada `Rejected` (Q01.FR.04). Stacja renegocjuje usługę z pojazdem (Q01.FR.05)
  albo kończy transakcję ze `stoppedReason = ReqEnergyTransferRejected` (Q01.FR.06) `[21-P2 Q01.FR.06]`.
- CSMS, który nie zdąży ustalić listy (np. potrzebna zgoda strony trzeciej), pomija ją w odpowiedzi (Q01.FR.08). Sesja
  startuje wtedy jako zwykłe ładowanie (Q02). Późniejszą zmianę dozwolonych sposobów CSMS zgłasza przez
  `NotifyAllowedEnergyTransferRequest`, a stacja renegocjuje usługę ISO 15118 (Q02.FR.05–07) `[21-P2 Q02.FR.05]`.
- Stacja SHALL obsługiwać co najmniej tryby `ChargingOnly`, `CentralSetpoint` i `CentralFrequency` (Q01.FR.31)
  `[21-P2 Q01.FR.31]`.

## 6. Sterowanie centralne i profile dynamiczne
- Q03: CSMS podaje `setpoint` w okresach z trybem `CentralSetpoint` (Q03.FR.01–02); może dodać `limit` i
  `dischargeLimit`, żeby ograniczyć zakres i przeregulowanie (Q03.FR.03) `[21-P2 Q03.FR.03]`.
- Q04, profil dynamiczny: `TxProfile` albo `TxDefaultProfile` z `chargingProfileKind = Dynamic` i jednym okresem.
  CSMS zmienia `setpoint` przez `UpdateDynamicScheduleRequest`. Druga możliwość: stacja co `dynUpdateInterval` pyta
  `PullDynamicScheduleUpdateRequest`. Gdy jest `duration`, a aktualizacja nie przyjdzie w tym czasie, harmonogram się
  kończy i stacja przechodzi do następnego ważnego profilu. Profil dynamiczny nie wymaga trybu dynamicznego ISO 15118-20
  `[21-P2 Q04]`.
- Q07, `CentralFrequency`: profil `Dynamic` z jednym okresem, bez `limit` i `dischargeLimit` (Q07.FR.02–03). CSMS
  zaleca się ustawić `duration`, żeby profil nie działał bez końca, gdy aktualizacje przestaną przychodzić (Q07.FR.04)
  `[21-P2 Q07.FR.04]`. Tryb ten służy np. do sytuacji, gdy kosztowny, skalibrowany pomiar częstotliwości nie może być w
  każdej stacji `[21-P2 Q §2.2]`.

## 7. Sterowanie zewnętrzne (EMS)
- Q05: CSMS pozwala na sterowanie zewnętrzne przez okres z trybem `ExternalSetpoint` albo `ExternalLimits` w swoim
  profilu (`TxProfile` lub `TxDefaultProfile`). Tylko w tym okresie wartości pochodzą z systemu zewnętrznego
  (Q05.FR.01–02). Przy profilu `Dynamic` i ustawionym `duration` brak aktualizacji przez `duration` od `dynUpdateTime`
  unieważnia profil, a nowa aktualizacja przywraca jego ważność (Q05.FR.07–08) `[21-P2 Q05.FR.07]`.
- Q06: system zewnętrzny wysyła limity albo setpointy bezpośrednio do stacji. Stacja zapisuje je jako profil
  `ChargingStationExternalConstraints`: harmonogram jako `Absolute`, pojedynczą wartość jako `Dynamic` (Q06.FR.01–04).
  Zgłasza je do CSMS przez `NotifyChargingLimitRequest` z `chargingLimitSource = EMS` (Q06.FR.10–11) `[21-P2 Q06.FR.10]`.
- Gdy `SmartChargingCtrlr.ExternalConstraintsProfileDisallowed = true`, stacja SHALL odrzucić takie ustawienia
  (Q06.FR.08) `[21-P2 Q06.FR.08]`.
- Konflikt setpointów zewnętrznego i z CSMS rozstrzyga `SmartChargingCtrlr.SetpointPriority`:
  - `ExternalControl` albo brak zmiennej: wygrywa zewnętrzny (Q06.FR.21);
  - `CSMS`: wygrywa `TxProfile` albo `TxDefaultProfile` (Q06.FR.22) `[21-P2 Q06.FR.20]`.
- Na `evseId = 0`: `ExternalLimits` ogranicza łączną moc czynną stacji (Q06.FR.30); `ExternalSetpoint` oznacza próbę
  dopasowania łącznej mocy stacji (Q06.FR.31) `[21-P2 Q06.FR.30]`.

**Wniosek:** w trybie V2X system zewnętrzny steruje stacją tylko w zakresie i czasie, na które pozwala CSMS (Q05),
albo przez profil zewnętrzny, który CSMS może zablokować zmienną `ExternalConstraintsProfileDisallowed` (Q06.FR.08).
W umowie z właścicielem EMS ustalasz, który mechanizm obowiązuje i jaki jest `SetpointPriority`.

## 8. Wsparcie częstotliwości lokalne (Q08)
- Opis OCA `[21-P2 Q §2.2]`:
  - FCR (rezerwa utrzymania częstotliwości) działa automatycznie w ciągu sekund;
  - aFRR (automatyczna rezerwa odbudowy częstotliwości) zastępuje FCR po 30 s i ma być w pełni dostępna w 15 minut.
    Jej sygnał idzie od OSP do CSO, a dalej do stacji przez `AFRRSignalRequest`.
  
  Parametry produktów bilansujących zależą od operatora systemu i nie są tu opracowane.
- `LocalFrequency` wymaga `chargingRateUnit = W` (Q08.FR.05), nie ma pól `limit`, `dischargeLimit`, `setpoint`,
  `setpointReactive` (Q08.FR.01). Ma krzywą `v2xFreqWattCurve` (co najmniej 2 punkty) i `v2xBaseline`, a opcjonalnie
  `v2xSignalWattCurve` dla aFRR (Q08.FR.02). Brak krzywej lub linii bazowej → `Rejected`, `NoFreqWattCurve` (Q08.FR.03)
  `[21-P2 Q08.FR.02]`.
- Setpoint = `v2xBaseline` + moc z krzywej, interpolowana dla zmierzonej częstotliwości. Przeliczenie następuje przy
  zmianie częstotliwości co najmniej o `V2XChargingCtrlr.LocalFrequencyUpdateThreshold` (Q08.FR.06–07). Sygnał aFRR
  dodaje deltę do tego setpointu (Q08.FR.10) `[21-P2 Q08.FR.06]`.

## 9. Lokalne równoważenie z budynkiem (Q09, po erratach)
- Stacja SHALL stale czytać moc z licznika na przyłączu (Q09.FR.03) `[21-P2 Q09.FR.03]`.
- Errata 2026-02 zmienia Q09.FR.04: stacja SHALL ustalić setpoint tak, żeby moc na liczniku w stanie ustalonym była
  między `LowerThreshold + LowerOffset` a `UpperThreshold + UpperOffset`. Algorytm z części 2 jest teraz tylko
  przykładem `[21-E §2.24]`.
- Zmienne: instancje `V2XChargingCtrlr.LocalLoadBalancing` (`UpperThreshold`, `LowerThreshold`, `UpperOffset`,
  `LowerOffset`) `[21-E §2.22]`. Q09.FR.02 po erracie: brak ustawień albo `UpperThreshold` ≤ `LowerThreshold` przy
  `AutoThresholds` = false lub nieustawionym → `Rejected`, `MissingDevModelInfo` `[21-E §2.24]`.
- Nowe Q09.FR.06: przy `AutoThresholds = true` stacja ustawia progi z minimalnej mocy ładowania i rozładowania pojazdu
  (z `NotifyEVChargingNeedsRequest`), a offsety na wartości przeciwne. Moc na przyłączu jest wtedy regulowana do 0 W
  `[21-E §2.24]`.
- Ograniczenie z erraty: przypadek działa dla jednej stacji, a wielu EVSE tylko wtedy, gdy stacja łączy ich setpointy.
  Równoważenie kilku stacji koordynuje CSMS albo Local Controller w trybie `CentralSetpoint` `[21-E §2.22]`.
- Setpoint jest zawsze ograniczony przez `limit` (dodatni) i `dischargeLimit` (ujemny) (Q09.FR.05) `[21-P2 Q09.FR.05]`.

## 10. Bezczynność (Q10)
- `Idle`: pojazd ma zużywać jak najmniej energii. Pole `preconditioningRequest` rozróżnia uśpienie i czuwanie (w
  czuwaniu pojazd szybko reaguje na nowy harmonogram) `[21-P2 Q §2.2]`.
- Okres `Idle` nie ma pól mocy; inaczej `Rejected`, `InvalidSchedule` (Q10.FR.01–02). Przy `evseSleep = true` i
  `SupportsEvseSleep = true` stacja wyłącza elektronikę danej transakcji do zdarzenia, które wymaga jej włączenia, i
  zgłasza `evseSleep = true` (Q10.FR.03–04) `[21-P2 Q10.FR.03]`.

## 11. Offline i powrót online
- `maxOfflineDuration` w profilu: gdy stacja jest offline dłużej, profil jest nieważny, a stacja używa niższego ważnego
  profilu (K01.FR.101). Po powrocie online profile znów mogą być ważne, chyba że mają `invalidAfterOfflineDuration =
  true` (K01.FR.102). Brak `maxOfflineDuration` → offline nie unieważnia profilu (K01.FR.103) `[21-P2 K01.FR.101]`.
- Q11: czas liczy się od wykrycia utraty łączności przez stację (zwykle do 30 s). CSMS nie powinien zgadywać dokładnej
  chwili przejścia na niższy profil. **Bez profilu zapasowego ładowanie trwa w trybie „charging only” bez limitów**
  `[21-P2 Q11]`.
- Q12: po powrocie online stacja ocenia profile od nowa. Z `invalidAfterOfflineDuration = false` wraca do profilu V2X,
  z `true` zostaje na profilu zapasowym `[21-P2 Q12]`.

**Wniosek:** sesję V2X budujesz z dwóch profili: wyższego (np. `CentralSetpoint`) z `maxOfflineDuration` i niższego
`ChargingOnly` z bezpiecznym limitem. Bez profilu zapasowego utrata łączności oznacza ładowanie bez limitu.
`invalidAfterOfflineDuration = true` ustawiasz, gdy po przerwie CSMS ma najpierw przeliczyć sterowanie (np. przy
usługach bilansujących).

## 12. DER: stacja jako rozproszone źródło (blok R)
- Sieć traktuje stację, która ładuje i rozładowuje, jako DER, który musi spełniać lokalne kodeksy sieciowe (reakcja na
  odchyłki częstotliwości i napięcia). Kodeks może dotyczyć też stacji tylko ładujących (np. wsparcie częstotliwości)
  `[21-P2 R §1]`.
- DC: falownik AC-DC jest w stacji, więc to ona jest DER. AC: falownik jest w pojeździe. Według OCA w chwili
  publikacji nie było regulacji rejestracji pojazdów AC z oddawaniem energii `[21-P2 R §1]` `[21-P2 R §2.2]`.
- OCPP zakłada, że **CSO działa jako agregator**: operator sieci łączy się z CSMS (np. IEC 61850, IEEE 2030.5, DNP3,
  Modbus), a CSMS planuje i wysyła komunikaty do stacji. Komunikaty OCPP nie są odpowiednikami jeden do jednego
  komunikatów IEC 61850 ani IEEE 2030.5 `[21-P2 R §2.1]`.
- Moc czynna i bierna (setpointy, limity) to zwykłe profile ładowania. Pozostałe nastawy wysyła `SetDERControlRequest`
  (z czasem startu i trwania), a odczytuje `GetDERControlRequest`. Nastawy obejmują krzywe wyłączenia napięciowego i
  częstotliwościowego, parametry ponownego załączenia, moc bierną, krzywe mocy czynnej i statyzm częstotliwościowy
  `[21-P2 R §2.7]`.
- Odchylenie od normalnej pracy z powodu krzywej DER stacja zgłasza `NotifyDERAlarmRequest`, a koniec zdarzenia ten sam
  komunikat z flagą zakończenia `[21-P2 R §2.8]`.
- Priorytety `[21-P2 R §2.9]`:
  - nastawy domyślne obowiązują, gdy nie działa nastawa zaplanowana tego samego typu;
  - z kilku nastaw jednego typu wygrywa najniższa wartość `priority` (0 = najwyższy);
  - nowa nastawa o wyższym priorytecie od razu wypiera nierozpoczęte, a już działającą dopiero od swojego startu (R04).
- Nastawy DER SHALL być trwałe po restarcie (R01.FR.03). Stacja DC z V2X wystawia dane znamionowe falownika w
  `DCDERCtrlr` dla każdego EVSE (R01.FR.01) `[21-P2 R01.FR.03]`.
- Errata 2026-09: R04.FR.01 (`NotSupported` dla nieobsługiwanego typu nastawy) dotyczy tylko EVSE DC. Stacja AC w
  zasadzie obsługuje każdą nastawę, bo przekazuje pojazdowi te, których sama nie wykona `[21-E §2.26]`.
- Errata 2026-06: `PowerMonitoringMustTrip` nie jest samodzielną nastawą DER, tylko częścią `LimitMaxDischarge`
  `[21-E §2.30]`.
- Architektura falownika (DC, AC z falownikiem w pojeździe, podział między pojazd i stację) nie ma znaczenia dla CSMS:
  CSMS wysyła nastawy do stacji `[21-P2 R §2.5]`.

## 13. Device Model
- `V2XChargingCtrlr.SupportedOperationModes`: obsługiwane tryby (Q01.FR.30). Rozdz. 2.17.3 nazywa tę zmienną
  odwołaniowo „V2XSupportedOperationModes” `[21-P2 Q01.FR.30]`. `V2XChargingCtrlr.SupportedEnergyTransferModes`:
  obsługiwane sposoby przesyłu (Q01.FR.32) `[21-APP]`.
- `SmartChargingCtrlr.SupportsDynamicProfiles`, `SupportsMaxOfflineDuration`, `SupportsEvseSleep`, `SupportsLimitAtSoC`,
  `SupportedAdditionalPurposes` (cele dodane w 2.1) `[21-APP]`.
- Komponent `ConnectedEV` z co najmniej `Available`, `VehicleId`, `VehicleCertificate`, `ProtocolAgreed`,
  `ProtocolSupportedByEV` (Q01.FR.36) `[21-P2 Q01.FR.36]`.

## 14. Rozbieżności i errata
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| oznaczenia przypadków DER | część 0: „R DER Control” z U01–U05 `[21-P0 rozdz. 2]` | część 2: R01–R05 `[21-P2 R01]` | część 2 (normatywna): R01–R05 |
| nazwa zmiennej trybów | Q01.FR.30: `V2XChargingCtrlr SupportedOperationModes`; Q07.FR.01, Q09.FR.01: „V2XSupportedOperationModes” `[21-P2 Q07.FR.01]` | rozdz. 2.17.3: odwołanie `V2XSupportedOperationModes` = komponent `V2XChargingCtrlr`, zmienna `SupportedOperationModes` `[21-P2 §2.17.3]` | ta sama zmienna; w Device Model `V2XChargingCtrlr.SupportedOperationModes` |
| odwołanie w Q05.FR.07 | warunek „( Q05.FR.03 OR Q03.FR.04 )” `[21-P2 Q05.FR.07]` | Q03 ma tylko FR.01–03 `[21-P2 Q03.FR.03]` | **Wniosek:** prawdopodobnie Q05.FR.04 (zmiana limitów przez system zewnętrzny); errata 2026-09 tego nie poprawia |
| setpoint w `LocalFrequency` | wstęp: „setpoint = get power from P/F table (Frequency)” `[21-P2 Q §2.2]` | Q08.FR.06: `v2xBaseline` + moc z krzywej `[21-P2 Q08.FR.06]` | wymaganie Q08.FR.06 |
| algorytm Q09 | Q09.FR.04 w części 2: obowiązkowy wzór z `DeltaSetpoint` `[21-P2 Q09.FR.04]` | errata 2026-02: wymóg stanu ustalonego, wzór jako przykład `[21-E §2.24]` | errata |
| przykładowy algorytm w erracie Q09 | „setpoint aktualizowany przez dodanie korekty do poprzedniego” `[21-E §2.22]` | w gałęzi „w granicach” przykład podaje `Setpoint_new = 0` `[21-E §2.23]` | **Wniosek:** przykład jest niespójny; normatywny jest tylko stan ustalony z Q09.FR.04 |
| limity w `LocalLoadBalancing` | tabela w części 2: brak `limit` / `dischargeLimit` `[21-P2 Q §2.2]` | errata 2026-06: opcjonalne `[21-E §2.19]`; Q09.FR.05 i tak je stosuje | errata |

## 15. Czego baza nie obejmuje
- ISO 15118-20 (z Amendment 1, usługa AC_BPT_DER), CHAdeMO, IEC 61851: normy płatne lub niezarejestrowane. Parametry
  komunikacji z pojazdem nie są opracowane.
- IEEE 1547, IEEE 2030.5, IEC 61850, UL 1741, SAE J3072, VDE-AR-N 4105 i kodeksy sieciowe: OCPP tylko je przywołuje
  `[21-P2 R §1]` `[21-P2 R §2.1]`. Wymagania przyłączeniowe dla V2G w PL i UE nie są opracowane.
- Pełne listy pól komunikatów 2.1 (np. `SetDERControlRequest`, `NotifyEVChargingNeedsRequest`) oraz bloki K18–K29 nie są
  rozpisane. W razie potrzeby sprawdź w `[21-P2]` i schematach `[21-P3]`.
