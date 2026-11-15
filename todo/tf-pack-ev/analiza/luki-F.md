# Luki pack-ev → ev-intelligence (grupa F)

Analiza tylko do odczytu, 2026-11-15. Niczego nie edytowałem, nie commitowałem i nie pobierałem z sieci.
Ścieżki skrótowe: `PE/` = `/home/user/tf/packs/pack-ev/`, `EI/` = `/home/user/ev-intelligence/`.

Klasy luk:
- **F**: fakt, który da się sprawdzić w źródle oficjalnym. Przeniesienie wymaga pobrania źródła, SHA-256 i znacznika `[id §]`.
- **P**: wiedza praktyczna lub rynkowa bez źródła oficjalnego. Według CLAUDE.md nie wolno jej przenieść, chyba że ev-intelligence ma na nią miejsce.
- **R**: procedura albo heurystyka bez faktów. Może trafić do sekcji Procedura lub Pułapki skilla bez cytatu, o ile nie niesie liczb ani twierdzeń o normach.

Uwaga ogólna: w pack-ev nie ma żadnych znaczników `[id §]`. Opiera się na „imporcie 2024–2025” (blogi, materiały
marketingowe), „wiedzy ogólnej” z oznaczeniem **[do weryfikacji]** i na cache `kb:<id> doc.txt:Lnn`. Żadnego zdania nie da się
więc przenieść dosłownie. Nawet fakty z klasy F wymagają ponownego przeczytania źródła z rejestru EI.

**Stan EI w moim zakresie.**
- `knowledge/` zawiera tylko szablon `implementation-intelligence/vendor-quirks/_szablon.yaml`.
- Nie ma słownika (`glossary/` z `docs/PLAN.md:125` nie powstał) ani modelu kanonicznego (`data-model/` z PLAN 0.5).
- Poddomeny D00.01 (słownik), D00.02 (model kanoniczny), D17 (biznes), D18 (lokalizacje) i D19 (segmenty) istnieją w taksonomii, ale nie mają treści.
- `ev-product-designer` jawnie wyłącza ekonomikę (`EI/skills/ev-product-designer/references/wymagania-produktu.md` §7,
  `rynek-dane.md` §7), a `sources/niedostepne.yaml:156-160` zawiera wpis „Dane rynkowe i ekonomika stacji”.

---

## 1. dom-ev-charging

### Luki
| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Typy pojazdów BEV/PHEV/HEV/RE-EV/FCEV i reguła rozróżniania | `PE/skills/dom-ev-charging/references/pojazdy-elektryczne.md:139-154` | D00.01 słownik (ev-domain-expert) lub D04 (ev-evse-diagnostics-expert) | F (BEV, PHEV, wodór: definicje AFIR art. 2, do sprawdzenia w tekście) / P (HEV, RE-EV, liczby z UK) | `AFIR` (zarejestrowany); rozbieżność Eurostat „ELC” ≠ BEV już opisana w `rynek-dane.md:54` |
| Komponenty BEV (OBC, DC/DC, BMS, chłodzenie) | `pojazdy-elektryczne.md:156-176` | D04 | P | brak źródła oficjalnego (Renewable Energy Institute) |
| Sprawność, środowisko, drugie życie baterii, serwis, kompetencje, kontekst rynkowy | `pojazdy-elektryczne.md:178-255` | D20.04 (ESG, p3), D17.03 | P | brak; liczby (2 t CO₂, 23 %, 20 mln) nieprzenoszalne |
| EVCI jako termin | `infrastruktura-ladowania.md:9-14` | D00.01 | P | driveco.com; AFIR ma własne pojęcia (recharging point/station/pool) |
| Punkt ładowania vs stacja ładowania | `infrastruktura-ladowania.md:16-28` | D00.01 | F | `AFIR art. 2`, `PL-EMOB art. 2` (zarejestrowane); częściowo pokryte w `ev-cpms-architect/SKILL.md:41-42` |
| Limit AC = min(moc stacji, ładowarka pokładowa), typowo 3,7–22 kW | `infrastruktura-ladowania.md:40-55`, `SKILL.md:41-42` | D02/D04 (ev-evse-hardware-expert) | R (zasada min) / P (przedział kW) | IEC 61851 płatna (niedostepne) |
| Złącza według regionów i mocy (Type 1 3–7 kW, CHAdeMO „spada”, NACS) | `infrastruktura-ladowania.md:57-78` | `ev-evse-hardware-expert/references/zlacza-i-moc.md` (enumy już są) | P (region, trend, moc) | IEC 62196 i SAE J1772/J3400 płatne; enumy `[201-P2 §3.22]` `[OCPI230 §8.4.x]` już w EI |
| Instalacja domowa (2–4 h, kryteria wyboru wallboxa, load balancing z PV) | `infrastruktura-ladowania.md:80-97` | D19.02 (ev-domain-expert, p3) | P/R | IEC 60364-7-722 płatna (niedostepne) |
| Instalacja komercyjna: fazy i commissioning | `infrastruktura-ladowania.md:99-119` | D18.03–D18.04 (ev-charging-operations-expert) | R | — |
| UK Workplace Charging Scheme | `infrastruktura-ladowania.md:107-110` | D12.07 | P (lub F z gov.uk, region uk poza zakresem) | niezarejestrowany |
| Terminologia USA Level 1 / Level 2 / DC fast | `infrastruktura-ladowania.md:103, 126-128` | D00.01 (jako pojęcie mylone) | F/P, **konflikt K4** | SAE J1772 płatna; w AFIR-655 „Level 1/2” to kategorie DC |
| Archetypy domeny (Party, Availability, Pricing, Accounting) i niezmienniki (CDR niezmienny, outbox) | `SKILL.md:63-72` | D00.02 model kanoniczny (ev-domain-expert; brak `data-model/`) | R | — (niezmienność CDR: `OCPI230 §10`, w EI w ev-billing-tariff-expert) |
| Historia OCPP 1.2 (2009/10), 1.5 (2012), 2.0 (2018); OCA od 2014, 400+ członków | `references/ocpp.md:18, 25-28, 204` | `ev-ocpp-expert/references/wersje-i-status.md` | F | strona OCA „about” niezarejestrowana; `OCA-DL` ma tylko pobrania |
| Ekosystem: listy producentów, CPO, dostawców CPMS; skalowalność (AMPECO 70+, EV Connect) | `references/ocpp.md:200-245` | D17.03 | P | marketing, nieprzenoszalne |
| Testy fizyczne a symulacja | `references/ocpp.md:246-256` | D13 (ev-evse-diagnostics-expert) | R/P | — |
| Historia OCPI 2.0 (2015), 2.1.1 (~2017), 2.2 (2019) | `references/ocpi.md:89-103` | `ev-ocpi-roaming-expert/references/wersje-i-role.md` (ma 2.2, 2.2.1, 2.3.0, 3.0) | F | `EVRF-DL`, `EVRF-V25` (zarejestrowane), do sprawdzenia |
| OCPI 2.3.0 „Edition 2” z Invoice Reconciliation (planowana) | `references/ocpi.md:98` | `wersje-i-role.md` | F (do sprawdzenia) | `EVRF-DL` |
| Zapowiadane funkcje OCPI 3.0 (P&C, wiadomości, DSO, GDPR) | `references/ocpi.md:188-196` | `wersje-i-role.md:12-16` (są tylko daty) | F | `EVRF-V25` |
| Korzyści OCPI według ról | `references/ocpi.md:175-187` | D06 | P | — |
| SoC niedostępne bez ISO 15118 (pułapka modelu sesji) | `SKILL.md:86` | D04 / ev-energy-smart-charging-expert | F (częściowo) | measurand `SoC` jest w `[16]` (`komunikaty-16.md:87`); część ISO 15118 płatna (niedostepne) |
| Warstwa OpenADR (sieć ↔ EMS) | `SKILL.md:36`, `ocpp.md:190-198` | D01.09 | — | specyfikacja OpenADR w `niedostepne.yaml:161-165` |

