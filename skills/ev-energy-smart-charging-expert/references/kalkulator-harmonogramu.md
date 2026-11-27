# Kalkulator harmonogramu złożonego OCPP (`scripts/composite_schedule.py`)

Źródła: OCPP 1.6 edition 2 `[16]` i errata `[16E]`, OCPP 2.0.1 Edition 4 część 2 `[201-P2]` z erratą 2026-09
`[201-E]` i przypadkami testowymi części 6 `[201-P6]`, OCPP 2.1 Edition 2 część 2 `[21-P2]` z erratą 2026-09 `[21-E]`.
Zdania **Wniosek** to rekomendacje wyprowadzone z cytowanych faktów. Tam, gdzie specyfikacja czegoś nie określa,
narzędzie to zgłasza (pole `undefined`, okres `NIEOKRESLONE`) zamiast zgadywać.

## Spis treści
1. Do czego służy
2. Uruchomienie
3. Wejście
4. Wyjście i kody wyjścia
5. Reguły składania profili
6. Jednostki i fazy
7. Czego specyfikacja nie określa
8. Czego narzędzie nie liczy
9. Rozbieżności w dokumentach
10. Testy

## 1. Do czego służy
- Liczy harmonogram złożony jednego EVSE (1.6: złącza) z zainstalowanych profili ładowania, tak jak stacja powinna go
  zwrócić w `GetCompositeSchedule`: od chwili otrzymania żądania przez `duration` sekund `[201-P2 K08.FR.02]`
  `[16E §3.29]`.
- Obsługuje OCPP 1.6, 2.0.1 i 2.1 (w 2.1 tylko tryb `ChargingOnly`, pkt 8).
- Tylko biblioteka standardowa Pythona, bez sieci.
- Wynik jest tylko orientacyjny, bo stacja uwzględnia też własne limity lokalne i równoważenie między EVSE
  `[201-P2 K08]` `[16 §5.7]`. Narzędzie ich nie zna, chyba że podasz `--local-limit`.

**Wniosek:** porównanie wyniku narzędzia z odpowiedzią stacji pokazuje, czy stacja ma te profile, których oczekuje
CSMS. Wynik narzędzia niższy niż odpowiedź stacji oznacza błąd po stronie stacji albo brak profilu na stacji. Wynik
wyższy może wynikać z limitu lokalnego stacji.

## 2. Uruchomienie
```bash
python3 skills/ev-energy-smart-charging-expert/scripts/composite_schedule.py <profile.json> \
    --ocpp 1.6|2.0.1|2.1 --evse N --start <RFC 3339> --duration <s> \
    [--unit A|W] [--supply AC|DC] [--voltage 230] [--transaction-id ID] [--charging-start <RFC 3339>] \
    [--local-limit X] [--priority-charging] [--assume-utc] [--json]
```
- `--evse` (alias `--connector`): EVSE > 0. Dla EVSE 0 stacja raportuje łączny oczekiwany pobór z sieci
  `[201-P2 K08.FR.03]` `[16 §5.7]`. Zależy on od obciążenia wszystkich EVSE, więc narzędzie go nie liczy (kod 2).
- `--start`: chwila otrzymania żądania, czyli `scheduleStart` odpowiedzi `[201-P2 §2.18]`. `--duration`: pole
  `duration` żądania `[201-P2 §1.20.1]`.
- `--unit`: `chargingRateUnit` z żądania („can be used to force a power or current profile”) `[201-P2 §1.20.1]`
  `[16 §6.21]`.
- `--supply AC|DC` i `--voltage`: potrzebne do przeliczenia A↔W (pkt 6) i do domyślnej liczby faz.
- `--transaction-id`: na EVSE trwa transakcja. Bez tej opcji `TxProfile` jest pomijany, bo bez transakcji stacja go
  nie przyjmuje `[201-P2 K01.FR.09]` `[16 §3.13.1]`.
