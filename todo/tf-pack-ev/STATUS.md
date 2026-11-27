# Stan scalania pack-ev → EV Intelligence

Oznaczenia pozycji jak w `analiza/luki-*.md`.

Stany:
- **przeniesione**: treść z cytatem w skillu `ev-*`;
- **odrzucone**: pozycja nie trafi do bazy (powód podany);
- **czeka**: wymaga źródła, decyzji albo pracy.

## Pilot (2026-11-15): `dom-ev-ocpp-16`, `dom-ev-ocpp-2x` → `ev-ocpp-expert`; analizator logu → `ev-evse-diagnostics-expert`
Dokumenty OCA pobrane z adresów w `sources/oca-ocpp.yaml` (sumy SHA-256 zgodne z rejestrem) i zaindeksowane
w `.cache/ev-kb/`. Każdy nowy znacznik ma status `OK` w `ev_kb.py check`.

| Pozycja | Stan | Gdzie / dlaczego |
|---|---|---|
| O16-1 tabela przejść statusów 1.6 | przeniesione | `ev-ocpp-expert/references/komunikaty-16.md` §2 `[16 §4.9]` `[16E §3.19–3.22]` |
| O16-2 typowa kolejność ramek sesji | częściowo | przejście `Preparing` → `Charging` z krótkim `Suspended*` `[16 §4.9]`; pełny przebieg sesji czeka (diagramy `[16]` rozdz. 4–5) |
| O16-3 Boot `Pending` / `Rejected` | przeniesione | `komunikaty-16.md` §3 `[16 §4.2]` `[16 §4.2.1]` `[16E §3.11]` |
| O16-4 backoff po zerwaniu w 1.6 | przeniesione | `wzorce.md` §3: brak Boot przy reconnect `[J16 §5.4]`, backoff po HTTP 404 `[J16E §3.4]`; parametrów 1.6 nie określa |
| O16-5 pola `StopTransaction`, energia sesji | przeniesione | `komunikaty-16.md` §3 `[16 §4.10]` `[16 §6.49–6.50]`, energia jako Wniosek |
| O16-6 OCPP-J / OCPP-S | przeniesione | `wersje-i-status.md` `[16 §3.1]` `[16 §3.2]` |
| O16-7 unikalność `messageId`, deduplikacja | przeniesione | `ramki-i-bledy.md` `[J16 §4.1.4]` `[J16E §3.7]` (wpis errat oznaczony DRAFT); zapasowy klucz StartTransaction odrzucony (pack: [założenie]) |
| O16-8 szybka odpowiedź, outbox | czeka | R → `ev-cpms-architect` (poza pilotem) |
| O16-9 test na nagranej ramce | czeka | R → `ev-evse-diagnostics-expert/references/metoda.md` §5 |
| O16-10 kolejka offline po stronie CSMS | czeka | R; kotwica `[16 §3.7]` już w `wzorce.md` §4 |
| O16-11 katalog „typowych odchyleń” 1.6 | **odrzucone** | P bez producenta, modelu, firmware i dowodu; nie spełnia szablonu `vendor-quirks/_szablon.yaml`; treść w `zrodlo/skills/dom-ev-ocpp-16/references/odchylenia-i-offline.md` |
| O16-12 zamykanie wiszącej sesji heurystyką | czeka | R → `ev-charging-operations-expert` |
| O16-13 tryb tolerancyjny walidacji | czeka | R → `ev-integration-architect` |
| O16-14 MeterValues ≠ licznik rozliczeniowy | czeka | → `ev-billing-tariff-expert` / `ev-compliance-expert` |
| O2-1 budowa Device Model | przeniesione | `komunikaty-201.md` §4 `[201-P1 §4.1–4.3]` `[201-P1 §4.6]` |
| O2-2 `GetBaseReport` → `NotifyReport` | przeniesione | `komunikaty-201.md` §4 `[201-P2 B07]` `[201-P2 B07.FR.*]` `[201-P2 §1.40]`; `SetVariables` per zmienna `[201-P2 B05.FR.*]` |
| O2-3 `connectorStatus` 2.0.1 ↔ 9 stanów 1.6 | przeniesione | `ev-ocpp-expert/SKILL.md` jako Wniosek `[16 §4.9]` `[201-P2 §3.16]` `[201-P2 §3.23]` |
| O2-4 polityka luk `seqNo` | częściowo | wykrywanie luk w analizatorze logu; polityka CSMS (timer, alarm) czeka (R) |
| O2-5 … O2-7 | czeka | R → `ev-cpms-architect` / `ev-integration-architect`; certyfikacja 2.1 wymaga rejestracji stron OCA |
| skrypt `ocpp_log_analyze.py` | przeniesione | `ev-evse-diagnostics-expert/scripts/`, testy `tests/test_ocpp_log_analyze.py` (unittest); poprawki: `transactionId = -1` jako osobne ustalenie `[16E §3.18]`, ramki 2.1 typu 5 i 6, `--timeout` opisany jako próg narzędzia `[J16 §4.1.1]` |
| scenariusze pack-ev (`zrodlo/tests/skill_evals/dom-ev-ocpp-*.json`) | częściowo | dwa nowe scenariusze napisane od nowa (`status-available-finishing-bez-idtag`, `get-base-report-niekompletny`); holdout pack-ev nieczytany przez autora zmian (zasada `docs/SKILLS-WORKFLOW.md`) |