### Nakładki (EI ma to samo lub więcej, z cytatami)
- Mapa warstw ISO 15118 / OCPP / OCPI (`SKILL.md:29-39`) jest w taksonomii D01 i w skillach `ev-integration-architect` oraz `ev-ocpp-expert`.
- Sesja end-to-end i cztery ścieżki autoryzacji (`SKILL.md:44-52`, `cykl-sesji-ladowania.md:39-108`): `START_SESSION` i preautoryzacja są w
  `ev-integration-architect/references/ocpp-ocpi-polaczenie.md`, `ev-ocpi-roaming-expert/references/moduly.md` i `ev-billing-tariff-expert`.
- Model Location → EVSE → Connector i „OCPI nie ma obiektu stacji” (`ocpi.md:34-88`) są w `ev-cpms-architect/SKILL.md:41-42` `[OCPI230 §8.1.2]`.
- Katalog komunikatów OCPP, profile bezpieczeństwa, smart charging i offline (`ocpp.md:95-189`) są w `ev-ocpp-expert`,
  `ev-iso15118-pki-expert` i `ev-energy-smart-charging-expert`. W EI są pełniejsze i z wymaganiami FR.
- ISO 15118 i Plug & Charge (`iso-15118.md`): EI ma `ev-iso15118-pki-expert`. Norma jest płatna (niedostepne).

---

## 2. dom-ev-glossary

### Czy EI ma rejestr terminów?
**Nie.** Taksonomia ma poddomenę **D00.01 „Słownik terminologii”** (`EI/taxonomy/taxonomy.yaml:82-90`, priorytet mvp,
właściciel ev-domain-expert). Jej tematy pokrywają się z glossary pack-ev: synonimy Charge Point/Station/EVSE/Connector,
różnice między protokołami, PL ↔ EN i pojęcia mylone (offline/unavailable/faulted, session/transaction, tariff/price). Treści
nie ma. `docs/PLAN.md:125` planuje `glossary/GLOSSARY.md` (około 150 pojęć), ale plik nie istnieje. Konwencja katalogów
(`taxonomy.yaml:7`, „key — nazwa katalogu w knowledge/<domain.key>/<subdomain.key>/”) daje
`knowledge/foundations/glossary/`.

**Wniosek: gdzie umieścić wpisy słownika.** Mam dwie propozycje do decyzji właściciela:
- `knowledge/foundations/glossary/` (zgodnie z konwencją taksonomii), z jednym plikiem na grupę pojęć, każdy termin z `[id §]`;
- alternatywnie `glossary/GLOSSARY.md` według PLAN.

W obu wariantach ev-domain-expert dostaje odsyłacz w references, a `tools/ev_kb.py search` indeksuje `knowledge/` (funkcja `corpus`).
Zasady nazw w kodzie (klasa R) pasują raczej do D00.02 niż do słownika.

