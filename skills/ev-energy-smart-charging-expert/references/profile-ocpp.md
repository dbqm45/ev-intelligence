# Profile ładowania OCPP 1.6 i 2.0.1: cele, stos, harmonogram złożony, jednostki, offline

Źródła: OCPP 1.6 edition 2 `[16]` i errata `[16E]`, schematy JSON 1.6 `[S16]`, OCPP 2.0.1 Edition 4: część 2, blok K
`[201-P2 K]`, załączniki części 2 `[201-APP]`, CSV Device Model `[201-CSV]`, errata 2026-09 `[201-E]`. Zdania
**Wniosek** to rekomendacje wyprowadzone z cytowanych wymagań.

## Spis treści
1. Cele profili (purpose)
2. Rodzaje profili (kind) i pola harmonogramu
3. Stos profili (stackLevel): różnica 1.6 i 2.0.1
4. Harmonogram złożony (composite schedule)
5. Jednostki, fazy, przeliczenie W na A
6. Zakładanie, zmiana i usuwanie profili
7. Zachowanie offline i po restarcie
8. Konfiguracja możliwości stacji
9. Rozbieżności w dokumentach

## 1. Cele profili
| 1.6 `[16 §3.13.1]` | 2.0.1 `[201-P2 K §3.2]` | Znaczenie |
|---|---|---|
| `ChargePointMaxProfile` (tylko `connectorId` 0) | `ChargingStationMaxProfile` (tylko `evseId` 0) | limit całej stacji, wspólny dla wszystkich złączy / EVSE |
| `TxDefaultProfile` | `TxDefaultProfile` | domyślny dla nowych transakcji; na 0 dotyczy wszystkich złączy / EVSE |
| `TxProfile` (tylko `connectorId` > 0) | `TxProfile` (tylko `evseId` > 0, K01.FR.16) | dla bieżącej transakcji; zastępuje `TxDefaultProfile` |
| — | `ChargingStationExternalConstraints` | limit ustawiony przez system zewnętrzny (EMS, DSO, licznik), nie przez CSMS |

- `TxProfile` bez aktywnej transakcji: 1.6 SHALL odrzucić `[16 §3.13.1]`; 2.0.1 status `Rejected`, zalecany
  `reasonCode = TxNotFound` (K01.FR.09) `[201-P2 K01.FR.09]`.
- 2.0.1: CSMS SHALL podać `transactionId` przy `TxProfile` (K01.FR.03); nieznany `transactionId` → odrzucenie
  (K01.FR.33) `[201-P2 K01.FR.03]`.
- 2.0.1: CSMS i Local Controller SHALL NOT ustawiać `ChargingStationExternalConstraints` (K01.FR.22, K03.FR.08)
  `[201-P2 K01.FR.22]`. Errata 2026-09 dodaje wymaganie dla stacji: taki profil od CSMS SHALL odrzucić (`Rejected`,
  opcjonalnie `UnsupportedPurpose`) `[201-E]` (nowe K01.FR.62).
- 1.6 `TxDefaultProfile`: profil na złączu > 0 zastępuje profil ze złącza 0 tylko dla tego złącza `[16 §3.13.1]`.
  2.0.1: `TxDefaultProfile` na EVSE 0 jest stosowany, ale nie kopiowany, na wszystkie EVSE (K01.FR.14). Profil o tym
  samym `stackLevel` na EVSE 0 i na konkretnym EVSE z innym `id` → `Rejected`, `DuplicateProfile` (K01.FR.52–53)
  `[201-P2 K01.FR.14]`.

## 2. Rodzaje profili i pola harmonogramu
- `Absolute` (okresy od stałego punktu w czasie), `Recurring` (powtarzany od pierwszego okresu), `Relative` (od punktu
  zależnego od sytuacji, np. startu transakcji) `[16 §7.9]`.
- 2.0.1 doprecyzowuje:
  - `Absolute` i `Recurring` wymagają `startSchedule` (K01.FR.40);
  - `Relative` SHALL NOT mieć `startSchedule` (K01.FR.41) i zaleca się liczyć okresy od chwili gotowości do
    dostarczania energii, czyli po autoryzacji i podłączeniu (K01.FR.42);
  - `recurrencyKind` tylko przy `Recurring` (K01.FR.60);
  - `ChargingStationMaxProfile` SHALL NOT być `Relative` (K01.FR.38) `[201-P2 K01.FR.38]`.
- Pierwszy okres ma `startPeriod = 0`; okresy rosnąco (K01.FR.31, K01.FR.35). Okres trwa do startu następnego albo do
  końca `duration` (K01.FR.12). Okres zaczynający się po `duration` nie jest wykonywany (K01.FR.11) `[201-P2 K01.FR.12]`.
