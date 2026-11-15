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

## Pozostałe skille pack-ev
Nieprzetworzone. Kolejność i decyzje: `analiza/luki-podsumowanie.md`. Decyzje właściciela z 2026-11-15:
- praktyka (P): przenosić, co pasuje; resztę zostawić tutaj z adnotacją;
- zakres USA (NEVI 23 CFR 680, NIST HB44): **tak**, wymaga rejestracji źródeł i rozszerzenia taksonomii D12.06;
- tematy bez skilla (identyfikatory, role rynku, eMSP, bateria, floty): do istniejących skilli `ev-*`, bez nowych.