- `--charging-start`: punkt startu profili `Relative`, czyli chwila gotowości EVSE do dostarczania energii (pkt 5).
- `--local-limit`: limit lokalny stacji w jednostce wyniku. OCPP nie podaje jego wartości (pkt 5).
- `--priority-charging`: 2.1, priorytet ładowania aktywowany na stacji lub przez `UsePriorityChargingRequest`
  `[21-P2 K §3.6]`. Aktywacja jest stanem stacji, a nie polem profilu.
- `--assume-utc`: czasy bez strefy traktuje jako UTC (pkt 9).
- Testy: `python3 -m unittest tests.test_composite_schedule`.

## 3. Wejście
Lista komunikatów albo `{"profiles": [...]}`. Ramka OCPP-J `[2, id, akcja, ładunek]` jest rozpakowywana.

| Wersja | Komunikat | Pola |
|---|---|---|
| 1.6 | `SetChargingProfile.req` | `connectorId`, `csChargingProfiles` `[16 §6.43]` |
| 2.0.1 / 2.1 | `SetChargingProfileRequest` | `evseId`, `chargingProfile` (obiekt) `[201-P2 §1.51.1]` |
| 2.0.1 / 2.1 | `ReportChargingProfilesRequest` | `evseId`, `chargingLimitSource`, `chargingProfile` (lista) `[201-P2 §1.43.1]` `[21-P2 §1.63.1]` |

- `ChargingStationExternalConstraints` (2.x) i `LocalGeneration` (2.1) podajesz tylko jako
  `ReportChargingProfilesRequest`. CSMS nie może ich wysłać w `SetChargingProfileRequest` `[201-P2 K01.FR.22]`
  `[201-E §2.15]` `[21-E §2.16.2]`. Gdy przyjdą w takim komunikacie, narzędzie kończy się kodem 2.
- Profil bez `validFrom` jest ważny od chwili otrzymania przez stację `[201-P2 §2.10]` `[16 §7.8]`. Narzędzie
  przyjmuje, że stacja otrzymała go przed oknem.
- Czasy w formacie RFC 3339 z przesunięciem strefy `[201-P2 §2.1.4]`. W 1.6 obowiązuje ISO 8601 `[16 §3.15]`, a UTC
  jest tylko zalecane `[16 §3.14]`. Czas bez strefy daje błąd wejścia, chyba że podasz `--assume-utc`.

## 4. Wyjście i kody wyjścia
- `periods`: okresy złożone. Każdy ma `startPeriod` (sekundy od `--start`), `limit`, opcjonalnie `numberPhases` i
  `phaseToUse`, `status` i `sources` (profil, który dał minimum). Statusy:
  - `OK`;
  - `BRAK_PROFILU`: nie obowiązuje żaden profil, a `--local-limit` nie podano, więc `limit` = `null`;
  - `NIEOKRESLONE`: specyfikacja nie określa wyniku, więc `limit` = `null`, a pole `reason` podaje oba cytaty.
- Kolejne okresy o tym samym limicie, fazach i statusie są łączone. Tak samo wyglądają oczekiwane odpowiedzi w
  przypadkach testowych `[201-P6]` (TC_K_41_CS).
- `response`: gotowa odpowiedź, tylko gdy wszystkie okresy mają liczbę.
  - 2.x: `{status, schedule: {evseId, duration, scheduleStart, chargingRateUnit, chargingSchedulePeriod}}`
    `[201-P2 §1.20.2]` `[201-P2 §2.18]`.
  - 1.6: `{status, connectorId, scheduleStart, chargingSchedule}` `[16 §6.22]`, bez `startSchedule` w
    `chargingSchedule` `[16E §3.57]`.
- `undefined`: punkty, których specyfikacja nie określa (pkt 7). `ignored`: profile pominięte z powodem.
  `warnings`: założenia, Wnioski i pominięte pola.
- Kody wyjścia:

| Kod | Znaczenie |
|---|---|
| 0 | harmonogram pełny, bez punktów nieokreślonych |
| 1 | harmonogram z lukami (`BRAK_PROFILU`, `NIEOKRESLONE`) albo zależny od punktu z `undefined` |
| 2 | błąd wejścia albo dane, których narzędzie nie liczy (pkt 8) |