- `Recurring` z `duration` krótszym niż okres powtarzania: po `duration` stacja SHALL wrócić do zachowania domyślnego
  (K01.FR.13) `[201-P2 K01.FR.13]`.
- Ważność: `validFrom` włącznie, `validTo` wyłącznie (K01.FR.36–37); bez obu profil ważny bezterminowo, do zastąpienia
  (K01.FR.10) `[201-P2 K01.FR.10]`. `startSchedule` w przyszłości: limit działa od tej chwili (K01.FR.30).
- `minChargingRate`: minimalna efektywna moc lub prąd pojazdu; pomaga algorytmowi lokalnemu w podziale mocy
  `[16 §7.13]` `[201-P2 K01.FR.21]`.

## 3. Stos profili: różnica 1.6 i 2.0.1
- 1.6: w danej chwili obowiązuje profil o najwyższym `stackLevel` spośród **ważnych** według `validFrom`/`validTo`
  `[16 §3.13.2]`. Nie wolno mieć dwóch profili o tym samym `stackLevel` i celu; nowy taki profil zastępuje stary
  `[16 §3.13.2]`. Najwyższy profil bez `duration` sprawia, że niższe nigdy nie zostaną wykonane `[16E §3.7]`.
- 2.0.1: dla każdego celu wiodący jest harmonogram, który **ma okres zdefiniowany dla danej chwili** i należy do
  ważnego profilu o najwyższym `stackLevel` `[201-P2 K §3.5]`. Profil na EVSE 0 jest aktywny na wszystkich EVSE
  `[201-P2 K §3.4]`. CSMS SHALL NOT wysłać profilu z kombinacją `stackLevel` + cel + `evseId`, która już istnieje z
  innym `id` i nakładającą się ważnością (K01.FR.06); dla `TxProfile` kombinacja `stackLevel` + `transactionId`
  (K01.FR.39) `[201-P2 K01.FR.06]`. Profil o znanym `id` jest zastępowany (K01.FR.05).
- Wyjątek z zakresu: w 2.0.1 nie da się zdefiniować okresu „bez limitu”. Specyfikacja w przykładzie wyjątków (niedziela,
  święto) używa dowolnie wysokiej wartości 999999 `[201-P2 K §3.6.1]`.

**Wniosek:** algorytm wyboru profilu w CSMS (np. do symulacji) musi zależeć od wersji. W 2.0.1 profil wyższy, ale bez
okresu w danej chwili (np. tylko 17:00–20:00), nie przykrywa niższego poza tym oknem.

## 4. Harmonogram złożony
- Liczony jako **minimum** w każdym przedziale z wiodących profili różnych celów; przedziały mogą mieć różną długość
  `[16 §3.13.3]` `[201-P2 K §3.5]`.
- `TxProfile` zastępuje `TxDefaultProfile`: przy obu ważnych `TxDefaultProfile` nie wchodzi do minimum
  `[201-P2 K §3.5]` `[16 §3.13.1]`.
- Limit `ChargePointMaxProfile` / `ChargingStationMaxProfile` dotyczy **wszystkich złączy / EVSE łącznie**; w 2.0.1
  łącznie z zużyciem samej stacji (K04.FR.05) `[16 §3.13.3]` `[201-P2 K04.FR.05]`.
- Reguła bezpieczeństwa 2.0.1: wynik połączenia limitów zewnętrznych i profili z najwyższym `stackLevel` celów
  `ChargingStationMaxProfile`, `ChargingStationExternalConstraints` i `TxDefaultProfile` (lub `TxProfile`) SHALL być ≤
  najniższej wartości w łączonych harmonogramach (SC.01) `[201-P2 K §4]`.
- `GetCompositeSchedule`: stacja liczy przedziały od otrzymania żądania przez `duration` sekund (K08.FR.02). Dla
  `evseId` 0 → oczekiwany łączny pobór z sieci (K08.FR.03). Bez transakcji: liczy tak, jakby trwała transakcja z
  `TxDefaultProfile` (K08.FR.06). Raportuje oczekiwany, czyli najniższy limit, także gdy pojazd (ISO 15118) zapowiada
  mniejszy pobór (SC.04) `[201-P2 K08.FR.02]`. W 1.6 wynik jest orientacyjny, bo może się zmienić np. przy
  równoważeniu lokalnym `[16 §5.7]`.

## 5. Jednostki, fazy, przeliczenie W na A
- `W`: **łączna** moc. Dla AC prąd fazy = moc / (napięcie nominalne × `numberPhases`), napięcie nominalne obszaru
  (230 albo 110 V), nie zmierzone `[16 §7.12]` `[201-P2 K01.FR.50]`.
