# EV Intelligence — podsumowanie koncepcji i plan realizacji

> Wersja planu: 1.0 · Data: 2026-11-07 · Status: Draft do akceptacji

Dokument zbiera w jednym miejscu pierwotną koncepcję, wnioski z porównania opinii kilku modeli AI (ChatGPT, Grok, Gemini, Perplexity) oraz pomysły na monetyzację. Na tej podstawie proponuje konkretny, etapowy plan działania.

---

## Część I — Podsumowanie

### 1. Co budujemy (w jednym zdaniu)

**EV Intelligence** to wersjonowany, opisany źródłami system wiedzy branżowej o elektromobilności i infrastrukturze ładowania, z którego agenci AI (Claude, inne modele, własne agenty) korzystają przez **Skills**, a docelowo przez **MCP/API**. Ma pozwalać nie tylko odpowiadać na pytania, ale **podejmować dobre decyzje projektowe** (CPMS, integracje, roaming, operacje, rozliczenia).

### 2. Zasady, co do których wszystkie źródła się zgadzają

| # | Zasada | Co to oznacza w praktyce |
|---|--------|--------------------------|
| 1 | **Modularność zamiast jednego mega-skilla** | Wąskie skille ładowane kontekstowo; ciężka treść w plikach referencyjnych (progressive disclosure). |
| 2 | **Rozdział Knowledge ↔ Skills** | Knowledge = *co wiemy* (fakty, standardy, urządzenia). Skills = *jak tego użyć* (procedury, checklisty, drzewa decyzyjne). |
| 3 | **Każdy fakt ma pochodzenie, wersję i poziom wiarygodności** | Metadane w każdym dokumencie; klasy źródeł A/B/C/D; rozróżnienie: standard / zalecenie / praktyka rynkowa / specyfika producenta / hipoteza. |
| 4 | **Kanoniczny model domenowy** | Location → ChargePoint/Station → EVSE → Connector; Token, Session, Transaction, CDR, Tariff, ChargingProfile… z mapowaniem na OCPP, OCPI, OICP i model wewnętrzny. |
| 5 | **Największa wartość = „brudna” wiedza praktyczna** | Edge cases, vendor quirks, różnice „deklarowane vs. rzeczywiste”, mapowania między protokołami, anti-patterns. To trudno skopiować. |
| 6 | **Najpierw repozytorium Git, potem silnik** | Git daje wersjonowanie, review, historię i działa od razu z Claude Code. RAG/graf/MCP dopiero, gdy treści jest dość dużo. |
| 7 | **Wiedza musi być testowana i aktualizowana** | Zestawy pytań kontrolnych na domenę; comiesięczny monitoring standardów; aktualizacja przez review, nigdy automatyczne nadpisanie. |
| 8 | **Budujemy pod konkretne zadania** | Każdy obszar jest uzasadniony zadaniem agenta (spec CPMS, mapowanie OCPI, drzewo diagnostyczne…). |

### 3. Architektura docelowa (3 warstwy)

```
┌──────────────────────────────────────────────────────────────┐
│ L3  Agent Interfaces   Claude Skills · MCP server · REST API │
├──────────────────────────────────────────────────────────────┤
│ L2  Knowledge Engine   full-text · semantic/RAG · filtry     │
│                        metadanych · Knowledge Graph · źródła │
├──────────────────────────────────────────────────────────────┤
│ L1  Knowledge Repo     Markdown + YAML/JSON (Git)            │
│                        schematy · przykłady · diagramy       │
└──────────────────────────────────────────────────────────────┘
```

Rodzaje wiedzy trzymane **rozdzielnie** (sugestia Perplexity, zgodna z modelem A/B/C/D):

- **normatywna** — specyfikacje i regulacje (klasa A),
- **producencka** — dokumentacja vendorów (klasa B),
- **ekspercka/rynkowa** — publikacje, dobre praktyki (klasa C),
- **implementacyjna/operacyjna** — obserwacje z wdrożeń, runbooki, known issues (klasa D, „EV Implementation Intelligence”),
- **produktowa (projektowa)** — decyzje dotyczące konkretnego CPMS klienta/naszego; nigdy nie mieszana z normą.