### Luki
| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Tabela mapowania nazw: kanoniczna ↔ OCPP 1.6 ↔ 2.0.1 ↔ OCPI ↔ slang (urządzenie, EVSE, złącze, backend) | `PE/skills/dom-ev-glossary/references/mapa-nazw-protokolow.md:6-13`, `SKILL.md:25-31` | D00.01 | F (kolumna slang: P) | `[16 §3.8]`, `[201-P1 §1.2.1]`, `[OCPI230 §8]` (zarejestrowane) |
| Mapowanie procesów: Transaction / Session / CDR / Token / MeterValue / status | `mapa-nazw-protokolow.md:15-24`, `SKILL.md:70-78` | D00.01 | F | `[16]`, `[201-P1]`, `[OCPI230 §9, §10, §12]` |
| Central System (1.6) / CSMS (2.0.1) / CPMS (slang) | `SKILL.md:53-60` | D00.01 | F (1.6, 2.0.1) / P (slang), **konflikt K6** | `[16]`, `[201-P0]` |
| „Punkt ładowania = EVSE, liczenie po EVSE” | `SKILL.md:33-37` | D00.01; fakt już jest w `ev-cpms-architect/SKILL.md:41-42` | F (pokryte) | `[AFIR art. 2]`, `[201-P1 §1.2.1]`, `[OCPI230 §2.6]` |
| W 1.6 connector pełni rolę EVSE [do weryfikacji] | `SKILL.md:64-65`, `mapa…:11` | D00.01 | F | `[16 §3.8]` (connectorId; `ev-ocpp-expert/SKILL.md:110`) |
| Słowniki statusów złącza 1.6 (9) i 2.0.1 (5) | `SKILL.md:87` | D00.01 jako pojęcie mylone; szczegóły w ev-ocpp-expert | F (pokryte w ev-ocpp-expert) | `[16]`, `[201-P2]` |
| Wersje i podprotokoły `ocpp1.6`, `ocpp2.0.1` | `SKILL.md:86` | D00.01 | F | `[J16]`, `[201-P4]` |
| Trzy definicje uptime: surowa, NEVI, SLA | `SKILL.md:88` | D00.01 + `ev-charging-operations-expert/references/alarmy.md:57-62` (AFIR bez uptime) | F (NEVI: 23 CFR 680.116, niezarejestrowany) / R (surowa, SLA) | brak `us-nevi` w rejestrze |
| Skróty: SECC, EVCC, EVCO, EMAID, DLM, SoC/SoH, Mode 1–4, NEVI, CCS2 | `SKILL.md:93-104`, `references/skroty-a-z.md:35-53` | D00.01 | F (EMAID, EVCO, SECC: sprawdzić słowniki terminów 201-P0/P1 i 21-P0; Mode: AFIR zał. II) / niedostępne (IEC 61851, ISO 15118) / P (DLM jako termin branżowy) | `201-P0`, `201-P1`, `21-P0`, `AFIR`; IEC 61851 i ISO 15118 w `niedostepne.yaml` |
| SoH jako odrębny wskaźnik, dane SoC/SoH pojazdu | `skroty-a-z.md:53`, egzamin `red3-art-20a-ust3` | D04 / D12.02 | F | RED III art. 20a (`eu-red-iii` niezarejestrowany) |
| „Mówimy / nie mówimy” oraz reguły nazw w kodzie (`evse_id`, `energy_kwh`, `Money`, UTC, enum w adapterze) | `SKILL.md:39-51, 106-119` | D00.02 (model kanoniczny) | R | — |
| Procedura migracji nazw w kodzie (grep, adapter, test) | `mapa-nazw-protokolow.md:26-30` | D00.02 / ev-integration-architect | R | — |
| Cennik nieobecny w OCPP 1.6 i 2.0.1 | `mapa-nazw-protokolow.md:24` | — | **konflikt K5** | `[201-P2 I01–I03]`, 21-P2 |

---

## 3. dom-ev-knowledge-base

### Luki
| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Rejestr dat standardów i aktów (stosowanie, transpozycja, okresy przejściowe) z `sprawdzono` i statusem stale/recent/upcoming/unverified | `PE/skills/dom-ev-knowledge-base/references/rejestr-standardow.json` (25 wpisów), `SKILL.md:30-39` | EI nie ma odpowiednika: daty są rozproszone po skillach, `metadata.przeglad` jest tylko per skill, a `skill_check` sprawdza jedynie format daty. Propozycja: pole `daty:` w `sources/*.yaml` plus polecenie w `tools/ev_kb.py` | F (każda data z cytatem) | AFIR, MID, OCPP, OCPI, OICP zarejestrowane; NIS2, CRA, Data Act, EPBD, RED III, RED DA, 2026/706, NEVI, HB44 niezarejestrowane |
| Daty AFIR w rejestrze (13.04.2024, 8.01.2026, 1.01.2027, 31.12.2027, 31.12.2030) | `rejestr-standardow.json`, wpis `eu-afir` | `ev-compliance-expert/references/afir-mapa.md`, `ev-evse-hardware-expert/references/wymagania-afir.md:26-31` | F (pokryte w EI) | `AFIR` |
| MID po zmianie (UE) 2026/706: MI-011, systemy pomiarowe EVSE, terminy 2028-04-10, 2028-10-10, 2030-04-10, 2038-04-10 | wpis `eu-mid-2026-706` | D10 (`ev-compliance-expert/references/metrologia.md`) | F | EUR-Lex 2026/706, **niezarejestrowany**; EI ma tylko `MID` (2014/32, tekst pierwotny) |
| NIS2 (transpozycja 17.10.2024, lista podmiotów 17.04.2025), CRA (11.06.2026, 11.09.2026, 11.12.2027), RED DA 2022/30 i jego uchylenie 2026/339 | wpisy `eu-nis2`, `eu-cra`, `eu-red-da-*` | D12.03 (ev-compliance-expert; w `DO-ZROBIENIA.md:21` „NIS2 i EN 18031 bez skilla”) | F | EUR-Lex, niezarejestrowane |
| Data Act (12.09.2025, 12.09.2026, 12.09.2027), EPBD (29/30.05.2026), RED III (1.07.2024, 21.05.2025) | wpisy `eu-data-act`, `eu-epbd`, `eu-red-iii` | D12.02, D12.03 | F | EUR-Lex, niezarejestrowane |
| NEVI 23 CFR 680 (28.02.2024: ISO 15118-2, OCPP 2.0.1, OCPI 2.2.1), NIST HB44 3.40 (2028-01-01) | wpisy `us-nevi`, `us-nist-hb44` | D12.06 „Inne kraje” (dziś bez USA; facet `region: us` istnieje). Decyzja właściciela o zakresie | F | eCFR, NIST, niezarejestrowane |
| Mapowanie person na obszary | `SKILL.md:41-53` | — (właściciel: bez person) | — | — |
| Przykład `step_size` z cytatem | `SKILL.md:55-63` | ev-billing-tariff-expert (pokryte) | F (pokryte) | `OCPI230 §11` |
| Pułapki: zablokowany EUR-Lex, treść norm płatnych „własnymi słowami” | `SKILL.md:65-69` | `niedostepne.yaml` (`hosty_zablokowane`) | **konflikt K7** (zasady) | — |

### Nakładki
- Rejestr źródeł (`zrodla.json`): EI ma bogatszy rejestr (SHA-256, licencja, pakiety i dokumenty).
- Wyszukiwanie z cytatem (`kb.py search`): `tools/ev_kb.py search/cite/check`.
- Cache poza gitem: `.cache/ev-kb/` w EI.

---

## 4. dom-ev-business-economics

EI świadomie nie ma ekonomiki: `ev-product-designer/SKILL.md:20-22` mówi „ekonomika stacji (CAPEX, OPEX, zwrot) … nie mają w bazie
źródeł oficjalnych”, a `niedostepne.yaml:156-160` opisuje D17 bez źródeł. Miejsce w taksonomii jest: **D17.02 Ekonomika i
finansowanie** (p3, właściciel ev-product-designer).

| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Struktura pozycji CAPEX i OPEX (ładowarki, przyłącze, transformator, budowa, terminale, energia, opłata za moc, serwis, łączność, dzierżawa, prowizje) | `PE/skills/dom-ev-business-economics/SKILL.md:27-41` | D17.02 (`ev-product-designer`, nowy plik references) | R (lista bez kwot) | — |
| Wzory jednostkowe: kWh/rok = EVSE × 8760 × utilization × moc średnia, marża/kWh, pełny koszt kWh, próg utilization | `SKILL.md:49-58`, `scripts/station_economics.py` | D17.02 + skrypt | R | — |
| Wnioski: koszty stałe dominują przy niskim utilization; liczyć moc średnią, nie nominalną; utilization wymaga definicji | `SKILL.md:53-58` | D17.02, Pułapki | R | — |
| Próg „15–20 % utilization dla DC” | `SKILL.md:59` | — | P (nieprzenoszalne) | brak |
| Modele cenowe i ich skutek ekonomiczny (kWh, minuta, start, idle fee, subskrypcja, dynamiczne, ad hoc, roaming) | `SKILL.md:61-74` | D17.02; składniki ceny już w `rynek-dane.md:108-122` `[EAFO-CENY]` i w ev-billing-tariff-expert | R (skutki) / F (składniki, pokryte) | `EAFO-CENY*`, `AFIR art. 5`, `OCPI230 §11` |
| Opłaty za moc: moc umowna vs szczyt zmierzony | `references/capex-opex.md:19-24` | D08 / D17.02 | F (PL: taryfy OSD zatwierdza Prezes URE) / P (inne kraje) | taryfy OSD i rozporządzenie taryfowe **niezarejestrowane** (kandydat) |
| BESS i smart charging obniżają moc umowną; rozbudowa etapami; przychody dodatkowe | `capex-opex.md:33-47`, `SKILL.md:76-83` | D17.02 / D08 | R | — |
| Dotacje: warunki wymuszają konfigurację; NEVI to program formułowy (23 CFR 680.100, 680.102) | `SKILL.md:43-47`, `capex-opex.md:26-31` | D12.07 (programy wsparcia, p3) | R (warunki) / F (NEVI) | eCFR 23 CFR 680, niezarejestrowany |
| NPV, okres zwrotu, wrażliwość, scenariusze, ryzyka spoza modelu | `SKILL.md:85-94`, `references/decyzja-i-ryzyka.md:56-74` | D17.02 | R | — |
| KPI finansowe z CDR | `SKILL.md:93-94` | `wymagania-produktu.md` §6 (wskaźniki z `total_time`, `total_parking_time`) | F (pokryte częściowo) | `OCPI230 §10.3.1` |

**Wniosek.** Klasa R (struktura kosztów, wzory, skrypt, pułapki) da się przenieść do D17.02 bez łamania zasady źródeł,
bo nie niesie liczb rynkowych. Liczby z przykładu (`SKILL.md:122-140`) trzeba oznaczyć jako ilustrację. Wymaga to jednak zmiany
deklaracji w `ev-product-designer/SKILL.md:20-22` i w `wymagania-produktu.md` §7 („baza tego nie obejmuje” stałoby się
„baza ma metodę, nie ma danych”). To decyzja właściciela.

---

## 5. dom-ev-site-development

Miejsce w taksonomii to D18 (p3, właściciel ev-charging-operations-expert, bez treści; `DO-ZROBIENIA.md:20-23`: „wybór lokalizacji
stacji (D17/D18) … wymaga najpierw źródeł oficjalnych”). `scripts/` w tym skillu nie istnieje.

| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Etapy i bramki pipeline: lead → ocena → umowa → projekt → przyłącze → budowa → commissioning → operacje | `PE/skills/dom-ev-site-development/SKILL.md:17-30` | D18.01–D18.04 (ev-charging-operations-expert) | R | — |
| Knock-outy przed punktacją | `SKILL.md:32-40` | D18.01 | R | — |
| Model punktacji z wagami, wrażliwość i kalibracja | `SKILL.md:50-62`, `references/wybor-lokalizacji.md:15-26` | D18.01 | R (wagi tylko jako ilustracja) | — |
| Czas postoju → typ ładowarki (5–40 min DC 150–400 kW itd.) | `SKILL.md:42-48`, `wybor-lokalizacji.md:28-36` | D19 | P (nieprzenoszalne) | brak |
| Dane wejściowe popytu (ruch, rejestracje EV, konkurencja z NAP) | `wybor-lokalizacji.md:5-13` | D18.01; rejestracje i punkty już w `rynek-dane.md` `[ESTAT-*]` `[EIPA-STAT]` | R / F (pokryte) | `ESTAT-EQS`, `EIPA-STAT`, `EAFO-*` |
| AFIR art. 3 ust. 4: pule co 60 km, moce sieci bazowej i kompleksowej | `SKILL.md:71-72`, `wybor-lokalizacji.md:49` | `ev-compliance-expert/references/afir-mapa.md:9-12` | F (pokryte), **rozbieżność K8** | `AFIR` |
| AFIR art. 3 ust. 5 (liczenie odcinków ≤ 60 km), ust. 6–9 (jedna pula na oba kierunki, odstępstwa do 100 km, próg ruchu 8 500 pojazdów/dobę), ust. 11 (odcinki transgraniczne) | `SKILL.md:73`, `wybor-lokalizacji.md:8, 50-51` | `afir-mapa.md` | F | `AFIR` (zarejestrowany) |
| AFIR art. 4: pojazdy ciężkie (pule 1 400 i 2 800 kW, punkty 350 kW, bezpieczne parkingi 2 i 4 stacje ≥ 100 kW, węzły miejskie 900 i 1 800 kW) | `SKILL.md:74`, `wybor-lokalizacji.md:45-46` | `afir-mapa.md` + D19.05 (grep „AFIR art. 4” w EI: 0 trafień) | F | `AFIR` |
| „AFIR wiąże państwa, nie CPO; wymóg wynika z dotacji lub koncesji” | `SKILL.md:77-78`, `wybor-lokalizacji.md:54` | `afir-mapa.md` (jest podział według adresata) | F/R (pokryte) | `AFIR` |
| NEVI 680.106(b), (d)(1), (e), (f): ≥ 4 porty DC, 250–920 V, ≥ 150 kW na port, 24/7, dostępność płatności | `SKILL.md:75-76`, `przylacze-i-budowa.md:123-124`, `pozwolenia-umowy-pipeline.md:177-178` | D12.06 (USA, decyzja o zakresie) | F | eCFR 23 CFR 680, niezarejestrowany |
| Przyłącze: kroki z OSD, kVA vs kW, stacja SN/nN, licznik OSD jako limit, potrzeby własne, sprawność DC | `SKILL.md:80-89`, `przylacze-i-budowa.md:64-87` | D18.02 / D08 | R (kroki, bilans) / F-kandydat (warunki i terminy przyłączenia: Prawo energetyczne i rozporządzenie przyłączeniowe) | niezarejestrowane (pack-ev też ich nie ma, `przylacze-i-budowa.md:73-74`) |
| Alternatywy przy słabym przyłączu (BESS, load management, etapowanie) | `przylacze-i-budowa.md:89-97` | D18 / D08 | R | — |
| PL-EMOB art. 12b ust. 9–10, 12c ust. 5, art. 62 ust. 4–6 i 11–12, art. 67 (cel publiczny); ustawa nie podaje terminu przyłączenia | `SKILL.md:90-92`, `przylacze-i-budowa.md:99-108` | `ev-compliance-expert/references/prawo-pl.md` (`:139` mówi, że art. 12–12c są nieopracowane) | F | `PL-EMOB` (zarejestrowany) |
| PL-EMOB art. 13, 15, 16 (normy, ppoż., dostępność, opinia i badanie UDT) | `SKILL.md:96-97`, `przylacze…:106-107` | `prawo-pl.md:64, 81-91` | F (pokryte) | `PL-EMOB`, `PL-R1316` |
| Budowa: fundamenty, bollardy, zadaszenie, oświetlenie, odwodnienie, oznakowanie, CCTV, MCS | `przylacze-i-budowa.md:111-125` | D18.03 | R/P; częściowo F (ochrona przed najechaniem `[PL-R1316 § 8]` już w `wymagania-produktu.md:217`) | `PL-R1316` |
| Łączność: LTE + światłowód, redundancja, UPS modemu | `przylacze-i-budowa.md:127-135` | D18.03 / D07 | P/R | — |
| Przepisy ppoż., parkingi podziemne, BESS, warunki techniczne miejsc, Prawo budowlane | `przylacze-i-budowa.md:137-141`, `pozwolenia…:153-163` | `niedostepne.yaml` (nowe wpisy `niezarejestrowane`) | — (brak źródła) | kandydaci: Prawo budowlane, rozporządzenie w sprawie warunków technicznych (ISAP) |
| Pozwolenia: plan miejscowy lub WZ, pozwolenie czy zgłoszenie, konserwator (PL-EMOB art. 12b ust. 11) | `pozwolenia-umowy-pipeline.md:153-163` | D18.02 | F (art. 12b ust. 11 w `PL-EMOB`) / F-kandydat (Prawo budowlane) | `PL-EMOB`; Prawo budowlane niezarejestrowane |
| Umowa z gospodarzem: tytuł, długość, czynsz lub udział, wyłączność, energia, zakończenie | `pozwolenia…:165-176` | D17.04 (partnerstwa) | R/P | — |
| EPBD art. 14 ust. 2 (budynki niemieszkalne > 20 miejsc: punkt na 10 miejsc albo kanały dla 50 %, od 1.01.2027) i ust. 4 (okablowanie wstępne) | `pozwolenia…:179-181, 215-216` | D12.02 (ev-compliance-expert) + D19.02 / D19.03 | F | EUR-Lex 2024/1275, niezarejestrowany |
| Pipeline jako dane: pola `site_id`, `stage`, `requested_kva`, `permits[]`, `gate_history[]` itd. | `pozwolenia…:183-197` | D18 / D00.02 | R | — |
| Future-proofing (rury, zapas pól, moc docelowa) | `pozwolenia…:206-216` | D18.03 | R | — |
| Przekazanie do rejestru assetów, CSMS, EIPA i UDT | `SKILL.md:118-122`, `pozwolenia…:218-228` | D18.04 | R (EIPA i UDT pokryte w `prawo-pl.md`) | `PL-EMOB` |
| Pola OCPI do publikacji lokalizacji: `parking_type` (wartości), `facilities` (lista), `opening_times` (reguła `twentyfourseven`), `time_zone`, `floor_level`, `parking_restrictions`, `GeoLocation` (5 miejsc po przecinku), `Parking` i `EVSEParking` (2.3.0), `VehicleType` (VAN < 275 cm itd.) | `SKILL.md:105-116`, `pozwolenia…:230-245`, `wybor-lokalizacji.md:38-46` | `ev-ocpi-roaming-expert/references/moduly.md` lub `ev-product-designer/references/wymagania-produktu.md` §1 (dziś tylko lista nazw pól, `:21-23`; `wersje-i-role.md:23` wspomina `Parking`) | F | `OCPI230 §8` (zarejestrowany), `OCPI230 §1.1` (nowe w 2.3.0) |

---

## 6. roles/ i personas/
- `PE/roles/*.yaml` (11) i `PE/personas/*.yaml` (11) zawierają wyłącznie routing (triggers, listy skilli), tożsamość i nawyki.
  **Nie ma w nich wiedzy domenowej, której nie ma żaden skill.** Fakty typu „AFIR TEN-T i NEVI jako wymogi lokalizacji”
  (`roles/network-development.yaml:4`) to tylko hasła.
- `PE/traits/*.md` (5) to heurystyki klasy R: units-strict (kW≠kWh, A→kW tylko z U i liczbą faz), protocol-version-explicit,
  multi-vendor-defensive (tolerancyjny parser, odchylenia modelu z flagą), safety-critical, regulation-aware.
  Większość jest już w EI: wersja protokołu w każdym skillu, D21 vendor quirks z szablonem.
  Jedynie safety-critical (masowe zmiany mocy rozkładane w czasie, próba na jednej stacji, bez obchodzenia RCD) mógłby trafić do Pułapek
  `ev-charging-operations-expert` lub `ev-energy-smart-charging-expert` jako R. Personas: zgodnie z decyzją właściciela, nie przenosić.

---

## 7. Diff rejestru źródeł