- `A`: prąd **na fazę**, nie suma faz `[16 §7.12]` `[201-P2 K01.FR.51]`. Dla AC wygodniejsze `A` (moc nie zależy wtedy
  od liczby faz), dla DC `W` `[16 §7.12]` `[201-P2 K01.FR.50]`.
- Brak `numberPhases` → przyjmuje się 3 `[16 §7.12]` `[201-P2 K01.FR.49]`. Regiony z siecią jednofazową powinny
  zawsze podawać `numberPhases = 1` `[201-P2 K01.FR.49]`.
- Liczba faz zależy od stacji, pojazdu i kabla; przełączanie faz w trakcie może uszkodzić niektóre pojazdy. Zdolność
  przełączania 3→1: 1.6 `ConnectorSwitch3to1PhaseSupported` `[16 §3.13.7]`, 2.0.1 `Phases3to1` `[201-P2 K §3.6]`.
- 1.6: przy `numberPhases` większym niż możliwe stacja SHALL użyć `limit` tak jak podany, bez przeliczania `[16E §3.34]`.
  2.0.1: AC, gdy stacja nie może zagwarantować nie więcej niż `numberPhases` faz → `Rejected` (K01.FR.43); może też
  przyjąć i ograniczyć do mniejszej liczby faz (K01.FR.45); DC → może przyjąć i zignorować pola faz (K01.FR.44)
  `[201-P2 K01.FR.43]`.
- `phaseToUse` (2.0.1) tylko przy `numberPhases = 1` i `ACPhaseSwitchingSupported = true` (K01.FR.19–20); konflikt
  `phaseToUse` między profilami → odrzucenie, a dla `numberPhases` bierze się najniższą wartość `[201-P2 K §3.7]`.
- 1.6 schemat: `limit` to liczba z krokiem 0,1 (`multipleOf: 0.1`) `[S16]`.

Przykład obliczenia, **Wniosek** z K01.FR.49–50: 11000 W, AC, bez `numberPhases` → 3 fazy, 11000 / (230 × 3) ≈ 15,9 A
na fazę. Ten sam profil przy aucie ładującym jedną fazą da tylko około 3,7 kW (15,9 A × 230 V), stąd zalecenie `A`
dla AC.

## 6. Zakładanie, zmiana i usuwanie
- Kiedy CSMS wysyła profil: przy starcie transakcji, w zdalnym starcie, w trakcie transakcji, poza transakcją (domyślne,
  limity stacji) `[16 §5.16]` `[201-P2 K §3.1]`.
- Zdalny start z profilem: cel zawsze `TxProfile` `[16 §5.16.2]` `[201-P2 K05.FR.02]`; w 1.6 bez `transactionId`
  `[16E §3.41]`. 2.0.1: stacja bez smart charging ignoruje profil (K05.FR.04), a stacja z obsługą przy błędnym
  profilu odrzuca polecenie (K05.FR.05) `[201-P2 K05.FR.04]`.
- 1.6: przed wysłaniem profilu po `StartTransaction` zaleca się sprawdzić `timestamp`, bo komunikat mógł czekać w
  kolejce offline `[16 §5.16.1]`.
- Nowy lub zmieniony `TxDefaultProfile` w trakcie transakcji: transakcja trwa i przełącza się na nowy profil
  `[16E §3.8]` `[201-P2 K01.FR.32]`. Usunięty `TxDefaultProfile`: transakcja trwa jak bez niego `[16E §3.8]`
  `[201-P2 K10.FR.07]`.
- Usuwanie: 1.6 bez pól → wszystkie profile; z polami → wszystkie pasujące (AND); `id` wyklucza inne pola `[16E §3.26]`.
  2.0.1: `id` albo co najmniej jedno z pól `stackLevel`, `evseId`, cel (K10.FR.02); profile
  `ChargingStationExternalConstraints` są pomijane, a gdy pasują tylko one → `Unknown` (K10.FR.08–09); po usunięciu
  stacja przelicza harmonogram (K10.FR.05) `[201-P2 K10.FR.02]`.
- Błędy 1.6: niepoprawna wartość enumeracji (np. `chargingRateUnit`) albo `connectorId` → CALLERROR
  `PropertyConstraintViolation`; stacja bez smart charging → `NotSupported` `[16E §3.38]` `[16E §3.39]`.
  2.0.1: brak obsługi → `NotSupported` albo `NotImplemented` (K01.FR.29) `[201-P2 K01.FR.29]`.

## 7. Offline i restart
- Profile z `SetChargingProfile` SHALL przetrwać restart i zanik zasilania `[16E §3.37]` `[201-P2 K01.FR.27]`.
- Offline po otrzymaniu `TxProfile`: stacja używa go do końca transakcji (w 2.0.1 albo do jego wygaśnięcia, co nastąpi
  wcześniej) `[16 §3.13.6]` `[201-P2 K06.FR.01]`.