### 4. Mapa domen (taksonomia v0 → do rozwinięcia w Etapie 0)

1. Protokoły i standardy komunikacji — OCPP 1.6J/2.0.1/2.1, OCPI 2.1.1/2.2.1/2.3, OICP, eMIP, OCHP, ISO 15118-2/-20, DIN SPEC 70121, IEC 61851, IEC 62196, Modbus, MQTT, OpenADR, IEEE 2030.5, EEBus
2. Urządzenia i producenci — AC/DC/HPC, modułowe i satelitarne, liczniki, kontrolery, RFID, terminale płatnicze, chłodzenie
3. CPMS/CSMS — architektura, flota, provisioning, konfiguracja, sesje, autoryzacja, firmware, multi-tenancy, white-label
4. Roaming i interoperacyjność — CPO/eMSP/hub, Hubject, Gireve, e-clearing.net, tokeny, CDR, settlement, reconciliation
5. Operacje — NOC, monitoring, incydenty, diagnostyka zdalna, field service, SLA, KPI
6. Energia i zarządzanie mocą — smart charging, DLM, EMS, peak shaving, DR, PV, BESS, V2G
7. Rozliczenia, taryfy, płatności — modele taryf, idle fee, ad hoc, VAT, waluty, korekty
8. EV–EVSE — BMS, krzywe ładowania, SOC/SOH, Plug & Charge, Autocharge, kompatybilność
9. Bezpieczeństwo — TLS, PKI, security profiles OCPP, secure firmware, IEC 62443
10. Regulacje i compliance — AFIR, MID, Eichrecht, NAP/dane, przepisy krajowe (PL), RED, NIS2, CRA
11. Architektura IT i integracje — REST, WebSocket, event-driven, Kafka, timeseries, observability, IAM
12. Produkt, UX i modele biznesowe — role, customer journeys, UX NOC/admin, flotowe, benchmarki
13. *(przekrojowo)* Słownik terminologii i kanoniczny model danych
14. *(przekrojowo)* Use cases — remote start, onboarding roamingu, diagnostyka, DLM, reconciliation

### 5. Biblioteka skilli (docelowo)

| Grupa | Skille |
|-------|--------|
| Router | **EV Domain Expert** — rozpoznaje zadanie i dobiera skille |
| Protokoły | OCPP Expert, OCPI/Roaming Expert, ISO 15118 & PKI Expert |
| Systemy | CPMS Architect, EV Integration Architect |
| Urządzenia | EVSE Hardware Expert, EVSE Diagnostics Expert |
| Operacje | Charging Operations Expert |
| Biznes | EV Billing & Tariff Expert, EV Product Designer, (później) Energy & Smart Charging Expert, Compliance Expert |

Każdy skill ma: *kiedy używać*, procedurę krok po kroku, wymagane cytowanie źródeł (wersja + sekcja), anti-patterns, odwołania do plików referencyjnych oraz własny zestaw testów.

### 6. Monetyzacja — synteza

Wszystkie źródła są zgodne: **da się zarabiać, ale nie na samej dokumentacji** (ta jest publiczna), tylko na oszczędności czasu, mniejszej liczbie błędów integracyjnych i dostępie do wiedzy praktycznej w formie gotowej dla agentów.

**Rekomendowana kolejność (konsensus):**

1. **Konsulting + baza jako dźwignia** (najszybszy przychód, jednocześnie źródło nowych przypadków z praktyki) — audyty zgodności OCPP/OCPI, architektura CPMS, specyfikacje, drzewa diagnostyczne.
2. **Produktyzacja** — płatne pakiety skilli + aktualizacje dla zespołów (prywatne repo / paczki dla Claude, Cursor itp.), 3–5 firm pilotażowych.
3. **Platforma** — SaaS + MCP/API, licencje Enterprise z prywatną wiedzą klienta.

