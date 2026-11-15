# Luki pack-ev → ev-intelligence, grupa C (energia, sprzęt, V2X, bateria, flota)

Stan: 2026-11-15. Analiza tylko do odczytu, bez sieci. Ścieżki pack-ev liczone od `/home/user/tf/packs/pack-ev/skills/`,
ścieżki ev-intelligence od `/home/user/ev-intelligence/`. Numery linii pochodzą z `cat -n`.

Klasy:
- **F**: fakt, który da się sprawdzić w specyfikacji lub akcie. Każdy ma jeden z trzech statusów:
  - *zarejestrowane*: źródło ma `id` w `sources/*.yaml`, więc treść można przenieść po sprawdzeniu sekcji;
  - *do rejestracji*: oficjalne i bezpłatne, ale nie ma go ani w rejestrze, ani w `niedostepne.yaml`;
  - *niedostępne*: norma jest w `sources/niedostepne.yaml`, więc treści nie przenosimy.
- **P**: praktyka, zachowanie producentów albo implementacja referencyjna (libocpp, josev), bez źródła oficjalnego.
- **R**: procedura lub heurystyka, czyli sposób pracy bez nowych faktów.

**Gdzie ev-intelligence trzyma praktykę.** W `knowledge/` jest tylko
`knowledge/implementation-intelligence/vendor-quirks/_szablon.yaml`. To szablon wiedzy klasy D: obserwacja konkretnego
modelu i firmware z dowodem. Katalogi z taksonomii (`knowledge/energy/…`, `knowledge/vehicle/…`,
`knowledge/segments/fleet-depot/`) nie istnieją. Ogólnej praktyki (P) nie ma więc gdzie przenieść. Wyjątkiem jest
zdanie **Wniosek** zbudowane na cytowanym fakcie. Procedury (R) mogą trafić do sekcji „Procedura”, „Pułapki” i
„Przykład” w SKILL.md, bo nie niosą faktów.

**Najważniejsza obserwacja.** Opracowanie profili OCPP, OCPP 2.1 V2X/DER, AFIR i złączy w ev-intelligence jest
**pełniejsze i lepiej zacytowane** niż w pack-ev. pack-ev opiera się na libocpp, josev i źródłach wtórnych, a w wielu
miejscach ma znacznik „[do weryfikacji]” tam, gdzie ev-intelligence ma już cytat ze specyfikacji OCA. Realne luki są
cztery:
- prawo: RED III, EPBD, ustawa o elektromobilności art. 11–12b;
- planowanie mocy lokacji i zajezdni (heurystyki R/P);
- pojazd i bateria (P/R, bez skilla docelowego);
- flota (model danych R, część faktów OCPI/OCPP do przeniesienia).

---

## 1. dom-ev-smart-charging → ev-energy-smart-charging-expert

**Pokrycia** (jedna linia każde; ev-intelligence ma cytaty OCA):
- cele i rodzaje profili, stackLevel, composite schedule: `profile-ocpp.md` §1–4;
- A/W, fazy, `numberPhases` = 3, krok 0,1: `profile-ocpp.md` §5;
- zakładanie i usuwanie profili, `ClearChargingProfile` (K10): `profile-ocpp.md` §6;
- offline i restart (K06, K07, K01.FR.27): `profile-ocpp.md` §7;
- ExternalConstraints, `NotifyChargingLimit`, `ClearedChargingLimit`: `sterowanie-i-topologie.md` §3;
- AFIR art. 2 pkt 65, art. 5 ust. 7–8: `sterowanie-i-topologie.md` §7;
- `minChargingRate` i „profil to limit, nie cel” `[OCPI230 §14]`;
- przykład 11 kW w W → 15,9 A: `profile-ocpp.md:104-106`;
- `phaseToUse`, `SmartChargingCtrlr`.

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| SC1 | RED III art. 20a ust. 4: nowe i wymieniane niepubliczne punkty normalnej mocy obsługują smart recharging; definicja art. 2 pkt 14m; transpozycja do 21.05.2025 | `dom-ev-smart-charging/references/testowanie-i-prawo.md:36-50`, `SKILL.md:131-134` | `ev-energy-smart-charging-expert/references/sterowanie-i-topologie.md` §7 (obok AFIR); odsyłacz w `ev-compliance-expert` | F | dyrektywa (UE) 2023/2413, EUR-Lex. **Do rejestracji**: brak w rejestrze i w niedostepne.yaml; taksonomia wymienia RED III tylko z nazwy |
| SC2 | Lista walidacji profilu po stronie CSMS w jednej tabeli: warunek → K01.FR, w tym brakujące K01.FR.28 (nieistniejące EVSE) i K01.FR.48. Nazwy kodów libocpp (`ChargingProfileFirstStartScheduleIsNotZero`…) to P i nie idą dalej | `dom-ev-smart-charging/references/walidacja-k01.md:9-36` | `profile-ocpp.md`, nowa sekcja „Walidacja przed wysłaniem” (dziś reguły są rozproszone po §1–6) | F | `201-P2` blok K01 (oca-ocpp201-ed4) — zarejestrowane |
| SC3 | Przebieg `GetChargingProfiles` → `NoProfiles`/`Accepted` → `ReportChargingProfiles` (z `requestId`); w 1.6 tego komunikatu nie ma, więc CSMS trzyma własny rejestr wysłanych profili | `dom-ev-smart-charging/references/komunikaty-i-pola.md:34-41` | `profile-ocpp.md` §6 (dziś tylko nazwa komunikatu w `sterowanie-i-topologie.md:52-53`) | F | `201-P2` K09, `201-P3`; `S16` (28 akcji, brak GetChargingProfiles) — zarejestrowane |
| SC4 | Uzgodnienie po `BootNotification`: `GetCompositeSchedule` i `GetChargingProfiles`, porównanie z oczekiwanym stanem, ponowne wysłanie brakujących | `dom-ev-smart-charging/SKILL.md:92-94`, checklista `:150` | `SKILL.md` „Procedura” pkt 5 jako **Wniosek** z K01.FR.27 i K09 | R | — (oparte na `201-P2` K01.FR.27, K09) |
| SC5 | Przypadki testowe po zmianie firmware lub CSMS (brak profili, sufit vs TxDefault, Tx vs TxDefault, dwa TxDefault, Recurring, W na 1 i 3 fazach, utrata łączności, restart, 5 A) | `dom-ev-smart-charging/references/testowanie-i-prawo.md:19-30` | nowy `references/testy.md` albo scenariusze `evals/skill_evals/ev-energy-smart-charging-expert.json`. Oczekiwania trzeba przepisać według specyfikacji (np. „brak profili” = brak limitu, K06.FR.02) | R | można zakotwiczyć w `201-P6` (przypadki TC_K_*), zarejestrowane; dziś cytowane tylko w ev-evse-diagnostics-expert |
| SC6 | Minimum 6 A (10 % PWM): planista przydziela 0 albo ≥ 6 A; limit 1–5 A = brak ładowania | `dom-ev-smart-charging/SKILL.md:98-101`, `:143` | tylko jako zdanie „wartość zależy od IEC 61851-1, nieopracowanej” w `profile-ocpp.md` §5 | F | **niedostępne**: IEC 61851-1 (`niedostepne.yaml:27`) |
| SC7 | Rzeczywisty pobór czytaj z `MeterValues` (`Current.Import`, `Power.Active.Import`); suma limitów nie jest obciążeniem przyłącza; `Accepted` ≠ działający limit | `dom-ev-smart-charging/SKILL.md:102-103`, `:144` | `sterowanie-i-topologie.md` §1 (obok „profil to limit, nie cel”) | F | `S16`/`201-P3` (enumeracja measurandów), `OCPI230 §14` — zarejestrowane |
| SC8 | Przypadki brzegowe składania profili według libocpp: ExtraSeconds, okresy z różnymi `numberPhases`, Recurring z poprzedniej doby, przykład validFrom/validTo | `dom-ev-smart-charging/references/composite-schedule-libocpp.md:7-64` | nieprzenośne jako fakt. Część ma odpowiednik w specyfikacji (K01.FR.13, K §3.5, K08), który ev-intelligence już ma. Reszta może posłużyć tylko jako wskazówka do testów skryptu | P | libocpp to biblioteka open-source (źródło wtórne) |
| SC9 | „Limit domyślny 48 A albo 0” według libocpp | `dom-ev-smart-charging/SKILL.md:62-67`, `composite-schedule-libocpp.md:22-35` | nieprzenośne; sprzeczne ze specyfikacją (konflikt K1) | P | — |
| SC10 | Przykład zajezdni 63 A: profile `TxProfile` na EVSE i `ChargePointMaxProfile` jako bezpiecznik | `dom-ev-smart-charging/SKILL.md:105-117` | `SKILL.md` „Przykład” (drugi przykład) po poprawce na `ChargingStationMaxProfile` (konflikt K2) | R | — |
| SC11 | Synchronizacja zegara stacji z `currentTime` z `BootNotification` (ważne dla `Absolute`/`Recurring`) | `dom-ev-smart-charging/SKILL.md:96` | `profile-ocpp.md` §2 albo §7 | F | `S16`, `201-P3` (`currentTime` wymagane, jest w ev-ocpp-expert) — zarejestrowane |
| SC12 | Pola odpowiedzi `GetCompositeSchedule` 2.0.1 (`scheduleStart` jako punkt odniesienia okresów, `statusInfo`) | `dom-ev-smart-charging/references/komunikaty-i-pola.md:26-32` | `profile-ocpp.md` §4 | F | `201-P3` — zarejestrowane |