- Offline przed transakcją albo przed `TxProfile`: stacja używa dostępnych profili (`ChargePointMaxProfile` /
  `ChargingStationMaxProfile`, `TxDefaultProfile`) `[16 §3.13.6]` `[201-P2 K07.FR.01]`.
- **Offline bez żadnych profili: transakcja bez ograniczeń** `[16 §3.13.6]` `[201-P2 K06.FR.02]`.
- 2.0.1: gdy `TxProfile` wygaśnie przed końcem transakcji, stacja wraca do najniższego z `TxDefaultProfile` i
  `ChargingStationMaxProfile`, a bez nich do własnego limitu lokalnego (K02.FR.08) `[201-P2 K02.FR.08]`.

**Wniosek:** przy sterowaniu centralnym ograniczenie przyłącza ustawiasz także jako trwały profil stacji
(`ChargingStationMaxProfile`, limit wszystkich EVSE łącznie), a nie tylko jako `TxProfile` per transakcja. Inaczej
stacja, która straci łączność przed startem transakcji, ładuje bez limitu. `TxDefaultProfile` na EVSE 0 obowiązuje
każde EVSE osobno (K01.FR.14), więc nie zastępuje limitu stacji.

## 8. Konfiguracja możliwości stacji
- 1.6 (wymagane dla stacji ze smart charging, odczyt przez `GetConfiguration`) `[16 §3.13.5]` `[16 §9.4]`:
  `ChargeProfileMaxStackLevel`, `ChargingScheduleAllowedChargingRateUnit` (`Current`, `Power`),
  `ChargingScheduleMaxPeriods`, `MaxChargingProfilesInstalled`; opcjonalnie `ConnectorSwitch3to1PhaseSupported`.
- 2.0.1 `SmartChargingCtrlr` `[201-APP §3.1.16]`: `Enabled`, `Available`, `ACPhaseSwitchingSupported`,
  `ProfileStackLevel` (np. 1 → najwyżej 2 profile na cel i EVSE), `RateUnit` (`A`, `W`), `PeriodsPerSchedule`,
  `ExternalControlSignalsEnabled`, `NotifyChargingLimitWithSchedules`, `Phases3to1`, `Entries` (z `maxLimit`),
  `LimitChangeSignificance` (zalecana niska wartość).

## 9. Rozbieżności w dokumentach
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| pole jednostki i typ `limit` w 1.6 | diagram klas: `schedulingUnit`, `limit: int` `[16 §7.8]` (rysunek 42) | tabela pól `chargingRateUnit`, `limit` decimal `[16 §7.13–7.14]`; schemat: `chargingRateUnit`, `number` z `multipleOf 0.1` `[S16]` | schemat i tabela |
| brzmienie `GetCompositeSchedule` 1.6 | errata 3.28: „from the moment the request PDU is received: Time X, up to X + Duration” `[16E §3.28]` | errata 3.29 (dodana w v4.0) zastępuje je: „from the moment of message receipt up to the Duration (in seconds)” `[16E §3.29]` | nowsza errata 3.29; to samo brzmienie co K08.FR.02 w 2.0.1 |
| nazwy zmiennych 2.0.1 | wymagania: `ChargingScheduleChargingRateUnit` (K01.FR.26, K08.FR.07), `EnableNotifyChargingLimitWithSchedules` (K11.FR.03) `[201-P2 K01.FR.26]` | załącznik i CSV: `SmartChargingCtrlr.RateUnit`, `NotifyChargingLimitWithSchedules` `[201-APP §3.1.16]` `[201-CSV]` | **Wniosek:** w implementacji nazwy z załącznika i CSV (Device Model); w wymaganiach to opisowe nazwy tych samych zmiennych |
| typ `LimitChangeSignificance` | załącznik: `integer` `[201-APP §3.1.16]` | CSV v1.5: `decimal` `[201-CSV]` | nierozstrzygnięte w sprawdzonych dokumentach; CSV v1.5 obejmuje też zmienne OCPP 2.1 |
| przykład stosu w 2.0.1 | okno 17:00–20:00 z `"duration": 1080` `[201-P2 K §3.6.1]` | 3 h = 10800 s | **Wniosek:** literówka w przykładzie; w implementacji 10800 |
| pierwsze pole okresu 1.6 | „The startSchedule of the first ChargingSchedulePeriod SHALL always be 0” `[16 §7.13]` | `ChargingSchedulePeriod` ma `startPeriod`, nie `startSchedule` `[16 §7.14]`; 2.0.1: „startPeriod of the first chargingSchedulePeriod … SHALL always be 0” (K01.FR.31) | chodzi o `startPeriod` |