Uzupełniająco: raporty i analizy, szkolenia/certyfikacja, sprzedaż w marketplace'ach.

Hipotezy cenowe do przetestowania (nie są potwierdzonymi stawkami rynkowymi): Starter 49–99 €/mies., Professional 199–499 €/mies., Enterprise 1–5 tys. €/mies. lub 3–12 tys. €/rok za zespół; projekty doradcze 15–50 tys. PLN.

Ocena realistyczna: **niszowy, wysokomarżowy biznes B2B** (kilkadziesiąt–kilkaset potencjalnych klientów w Europie: CPO, eMSP, producenci EVSE, twórcy CPMS, firmy energetyczne, integratorzy), a nie masowy SaaS. O sukcesie decydują: aktualność, głębokość wiedzy praktycznej, mapowanie na decyzje produktowe i wiarygodność autora.

### 7. Ryzyka i luki, których w dotychczasowych analizach zabrakło

| Ryzyko | Dlaczego istotne | Mitygacja |
|--------|------------------|-----------|
| **Prawa autorskie do norm** | Normy ISO/IEC (15118, 61851, 62196, 62443) są płatne i chronione — nie można ich redystrybuować ani kopiować fragmentów do płatnego produktu. Specyfikacje OCA/EVRF mają własne licencje. | Własne opracowania i streszczenia, odwołania do numerów sekcji, bez kopiowania tekstu norm. Sprawdzić licencję każdej specyfikacji przed użyciem (zadanie w Etapie 0). |
| **Poufność wiedzy z wdrożeń** | Obserwacje z projektów (klasa D) mogą być objęte NDA klientów lub producentów. | Anonimizacja, zgoda na wykorzystanie, pole `confidentiality` w metadanych, osobne prywatne repo. |
| **Odpowiedzialność za treść** | Klient Enterprise oprze decyzje na wiedzy — błąd kosztuje. | Wyraźne poziomy pewności, cytowania, disclaimer, testy wiedzy, proces review. |
| **Zbyt szeroki zakres** | 12+ domen to praca na lata; ryzyko płytkiej treści wszędzie. | Szeroka taksonomia, ale głęboka treść tylko w MVP (OCPP, OCPI, CPMS, EVSE, Operations). |
| **Konkurencja dużych graczy** | Vendorzy CPMS (np. developer huby z API i MCP) dają darmową dokumentację. | Nie konkurujemy ilością dokumentacji; wyróżnikiem jest wiedza przekrojowa i neutralna (niezależna od jednego vendora). |
| **Starzenie się wiedzy** | OCPP 2.1, OCPI 2.3/3.0, AFIR, nowe firmware'y. | Comiesięczny monitoring + pola `last_verified`, `status`; raport zmian. |
| **Halucynacje agentów** | Agent może „dopowiedzieć” parametry. | Skille wymagają cytowania; testy „nie wymyślaj parametrów”; walidatory JSON/schematów. |

> Uwaga: informacje o najnowszych wersjach (np. OCPP 2.1, OCPI 2.3.0, OCPP 2.0.1 jako IEC 63584) należy potwierdzić w źródłach pierwotnych w Etapie 0 — w tym dokumencie traktujemy je jako punkt wyjścia, nie jako zweryfikowane fakty.

---

## Część II — Plan realizacji

Założenie robocze: jedna osoba-ekspert + agenci AI, ok. 15–20 h tygodniowo. Przy większym zespole etapy można zrównoleglić.

### Etap 0 — Fundamenty (tydzień 1–3)

Cel: ustalić „reguły gry”, zanim powstanie treść. Bez tego za pół roku repozytorium będzie niespójne.