## 2. dom-ev-energy-management → ev-energy-smart-charging-expert (D08.02–D08.05)

**Pokrycia:**
- cztery typy sterowania i Local Controller (`sterowanie-i-topologie.md` §1–2);
- limity zewnętrzne i źródła `EMS`/`SO`/`CSO` (§3);
- offline i bezpieczny limit stacji (przykład w `SKILL.md:51-69`);
- AFIR art. 5 ust. 8;
- `phaseToUse`;
- algorytm CSMS poza zakresem OCPP `[16 §3.13.4]`.

ev-intelligence wprost deklaruje, że **D08.04 przyłączenie i D08.05 rynek energii nie są opracowane**
(`sterowanie-i-topologie.md:149-150`), a PL-EMOB art. 12–12c pozostaje „nie opracowano” (`ev-compliance-expert/references/prawo-pl.md:138-139`).

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| EM1 | Ustawa o elektromobilności: art. 11 (infrastruktura transportu publicznego to cel publiczny), art. 12 ust. 1 (moc przyłączeniowa pod punkty ≥ 3,7 kW), art. 12a ust. 1, art. 12b ust. 9–10 (koszty ekspertyzy, układ pomiarowy OSD) | `dom-ev-energy-management/references/przepisy-przylacze.md:19-25` | `ev-compliance-expert/references/prawo-pl.md` (zamyka „nie opracowano”); odsyłacz z `sterowanie-i-topologie.md` §9 | F | `PL-EMOB` (pl-prawo.yaml) — **zarejestrowane** |
| EM2 | RED III art. 20a ust. 1–2 (OSP i OSD udostępniają udział OZE i emisyjność co ≤ 1 h), ust. 3 (dane z pojazdu: SoC, SoH, power set point), ust. 5 (agregacja małych zasobów) | `dom-ev-energy-management/references/przepisy-przylacze.md:8-11`, `pv-bess-taryfy-sygnaly.md:27-28,43` | `sterowanie-i-topologie.md` §7 (nowy podpunkt „RED III”) albo ev-compliance-expert | F | dyrektywa (UE) 2023/2413 — **do rejestracji** |
| EM3 | EPBD art. 14 ust. 6 (punkty w budynkach zdolne do smart charging, protokoły niezastrzeżone i niedyskryminujące), ust. 4 (wymiarowanie budynków mieszkalnych) | `dom-ev-energy-management/references/przepisy-przylacze.md:13-14` | `sterowanie-i-topologie.md` §7 + ev-compliance-expert | F | dyrektywa (UE) 2024/1275 — **do rejestracji** |
| EM4 | Moc przyłączeniowa, moc umowna i zabezpieczenie przedlicznikowe; limit DLM = najmniejszy z nich; rozliczanie przekroczeń mocy umownej | `dom-ev-energy-management/references/przepisy-przylacze.md:27-35`, `SKILL.md:17-18` | `sterowanie-i-topologie.md` §9 → nowa sekcja D08.04. Wzór `limit_A = min(…)` jako R; definicje z prawa | F (+R) | Prawo energetyczne i rozporządzenia (systemowe, taryfowe) — **do rejestracji**; dziś brak nawet wpisu w niedostepne.yaml |
| EM5 | DLM statyczny i dynamiczny z pomiarem budynku: `EV_max(x) = limit(x) − budynek(x) − rezerwa` na fazę; stacja 3-fazowa dostaje minimum z faz; błąd liczenia z sumy faz | `dom-ev-energy-management/SKILL.md:28-37`, `references/algorytmy-podzialu.md:35-48` | `sterowanie-i-topologie.md`, nowa sekcja „Podział mocy w lokacji” jako **Wniosek** z `[16 §7.12]`/`[201-P2 K01.FR.51]` (A na fazę) i K04 | R | — |
| EM6 | Porównanie algorytmów podziału: równy, proporcjonalny, FIFO, EDF, LLF, priorytety, cena | `dom-ev-energy-management/references/algorytmy-podzialu.md:21-33`, `SKILL.md:48-58` | ta sama nowa sekcja; zgodne z taksonomią D08.01 („równy podział, priorytety, departure time, koszt”) | R | — (OCPP: algorytm poza zakresem `[16 §3.13.4]`) |
| EM7 | Najwyżej ⌊limit / 6⌋ pojazdów naraz; przydział < 6 A = 0; moce 6/16/32/63 A na 1 i 3 fazach | `dom-ev-energy-management/references/algorytmy-podzialu.md:3-19` | tylko arytmetyka (tabela mocy) jako Wniosek z `[16 §7.12]`; progu 6 A nie przenosimy | F | **niedostępne**: IEC 61851-1 |
| EM8 | Pojazdy 1-fazowe: rotacja faz przy instalacji; pojazd sam wybiera fazę (zwykle L1), CSMS jej nie zna | `dom-ev-energy-management/references/algorytmy-podzialu.md:39-41` | — (ewentualnie obserwacje D21) | P | — |
| EM9 | Odzyskiwanie niewykorzystanego prądu (pobór < 80 % limitu przez N próbek → limit = pobór + 2 A) | `dom-ev-energy-management/references/algorytmy-podzialu.md:56-60` | nieprzenośne (same założenia) | P | — |
| EM10 | Sprawdzenie wykonalności przed planem: `max_a × U × fazy × czas_postoju ≥ potrzeba`; zgłoszenie niewykonalnych | `dom-ev-energy-management/references/zajezdnia-floty.md:12-15`, `SKILL.md:21` | nowa sekcja planowania (Procedura) | R | — |
| EM11 | SoC → kWh ze sprawnością ~0,90 i buforem przed odjazdem | `dom-ev-energy-management/references/zajezdnia-floty.md:7-10` | nieprzenośne (sprawność to założenie) | P | — |
| EM12 | Ponowne planowanie po zdarzeniach; stała kolejność remisów (priorytet, luz), nie nazwa EVSE; brak nowych profili, gdy plan się nie zmienił | `dom-ev-energy-management/references/zajezdnia-floty.md:17-20` | nowa sekcja planowania | R | — |
| EM13 | Gdzie liczyć: CSMS, lokalny kontroler czy master–slave w ładowarce; „sekundy lokalnie, godziny w CSMS” | `dom-ev-energy-management/references/architektura-odpornosc.md:3-15` | fakty o typach są już w §1–2; plusy i minusy to P | P | (fakty: `201-P2 K §2`, już cytowane) |
| EM14 | Fail-safe przy nieaktualnym pomiarze budynku; restart kontrolera startuje z fail-safe; „obcinaj szybko, podnoś wolno”; logowanie obcięć | `dom-ev-energy-management/references/architektura-odpornosc.md:17-29`, `SKILL.md:94,98` | Pułapki jako R; wartości (histereza) nieprzenośne | P | (pokrewne F: `LimitChangeSignificance` `[201-APP §3.1.16]`, już w ev-intelligence) |
| EM15 | `isGridCritical` w `NotifyChargingLimit`: limit krytyczny dla sieci ma pierwszeństwo przed celami komercyjnymi | `dom-ev-energy-management/references/architektura-odpornosc.md:35-36`, `pv-bess-taryfy-sygnaly.md:42`; `dom-ev-smart-charging/references/komunikaty-i-pola.md:44-47` | `sterowanie-i-topologie.md` §3 (dziś bez `isGridCritical`) | F | `201-P3` (NotifyChargingLimitRequest), `201-P2` §2 (ChargingLimitType) — zarejestrowane |
| EM16 | PV: ładowanie z nadwyżki tylko powyżej minimum 1,38/4,14 kW; PV nie obniża limitu bezpieczeństwa; filtrowanie i histereza; tryby | `dom-ev-energy-management/references/pv-bess-taryfy-sygnaly.md:8-15` | nieprzenośne (próg 6 A z IEC, reszta to praktyka) | P | — |
| EM17 | Magazyn energii (BESS): peak shaving, rezerwa SoC, osobna pętla w EMS | `dom-ev-energy-management/references/pv-bess-taryfy-sygnaly.md:17-22` | nieprzenośne | P | — |
| EM18 | Plan cenowy: najpierw wykonalność terminu, potem tanie sloty; taryfy strefowe OSD (G12, C12) | `dom-ev-energy-management/references/pv-bess-taryfy-sygnaly.md:24-30` | procedura jako R; taryfy strefowe to D08.05 | R | taryfy OSD: Prawo energetyczne i taryfy URE — do rejestracji |
| EM19 | Sygnał OSD → limit w A lub kW na okres, dołączony jako kolejne minimum, z zapisanym źródłem | `dom-ev-energy-management/references/pv-bess-taryfy-sygnaly.md:32-43` | **Wniosek** w `sterowanie-i-topologie.md` §3–4 (SC.01, `[201-P2 §3.11]`); OpenADR, IEEE 2030.5 i EEBUS tylko z nazwy | R | OpenADR/EEBUS: **niedostępne** (`niedostepne.yaml:161`); IEEE 2030.5: **niedostępne** (`:82`) |
| EM20 | Bilans w punkcie przyłączenia: `sieć = budynek + EV + ładowanie BESS − PV − rozładowanie BESS`, mierzony na liczniku OSD | `dom-ev-energy-management/references/pv-bess-taryfy-sygnaly.md:3-6` | nowa sekcja planowania | R | — |
| EM21 | Scenariusze testowe z liczbami: DLM D1–D7, zajezdnia Z1–Z6, awarie A1–A5; niezmiennik „suma na fazie ≤ limit w każdym slocie” | `dom-ev-energy-management/references/scenariusze-testowe.md:3-40` | scenariusze w `evals/skill_evals/ev-energy-smart-charging-expert.json` albo testy skryptu (sekcja 7) | R | — |
| EM22 | Dopuszczalna asymetria prądów faz | `dom-ev-energy-management/references/algorytmy-podzialu.md:44` | wpis „nie opracowano” | F | instrukcje sieciowe OSD i normy instalacyjne — źródło nieustalone, **do rejestracji** albo do niedostepne.yaml |