## 5. Reguły składania profili
| Reguła | 1.6 | 2.0.1 | 2.1 |
|---|---|---|---|
| cele | `ChargePointMaxProfile`, `TxDefaultProfile`, `TxProfile` `[16 §3.13.1]` | dodatkowo `ChargingStationExternalConstraints` `[201-P2 K §3.2]` | dodatkowo `PriorityCharging`, `LocalGeneration` `[21-P2 K §3.2]` |
| profil Max | tylko złącze 0 `[16 §3.13.1]` | tylko EVSE 0 `[201-P2 K §3.2]`, nie `Relative` `[201-P2 K01.FR.38]` | jak 2.0.1 |
| `TxProfile` | tylko złącze > 0; `transactionId` opcjonalne `[16 §3.13.1]` `[16 §7.8]` | tylko EVSE > 0, `transactionId` wymagane `[201-P2 K01.FR.16]` `[201-P2 K01.FR.03]` | jak 2.0.1 |
| profil na 0 a EVSE | `TxDefaultProfile` złącza zastępuje profil ze złącza 0 tylko dla tego złącza `[16 §3.13.1]` | profil na EVSE 0 działa na każdym EVSE `[201-P2 K §3.4]` | jak 2.0.1 |
| ważność | `validFrom`/`validTo` `[16 §3.13.2]` | `validFrom` włącznie, `validTo` wyłącznie `[201-P2 K01.FR.36]` `[201-P2 K01.FR.37]` | jak 2.0.1 |
| start `Relative` | punkt ustala stacja `[16 §7.9]`, „relative to start of charging” `[16 §7.13]` | gotowość do dostarczania energii, RECOMMENDED `[201-P2 K01.FR.42]` | to samo jako SHALL `[21-P2 K01.FR.42]` |
| `Absolute`/`Recurring` bez `startSchedule` | liczone od startu ładowania `[16 §7.13]` | niedozwolone `[201-P2 K01.FR.40]` | jak 2.0.1 |
| powtarzanie | co 24 h / 7 dni od `startSchedule` `[16 §7.37]` `[16E §3.79]` | to samo `[201-P2 §3.68]` | to samo |
| przed `startSchedule` | nie zapisane wprost (pkt 7) | profil nie ogranicza `[201-P2 K01.FR.30]` | jak 2.0.1 |
| okresy | pierwszy `startPeriod` = 0 `[16 §5.16.4]`; kolejny kończy poprzedni `[16 §7.14]` | pierwszy 0, rosnąco `[201-P2 K01.FR.31]` `[201-P2 K01.FR.35]`; okres trwa do następnego albo do końca `duration` `[201-P2 K01.FR.12]`, okres od `duration` wzwyż nie jest wykonywany `[201-P2 K01.FR.11]` | jak 2.0.1 |
| brak `duration` | ostatni okres trwa dalej `[16 §7.13]` | to samo `[201-P2 §2.12]` | to samo `[21-P2 §2.19]` |
| okresy dłuższe niż powtarzanie | reszta nie jest wykonywana `[16 §5.16.4]` | brak osobnej reguły; narzędzie tnie tak samo (Wniosek z „restarts every 24 hours” `[201-P2 §3.68]`) i ostrzega | jak 2.0.1 |
| wybór w stosie | najwyższy ważny `stackLevel` `[16 §3.13.2]`; najwyższy bez `duration` nie wraca do niższych `[16E §3.7]`; `Recurring` po `duration` wraca do niższego `[16 §5.16.4]` `[16E §3.43]` | harmonogram z okresem zdefiniowanym w danej chwili, z ważnego profilu o najwyższym `stackLevel` `[201-P2 K §3.5]` `[201-P2 K01.FR.17]` | jak 2.0.1 |
| `TxProfile` a `TxDefaultProfile` | `TxProfile` zastępuje `TxDefaultProfile` `[16 §3.13.1]` | to samo `[201-P2 K §3.5]`; po końcu `duration` `TxProfile` powrót do `TxDefaultProfile` `[201-P2 K02.FR.08]` | jak 2.0.1; `PriorityCharging` po aktywacji zastępuje oba `[21-P2 K §3.6]` |
| wynik | minimum w każdym przedziale `[16 §3.13.3]` | minimum wiodących harmonogramów Max, ExternalConstraints i Tx/TxDefault `[201-P2 K §3.5]` `[201-P2 K08.FR.04]` | to samo; limit `LocalGeneration` dodawany do wyniku `[21-P2 K §3.6]` `[21-P2 K08.FR.04]` |
| bez transakcji | nie określone (pkt 7) | jak przy transakcji z `TxDefaultProfile` `[201-P2 K08.FR.06]` | to samo z `randomizedDelay` = 0 `[21-P2 K08.FR.06]` |