| # | Zadanie | Rezultat (plik) |
|---|---------|-----------------|
| 0.1 | **EV Knowledge Taxonomy v1.0** — pełna mapa domen, poddomen i zależności, także mniej oczywistych obszarów · ✅ zaakceptowana (D0, 2026-11-07) | [`taxonomy/TAXONOMY.md`](../taxonomy/TAXONOMY.md) + `taxonomy/taxonomy.yaml` |
| 0.2 | **EV Knowledge Standard** — szablon dokumentu, metadane, klasy źródeł A–D, poziomy pewności, zasady cytowania, wersjonowanie, statusy | `standards/KNOWLEDGE-STANDARD.md`, `templates/knowledge-doc.md` |
| 0.3 | **EV Skills Architecture** — budowa skilla, zależności, router, konwencje nazw, sposób odwoływania się do wiedzy | `standards/SKILLS-ARCHITECTURE.md`, `templates/SKILL.md` |
| 0.4 | **Słownik terminologii** (ok. 150 pojęć, synonimy i różnice między protokołami) | `glossary/GLOSSARY.md` |
| 0.5 | **Kanoniczny model domenowy v0** — encje i relacje | `data-model/canonical-model.md` + `data-model/schema/*.yaml` |
| 0.6 | **Rejestr źródeł** z oceną licencji (co wolno cytować / streszczać / nie wolno) · 🟡 rozpoczęty: OCPP (OCA) | `sources/*.yaml` |
| 0.7 | Struktura repozytorium + lint metadanych (prosty skrypt walidujący frontmatter) | katalogi, `tools/validate_metadata.py`, CI |
| 0.8 | **Walidacja skilli narzędziami fabryki tf** (bramka jakości, scenariusze, audyt) bez przejmowania jej struktury · ✅ działa, pilotaż `ev-domain-expert` przeszedł bramkę | [`docs/SKILLS-WORKFLOW.md`](SKILLS-WORKFLOW.md), `tools/factory_check.py` |

Proponowany frontmatter każdego dokumentu wiedzy:

```yaml
---
id: ocpp-16-heartbeat
domain: protocols/ocpp
topic: Heartbeat
applies_to: [OCPP 1.6J]
knowledge_type: normative | vendor | expert | implementation | product
source_class: A | B | C | D
sources:
  - title: OCPP 1.6 Edition 2
    section: "4.6 Heartbeat"
    url: https://openchargealliance.org/...
published: 2017-09-28
last_verified: 2026-11-07
status: active | deprecated | draft
confidence: official | verified | observed | hypothesis
confidentiality: public | internal | client-restricted
related: [ocpp-16-bootnotification, ops-offline-detection]
---
```

**Punkt decyzyjny D0:** akceptacja taksonomii, standardu i architektury skilli.

### Etap 1 — MVP wiedzy i pierwszych skilli (tydzień 4–10)

Cel: pierwsze realnie użyteczne skille na 5 domenach MVP.

| Domena | Minimalny zakres treści | Skill |
|--------|------------------------|-------|
| OCPP | 1.6J vs 2.0.1 (różnice, niekompatybilność), cykl życia transakcji, Boot/Heartbeat/Status, Authorize, Remote Start/Stop, MeterValues, konfiguracja vs Device Model, firmware/diagnostics, security profiles, offline behavior | **OCPP Expert** |
| OCPI | role, wersje, Credentials, Locations, Tariffs, Tokens, Sessions, CDRs, Commands; push vs pull; hub; korekty CDR | **OCPI/Roaming Expert** |
| CPMS | moduły, maszyna stanów sesji, zarządzanie własnymi vs roamingowymi ładowarkami, statusy (offline/unavailable/faulted), multi-tenancy | **CPMS Architect** |
| EVSE | model danych EVSE, karta techniczna urządzenia (szablon), 3–5 przykładowych kart rodzin urządzeń | **EVSE Hardware Expert** |
| Operations | 10 scenariuszy operacyjnych (np. „online, ale nie startuje sesja”, „brak Heartbeat”), drzewa diagnostyczne | **EV Operations / Diagnostics Expert** |
| Przekrojowo | mapowanie OCPP ↔ OCPI (statusy, sesje, CDR) | **EV Domain Expert** (router) |