## 3. dom-ev-v2x → ev-energy-smart-charging-expert (`references/v2x-der-ocpp21.md`)

**Pokrycia:**
- OCPP 2.1 blok Q i R w całości: setpoint, `limit`/`dischargeLimit`, tryby, autoryzacja V2X, profile dynamiczne, FCR/aFRR, Q09, offline, DER;
- położenie falownika w AC i DC `[21-P2 R §1]`;
- definicje V2G/V2H/V2B/V2L `[21-P2 Q §1]`;
- AFIR: bidirectional recharging i ocena potencjału.

pack-ev uważa OCPP 2.1 za niedostępne, a ev-intelligence je ma (`21-P0`, `21-P2`, `21-E`).

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| VX1 | Kryterium V2G vs V2H/V2B: czy energia przechodzi przez licznik przyłącza; zero-export wymaga pomiaru na przyłączu; V2L poza CSMS | `dom-ev-v2x/SKILL.md:17-28` | `v2x-der-ocpp21.md` §1 jako **Wniosek** (V2L bez OCPP jest już zacytowane) | P | (częściowo `21-P2 Q §1`) |
| VX2 | Pola BPT z ISO 15118-20 według josev: `ServiceV20`, `ControlMode`, `BPTChannel`, `GeneratorMode`, `GridCodeIslandingDetectionMode`, pola `…DischargePower/Current`, `ScheduleTuple`, `BPT_ChannelSelection` | `dom-ev-v2x/SKILL.md:32-59`, `references/bpt-iso15118-20.md:1-64` | nieprzenośne (byłoby to ev-iso15118-pki-expert, poza grupą) | F | **niedostępne**: ISO 15118-20 (`niedostepne.yaml:21`); josev to źródło wtórne |
| VX3 | Grid-forming vs grid-following, ochrona przed pracą wyspową, tryb awaryjny V2H | `dom-ev-v2x/SKILL.md:21,66-67,120` | wpis „nie opracowano” (już jest w `v2x-der-ocpp21.md` §15) | F | **niedostępne**: ISO 15118-20, IEEE 1547, VDE-AR-N 4105 |
| VX4 | Kodeks sieciowy RfG, rozporządzenie (UE) 2016/631, jako podstawa wymogów przyłączeniowych dla V2G | `dom-ev-v2x/references/luki-i-weryfikacja.md:8` | `v2x-der-ocpp21.md` §15 | F | rozporządzenie (UE) 2016/631, EUR-Lex — **do rejestracji** |
| VX5 | RED III art. 20a ust. 4 (funkcje dwukierunkowe w punktach niepublicznych), ust. 3 i ust. 5 w kontekście V2X | `dom-ev-v2x/SKILL.md:86-94` | `sterowanie-i-topologie.md` §7 (razem z SC1/EM2) | F | 2023/2413 — **do rejestracji** |
| VX6 | Rozliczenie energii oddanej: osobne rejestry importu i eksportu, measurand `Energy.Active.Export.Register`; jeden rejestr netto nie wystarcza | `dom-ev-v2x/SKILL.md:96-99`, pułapka `:139` | `v2x-der-ocpp21.md`, nowa sekcja „Pomiar i rozliczenie”; nowe measurandy bloku J z `[21-P0 rozdz. 2]` | F | `S16`, `201-P3`, `21-P3` — zarejestrowane (enum już w `ev-ocpp-expert/references/komunikaty-16.md:83`) |
| VX7 | OCPI CDR: `total_energy` to jedna wartość, brak pola energii oddanej → eksport wymaga umowy lub rozszerzenia | `dom-ev-v2x/SKILL.md:100-101`, `references/luki-i-weryfikacja.md:7` | ev-billing-tariff-expert (`cdr-i-wycena.md`) i odsyłacz w v2x | F | `OCPI230` §10 (CDR), `OCPI221` — zarejestrowane; sprawdzić, czy 2.3.0 nie dodało pola |
| VX8 | Zgoda kierowcy na rozładowanie (kto, kiedy, zakres, wycofanie), minimalny SoC, gwarancja i degradacja | `dom-ev-v2x/SKILL.md:106-112` | Pułapki i Procedura V2X jako R; parametry V2X z `NotifyEVChargingNeeds` są już w `v2x-der-ocpp21.md` §5 | P | (MinimumSOC: ISO 15118-20 niedostępne) |
| VX9 | Modele biznesowe V2X: arbitraż, elastyczność, peak shaving w V2B, zasilanie awaryjne V2H | `dom-ev-v2x/SKILL.md:114-122` | nieprzenośne (fakty FCR/aFRR już są) | P | — |
| VX10 | Podatki i ceny energii oddanej | `dom-ev-v2x/SKILL.md:103-104` | wpis „nie opracowano” | P | — |
| VX11 | Zakres rozładowania = przecięcie wartości pojazdu i stacji (moc i prąd) | `dom-ev-v2x/SKILL.md:128-129,138` | Pułapki V2X jako R (`EVSE.DischargePower` `[201-CSV]` już jest) | R | — |