- Limit profilu Max dotyczy wszystkich EVSE łącznie `[201-P2 K §3.5]` `[16 §3.13.3]`. Dla jednego EVSE narzędzie
  traktuje go jako górną granicę. Podziału między EVSE nie zna.
- **Brak profilu.** Stacja wraca do własnego limitu lokalnego: „it falls back to the local limit of the Charging
  Station” `[201-P2 K02.FR.08]`. Przypadki testowe oczekują wtedy „Local limit of Charging Station” `[201-P6]`
  (TC_K_09_CS, TC_K_22_CS, TC_K_23_CS). Bez żadnych profili transakcja przebiega „as if no constraints apply”
  `[201-P2 K06.FR.02]` `[16 §3.13.6]`. **OCPP nie podaje liczby.** Narzędzie nie zakłada prądu domyślnego: bez
  `--local-limit` taki okres ma `limit` = `null` i kod 1. Podany `--local-limit` bierze udział w minimum przez cały
  czas, bo wynik stacji obejmuje „possible local limits” `[201-P2 K08]`.
- 2.1 `LocalGeneration`: przykład specyfikacji: `TxDefaultProfile` 5000 W plus `LocalGeneration` 2000 W daje
  7000 W, a po spadku do 1000 W daje 6000 W `[21-P2 K27]`. Dodatek działa więc także wtedy, gdy minimum wyznacza
  `TxDefaultProfile`, a nie profil Max.

## 6. Jednostki i fazy
- `A` to prąd na fazę, `W` to łączna moc. Dla AC prąd fazy = moc / (napięcie nominalne × `numberPhases`). Napięcie
  nominalne to napięcie ustalone dla obszaru (230 albo 110 V), a nie zmierzone. `numberPhases` pochodzi z okresu
  profilu, domyślnie 3 `[201-P2 K01.FR.49]` `[201-P2 K01.FR.50]` `[201-P2 K01.FR.51]` `[16 §7.12]`.
- Wynik uwzględnia różne jednostki („taking the different chargingRateUnits into account”) `[201-P2 K §3.5]`.
  Narzędzie przelicza każdy limit na jednostkę wyniku liczbą faz jego własnego okresu. A→W to odwrotność tego wzoru
  (**Wniosek**).
- Przeliczenie działa tylko z `--supply AC` i `--voltage`. Dla DC specyfikacja nie podaje wzoru, więc profili w A i W
  na DC narzędzie nie łączy (kod 2).
- Bez `--unit`, gdy profile mają różne jednostki: specyfikacja nie mówi, w jakiej jednostce stacja odpowie
  `[201-P2 §1.20.1]` `[16 §6.21]`. To błąd wejścia.
- `numberPhases` okresu złożonego: najniższa wartość z profili, które go tworzą `[201-P2 K §3.7]`. W 1.6 takiej
  reguły nie ma: przy różnych wartościach pole jest pomijane z ostrzeżeniem. Dla DC `numberPhases` się pomija
  `[201-P2 §2.11]`.
- Sprzeczne `phaseToUse` uniemożliwiają złożenie okresu `[201-P2 K §3.7]`, więc narzędzie kończy się kodem 2.
  `phaseToUse` trafia do wyniku tylko przy `numberPhases` = 1.