Plus **5 use cases end-to-end**: remote-start, heartbeat-loss detection, roaming onboarding, charger diagnostics, session reconciliation.

Miara gotowości: ≥ 50 dokumentów wiedzy z kompletnymi metadanymi, 6 skilli, każdy z ≥ 15 pytaniami testowymi.

**Punkt decyzyjny D1:** czy skille dają lepsze wyniki niż „goły” model? (porównanie na zestawie testowym).

### Etap 2 — Testowanie wiedzy i monitoring (równolegle z Etapem 1, od tygodnia 6)

| Zadanie | Rezultat |
|---------|----------|
| Zestawy pytań kontrolnych na domenę (poprawność, cytowanie, brak zmyślonych parametrów, rozróżnianie normy od praktyki) | `evals/<domena>/*.yaml` |
| Prosty runner ewaluacji (agent ze skillem vs bez; ocena wg rubryki) | `tools/run_evals.py`, raport w `evals/reports/` |
| **Comiesięczny monitoring standardów** — raport po polsku: najważniejsze zmiany, pozostałe obserwacje, tabela (standard / wersja / status / data / wpływ), lista sprawdzonych źródeł, rozdział potwierdzone vs. projekty/niezweryfikowane | `monitoring/reports/RRRR-MM.md`, `monitoring/SOURCES-WATCHLIST.md` |
| Proces aktualizacji: zmiana → issue → review → aktualizacja dokumentów → ponowne evals | `CONTRIBUTING.md` |

### Etap 3 — Walidacja rynkowa (tydzień 8–16)

Cel: sprawdzić, czy ktoś za to zapłaci, zanim zbudujemy platformę.

1. Wykorzystać bazę we własnych projektach / konsultingu (dowód wartości + nowe przypadki klasy D).
2. Pozyskać **3–5 firm pilotażowych** (CPO, twórca CPMS, producent EVSE, integrator) — płatny pilotaż z dostępem do prywatnego repo ze skillami.
3. Zebrać metryki: czas przygotowania specyfikacji/audytu z bazą vs bez, liczba wykrytych błędów integracyjnych, opinie użytkowników.
4. Przetestować hipotezy cenowe i pakietowanie (Starter / Professional / Enterprise vs roczna licencja zespołowa).

**Punkt decyzyjny D2:** go / pivot / stop dla wersji komercyjnej; wybór modelu (licencja repo vs SaaS vs Enterprise).

### Etap 4 — Rozszerzenie wiedzy (tydzień 12–26)

Kolejność według wartości dla pilotów (domyślna propozycja):

1. Rozliczenia, taryfy, CDR, płatności ad hoc → **EV Billing & Tariff Expert**
2. Smart charging, DLM, EMS → **Energy & Smart Charging Expert**
3. ISO 15118, Plug & Charge, PKI, bezpieczeństwo OCPP → **ISO 15118 & PKI Expert**
4. Regulacje (AFIR, MID, Eichrecht, PL) → **Compliance Expert**
5. OICP/Hubject, eMIP/Gireve, OCHP; OCPP 2.1; OCPI 2.3
6. **EV Implementation Intelligence** — vendor quirks i macierz kompatybilności (model + firmware + źródło obserwacji)
7. Produkt i UX → **EV Product Designer**, **EV Integration Architect**

### Etap 5 — Knowledge Engine i MCP (od ok. 6. miesiąca, gdy > 300 dokumentów)