Źródła: `PE/skills/dom-ev-knowledge-base/references/zrodla.json` (33 wpisy) i `rejestr-standardow.json` (25 wpisów).
Porównanie z `EI/sources/*.yaml` (82 dokumenty według `ev_kb.load_sources`) i z `niedostepne.yaml`.

### 7.1 Są w rejestrze EI (inny artefakt lub wersja)
| id pack-ev | URL pack-ev | odpowiednik EI |
|---|---|---|
| ocpi-2.2.1-d2 | github.com/ocpi/ocpi/tree/v2.2.1-d2 (asciidoc) | `OCPI221` (PDF evroaming.org; wewnątrz „2.2.1-d3-pre1”), `OCPI221-CH` (konflikt K9) |
| ocpi-2.3.0 | github.com/ocpi/ocpi/tree/v2.3.0 | `OCPI230` (PDF 2025-02-21) |
| evroaming | evroaming.org | `EVRF-DL`, `EVRF-VME`, `EVRF-V25` |
| oicp | github.com/hubject/oicp | `OICP-README`, `OICP23-*` (commit 119c5d5) |
| oca-ocpp | openchargealliance.org/protocols/… | `oca-ocpp16`, `oca-ocpp16-security`, `oca-ocpp201-ed4`, `oca-ocpp21-ed2`, `OCA-*` |
| eu-afir | eur-lex …/eli/reg/2023/1804/oj | `AFIR` (konsolidacja 2026-01-08), `AFIR-OJ`, `AFIR-655` |
| eu-mid | eur-lex …/eli/dir/2014/32/oj | `MID` (tekst pierwotny) |
| pl-elektromobilnosc | isap.sejm.gov.pl …WDU20180000317 | `PL-EMOB` (Dz.U. 2026 poz. 1243, api.sejm.gov.pl) |
| pl-eipa | eipa.udt.gov.pl | `EIPA-STAT`, `EIPA-OPIS`, `EIPA-API` |

### 7.2 Są w `niedostepne.yaml`
| id pack-ev | URL | wpis EI |
|---|---|---|
| ocmf | github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format | `niezarejestrowane`: „OCMF … i format EDL” (`:137-141`). Repo GitHub jest publiczne, więc to **kandydat do pobrania** (licencję trzeba sprawdzić) |
| iso-15118-20 | iso.org/standard/77845.html | `normy_platne` ISO 15118 (`:21-26`) |
| iec-61851-1 | webstore.iec.ch/…/6029 | `normy_platne` (`:27-32`) |
| (rejestr-standardow) iso-15118-2, iec-62196, din-70121 | iso.org, webstore.iec.ch, din.de | `normy_platne` (`:21-38`, `:51-56`) |
| (rejestr-standardow) ocpp-2.1 jako IEC 63584-210 | — | `normy_platne` (`:118-124`) |

### 7.3 Brak w rejestrze EI i w `niedostepne.yaml` (kandydaci do pobrania z SHA-256)
| # | id pack-ev | URL | uwaga |
|---|---|---|---|
| 1 | eu-mid-2026-706 | https://eur-lex.europa.eu/eli/dir/2026/706/oj | otwarty; MI-011 dla EVSE; istotny dla D10 |
| 2 | eu-nis2 | https://eur-lex.europa.eu/eli/dir/2022/2555/oj | otwarty; D12.03 |
| 3 | eu-cra | https://eur-lex.europa.eu/eli/reg/2024/2847/oj | otwarty; D12.03 |
| 4 | eu-red-da | https://eur-lex.europa.eu/eli/reg_del/2022/30/oj | otwarty; D12.03/D12.04 |
| 5 | eu-red-da-uchylenie | https://eur-lex.europa.eu/eli/reg_del/2026/339/oj | otwarty |
| 6 | eu-epbd | https://eur-lex.europa.eu/eli/dir/2024/1275/oj | otwarty; D12.02 |
| 7 | eu-data-act | https://eur-lex.europa.eu/eli/reg/2023/2854/oj | otwarty; D12.03 |
| 8 | eu-red-iii | https://eur-lex.europa.eu/eli/dir/2023/2413/oj | otwarty; D12.02 (art. 20a dane baterii) |
| 9 | us-nevi | https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-680 | otwarty; region us poza dzisiejszym D12.06 |
| 10 | us-nist-hb44 | https://www.nist.gov/pml/owm/nist-handbook-44-current-edition | otwarty; D10 / D12.06 |
| 11 | sae-j3400 | https://www.sae.org/standards/content/j3400_202409/ | płatna, więc tylko wpis do `niedostepne.yaml` (`normy_platne`) |
| 12 | (rejestr-standardow) sae-j1772 | https://www.sae.org/ | płatna, więc wpis do `niedostepne.yaml`; przywołuje ją `201-P2 §3.22` („Type 1 (J1772)”) |
| 13 | pl-udt | https://www.udt.gov.pl | strona urzędu, nie dokument; rejestrować konkretne dokumenty |
| 14 | pl-ure | https://www.ure.gov.pl | jak wyżej (np. taryfy OSD, rejestr) |
| 15 | us-afdc | https://afdc.energy.gov | strona urzędu; dane o stacjach w USA |
| 16 | us-joint-office | https://driveelectric.gov | strona urzędu |

Dokumenty przywołane w treści pack-ev, których nie ma w żadnym rejestrze (kandydaci do `niedostepne.yaml` jako
`niezarejestrowane`): Prawo energetyczne i rozporządzenie przyłączeniowe (warunki i terminy przyłączenia), taryfy OSD (opłaty za
moc), Prawo budowlane i rozporządzenie o warunkach technicznych (miejsca, ppoż., garaże), przepisy ppoż. dla BESS.

### 7.4 Źródła wtórne (W) w pack-ev, niedozwolone jako dowód (CLAUDE.md)
`mobilityhouse-ocpp`, `steve`, `everest`, `everest-libocpp-smart-charging`, `ocpp-json-schemas` (mobilityhouse; schematy OCA EI ma
już jako `S16`, `201-*` z pakietów OCA), `josev-iso15118`. Mogą służyć tylko za wskazówkę.

**Liczby.** Z 33 wpisów `zrodla.json`: 9 ma odpowiednik w EI, 3 są w `niedostepne.yaml`, 6 to źródła wtórne, a 15 brakuje.
Z tych 15 jest 10 otwartych aktów, które można pobrać, 1 płatna norma i 4 strony urzędów. `rejestr-standardow.json` dokłada
SAE J1772 (płatna, brak także w `niedostepne.yaml`).

