# pack-ev → ev-intelligence: analiza luk (2026-11-15)

Analiza tylko do odczytu, 6 grup. Raporty szczegółowe (tabela luk z plikiem:linią w pack-ev, celem w ev-intelligence,
klasą i źródłem) leżą obok tego pliku: `luki-A.md` … `luki-F.md`.

Klasy luk:
- **F** — fakt do sprawdzenia w źródle oficjalnym;
- **P** — praktyka bez źródła oficjalnego;
- **R** — procedura, bez faktów.

## Liczby

| Grupa | pack-ev → ev-intelligence | Luki | F | P | R |
|---|---|---|---|---|---|
| A | OCPP 1.6/2.x, symulacja, certyfikacja, diagnostyka, onboarding → ev-ocpp-expert, ev-evse-diagnostics-expert | 59 | 19 | 3 | 37 |
| B | OCPI, OICP, taryfy, CDR, płatności, eMSP, identyfikatory, role → ev-ocpi-roaming-expert, ev-billing-tariff-expert | 107 | 68 | 16 | 23 |
| C | smart charging, energia, V2X, sprzęt, bateria, floty → ev-energy-smart-charging-expert, ev-evse-hardware-expert | 84 | 40 | 21 | 23 |
| D | regulacje EU/PL/US, metrologia, bezpieczeństwo, ISO 15118 → ev-compliance-expert, ev-iso15118-pki-expert | 96 | 72 | 11 | 13 |
| E | architektura CPMS, migracja, sesja, aktywa, KPI → ev-cpms-architect, ev-integration-architect, ev-charging-operations-expert | 93 | 25 | 57 | 11 |
| F | przegląd, słownik, baza wiedzy, ekonomika, rozwój lokalizacji → ev-domain-expert, ev-product-designer | ≈65 | ≈30 | ≈15 | ≈20 |
| **Razem** | | **≈504** | **≈254** | **≈123** | **≈127** |

**Najważniejsze ustalenie:** pack-ev nie ma ani jednego znacznika `[id §sekcja]` i opiera się na źródłach wtórnych
(libocpp, josev, blogi). Niczego nie da się skopiować dosłownie. Z pack-ev bierzemy **temat**, a fakt opracowujemy od
nowa z dokumentu w rejestrze.

W kilkudziesięciu miejscach pack-ev jest **sprzeczny** z ev-intelligence (≈60 konfliktów opisanych w raportach). Prawie
zawsze rację ma ev-intelligence (np. stacja bez profili ładuje bez limitu, a nie 48 A; `transactionId = -1` offline
w 1.6; edycje OCPP 2.0.1 i Security Whitepaper; ceny w OCPI 2.3.0 jako `before_taxes`/`taxes`).

## Co da się zrobić od razu (źródło już w rejestrze)
Około 100 luk F ma dokument w `sources/*.yaml`; trzeba tylko znaleźć i sprawdzić sekcję. Najcenniejsze:
- **OCPP:**
  - pełna tabela przejść statusów 1.6;
  - Boot `Pending`/`Rejected`;
  - „`Accepted` ≠ zastosowano”;
  - Device Model i `GetBaseReport` → `NotifyReport`;
  - tabela walidacji K01, K09, `isGridCritical`.
- **OCPI:**
  - PATCH w Sessions dubluje `charging_periods`;
  - moduł Tokens (`AuthorizationInfo`, `LocationReferences`, kody 2002/2004);
  - moduł Payments 2.3.0;
  - Broadcast Push, Open Routing, `hub_party_id`;
  - pola publikacji lokalizacji (`parking_type`, `facilities`…).
- **OICP:** pełna tabela kodów i obowiązki EMP.
- **Sesja OCPP↔OCPI end-to-end** (transakcja, Session, CDR, późna transakcja po offline) → ev-integration-architect.
- **Migracja CSMS:** co nie przenosi się samo, `NetworkConnectionProfile`, ponowna wymiana credentials.
- **Prawo PL** (ustawa o elektromobilności): art. 11–12c, 29f, 42, 62, 67, kary. ev-compliance-expert oznacza je dziś
  jako „nie opracowano”.
- **AFIR:** art. 3 ust. 5–11, art. 4.

## Źródła do zarejestrowania (pobranie + SHA-256 — hosty dostępne z kontenera)
- **Akty UE:**
  - RED III art. 20a;
  - EPBD art. 14 i 16;
  - NIS2 (art. 21, 23, 34);
  - CRA (art. 13, 14, aneks I; zgłaszanie podatności od 11.09.2026);
  - Data Act 2023/2854;
  - RED DA 2022/30 i 2026/339;
  - dyrektywa 2000/84/WE;
  - zmiana MID 2026/706 (MI-011, liczniki EVSE). Jej istnienie trzeba najpierw sprawdzić w EUR-Lex; jeśli istnieje,
    `metrologia.md` jest nieaktualny w sprawie liczników DC.
- **Specyfikacje:**
  - OCMF (wydawca S.A.F.E. e.V. — da się zarejestrować, dziś w `niedostepne.yaml`);
  - RFC 6455;
  - repozytorium ocpi/ocpi (przykłady JSON);
  - strony certyfikacji OCA i OCTT.