- `limit` przyjmuje najwyżej jedną cyfrę po przecinku `[201-P2 §2.11]` `[16 §7.14]`. Kierunku zaokrąglenia po
  przeliczeniu OCPP nie podaje. Narzędzie nie zaokrągla wyniku i ostrzega.

## 7. Czego specyfikacja nie określa
| Sytuacja | Cytaty | Narzędzie |
|---|---|---|
| 2.x: `TxProfile` ważny, ale przed swoim `startSchedule`, a `TxDefaultProfile` ma okres | K §3.5: przy ważnym `TxProfile` nie bierze się `TxDefaultProfile` `[201-P2 K §3.5]`; K01.FR.30: `TxProfile` ogranicza dopiero od `startSchedule` `[201-P2 K01.FR.30]` | `NIEOKRESLONE` |
| 1.6: `TxProfile` ważny, ale bez okresu w danej chwili, a `TxDefaultProfile` ma okres | `TxProfile` zastępuje `TxDefaultProfile` `[16 §3.13.1]`; powrót do niższego `stackLevel` dotyczy jednego celu `[16 §5.16.4]`; 1.6 nie ma odpowiednika K02.FR.08 | `NIEOKRESLONE` |
| 1.6 bez transakcji: czy liczyć `TxDefaultProfile` | `TxDefaultProfile` dotyczy nowych transakcji `[16 §7.10]`; 2.0.1 ma regułę K08.FR.06 `[201-P2 K08.FR.06]`, a 1.6 nie | liczy, wpis w `undefined` |
| 1.6: `TxDefaultProfile` złącza i złącza 0 o różnych `stackLevel` | tekst mówi tylko o zastąpieniu dla złącza `[16 §3.13.1]` | zostawia oba w stosie, wpis w `undefined` |
| 1.6: powrót do niższego `stackLevel` po `duration` profilu, który nie jest `Recurring`, i przed `startSchedule` | wprost tylko dla `Recurring` `[16 §5.16.4]`; najwyższy bez `duration` nie wraca `[16E §3.7]`; zalecenie, by nie było „period of default charging behaviour” `[16 §5.16.4]` | wraca do niższego, ostrzeżenie (**Wniosek**) |
| wartość limitu bez profilu | `[201-P2 K02.FR.08]` `[201-P6]` | `BRAK_PROFILU` bez `--local-limit` |

## 8. Czego narzędzie nie liczy
Kod 2 z komunikatem:
- EVSE 0 (łączny pobór stacji, pkt 2).
- Kilka `chargingSchedule` w profilu, czyli wybór harmonogramu w ISO 15118 `[201-P2 K01.FR.34]`.
- 2.1, pola i tryby spoza `ChargingOnly` `[21-P2 §2.17]` `[21-P2 §2.18]` `[21-P2 §2.19]`:
  - rodzaj `Dynamic`, `dynUpdateInterval`, `dynUpdateTime`;
  - `operationMode` inny niż `ChargingOnly` (dla `LocalGeneration` dozwolone także `ExternalLimits` z `limit`)
    `[21-P2 K §3.2]`;
  - pola `setpoint*`, `dischargeLimit*`, `limit_L2`, `limit_L3` (wynik dla faz opisuje `[21-P2 K08.FR.09]`), `v2x*`,
    `evseSleep`, `limitAtSoC`, `useLocalTime`;
  - limit ujemny, który w 2.1 istnieje tylko dla zgodności wstecz jako limit rozładowania `[21-P2 §2.18]`.
- `randomizedDelay` > 0 (losowe przesunięcie okresów). Wyjątek: `TxDefaultProfile` bez transakcji liczy się z
  `randomizedDelay` = 0 `[21-P2 K08.FR.06]`. W celach innych niż `TxProfile`/`TxDefaultProfile` od CSMS pole jest
  niedozwolone `[21-P2 K01.FR.95]`.