---

## 8. Skrypty i egzamin

| artefakt | co robi | zależności | testy | odpowiednik w EI | werdykt |
|---|---|---|---|---|---|
| `dom-ev-knowledge-base/scripts/kb.py` | 17-liniowy przekaźnik (shim) do `tf/core/skills/core-knowledge/scripts/kb.py`: wyszukiwanie BM25 w skillach i cache, `sources`, `ingest` (pobieranie z sieci), `status` (wiek cache), `remove` | rdzeń tf ≥ 5.6.0 (bez niego kod 2) | `tests/test_kb_ev.py` (walidacja `zrodla.json` mechanizmem rdzenia) | `tools/ev_kb.py`: `route/search/cite/check/skill/index`, bez sieci, dopasowanie po SHA-256, kontrola znaczników `[id §]`, pole `unavailable`; MCP `tools/ev_kb_mcp.py` | **Duplikat funkcji wyszukiwania** o słabszym modelu dowodu (cache bez SHA, `ingest` z sieci sprzeczny z zasadą ręcznego pobrania i sumy). Nie przenosić; usunąć razem z testem |
| `dom-ev-knowledge-base/scripts/standards_check.py` | rejestr dat standardów: stale (sprawdzono > `przeglad_miesiecy`), recent (data minęła po sprawdzeniu), upcoming (`--horizon`), unverified; `--strict` daje kod 1 | tylko stdlib; `ROOT` szuka `.claude/skills` | `tests/test_standards_check.py` (S-1…) | **brak** (`skill_check.py` sprawdza tylko format `metadata.przeglad`) | **Warto przenieść ideę**, nie dane. **Wniosek:** pole `daty:` przy dokumencie w `sources/*.yaml` (każda data z sekcją dokumentu) i polecenie `ev_kb.py dates --horizon N` albo osobny `tools/`. Dane z `rejestr-standardow.json` wskazują `kb:<id> doc.txt:Lnn` (cache tf), więc każdą datę trzeba ponownie sprawdzić w źródle EI |
| `dom-ev-business-economics/scripts/station_economics.py` | NPV, okres zwrotu (interpolacja), marża i pełny koszt kWh, próg utilization (EBITDA ≥ 0), wrażliwość (utilization ×0,8 i ×1,2, cena ×0,9 i ×1,1, energia ×1,2); kody 0, 1 (NPV < 0), 2 | tylko stdlib, bez sieci | `tests/test_station_economics.py` (E-1…E-17 + walidacja wejścia) | brak; w EI jedyny skrypt skilla to `skills/ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py` z testem w `tests/` | **Można przenieść (klasa R)** do `skills/ev-product-designer/scripts/` i `tests/`, jeśli właściciel otworzy D17.02 na metodę bez danych. Do zmiany: ścieżki `.claude/skills/…` na `skills/…`; przykład z liczbami oznaczyć jako ilustrację |
| `tests/run_ev_exam.py` + `tests/ev_exam/*.json` (8 obszarów × 13 = 104 pytania) | egzamin „z fabryką vs bez niej” przez `claude -p`; `--validate` w CI; pytanie, wzorzec, `checks.all/none`, `zrodlo` (dom-ev-* lub `kb:<id>`), trudność 1–3 | importuje `tf/core/tests/run_skill_evals.py`, CLI `claude`, `zrodla.json` (walidacja `kb:`) | `tests/test_ev_exam.py` (atrapa claude) | `tools/skill_eval.py` + `evals/skill_evals/*.json` (13 skilli, 82 scenariusze dev i 55 holdout): routing i odpowiedź per skill, `--dry-run`, budżet, **bez porównania z bazowym modelem bez skilla** | **Runnera nie przenosić** (zależny od tf). **Pytania** to kandydaci na scenariusze `evals/skill_evals/<ev-skill>.json`, bo format `checks.all/none` jest zgodny. Każdy `wzorzec` niesie fakty bez cytatu, więc najpierw weryfikacja w źródle EI. Około 25 pytań opiera się na źródłach spoza rejestru EI (NEVI, HB44, NIS2, CRA, Data Act, RED, 2026/706, OCMF). **Wniosek:** tryb baseline (bez skilla) dałoby się dodać do `skill_eval.py`; przebieg płatny tylko za zgodą |
| `tests/skill_evals/dom-ev-{charging,glossary,knowledge-base,business-economics,site-development}.json` (4+5+4+3+4 = 20 scenariuszy) | scenariusze routingu i odpowiedzi | `run_skill_evals.py` tf | — | `evals/skill_evals/ev-*.json` | prompty do wykorzystania przy nowych scenariuszach `ev-domain-expert` (słownik), `ev-product-designer` (D17), `ev-charging-operations-expert` (D18); `checks` do przepisania na fakty z cytatem |

---

## 9. Konflikty