## 4. dom-ev-charger-hardware → ev-evse-hardware-expert (D02, D03)

**Pokrycia:**
- złącza w UE według AFIR aneks II;
- `ConnectorEnumType`/OCPI `standard`/`format`/`power_type`;
- klasy mocy AFIR;
- jeden punkt AFIR to jeden pojazd naraz;
- statusy OCPP 1.6/2.0.1 (`ev-cpms-architect/references/model-statusow.md:8-9`);
- `SuspendedEV`/`SuspendedEVSE` `[16 §7.7]` (`ev-charging-operations-expert/references/diagnostyka.md:37-41`);
- `GroundFailure` `[16 §7.6]`;
- Signed Meter Values `OCA-AN-SMV`, Eichrecht `DE-MESSEG-33`, MID (ev-compliance-expert).

ev-intelligence ma scenariusz `norma-platna-styki`, który oczekuje **odmowy** odpowiedzi z norm IEC. Prawie cała treść
sprzętowa pack-ev (CP, PWM, PP, tryby, RCD) pochodzi z tych norm i ze źródeł wtórnych. Nie wolno jej przenieść.

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| HW1 | Stany Control Pilot A–F i ich napięcia | `dom-ev-charger-hardware/SKILL.md:26-38`, `references/fakty-do-weryfikacji.md:7-8` | nieprzenośne; najwyżej zdanie „zależy od IEC 61851-1” | F | **niedostępne**: IEC 61851-1 (`niedostepne.yaml:27`); SAE J1772 **brak nawet w niedostepne.yaml** → dopisać |
| HW2 | Tabela stan CP → status OCPP (np. B w transakcji = `SuspendedEV`, C przy 0 A = `SuspendedEVSE`) | `dom-ev-charger-hardware/SKILL.md:29-44` | strona OCPP jest już zacytowana; samo mapowanie pack-ev nazywa „konwencją producentów” (`:44`) → ewentualnie wpisy D21 | P | (OCPP: `16 §7.7`, `201-P2 §3.23`, już w ev-intelligence) |
| HW3 | Wzory PWM → prąd (D × 0,6 A; (D − 64) × 2,5 A), przeliczenie odwrotne, przykłady 16/32/63 A | `dom-ev-charger-hardware/SKILL.md:46-60` | nieprzenośne | F | **niedostępne**: IEC 61851-1 Annex A; SAE J1772 (dopisać) |
| HW4 | Wypełnienie 3–7 % (5 %) = komunikacja cyfrowa ISO 15118 | `dom-ev-charger-hardware/SKILL.md:53,59-60,147` | nieprzenośne | F | **niedostępne**: IEC 61851-1, ISO 15118-3 |
| HW5 | Rezystor PP → prąd kabla (1,5 kΩ/13 A … 100 Ω/63 A); Type 2 obcina PWM do limitu kabla | `dom-ev-charger-hardware/SKILL.md:62-74` | nieprzenośne | F | **niedostępne**: IEC 61851-1 Annex B, EN IEC 62196-2 (`niedostepne.yaml:33`) |
| HW6 | Tryby Mode 1–4 i ich limity prądu | `dom-ev-charger-hardware/SKILL.md:76-83` | nieprzenośne (AFIR aneks II używa nazw trybów, to jest już opisane) | F | **niedostępne**: IEC 61851-1, EN 61851-23-1 |
| HW7 | Złącza poza UE: USA Type 1 i NACS (SAE J3400, daty TIR 2023-12-18 i RP 2024-09-30), Japonia CHAdeMO | `dom-ev-charger-hardware/SKILL.md:85-94` | `zlacza-i-moc.md` §1 (enum `SAE_J3400` z OCPI już jest); daty statusu tylko po rejestracji | F | SAE J3400 — **do rejestracji** albo do niedostepne.yaml (sae.org niedostępne z sesji researchera pack-ev); CHAdeMO: **niedostępne** (`:161`) |
| HW8 | Prąd dostępny = minimum z PWM, kabla (PP), profilu, zabezpieczenia i ładowarki pokładowej (OBC) | `dom-ev-charger-hardware/SKILL.md:21-22`, checklista `:154` | `zlacza-i-moc.md` §2 jako **Wniosek**, z wyraźnym znacznikiem, że PWM i PP są w normie nieopracowanej | R | — |
| HW9 | RCD typu B albo typu A + RDC-DD 6 mA DC; po zadziałaniu `Faulted` i często ponowne wpięcie | `dom-ev-charger-hardware/SKILL.md:111-116` | nieprzenośne (tylko `GroundFailure` `[16 §7.6]`, już jest) | F | **niedostępne**: IEC 61851-1 §8.5, IEC 60364-7-722 (`:45`); IEC 62955 **brak w niedostepne.yaml** → dopisać |
| HW10 | MID + dyrektywa (UE) 2026/706: MI-011 „system pomiarowy EVSE” (AC i DC, klasy A/B/C, MMQ, stosowanie od 10.10.2028) | `dom-ev-charger-hardware/SKILL.md:121`, `references/fakty-do-weryfikacji.md:16` | `ev-compliance-expert/references/metrologia.md` + pole „klasa licznika” w `ev-evse-hardware-expert/references/karta-urzadzenia.md` | F | 2026/706 — **do rejestracji**. Najpierw trzeba sprawdzić w EUR-Lex, czy akt istnieje i co zawiera: pack-ev ma to ze źródeł wtórnych, a `MID` w rejestrze to tylko tekst pierwotny |
| HW11 | USA: NIST HB44 §3.40 (EV Fueling Systems) | `dom-ev-charger-hardware/SKILL.md:125` | poza zakresem (UE/PL/DE); co najwyżej niedostepne.yaml | F | NIST HB44 — do rejestracji, niski priorytet |
| HW12 | Wzory mocy z √3 × 400 V; USA 120/240 V split-phase (Level 1/2) | `dom-ev-charger-hardware/SKILL.md:96-109` | wzór dla UE jest już z `[16 §7.12]`; część USA nieprzenośna (OCPI `AC_2_PHASE_SPLIT` jest) | R | — |
| HW13 | Type 1 bez PP; gniazdo kontra kabel stały ustala limit kabla | `dom-ev-charger-hardware/SKILL.md:72-74,146` | nieprzenośne | F | **niedostępne**: IEC 61851-1, IEC 62196 |