Konflikty rozstrzygnięte na korzyść EV Intelligence (pack-ev ich nie wnosi): K1 timeout, K3 edycja Security
Whitepaper, K4 `DataTransfer` w Core, K5 `transactionId = -1`, K6 `seqNo` per EVSE, K7 brak wspólnego podprotokołu,
K10 fakty 2.1 (`analiza/luki-A.md` §8).

## Fala 1 (2026-11-15): OCPI, OICP, rozliczenia → `ev-ocpi-roaming-expert`, `ev-billing-tariff-expert`
Dokumenty EVRoaming (OCPI 2.3.0, 2.2.1, zmiany 2.2.1, TSG, Direct Payment) i OICP 2.3 (Hubject, commit `119c5d5`)
pobrane z adresów w rejestrze, SHA-256 zgodne, zaindeksowane w `.cache/ev-kb/`. Każdy plik przeszedł dwie kontrole:
autor (cytat dla każdego faktu, `ev_kb check`) i niezależny recenzent wierności (zdanie po zdaniu wobec cytowanego
fragmentu; przykłady liczbowe przeliczone). Recenzenci poprawili 17 zdań (głównie siłę wymogu i numery sekcji) i usunęli 2 fragmenty niepotwierdzone.

| Pozycje (`analiza/luki-B.md`) | Stan | Gdzie / dlaczego |
|---|---|---|
| O1, O3, O4, O7, O8, O13–O22 (moduły OCPI) | przeniesione | `ev-ocpi-roaming-expert/references/moduly.md` (§1–3, §6–8) |
| O23 nowości Locations 2.3.0 | częściowo | `moduly.md` §2; format `evse_id` (IDACS „E-mobility ID-codes”, eMI3) poza rejestrem — czeka |
| O2, O5, O6, O9–O12, O24 (transport, wersje, huby) | przeniesione | `transport.md`, `wersje-i-role.md` |
| O26 migracja 2.2.1 → 2.3.0 | przeniesione jako Wniosek | `wersje-i-role.md` |
| O27 test kontraktowy | częściowo | tabela „objaw → hipoteza” w `transport.md`; scenariusze Sessions/Tokens/Commands czekają (cel: SKILL.md albo `onboarding.md`) |
| O25 tagi repozytorium ocpi/ocpi | czeka | github.com/ocpi/ocpi poza rejestrem |
| I1–I8, I10 (OICP) | przeniesione | `oicp.md` |
| I11 architektura adapterów | przeniesione jako Wniosek | `oicp.md` §11 |
| I9 Dynamic Pricing | częściowo | `oicp.md` §7; Functional Guide Hubject poza rejestrem — czeka |
| I12 P2P czy hub, koszty | **odrzucone / czeka** | brak źródła oficjalnego (Gireve IG nieopracowany) |
| T1–T5, T7–T12, T16 (taryfy) | przeniesione (część jako Wniosek) | `ev-billing-tariff-expert/references/taryfy-ocpi.md`, `ceny-afir-ocpp.md` |
| T6 błędy w przykładach | przeniesione | `taryfy-ocpi.md` §7, `kalkulator.md` §8: przeliczone — sobota 2,375 (spec 2,28), postój po 20:00 0,73 (spec 0,80), `PROFILE_CHEAP` tabela bez `step_size`, CDR bez `tax_included`; wynik „2.2.1 pierwotnego” niesprawdzalny |
| T13 USA (podatki, limity cen) | czeka | 23 CFR 680 poza rejestrem |
| T14, T15 praktyka zaokrągleń | częściowo | Wniosek „bez zaokrągleń pośrednich”; `Decimal` i tolerancja 0,01 — praktyka bez źródła, treść w `zrodlo/` |
| C1, C2, C4, C7 (CDR) | przeniesione (C4, C7 jako Wniosek) | `cdr-i-wycena.md` |
| C3, C5 (mechanika CDR) | czeka | cel `ev-ocpi-roaming-expert/references/moduly.md`, następna fala |
| C6, C8 | czeka | procedura bez źródła; prawo VAT i faktur poza rejestrem |
| Y1, Y2, Y4, Y5, Y10, Y11 (płatności) | przeniesione (Y10, Y11 jako Wniosek) | `cdr-i-wycena.md` §5, `sesja-przerwana.md` §4 |
| Y3 endpointy Payments | czeka | cel `moduly.md`, następna fala |
| Y6, Y7 | czeka | AFIR i PSD2 są w rejestrze, ale bez lokalnego tekstu w tej sesji |
| Y8, Y9, Y12–Y15 | czeka | PCI DSS (`niedostepne.yaml`), zasady schematów kartowych, VAT, RODO — poza rejestrem |
| skrypt `ocpi_tariff_calc.py` | przeniesione | `ev-billing-tariff-expert/scripts/`, `references/kalkulator.md`, testy `tests/test_ocpi_tariff_calc.py` (43): model 2.3.0 (`before_taxes`/`taxes`, `PriceLimit`, `tax_included`) i 2.2.1; poprawki: `day_of_week: []`, zaokrąglanie tylko postoju przy TIME + PARKING_TIME, nadwyżka czasu do ostatniego okresu tylko dla wymiaru czasu |
| skrypt `cdr_flow.py` (przykład) | odrzucone | poza zakresem kalkulatora; dane przykładu użyte w teście |
| skrypt `ev_id_check.py` | czeka | reguły ze źródeł wtórnych, sprzeczne z OICP `EvcoIDType`; do przebudowy z OICP23-CPO-DT |
| sekcje 6–8 (eMSP, identyfikatory, role rynku) | czeka | następna fala; cel: istniejące skille (decyzja 2026-11-15) |