- **USA** (tylko po Twojej decyzji o zakresie): 23 CFR 680 (NEVI: uptime 97 %, raportowanie), NIST HB44 3.40.
- **Do `niedostepne.yaml`** (płatne):
  - SAE J1772;
  - SAE J3400;
  - IEC 62955.

  Sprzęt (CP/PWM, tryby, RCD) i ISO 15118 opierają się na normach niedostępnych, więc z tych skilli przenosimy
  prawie wyłącznie pola OCPP.
- Drobna niespójność w samym ev-intelligence: `niedostepne.yaml` oznacza PSD2 jako niezarejestrowaną, choć
  `eu-inne.yaml` ma wpis.

## Skrypty
| Skrypt (pack-ev) | Decyzja | Cel w ev-intelligence | Warunek |
|---|---|---|---|
| `ocpp_log_analyze.py` | przenieść | ev-evse-diagnostics-expert/scripts | poprawić `transactionId = -1`, ramki 2.1 typu 5/6, opis progu 30 s |
| `ocpi_tariff_calc.py` | przenieść | ev-billing-tariff-expert/scripts | dodać model 2.3.0 (`before_taxes`/`taxes`, PriceLimit), sprawdzić step_size |
| `composite_schedule.py` | przenieść po przebudowie | ev-energy-smart-charging-expert/scripts | reguły z libocpp → z OCA (K06.FR.02, różnice 1.6/2.0.1) |
| `uptime_kpi.py` | przenieść | ev-charging-operations-expert/scripts | bez trybu NEVI albo po rejestracji 23 CFR 680 |
| `ocmf_check.py` | przenieść | ev-compliance-expert/scripts | po rejestracji OCMF |
| `charge_sim.py`, `ocpp_ws.py` | po poprawkach | ev-integration-architect/scripts | `Charging` przed `StartTransaction`; handshake bez podprotokołu wg [J16 §3.2] |
| `station_economics.py` | do decyzji | ev-product-designer/scripts | czy poddomena D17.02 przyjmuje metodę bez danych rynkowych |
| `ev_id_check.py` | nie (przebudować) | — | reguły ze źródeł wtórnych, sprzeczne z OICP EvcoIDType |
| `kb.py` + `test_kb_ev.py` | nie | — | dubluje `tools/ev_kb.py`, słabszy model dowodu |
| `standards_check.py` | idea, nie kod | `tools/ev_kb.py` + pole dat w `sources/*.yaml` | — |
| `run_ev_exam.py` | nie (runner zależy od tf) | `evals/skill_evals` | 104 pytania jako scenariusze po weryfikacji faktów |

Wszystkie są w samej bibliotece standardowej. Testy (własne `main()` + ścieżki `.claude/`) trzeba przepisać na
`unittest`, żeby uruchomiła je bramka `skill_check.py`.

## Decyzje do podjęcia
1. **Praktyka (P, ≈123):** ev-intelligence nie ma na nią miejsca. `knowledge/` przyjmuje tylko obserwacje urządzeń
   klasy D. Do wyboru: nie przenosić, albo przenosić tylko jako **Wniosek** wyprowadzony z faktów F z cytatem.
2. **Zakres USA** (NEVI, HB44): taksonomia D12.06 dziś go nie obejmuje.
3. **Słownik** (taksonomia D00.01 istnieje, treści brak; `docs/PLAN.md` zakładał `glossary/GLOSSARY.md`): gdzie ma
   trafić.
4. **Tematy bez skilla docelowego:**
   - identyfikatory i role rynku → ev-domain-expert;
   - platforma eMSP → ev-product-designer;
   - bateria pojazdu i floty → ev-evse-diagnostics-expert / ev-domain-expert, rozproszone po billing/OCPI/OCPP.

   Do wyboru: tak, czy nowe skille `ev-*` w taksonomii.
5. **Nazwa:** CPMS (ev-intelligence) czy CSMS (pack-ev, OCPP 2.x) jako kanoniczna.
6. **Procedury (R, ≈127):** dotyczą „jak pracować” (np. macierz testów T1–T14, katalog scenariuszy awarii, drzewo
   diagnozy rozjazdu energii). Proponuję brać tylko te, które opierają się na faktach F z cytatem.

## Proponowana kolejność
1. **Fala 1** — luki F ze źródłem już w rejestrze, skill po skillu. Dla każdego skilla: scenariusze → treść z cytatami
   → `ev_kb.py check` → `skill_check.py` PASS. Pilot: ev-ocpp-expert, potem OCPI/billing, potem prawo PL.
2. **Fala 2** — skrypty z warunkami spełnionymi bez nowych źródeł: `ocpp_log_analyze`, `ocpi_tariff_calc`,
   `composite_schedule`, `uptime_kpi` bez NEVI.
3. **Fala 3** — rejestracja nowych źródeł UE i OCMF, potem treść, która od nich zależy, oraz `ocmf_check`.
4. **Fala 4** — decyzje 1–5 (USA, słownik, nowe skille), potem ich treść.
5. **Na końcu** — usunięcie pack-ev z tf (osobny PR na #265, z notą migracyjną dla istniejących instalacji).