| # | pack-ev | ev-intelligence | rozstrzygnięcie |
|---|---|---|---|
| K1 | Aktualna edycja OCPP 2.0.1 to „np. Edition 3” (`PE/skills/dom-ev-charging/references/ocpp.md:32`); `rejestr-standardow.json`, wpis `ocpp-2.0.1`: „2.0.1 Edition 3 [do weryfikacji]” | Edition 4 (części z 2025-12-03), errata 2026-09 (`EI/skills/ev-ocpp-expert/references/wersje-i-status.md:9`; `EI/sources/oca-ocpp.yaml:31-33`) | EI (pakiet OCA z SHA-256) |
| K2 | Security Whitepaper „edition 2” dla 1.6 (`ocpp.md:148-149, 161`) | Edition 4 z 2026-02-05 (`oca-ocpp.yaml:23-27`, `wersje-i-status.md:12`) | EI |
| K3 | OCPP 2.1: „styczeń 2025, do weryfikacji” (`ocpp.md:30`); IEC 63584-210 „nie przepisuję jako faktu” (`rejestr-standardow.json`, `ocpp-2.1`) | potwierdzone `[OCA-N1]` `[OCA-N2]` (`wersje-i-status.md:25-27`) | EI; pack-ev nieaktualny, nie sprzeczny |
| K4 | „Level 1 / Level 2” to amerykańskie nazwy AC, DC fast to DC (`infrastruktura-ladowania.md:103, 126-128`) | AFIR-655: „Level 1 – Ultra-fast DC” 150–350 kW i „Level 2 – Ultra-fast DC” ≥ 350 kW (`EI/skills/ev-evse-hardware-expert/references/zlacza-i-moc.md:76-77`) | dwa różne znaczenia terminu; w słowniku D00.01 rozdzielić z cytatem AFIR-655, a wersja USA (SAE J1772) jest niedostępna |
| K5 | Cennik „poza OCPP 1.6 i 2.0.1” (`PE/skills/dom-ev-glossary/references/mapa-nazw-protokolow.md:24`) | OCPP 2.0.1 blok I: taryfa jako tekst w `personalMessage`, koszt bieżący i `totalCost` (`EI/skills/ev-product-designer/references/wymagania-produktu.md:188-190` `[201-P2 I03.FR.04]`); taryfy w 2.1 w ev-billing-tariff-expert | EI: 2.0.1 ma prezentację ceny i kosztu, nie ma strukturalnej taryfy; strukturę taryfy w 2.1 sprawdzić w `21-P2` |
| K6 | CSMS to nazwa kanoniczna, „CPMS to slang, nie w nowym kodzie” (`dom-ev-glossary/SKILL.md:46, 57-59`) | EI używa CPMS jako głównej nazwy: skill `ev-cpms-architect`, domena D05 „CPMS / CSMS” (`EI/taxonomy/taxonomy.yaml:438-440`, `:108`) | konwencja, nie fakt; decyzja właściciela przy tworzeniu D00.01. Fakty: „Central System” w `[16]`, „CSMS” w `[201-P0]` |
| K7 | Treść norm płatnych „tylko własnymi słowami” (`dom-ev-knowledge-base/SKILL.md:68`); „wiedza ogólna … [do weryfikacji]” (`dom-ev-glossary/SKILL.md:12-13, 162`; `dom-ev-charging/SKILL.md:13-14`) | „Nic z pamięci modelu”, a o treści normy niedostępnej nie piszemy wcale (`EI/CLAUDE.md` „Zasada źródeł”; `EI/sources/niedostepne.yaml:7-8`) | EI; żadne zdanie z [do weryfikacji] ani streszczenie normy płatnej nie przechodzi |
| K8 | Sieć kompleksowa: ≥ 300 kW i ≥ 1 punkt ≥ 150 kW „2027 dla ≥ 50 % długości, 2030 dla całości” (`dom-ev-site-development/SKILL.md:72`) | „do 31.12.2027 na ≥ 50 % długości ≥ 300 kW z punktem ≥ 150 kW; do 31.12.2030 ≥ 300 kW” (bez punktu ≥ 150 kW dla 2030) (`EI/skills/ev-compliance-expert/references/afir-mapa.md:11`) | sprawdzić `[AFIR art. 3 ust. 4 lit. b]`; jedna z wersji pomija warunek punktu ≥ 150 kW dla 2030 |
| K9 | OCPI 2.2.1-d2 z tagu GitHub `v2.2.1-d2` (asciidoc), cytaty `doc.txt:Lnn` (`zrodla.json`, `ocpi-2.2.1-d2`) | PDF „OCPI-2.2.1-d2.pdf”, wewnątrz „2.2.1-d3-pre1, 2023-09-07” (`EI/sources/evrf-ocpi.yaml:27-29`; `ev-ocpi-roaming-expert/references/wersje-i-role.md:18`) | różne artefakty tej samej wersji; odwołania liniowe pack-ev nie przenoszą się; cytować `OCPI221 §` |
| K10 | OCPP 1.6: „28 unikalnych akcji (10 Charge Point, 18–19 CPMS + DataTransfer)” (`ocpp.md:27`) i „10 + 18 + DataTransfer” (`ocpp.md:148`) | „Schematy JSON OCPP 1.6 (56 plików, 28 akcji)” (`oca-ocpp.yaml`, dokument `S16`) | niespójność wewnątrz pack-ev (28 czy 29); EI liczy ze schematów: 28 |
| K11 | „Zgodność z AFIR (definicja punktu) [do weryfikacji]” (`dom-ev-glossary/SKILL.md:36-37`) | zweryfikowane: EVSE = recharging point, jeden pojazd naraz `[AFIR art. 2]` (`EI/skills/ev-cpms-architect/SKILL.md:41-42`) | EI; pack-ev nieaktualny |

---

## 10. Podsumowanie klas (moja grupa)
- **F (sprawdzalne):** około 30 pozycji. Najwięcej z AFIR art. 3 i 4, PL-EMOB art. 12b, 12c, 62, 67, OCPI230 §8 (wartości
  pól Location i Parking), słownika D00.01 (16/201/OCPI230) i dat aktów UE i USA. Część wymaga nowych źródeł (EPBD, NIS2,
  CRA, Data Act, RED III, RED DA, 2026/706, NEVI, HB44).
- **P (bez źródła, nieprzenoszalne):** około 15. Typy i komponenty pojazdów poza definicjami, ESG, rynek i dostawcy, progi postoju,
  utilization 15–20 %, typowe moce OBC, regionalność złączy, UK WCS.
- **R (procedury):** około 20. Pipeline i bramki, punktacja, knock-outy, struktura CAPEX/OPEX, wzory i skrypt ekonomii, reguły
  nazw w kodzie, archetypy, future-proofing, przekazanie.

**Pięć najcenniejszych luk:**
1. Słownik D00.01: tabela mapowania nazw OCPP 1.6 / 2.0.1 / OCPI z cytatami. EI ma na to poddomenę mvp bez treści.
2. AFIR art. 3 ust. 5–11 i art. 4 (pojazdy ciężkie, bezpieczne parkingi, węzły miejskie), źródło `AFIR` już w rejestrze.
3. PL-EMOB art. 12b, 12c, 62 i 67 (przyłącza w budynkach, plany gmin i programy OSD, cel publiczny), `PL-EMOB` w rejestrze.
4. Wartości pól OCPI 2.3.0 Location, Parking, EVSEParking i VehicleType dla publikacji lokalizacji, `OCPI230 §8` w rejestrze.
5. Mechanizm rejestru dat standardów (idea `standards_check.py`), połączony z dodaniem do rejestru aktów 2026/706, NIS2,
   CRA, EPBD, Data Act i RED III.