Sprzeczności rozstrzygnięte na korzyść źródła: `Price` w 2.3.0 to `before_taxes`/`taxes` (pack-ev: `excl_vat`/`incl_vat`;
uwaga: przykłady FAC w samym 2.3.0 mają starą postać), kierunek zmiany `MeteringSignature` → `SignedMeteringValues`
(OICP 2.3), SOAP w OICP (zakres „nowe usługi od 2.2” vs „od 2.3 tylko REST”), `group_id` (`CiString(36)`, 20 znaków to
rada), kody 2002/2004, reguła 15 minut zależna od typu tokenu, `parking_places` vs `parking`, równoległe połączenia
2.2.1/2.3.0 (specyfikacja nie opisuje). Niespójności w samych specyfikacjach są opisane w plikach (np. `RESERVED` vs
`RESERVATION`, `ModuleID` bez `payments`, `lang` w `InfoTextType`).

## Fala 1, część 2 (2026-11-18 – 2026-11-27): pozostałe skille i USA
Treść pisali agenci, każdy na osobnych plikach. Przed merdżem kluczowe twierdzenia każdego z nich sprawdzono w tekście
dokumentów z `.cache/ev-kb/`. Wszystkie znaczniki mają status `OK` w `ev_kb.py check`; znaczniki z literą bloku OCPP
są od 2026-11-18 sprawdzane tylko w swoim bloku.