## 5. dom-ev-vehicle-battery → brak skilla docelowego

W ev-intelligence nie ma skilla „pojazd i bateria”. Taksonomia przypisuje D04 (pojazd, bateria, interakcja EV–EVSE)
do **ev-evse-diagnostics-expert** (`skills/ev-domain-expert/references/taksonomia-drzewo.md:17,342-380`). Najbliższe
miejsca:
- „ładuje wolno”: ev-evse-diagnostics-expert albo `ev-charging-operations-expert/references/diagnostyka.md`, który ma
  już `SuspendedEV`/`SuspendedEVSE`;
- „limit ≠ pobór”: ev-energy-smart-charging-expert;
- ETA w aplikacji: ev-product-designer.

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| VB1 | Pojęcia BEV, PHEV, HEV, FCEV; pojemność nominalna vs użytkowa; BMS, SoC, SoH, OBC | `dom-ev-vehicle-battery/SKILL.md:16-27` | ev-domain-expert (glosariusz) albo ev-evse-diagnostics-expert. Definicje BEV/PHEV sprawdzić w `[AFIR art. 2]`; AFIR art. 3 jest już cytowany w `ev-compliance-expert/references/afir-mapa.md:8` | P | częściowo `AFIR` art. 2 (zarejestrowane), reszta bez źródła |
| VB2 | „Ładowarka oferuje, auto decyduje”: AC przez PWM, DC przez żądanie prądu i napięcia (DIN 70121, ISO 15118) | `dom-ev-vehicle-battery/SKILL.md:29-40` | strona OCPP jest już zacytowana (`[OCPI230 §14]`, `Current.Offered`); część pojazdu nieprzenośna | F | **niedostępne**: IEC 61851-1, DIN SPEC 70121 (`:51`), ISO 15118 |
| VB3 | Kształt krzywej ładowania, zasada 10–80 %, temperatura, preconditioning | `dom-ev-vehicle-battery/SKILL.md:42-59` | nieprzenośne. D04.02 ma w taksonomii katalog `knowledge/vehicle/charging-curves/`, który nie istnieje, a `knowledge/` przyjmuje tylko obserwacje modelu i firmware (klasa D) | P | — |
| VB4 | OBC i fazy: auto 1-fazowe na stacji 3-fazowej ≈ 7,4 kW; OCPI `PowerType` opisuje ładowarkę, nie auto | `dom-ev-vehicle-battery/SKILL.md:61-70` | część jest już w przykładzie `profile-ocpp.md:104-106` (`[201-P2 K01.FR.49]`); reszta jako Wniosek | P | częściowo `201-P2` K01.FR.49, `OCPI230 §8` |
| VB5 | 400 V i 800 V: zakres napięcia stacji ogranicza moc; „150 kW” nie mówi, ile dostanie auto | `dom-ev-vehicle-battery/SKILL.md:72-81` | pole zakresu napięcia w karcie urządzenia (`karta-urzadzenia.md`) jako R; `max_voltage`/`max_amperage` już są | P | — |
| VB6 | Siedem przyczyn, dla których CSMS widzi mniej niż moc nominalna | `dom-ev-vehicle-battery/SKILL.md:83-91` | ev-evse-diagnostics-expert albo `ev-charging-operations-expert/references/diagnostyka.md` | R | — |
| VB7 | SoC w `MeterValues` tylko wtedy, gdy stacja ma go od auta; w AC zwykle brak → SoC w modelu jako `null` | `dom-ev-vehicle-battery/SKILL.md:93-98` | ev-cpms-architect (model sesji) jako Wniosek; measurand `SoC` z `[S16]`/`[201-P3]` | F | `S16`, `201-P3` — zarejestrowane; „AC bez SoC” zależy od IEC 61851 (niedostępne) |
| VB8 | Model ETA odcinkowy i przeliczanie w trakcie sesji; pokazywanie przedziału | `dom-ev-vehicle-battery/SKILL.md:100-109`, `references/krzywa-i-eta.md:18-57` | ev-product-designer (poza grupą) jako R; liczby z przykładu to ilustracja | R | — |
| VB9 | Drzewo przyczyn „ładuje wolno” z pytaniami do kierowcy i formatem odpowiedzi dla supportu | `dom-ev-vehicle-battery/references/ladowanie-wolno-drzewo.md:1-33` | `ev-charging-operations-expert/references/diagnostyka.md` albo ev-evse-diagnostics-expert | R | (kroki OCPP: `16 §7.7`, measurandy — zarejestrowane) |
| VB10 | Dane z API producenta; RED III art. 20a ust. 3; paszport baterii, rozporządzenie (UE) 2023/1542 | `dom-ev-vehicle-battery/SKILL.md:115-121` | ev-compliance-expert (D12) | F | 2023/2413 i 2023/1542 — **do rejestracji** |
| VB11 | Pola DC ISO 15118-2/-20 (`EVTargetCurrent`, `RemainingTimeToFullSoC`, `EVMaximumChargePower`…) według josev | `dom-ev-vehicle-battery/SKILL.md:35-40` | nieprzenośne | F | **niedostępne**: ISO 15118 |

## 6. dom-ev-fleet-charging → brak skilla docelowego

Taksonomia: D19.03 (miejsce pracy, zwrot za ładowanie w domu) i D19.04 (floty i zajezdnie) należą do
**ev-domain-expert** (`taksonomia-drzewo.md:1095-1108`). Treść rozkłada się jednak na skille poza grupą:
- ev-billing-tariff-expert: koszty, zwrot, taryfa zerowa;
- ev-ocpi-roaming-expert: tokeny;
- ev-ocpp-expert: IdTokenInfo;
- ev-cpms-architect: model danych;
- ev-compliance-expert: EPBD, PL-EMOB.