| Zadanie | Uwagi |
|---------|-------|
| Indeks full-text + semantic search z filtrami metadanych (wersja, klasa źródła, status) | Repo Git pozostaje jedynym źródłem prawdy; indeks generowany z niego. |
| **EV Knowledge MCP Server**: `search_ev_knowledge`, `get_protocol_details`, `compare_protocol_versions`, `get_evse_specification`, `get_ocpp_capabilities`, `get_error_diagnostics`, `get_roaming_data_model`, `get_use_case`, `get_implementation_guidance` | Każda odpowiedź zwraca źródła i poziom pewności. |
| Knowledge Graph (relacje z pola `related` + jawne relacje typu `supports`, `requires`, `implemented_by`, `affects`) | Start od grafu generowanego z YAML; dedykowana baza grafowa dopiero przy realnej potrzebie. |
| Walidatory: JSON Schema dla wiadomości OCPP/OCPI, sprawdzanie mapowań | Agent weryfikuje wynik, a nie tylko generuje tekst. |
| Kontrola dostępu i tiery (public / pro / enterprise / client-private) | Przygotowanie pod SaaS. |

### Etap 6 — Ekosystem agentów i produkt (od ok. 9. miesiąca)

- Agenci zadaniowi: CPMS Product Agent, EV Integration Agent, Operations Agent, EV Solution Architect.
- Prywatne instancje Enterprise (wiedza klienta + nasza baza).
- Raporty branżowe, szkolenia, ewentualnie marketplace.

### Harmonogram w skrócie

```
Tydzień:      1   3   6   8  10  12  16      26        ~36
Etap 0        ████
Etap 1            ███████████
Etap 2                ███████████████████████████ (ciągle)
Etap 3                    ██████████████
Etap 4                            ████████████████
Etap 5                                         ██████████
Etap 6                                                  ████→
Decyzje:         D0          D1         D2
```

### Docelowa struktura repozytorium

```
ev-intelligence/
├── README.md
├── EV-KNOWLEDGE-INDEX.md
├── SOURCES.md
├── CONTRIBUTING.md
├── docs/PLAN.md                 ← ten dokument
├── standards/                   ← Knowledge Standard, Skills Architecture
├── templates/                   ← szablony dokumentu, skilla, karty urządzenia
├── taxonomy/
├── glossary/
├── data-model/                  ← model kanoniczny + mapowania OCPP/OCPI
├── knowledge/                   ← knowledge/<domena.key>/<poddomena.key>/ wg taxonomy.yaml
│   ├── foundations/  protocols/{ocpp,ocpi,oicp,iso-15118,...}
│   ├── hardware/  cpms/  roaming/  operations/  energy/  billing/  metering/
│   ├── security/  regulations/  testing/  it-architecture/  ...
│   └── implementation-intelligence/   ← vendor quirks (klasa D)
├── skills/
│   ├── ev-domain-expert/SKILL.md
│   ├── ev-ocpp-expert/{SKILL.md, references/}
│   └── ...
├── use-cases/
├── evals/
├── monitoring/reports/
└── tools/                       ← walidacja metadanych, evals, indeks
```

### KPI projektu

| Obszar | Miara | Cel MVP (tydz. 10) | Cel 6 mies. |
|--------|-------|--------------------|-------------|
| Treść | dokumenty z kompletnymi metadanymi | 50 | 300 |
| Skille | aktywne skille z testami | 6 | 12 |
| Jakość | odsetek poprawnych odpowiedzi w evals | ≥ 80% | ≥ 90% |
| Jakość | odpowiedzi z poprawnym cytowaniem | ≥ 90% | ≥ 95% |
| Aktualność | dokumenty z `last_verified` < 12 mies. | 100% | ≥ 95% |
| Biznes | firmy pilotażowe | — | 3–5 |
| Biznes | pierwszy przychód | — | konsulting + ≥ 1 płatny pilot |

### Najbliższe kroki (do zrobienia teraz)

1. Zaakceptować ten plan lub wskazać zmiany (zwłaszcza zakres MVP i kolejność Etapu 4).
2. Rozpocząć **Etap 0.1 — EV Knowledge Taxonomy v1.0** (szeroko, z mniej oczywistymi obszarami).
3. Równolegle Etap 0.2–0.3: standard dokumentu i architektura skilli + szablony.
4. Skonfigurować comiesięczne uruchamianie monitoringu standardów (raport po polsku do `monitoring/reports/`).