- Profile, które stacja odrzuciłaby albo których CSMS nie może wysłać. Narzędzie sprawdza między innymi K01.FR.03,
  K01.FR.06, K01.FR.16, K01.FR.19, K01.FR.31, K01.FR.35, K01.FR.38–41, K01.FR.52–53 i K01.FR.60 `[201-P2 K01.FR.06]`
  `[201-P2 K01.FR.53]`, a w 1.6 ten sam `stackLevel` i cel `[16 §3.13.2]`. To samo `id` dwa razy oznacza zastąpienie
  profilu `[201-P2 K01.FR.05]` `[16 §5.16.3]`, więc podajesz stan po zastąpieniu.
- `maxOfflineDuration` i `invalidAfterOfflineDuration` (2.1) pomija z ostrzeżeniem, bo liczy stację online.

## 9. Rozbieżności w dokumentach
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| `TxProfile` po końcu `duration` (2.0.1) | „when both a TxDefaultProfile and a TxProfile are valid … the TxProfile will always overrule the TxDefaultProfile” `[201-P2 K §3.5]` | po końcu harmonogramu `TxProfile` przez `duration` lub `validTo` stacja „SHALL fall back to using the lowest limit of the active TxDefaultProfile and ChargingStationMaxProfile” `[201-P2 K02.FR.08]` | wymaganie ma pierwszeństwo przed opisem `[201-P2 §2.1.2]`; tak samo przypadek testowy TC_K_41_CS `[201-P6]` |
| źródło `LocalGeneration` (2.1) | „can also be provided by a CSMS” `[21-P2 K §3.2]` | errata usuwa to zdanie i dodaje K01.FR.63–64: CSMS SHALL NOT, stacja odrzuca `[21-E §2.16.1]` `[21-E §2.16.2]` | errata 2026-09 |
| czas bez strefy w przykładach | `"startSchedule": "2020-01-09T17:00:00"` `[201-P2 K §3.6.1]` | dateTime według RFC 3339 `[201-P2 §2.1.4]` | RFC 3339; przykład liczysz z `--assume-utc` albo dopisujesz `Z` |
| `duration` w przykładzie stosu | okno 17:00–20:00 z `"duration": 1080` `[201-P2 K §3.6.1]` | 3 h = 10800 s | literówka (`references/profile-ocpp.md` §11); test sprawdza oba warianty |
| wybór w stosie 1.6 | „highest stackLevel among the profiles that are valid” `[16 §3.13.2]` | po `duration` `Recurring` „SHALL use a ChargingProfile with a lower stackLevel if available” `[16 §5.16.4]` `[16E §3.43]` | errata uzupełnia regułę o powrót po `duration`; reszta w pkt 7 |
| `LocalGeneration` a limit stacji (2.1) | łączny pobór ≤ `ChargingStationMaxProfile` + `LocalGeneration` `[21-P2 K04.FR.05]` | dodatek do wyniku złożonego `[21-P2 K §3.6]` `[21-P2 K08.FR.04]` | to nie jest sprzeczność: przykład 5000 W + 2000 W `[21-P2 K27]` pokazuje dodatek do wyniku z `TxDefaultProfile` |

## 10. Testy
`tests/test_composite_schedule.py` (unittest, 31 testów):
- Przypadki testowe OCPP 2.0.1 `[201-P6]`, z x = 5 s i mnożnikiem limitu 1:
  - TC_K_41_CS: łączenie celów i powrót do `TxDefaultProfile` po końcu `TxProfile`;
  - TC_K_40_CS: stos;
  - TC_K_09_CS, TC_K_21_CS, TC_K_22_CS, TC_K_23_CS: limit lokalny, `validFrom`, `validTo`, `startSchedule` w
    przyszłości.
- Przykłady specyfikacji:
  - profil dzienny 11 kW / 6 kW `[201-P2 K §3.6]` `[16 §3.13.7]`;
  - wyjątki w stosie (niedziela, Boże Narodzenie) `[201-P2 K §3.6.1]`;
  - `LocalGeneration` `[21-P2 K27]`.
- Testy pojedynczych reguł: 1.6 (stos, zastępowanie profilu złącza 0, punkty nieokreślone), A↔W i fazy, walidacja
  K01, odmowy 2.1, CLI i kody wyjścia.