**Pokrycia:**
- taryfa bezpłatna `FLAT` 0.00 (`ev-billing-tariff-expert/references/taryfy-ocpi.md:33`, `cdr-i-wycena.md:19`);
- `whitelist` (`ev-ocpi-roaming-expert/references/moduly.md:93-104`);
- `publish_allowed_to` (ev-ocpi, ev-product-designer);
- `groupIdToken` w `RequestStartTransaction`.

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| FL1 | Karta na kierowcę, na auto czy obie (zalety, wady, kiedy) | `dom-ev-fleet-charging/SKILL.md:31-40` | nieprzenośne | P | — |
| FL2 | Model danych organizacja → centrum kosztów → kierowca → token → auto, z przypisaniami z okresem ważności; raport łączy sesję z przypisaniem z chwili startu; korekty zamiast nadpisań | `dom-ev-fleet-charging/references/model-danych-i-uprawnienia.md:5-31,60-63` | ev-cpms-architect (model danych) jako R | R | — |
| FL3 | Polityki flotowe (lokalizacje, godziny, limity kWh i kwotowe); limity kwotowe wymagają kosztu w trakcie sesji (rola eMSP), CPO wymusza tylko lokalizację i ważność | `dom-ev-fleet-charging/SKILL.md:42-45` | ev-ocpi-roaming-expert jako R; podstawa: real-time authorization `[OCPI230]` (już jest) | R | — |
| FL4 | OCPI `AuthorizationInfo.allowed` (`ALLOWED`, `NOT_ALLOWED`, `BLOCKED`, `EXPIRED`, `NO_CREDIT`) i `LocationReferences`; bez lokalizacji eMSP nie oceni polityki („tylko te lokalizacje” wymaga real-time, nie `ALWAYS`) | `dom-ev-fleet-charging/references/model-danych-i-uprawnienia.md:33-40` | `ev-ocpi-roaming-expert/references/moduly.md` (dziś brak `AuthorizationInfo`) | F | `OCPI230` (moduł Tokens) — zarejestrowane; kod 2002 jest w `transport.md:67` |
| FL5 | OCPP 2.0.1 `IdTokenInfo`: `evseId` (token tylko na wybranych EVSE), `groupIdToken`, `cacheExpiryDateTime` (krótko dla gości), `chargingPriority`; 1.6 `parentIdTag` (≤ 20 znaków) | `dom-ev-fleet-charging/references/model-danych-i-uprawnienia.md:42-51`, `:19` | ev-ocpp-expert (`komunikaty-201.md`, `komunikaty-16.md`) | F | `201-P3`, `201-P2` blok C, `S16` — zarejestrowane |
| FL6 | Sesja OCPI: `total_cost` = 0 oznacza darmową, brak pola nie oznacza darmowej; darmowa oferta ma niezerowy koszt wewnętrzny | `dom-ev-fleet-charging/references/praca-b2b-budynki.md:12-20` | ev-billing-tariff-expert | F | `OCPI230` (Sessions/CDR) — zarejestrowane, sprawdzić brzmienie |
| FL7 | Zamówienie wallboxa pracownika: kwalifikacja, audyt instalacji, zgody, montaż, uruchomienie, podłączenie do CSMS | `dom-ev-fleet-charging/SKILL.md:58-67`, `references/ladowanie-domowe-zwrot.md:5-20` | nieprzenośne poza odsyłaczem do PL-EMOB art. 12b (FL12) i IEC 60364-7-722 (niedostępne) | P | — |
| FL8 | Zwrot kosztów energii: rodzaje stawek, stawka wersjonowana od daty, wzór, eksport do płac, korekty jako osobne wiersze | `dom-ev-fleet-charging/SKILL.md:69-75`, `references/ladowanie-domowe-zwrot.md:22-38,59-66` | ev-billing-tariff-expert jako R | R | — |
| FL9 | Oddzielenie sesji służbowych od prywatnych: token auta służbowego, EMAID w Plug & Charge, potwierdzenie w aplikacji, telematyka | `dom-ev-fleet-charging/SKILL.md:77-80`, `references/ladowanie-domowe-zwrot.md:40-47` | ev-billing-tariff-expert jako R; EMAID w ev-iso15118-pki-expert | R | — |
| FL10 | Zasady RODO dla danych domowych (cel, minimalizacja, podstawa, retencja, dostęp) | `dom-ev-fleet-charging/references/ladowanie-domowe-zwrot.md:49-57` | ev-compliance-expert | F | rozporządzenie (UE) 2016/679 — **do rejestracji** (brak też w niedostepne.yaml) |
| FL11 | Podział kosztów między najemców: licznik ładowarki jako źródło, koszty zmienne i stałe, klucz z umowy | `dom-ev-fleet-charging/references/praca-b2b-budynki.md:22-28` | ev-billing-tariff-expert jako R | R | — |
| FL12 | Ustawa o elektromobilności: art. 12 ust. 1, art. 12a ust. 1–2, art. 12b ust. 1–4 (zgoda zarządu wspólnoty, punkt < 11 kW jako czynność zwykłego zarządu, ekspertyza w 30 dni) | `dom-ev-fleet-charging/references/praca-b2b-budynki.md:43-51`, `SKILL.md:66-67` | `ev-compliance-expert/references/prawo-pl.md` (art. 12–12c oznaczone „nie opracowano”) | F | `PL-EMOB` — **zarejestrowane** |
| FL13 | EPBD art. 14 ust. 1, 2, 4, 6, 7; art. 16 ust. 1; transpozycja art. 35 (29.05.2026) | `dom-ev-fleet-charging/references/praca-b2b-budynki.md:30-41` | ev-compliance-expert (D12) + odsyłacz z ev-energy (EM3) | F | 2024/1275 — **do rejestracji** |
| FL14 | Przykład duński i różnice krajowe | `dom-ev-fleet-charging/SKILL.md:65`, `references/ladowanie-domowe-zwrot.md:17-18` | nieprzenośne | P | — |
| FL15 | Raport floty: kolumny, agregaty, koszt na kWh i na 100 km, kolumna „do wyjaśnienia” | `dom-ev-fleet-charging/SKILL.md:47-50`, `references/model-danych-i-uprawnienia.md:53-58` | ev-cpms-architect albo ev-product-designer jako R | R | — |

---

## 7. Skrypty i testy