| Pozycje | Stan | Gdzie |
|---|---|---|
| sesja OCPP↔OCPI end-to-end (luki-podsumowanie) | przeniesione | `ev-integration-architect/references/sesja-ocpp-ocpi.md` |
| migracja CSMS (luki-E, luki-podsumowanie) | przeniesione | `ev-integration-architect/references/migracja-i-rozszerzenia.md` §7–12 |
| prawo PL art. 11–12c, 29f, 42, 60–67, kary; AFIR art. 3 ust. 5–11, art. 4 (luki-D) | przeniesione | `ev-compliance-expert/references/prawo-pl.md`, `afir-mapa.md` |
| C3, C5, Y3; Sessions PATCH, Tokens 2001–2004, Payments 2.3.0 (luki-B) | przeniesione | `ev-ocpi-roaming-expert/references/moduly.md` |
| SC2, SC3, SC7, SC11, SC12, EM15, VX6, VX7; K01/K09, `isGridCritical`, „Accepted ≠ zastosowano” (luki-C, luki-A) | przeniesione | `ev-energy-smart-charging-expert/references/` (3 pliki) |
| HW1, HW3, HW4, HW5, HW6, HW7, HW9, HW10, HW13 (luki-C §4) | częściowo | `ev-evse-hardware-expert/references/` — tylko strona protokołów; treść IEC 61851-1, EN IEC 62196, IEC 60364-7-722 niedostępna |
| wiersze 138, 174, 175 (część), 176, 222, 223; 179/180, 186, 226 jako Wniosek (luki-E) | przeniesione | `ev-cpms-architect/references/`, `ev-charging-operations-expert/references/` |
| D1–D3, D5–D8, E1, E2 (część), E4–E6, E12, M1 (część), M3 (część) (luki-B §6–8); luki-F §1, §4, §5 (część) | przeniesione | `ev-domain-expert/references/identyfikatory-i-role.md`, `ev-product-designer/references/` |
| T13, wiersze 172, 173, 219–221 (USA, NEVI) | przeniesione | `ev-compliance-expert/references/usa.md`; źródła `sources/us-prawo.yaml` (23 CFR 680, NIST HB44 §3.40) |

Czeka albo odrzucone (powód):
- SC1, EM2, EM3, VX4, VX5: RED III, EPBD, RfG niezarejestrowane — fala 3; EUR-Lex od 2026-11-18 blokuje pobieranie.
- SC6, EM7, HW1/HW5/HW6/HW9/HW13 (treść normy), VX2, VX3: normy płatne (`sources/niedostepne.yaml`).
- HW10: zmiana MID 2026/706 niesprawdzona (EUR-Lex); `metrologia.md` może być nieaktualny dla liczników DC.
- wiersz 177 (legalizacja licznika): Prawo o miarach niezarejestrowane; wiersz 224 (DST): dyrektywa 2000/84/WE
  niezarejestrowana; wiersz 141 (free vend): nie sprawdzono w 201-P2 C.
- D4 (cyfra kontrolna EMAID), format EVSE ID: dokument EVRF „E-mobility ID-codes”, eMI3, DIN SPEC 91286 niezarejestrowane.
- E15 (RODO), M1 (host, producent, flota), luki-F §4 (opłaty dystrybucyjne): brak źródła w rejestrze.
- klasy P i R bez faktów, z których dałoby się wyprowadzić Wniosek: SC4, SC5, SC8–SC10, EM5–EM14, EM16–EM22, E3, E7–E9,
  E11, E13, E14, M2, M4–M6 — zostają tutaj.

Błędy w analizie luk wykryte przy pracy:
- luki-E wiersz 180 cytuje StatusSchedule jako `[OCPI230 §8.4.24]`; poprawnie §8.4.27 (§8.4.24 to PublishTokenType).
- luki-B D5/D6 cytują `OCPI230 §16.1` dla CiString; w 2.3.0 to §17.4 (§16 to moduł Payments).
- pack-ev podaje dla EVSE ID „1–31 znaków” po `E`; wyrażenie OICP dopuszcza 1–30 `[OICP23-CPO-DT #EvseIDType]`.

## Pozostałe skille pack-ev
Nieprzetworzone: pozycje nieujęte w tabelach powyżej. Kolejność i decyzje: `analiza/luki-podsumowanie.md`. Decyzje właściciela z 2026-11-15:
- praktyka (P): przenosić, co pasuje; resztę zostawić tutaj z adnotacją;
- zakres USA (NEVI 23 CFR 680, NIST HB44): **tak**, wymaga rejestracji źródeł i rozszerzenia taksonomii D12.06;
- tematy bez skilla (identyfikatory, role rynku, eMSP, bateria, floty): do istniejących skilli `ev-*`, bez nowych.