| Katalog | Co robi | Odpowiednik w ev-intelligence | Zależności | Testy | Gdzie pasuje |
|---|---|---|---|---|---|
| `dom-ev-smart-charging/scripts/composite_schedule.py` (227 l.) | Liczy composite schedule z profili OCPP 1.6 i 2.0.1 (lista, `{"profiles"}` albo ładunki `SetChargingProfile`): grupy Max, External, TxDefault i Tx, najwyższy stackLevel w grupie, Absolute/Relative/Recurring, validFrom/To, `duration`, A↔W i fazy, częściowa walidacja K01; kody 0, 1, 2; `--default-limit 48` | **brak**. W ev-intelligence jedyny skrypt skilla to `skills/ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py`; w `tools/` są `ev_kb*`, `skill_*`, `render_taxonomy`, `factory_check`, bez kalkulatora profili | tylko biblioteka standardowa (`argparse`, `datetime`, `json`, `math`, `sys`, `pathlib`), bez sieci | `packs/pack-ev/tests/test_composite_schedule.py`: 22 asercje, w tym C-1…C-5 z testów libocpp, C-6/C-7 z dokumentacji libocpp, walidacja i kody wyjścia. Pośrednio `test_depot_smart_charging.py`: 10 asercji, pomijany bez `examples/` | `ev-energy-smart-charging-expert/scripts/` |
| (spoza grupy, ale używany przez dom-ev-energy-management) `tf/examples/depot-smart-charging/depot.py` (117 l.) | Plan zajezdni EDF w slotach pod limit przyłącza → `TxProfile` na EVSE; próg < 6 A → 0; kod 1 przy niespełnionym pojeździe | brak | tylko biblioteka standardowa | `test_depot_smart_charging.py` (10 asercji) | ewentualnie `ev-energy-smart-charging-expert/scripts/` jako heurystyka R |
| `dom-ev-energy-management`, `dom-ev-v2x`, `dom-ev-charger-hardware`, `dom-ev-vehicle-battery`, `dom-ev-fleet-charging` | **nie mają katalogu `scripts/`** | — | — | tylko scenariusze `tests/skill_evals/dom-ev-*.json` (5, 3, 4, 3, 3) | — |

**Werdykt dla `composite_schedule.py`: wart przeniesienia, ale tylko po przebudowie reguł na specyfikację OCA.** Dziś
koduje zachowanie libocpp, a zasada źródeł wyklucza libocpp jako dowód. Zmiany są niezbędne:
1. **Brak profili:** wynik „bez limitu” zamiast 48 A `[16 §3.13.6]` `[201-P2 K06.FR.02]`. Wartość 48 A może zostać
   najwyżej jako jawna opcja testowa (konflikt K1).
2. **Wybór w stosie zależny od wersji:** w 1.6 obowiązuje najwyższy ważny `stackLevel` `[16 §3.13.2]` `[16E §3.7]`, a w
   2.0.1 profil z okresem zdefiniowanym w danej chwili `[201-P2 K §3.5]`. Skrypt stosuje jedną regułę (konflikt K4).
3. **Recurring z krótkim `duration`:** zachowanie domyślne według K01.FR.13, nie „limit domyślny 48 A”.
4. **Dopisanie reguł,** których skrypt nie ma:
   - K01.FR.14 i K01.FR.52–53 (`TxDefaultProfile` na EVSE 0 kontra na konkretnym EVSE);
   - K01.FR.43–45 (fazy);
   - `phaseToUse`;
   - SC.01.
5. **Komunikaty walidacji** z numerami K01.FR zamiast kodów libocpp.
6. **Testy:** C-1…C-7 trzeba przeliczyć według specyfikacji. C-6a oczekuje dziś 48 A, co jest sprzeczne z K06.FR.02.
   Pliki mają postać `main()`, a bramka ev-intelligence uruchamia `python3 -m unittest discover tests`, więc bez
   przepisania na `unittest.TestCase` nic by się nie uruchomiło. Ścieżkę `ROOT` szukają przez `.claude/hooks`, czyli
   według układu tf.

`depot.py` nie niesie faktów poza progiem 6 A (IEC, niedostępne). Może trafić do ev-intelligence tylko jako przykład
heurystyki z progiem jako parametrem, a nie stałą „z normy”.

Scenariusze `tests/skill_evals/dom-ev-*.json` mają ten sam format co ev-intelligence (`id`, `expect`, `prompt`,
`checks`). Do przeniesienia po przepisaniu `checks` na odpowiedzi zgodne ze specyfikacją nadają się:
- `dlm-fazy-budynek-v2`, `zajezdnia-edf-niespelnione`, `offline-pv-bess-fail-safe` (energy);
- `max-w-vs-txdefault-a`, `policz-composite-bez-stacji` (smart-charging);
- `b2b-za-darmo-i-uprawnienia` (fleet).

Scenariusz `domyslny-limit-48-vs-zero` przenieść tylko z odwróconym oczekiwaniem (specyfikacja: bez profili brak limitu).
Scenariusze sprzętowe (`pwm-prad-kabel-pp`, `stany-cp-a-status-ocpp`) w ev-intelligence stają się scenariuszami odmowy,
na wzór `norma-platna-styki`.

---

## 8. Konflikty (różne twierdzenia o tym samym)

| # | Temat | pack-ev | ev-intelligence | Rozstrzygnięcie |
|---|---|---|---|---|
| K1 | Stacja bez profili | „limit domyślny nieznany (0 albo 48 A)”: `dom-ev-smart-charging/SKILL.md:62-67,139`; `references/composite-schedule-libocpp.md:22-35`; `references/testowanie-i-prawo.md:22` | „Bez żadnych profili stacja ładuje bez ograniczeń” `[201-P2 K06.FR.02]` `[16 §3.13.6]`: `skills/ev-energy-smart-charging-expert/SKILL.md:58`, `references/profile-ocpp.md:133` | specyfikacja OCA; 48 A to zachowanie libocpp |
| K2 | Bezpieczny limit offline przez `TxDefaultProfile` | `TxDefaultProfile` jako bezpieczny limit lub bezpiecznik, „suma domyślnych limitów ≤ przyłącze (limit ÷ liczba stacji)”: `dom-ev-smart-charging/SKILL.md:25,89-90,149`; `dom-ev-energy-management/SKILL.md:24`; `references/architektura-odpornosc.md:20` | `TxDefaultProfile` na EVSE 0 działa na każde EVSE osobno (K01.FR.14), więc przy kilku EVSE nie chroni przyłącza; trwały limit to `ChargingStationMaxProfile` (łącznie, K04.FR.05): `SKILL.md:63-69`, `references/profile-ocpp.md:137-140` | ev-intelligence; pack-ev jest poprawny tylko dla stacji z jednym EVSE |
| K3 | Dwa profile o tym samym celu i `stackLevel` | „wynik zależy od stacji; może być Rejected”: `dom-ev-smart-charging/SKILL.md:141` | 1.6: nowy zastępuje stary `[16 §3.13.2]`; 2.0.1: CSMS SHALL NOT (K01.FR.06), EVSE 0 kontra EVSE → `DuplicateProfile` (K01.FR.52–53): `references/profile-ocpp.md:34-36,57-59,62-64` | specyfikacja |
| K4 | Wybór profilu w stosie | jedna reguła dla obu wersji („w każdej chwili aktywny profil o najwyższym stackLevel”, poza `duration` nieaktywny): `dom-ev-smart-charging/SKILL.md:58`; `scripts/composite_schedule.py:15-17` | reguła zależy od wersji: 1.6 najwyższy ważny (`[16 §3.13.2]`, najwyższy bez `duration` blokuje niższe `[16E §3.7]`), 2.0.1 profil z okresem zdefiniowanym w danej chwili `[201-P2 K §3.5]`: `SKILL.md:72-74`, `references/profile-ocpp.md:56-69` | ev-intelligence; skrypt wymaga zmiany |
| K5 | Numer K01.FR.03 | przypisany zarówno do „sufit stacji z `evseId` > 0”, jak i do „`TxProfile` bez `transactionId`”: `dom-ev-smart-charging/references/walidacja-k01.md:20,25` | K01.FR.03 = CSMS SHALL podać `transactionId` przy `TxProfile`: `references/profile-ocpp.md:28-29` | sprawdzić w `[201-P2 K01]`; mapowanie libocpp dla sufitu stacji jest prawdopodobnie błędne |
| K6 | Znak limitu przy V2X | „Ujemny limit w profilu = polecenie oddawania mocy”, „Backend (2.1) wysyła profil z ujemnym limitem”, OCPP 2.1 „[do weryfikacji]”: `dom-ev-v2x/SKILL.md:79,81,131,137`; `references/luki-i-weryfikacja.md:5-6` | OCPP 2.1: `limit` tylko dodatni, rozładowanie przez ujemny `dischargeLimit` i znak `setpoint` (V2X.03–05) `[21-P2 Q §2.1]` `[21-P2 Q §2.5]`: `references/v2x-der-ocpp21.md:33-44` | ev-intelligence (OCPP 2.1 jest w rejestrze) |
| K7 | Odesłanie RED III art. 20a ust. 4 do AFIR art. 15 ust. 3–4 | „nie pasuje do tekstu AFIR (art. 15 ust. 3 to ocena elastyczności)”, „nie wyprowadzaj obowiązków”: `dom-ev-smart-charging/references/testowanie-i-prawo.md:49-50`; `dom-ev-energy-management/references/przepisy-przylacze.md:16-17`; `dom-ev-v2x/SKILL.md:90-91` | AFIR art. 15 ust. 3–4 to ocena wsparcia elastyczności i **potencjału ładowania dwukierunkowego** przez regulatora `[AFIR art. 15 ust. 3–4]`: `references/sterowanie-i-topologie.md:121-125`. RED III mówi o funkcjach dwukierunkowych „zgodnie z art. 15 ust. 3 i 4”, więc odesłanie może być trafne | do rozstrzygnięcia po rejestracji RED III; dosłownie porównać RED III art. 20a ust. 4 z `[AFIR art. 15]` |
| K8 | Początek profilu `Relative` | „początek = start transakcji”: `dom-ev-smart-charging/SKILL.md:41` | zaleca się liczyć od gotowości do dostarczania energii (po autoryzacji i podłączeniu), K01.FR.42: `references/profile-ocpp.md:43-44` | specyfikacja (różnica w niuansie) |
| K9 | Moc 3 × 16 A | 11,1 kW (400 × 16 × 1,732): `dom-ev-charger-hardware/SKILL.md:99,105`. W samym pack-ev: 11,04 kW, `dom-ev-energy-management/references/algorytmy-podzialu.md:9` | W = A × napięcie nominalne fazowe (230 V) × `numberPhases` `[16 §7.12]` `[201-P2 K01.FR.50]` → 11,04 kW: `references/profile-ocpp.md:88-89` | dla przeliczeń OCPP: 230 V × fazy |
| K10 | Pomiar DC w MID | MID + 2026/706 obejmuje DC (MI-011): `dom-ev-charger-hardware/SKILL.md:121`; `references/fakty-do-weryfikacji.md:16` | „Dyrektywa nie mówi wprost o licznikach prądu stałego… wymaga potwierdzenia”; sprawdzono tylko tekst pierwotny MID: `skills/ev-compliance-expert/references/metrologia.md:38-39`, `sources/eu-inne.yaml` (MID) | ewentualna aktualizacja ev-intelligence po rejestracji 2026/706; dziś pack-ev opiera się na źródłach wtórnych |
| K11 | `ExternalConstraints` z istniejącym `id` | „odrzucane (K01.FR.05)”: `dom-ev-smart-charging/references/walidacja-k01.md:23,36` | K01.FR.05: profil o znanym `id` jest zastępowany; CSMS nie zakłada ani nie zastępuje profili ExternalConstraints (K01.FR.05, K01.FR.22): `references/profile-ocpp.md:64`, `references/sterowanie-i-topologie.md:61-62` | sprawdzić brzmienie K01.FR.05 w `[201-P2]` |

**Nieaktualne „[do weryfikacji]” w pack-ev,** które ev-intelligence już rozstrzygnęło cytatem (nie są to konflikty):
- kto ustawia `ExternalConstraints`: `architektura-odpornosc.md:32-34` → `sterowanie-i-topologie.md:58-62` (K01.FR.22, errata K01.FR.62);
- `ClearedChargingLimit`: `komunikaty-i-pola.md:46` → `sterowanie-i-topologie.md:54-57` (K13);
- `TxProfile` po wygaśnięciu i offline: `dom-ev-smart-charging/SKILL.md:91` → `profile-ocpp.md:129-135`;
- statusy OCPP 2.x: `dom-ev-charger-hardware/SKILL.md:42-43` → `ev-cpms-architect/references/model-statusow.md:9`;
- odpowiedź `SetChargingProfile` 1.6 (`NotSupported`): `komunikaty-i-pola.md:14` → `profile-ocpp.md:123-124` (`[16E §3.38-3.39]`);
- OCPP 2.1 V2X/DER: `dom-ev-v2x/references/luki-i-weryfikacja.md:5` → `v2x-der-ocpp21.md` (całość).

---

## 9. Podsumowanie liczbowe

84 luki: **F 40**, **P 21**, **R 23**.

| Skill | luki | F | P | R |
|---|---|---|---|---|
| dom-ev-smart-charging | 12 | 7 | 2 | 3 |
| dom-ev-energy-management | 22 | 7 | 7 | 8 |
| dom-ev-v2x | 11 | 6 | 4 | 1 |
| dom-ev-charger-hardware | 13 | 10 | 1 | 2 |
| dom-ev-vehicle-battery | 11 | 4 | 4 | 3 |
| dom-ev-fleet-charging | 15 | 6 | 3 | 6 |

Faktów F (40) według statusu:
- **14 zarejestrowanych** (do przeniesienia po sprawdzeniu sekcji): SC2, SC3, SC7, SC11, SC12, EM1, EM15, VX6, VX7, VB7, FL4, FL5, FL6, FL12;
- **13 do rejestracji**: SC1, EM2, EM3, EM4, EM22, VX4, VX5, HW7, HW10, HW11, VB10, FL10, FL13. Dotyczą:
  - RED III 2023/2413 (SC1, EM2, VX5, VB10);
  - EPBD 2024/1275 (EM3, FL13);
  - Prawo energetyczne (EM4);
  - RfG 2016/631 (VX4);
  - RODO 2016/679 (FL10);
  - rozporządzenie bateryjne 2023/1542 (VB10);
  - 2026/706 (HW10);
  - SAE J3400 (HW7);
  - NIST HB44 (HW11);
  - asymetria faz według OSD (EM22);
- **13 niedostępnych** (IEC 61851-1, ISO 15118, DIN 70121, IEC 62196, IEC 60364-7-722): SC6, EM7, VX2, VX3, HW1, HW3, HW4, HW5, HW6, HW9, HW13, VB2, VB11.

Do dopisania w `niedostepne.yaml` (dziś ich brak): SAE J1772, SAE J3400, IEC 62955. Do rozważenia NIST HB44 oraz
Prawo energetyczne i rozporządzenia, jeśli nie zostaną zarejestrowane.
