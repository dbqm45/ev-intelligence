<!-- AUTO-GENERATED copy of taxonomy/TAXONOMY-TREE.md by tools/render_taxonomy.py — do not edit by hand. -->

<!-- AUTO-GENERATED from taxonomy/taxonomy.yaml by tools/render_taxonomy.py — do not edit by hand. -->

# EV Knowledge Taxonomy — drzewo (v1.1.0, accepted, 2026-11-08)

**Domeny: 23 · poddomeny: 128 · tematy: 316.** Legenda: `MVP` = Etap 1, `P2` = Etap 4, `P3` = później; ⚠️ = wersje/numery do weryfikacji w źródle pierwotnym.

## Spis domen

| ID | Domena | Priorytet | Poddomeny | Skille | Zależy od |
|----|--------|-----------|-----------|--------|-----------|
| D00 | [Fundamenty, terminologia i model domenowy](#d00--foundations) *(przekrojowa)* | MVP | 5 | `ev-domain-expert` | — |
| D01 | [Protokoły i standardy komunikacji](#d01--protocols) | MVP | 11 | `ev-ocpp-expert`, `ev-ocpi-roaming-expert`, `ev-iso15118-pki-expert` | D00 |
| D02 | [Normy elektrotechniczne i fizyka ładowania](#d02--electrical) | P2 | 5 | `ev-evse-hardware-expert` | D00 |
| D03 | [Urządzenia, komponenty i producenci](#d03--hardware) | MVP | 7 | `ev-evse-hardware-expert`, `ev-evse-diagnostics-expert`, `ev-charging-operations-expert` | D00, D01, D02 |
| D04 | [Pojazd, bateria i interakcja EV–EVSE](#d04--vehicle) | P2 | 5 | `ev-evse-diagnostics-expert` | D01, D02 |
| D05 | [CPMS / CSMS i systemy zarządzania](#d05--cpms) | MVP | 9 | `ev-cpms-architect`, `ev-integration-architect`, `ev-product-designer` | D00, D01, D03 |
| D06 | [Roaming i interoperacyjność](#d06--roaming) | MVP | 5 | `ev-ocpi-roaming-expert` | D00, D01, D05, D09 |
| D07 | [Operacje, utrzymanie i serwis](#d07--operations) | MVP | 6 | `ev-charging-operations-expert` | D03, D05 |
| D08 | [Energia, sieć i elastyczność](#d08--energy) | P2 | 6 | `ev-energy-smart-charging-expert` | D01, D02, D05 |
| D09 | [Taryfy, rozliczenia i płatności](#d09--billing) | P2 | 5 | `ev-billing-tariff-expert` | D00, D05, D10 |
| D10 | [Pomiary i metrologia prawna](#d10--metering) | P2 | 4 | `ev-billing-tariff-expert`, `ev-compliance-expert` | D02, D03 |
| D11 | [Bezpieczeństwo i cyberbezpieczeństwo](#d11--security) | P2 | 5 | `ev-iso15118-pki-expert` | D01, D14 |
| D12 | [Regulacje i compliance](#d12--regulations) | P2 | 7 | `ev-compliance-expert` | D00 |
| D13 | [Testy, zgodność i certyfikacja](#d13--testing) | P2 | 4 | `ev-evse-diagnostics-expert`, `ev-integration-architect`, `ev-compliance-expert` | D01, D03, D05 |
| D14 | [Architektura IT i integracje](#d14--it-architecture) | P2 | 6 | `ev-cpms-architect`, `ev-integration-architect` | D05 |
| D15 | [Dane, analityka i AI](#d15--data-analytics) | P3 | 5 | `ev-product-designer` | D05, D07 |
| D16 | [Produkt, UX i doświadczenie klienta](#d16--product-ux) | P3 | 5 | `ev-product-designer` | D05, D07 |
| D17 | [Modele biznesowe i rynek](#d17--business) | P3 | 4 | `ev-product-designer` | D00 |
| D18 | [Rozwój lokalizacji i wdrażanie infrastruktury](#d18--site-deployment) | P3 | 4 | `ev-charging-operations-expert` | D02, D08, D12 |
| D19 | [Segmenty i konteksty ładowania](#d19--segments) | P3 | 7 | `ev-domain-expert` | D00 |
| D20 | [Zrównoważony rozwój i ESG](#d20--sustainability) | P3 | 4 | `ev-compliance-expert` | D08, D12 |
| D21 | [EV Implementation Intelligence](#d21--implementation-intelligence) *(przekrojowa)* | MVP | 4 | `ev-evse-diagnostics-expert`, `ev-integration-architect`, `ev-charging-operations-expert` | D01, D03, D05 |
| D22 | [Katalog przypadków użycia](#d22--use-cases) *(przekrojowa)* | MVP | 5 | `ev-domain-expert` | D01, D05, D06, D07 |

## D00 · foundations

**Fundamenty, terminologia i model domenowy** — *Foundations, terminology & domain model* · priorytet **MVP** · katalog `knowledge/foundations/`

Wspólny język i model, do którego mapowane są wszystkie protokoły i systemy.

### D00.01 Słownik terminologii `MVP`

`knowledge/foundations/glossary/`

- Definicje pojęć i ich synonimy (Charge Point / Station / EVSE / Connector / Outlet)
- Różnice znaczeń tego samego terminu między OCPP, OCPI, OICP, ISO 15118 i IEC
- Terminologia PL ↔ EN, nazwy stosowane w przepisach krajowych
- Pojęcia mylone (offline vs unavailable vs faulted, session vs transaction, tariff vs price)

### D00.02 Kanoniczny model domenowy `MVP`

`knowledge/foundations/canonical-model/`

- Hierarchia fizyczna (Site/Location → Station/ChargePoint → EVSE → Connector)
- Encje transakcyjne (Token, Authorization, Session, Transaction, MeterValue, CDR)
- Encje handlowe (Tariff, PriceComponent, Contract, Party, Agreement)
- Encje operacyjne (Alarm, Incident, WorkOrder, MaintenanceWindow, Firmware)
- Encje energetyczne (ChargingProfile, PowerLimit, Schedule, GridConnection)
- Mapowanie modelu kanonicznego na OCPP, OCPI, OICP i model wewnętrzny CPMS

### D00.03 Aktorzy i role rynkowe `MVP`

`knowledge/foundations/actors-roles/`

- CPO, eMSP/MSP, hub, CSMS/CPMS vendor, site host, charge point owner
- Role energetyczne (DSO, TSO, sprzedawca, agregator, BRP)
- Role łączone (CPO+eMSP, white-label, platform operator)
- Macierz odpowiedzialności i przepływów danych między rolami

### D00.04 Identyfikatory i rejestry `MVP` ⚠️

`knowledge/foundations/identifiers/`

- EVSE ID, Operator ID, Provider ID (formaty eMI3 / ISO 15118)
- Contract ID / EMAID, PCID, VIN, RFID UID
- OCPI country_code + party_id, rejestry ID krajowe i ich operatorzy
- Unikalność, normalizacja i walidacja identyfikatorów w CPMS

### D00.05 Mapa ekosystemu i organizacji standaryzacyjnych `MVP`

`knowledge/foundations/ecosystem-map/`

- Open Charge Alliance, EVRoaming Foundation, CharIN, Hubject, Gireve, e-clearing.net
- ISO, IEC, CEN-CENELEC, ETSI, SAE, OpenADR Alliance, EEBus Initiative, S.A.F.E.
- Instytucje UE i krajowe (Komisja Europejska, regulatorzy energii, NAP)
- Relacje między standardami — który dokument nadpisuje / odwołuje się do którego

## D01 · protocols

**Protokoły i standardy komunikacji** — *Communication protocols & standards* · priorytet **MVP** · katalog `knowledge/protocols/`

Fundament techniczny — komunikacja EV↔EVSE, EVSE↔CSMS, CPO↔eMSP, system↔energia.

### D01.01 OCPP (EVSE ↔ CSMS) `MVP` ⚠️

`knowledge/protocols/ocpp/`

Skill: `ev-ocpp-expert`

- Wersje 1.5, 1.6J (Edition 2), 2.0.1, 2.1 — różnice, erraty, niekompatybilność 1.6 ↔ 2.x
- Status OCPP 2.0.1 jako normy IEC 63584
- Architektura (WebSocket, JSON-RPC-like, SOAP w 1.5/1.6S), sub-protokoły, kolejkowanie
- Profile/Functional Blocks (Core, Smart Charging, Firmware, Reservation, Local Auth List…)
- Komunikaty — warunki użycia, odpowiedzi, timeouty, retry
- {'Konfiguracja (Configuration Keys 1.6) vs Device Model (2.x': 'Components/Variables)'}
- Cykl życia transakcji 1.6 vs 2.x (TransactionEvent), offline behavior, kolejka transakcji
- Security profiles, certyfikaty, logi bezpieczeństwa
- DataTransfer i rozszerzenia producentów
- Zgodność i certyfikacja (OCTT, profile certyfikacyjne)

### D01.02 OCPI (CPO ↔ eMSP / hub) `MVP` ⚠️

`knowledge/protocols/ocpi/`

Skill: `ev-ocpi-roaming-expert`

- Wersje 2.1.1, 2.2, 2.2.1, 2.3.0 oraz prace nad 3.0 — różnice i ścieżki migracji
- Role (CPO, eMSP, Hub, NAP, NSP, SCSP) i moduły Credentials/Versions
- Locations, EVSE, Connector — model i aktualizacje
- Tariffs, Tokens, Sessions, CDRs, Commands, ChargingProfiles, HubClientInfo
- Push vs pull, paginacja, routing przez hub, nagłówki OCPI-to/from
- Signed data / signed meter values, korekty CDR (credit CDR)
- Rozszerzenia (np. płatności ad hoc / DirectPayment) i rekomendacje branżowe

### D01.03 OICP (Hubject) `P2` ⚠️

`knowledge/protocols/oicp/`

Skill: `ev-ocpi-roaming-expert`

- Wersje OICP, architektura CPO/EMP ↔ Hubject
- EVSE Data/Status, Authorization, Charge Detail Records, Pricing, Plug & Charge
- Różnice modelu danych OICP vs OCPI i mapowanie

### D01.04 eMIP (Gireve) `P3` ⚠️

`knowledge/protocols/emip/`

Skill: `ev-ocpi-roaming-expert`

- Architektura i obiekty eMIP, różnice względem OCPI
- Rola Gireve i współistnienie eMIP z OCPI

### D01.05 OCHP i inne protokoły roamingowe `P3` ⚠️

`knowledge/protocols/ochp/`

Skill: `ev-ocpi-roaming-expert`

- OCHP / OCHPdirect (e-clearing.net) — status i zastosowanie
- Protokoły historyczne i lokalne, migracje do OCPI

### D01.06 ISO 15118 (EV ↔ EVSE, high-level communication) `P2` ⚠️

`knowledge/protocols/iso-15118/`

Skill: `ev-iso15118-pki-expert`

- Części -1, -2, -3, -8, -10, -20 i -20 vs -2 (BPT, WPT, dynamic mode)
- Sekwencje komunikacji (SLAC, SDP, TLS, sesja V2G)
- Plug & Charge — kontrakty, certyfikaty, rola backendu i OCPP
- Integracja ISO 15118 z OCPP 2.x (certyfikaty, autoryzacja, profile ładowania)

### D01.07 DIN SPEC 70121 `P2`

`knowledge/protocols/din-70121/`

Skill: `ev-iso15118-pki-expert`

- Zakres i ograniczenia względem ISO 15118-2
- Autocharge (MAC jako identyfikator) — mechanizm, ryzyka

### D01.08 Inne systemy komunikacji EV ↔ EVSE `P3` ⚠️

`knowledge/protocols/other-ev-evse/`

Skill: brak skilla (luka w bazie)

- CHAdeMO (wersje, CAN, V2X)
- GB/T, ChaoJi
- SAE J1772, SAE J3400 (NACS) i komunikacja
- MCS — Megawatt Charging System (CharIN, SAE J3271, ISO/IEC)

### D01.09 Protokoły zarządzania energią `P2` ⚠️

`knowledge/protocols/energy-protocols/`

Skill: brak skilla (luka w bazie)

- OSCP (Open Smart Charging Protocol)
- OpenADR 2.0 / 3.0
- IEEE 2030.5
- EEBus (SHIP/SPINE) — integracja z HEMS
- IEC 61850 w kontekście stacji i magazynów

### D01.10 Komunikacja polowa i urządzeń `P2`

`knowledge/protocols/field-protocols/`

Skill: brak skilla (luka w bazie)

- Modbus RTU/TCP — liczniki, falowniki, BESS, rejestry
- SunSpec
- MQTT — architektura, QoS, bezpieczeństwo, zastosowania w EMS/IoT
- M-Bus / DLMS-COSEM w pomiarach
- CAN w urządzeniach DC

### D01.11 Standardy w przygotowaniu `P3` ⚠️

`knowledge/protocols/emerging-standards/`

Skill: brak skilla (luka w bazie)

- IEC 63110 (zarządzanie infrastrukturą ładowania)
- IEC 63119 (wymiana informacji roamingowych)
- Nowe wersje OCPP/OCPI/ISO — projekty, konsultacje, zapowiedzi

## D02 · electrical

**Normy elektrotechniczne i fizyka ładowania** — *Electrical standards & charging physics* · priorytet **P2** · katalog `knowledge/electrical/`

Warstwa fizyczna — tryby ładowania, złącza, instalacja, ochrona, jakość energii.

### D02.01 IEC 61851 — systemy ładowania przewodowego `P2` ⚠️

`knowledge/electrical/iec-61851/`

- Tryby ładowania 1–4, stany pilotowe A–F, sygnał CP i PP
- Części -1, -21-x, -23, -24, -25 — zakres
- Sygnalizacja PWM, ograniczenie prądu, wake-up

### D02.02 Złącza i gniazda (IEC 62196 i inne) `P2`

`knowledge/electrical/connectors/`

- Type 1, Type 2, CCS1, CCS2, CHAdeMO, GB/T, NACS, MCS
- Kable przytwierdzone vs gniazda, blokady, chłodzenie kabli
- Mapowanie typów złączy na wartości enum w OCPP/OCPI

### D02.03 Instalacja elektryczna i ochrona `P2` ⚠️

`knowledge/electrical/installation/`

- IEC 60364-7-722 i wymagania krajowe
- RCD typ A/B, detekcja DC 6 mA, zabezpieczenia nadprądowe, przepięciowe
- Uziemienie, PEN fault detection, układy sieci TN/TT/IT

### D02.04 Podstawy energoelektroniki i ładowania DC `P3`

`knowledge/electrical/power-electronics/`

- AC vs DC, prostowniki, moduły mocy, sprawność
- Architektury 400 V / 800 V, napięcia i prądy graniczne
- Chłodzenie, derating termiczny

### D02.05 Jakość energii i EMC `P3`

`knowledge/electrical/power-quality/`

- Współczynnik mocy, THD, harmoniczne, asymetria faz
- Wymagania EMC i stopnie ochrony IP/IK

## D03 · hardware

**Urządzenia, komponenty i producenci** — *Hardware, components & manufacturers* · priorytet **MVP** · katalog `knowledge/hardware/`

Karty techniczne urządzeń, możliwości OCPP, firmware, diagnostyka sprzętowa.

### D03.01 Kategorie urządzeń `MVP`

`knowledge/hardware/device-categories/`

Skill: `ev-evse-hardware-expert`

- AC wallbox, AC słupek, DC kompakt, DC fast, HPC
- Ładowarki modułowe, systemy satelitarne (power cabinet + dispensers)
- Ładowarki z magazynem energii, mobilne

### D03.02 Komponenty `P2`

`knowledge/hardware/components/`

Skill: `ev-evse-hardware-expert`

- Kontrolery komunikacyjne i ładowania, modemy LTE/Ethernet/Wi-Fi
- Liczniki energii (AC/DC, MID, Eichrecht), czytniki RFID, wyświetlacze
- Terminale płatnicze, moduły mocy, styczniki, chłodzenie, zabezpieczenia

### D03.03 Karty techniczne urządzeń `MVP`

`knowledge/hardware/device-cards/`

Skill: `ev-evse-hardware-expert`

- Szablon karty (identyfikacja, moc, złącza, komunikacja, OCPP, parametry, ograniczenia, diagnostyka, firmware)
- Karty rodzin urządzeń wiodących producentów
- Deklarowane vs zweryfikowane funkcje OCPP (capability matrix)

### D03.04 Producenci `P2`

`knowledge/hardware/manufacturers/`

Skill: `ev-evse-hardware-expert`

- Profile producentów, portfolio, rynki, kanały wsparcia
- Dokumentacja i portale serwisowe, polityka aktualizacji

### D03.05 Firmware i cykl życia oprogramowania urządzeń `MVP`

`knowledge/hardware/firmware/`

Skill: `ev-evse-diagnostics-expert`

- Wersjonowanie, release notes, kompatybilność z CPMS
- Procedury aktualizacji zdalnej i rollbacku
- Znane problemy wersji (link do D21)

### D03.06 Kody błędów i diagnostyka sprzętowa `MVP`

`knowledge/hardware/hardware-diagnostics/`

Skill: `ev-charging-operations-expert`

- Kody błędów OCPP (ErrorCode, vendorErrorCode) vs kody producentów
- Logi, alarmy, zdarzenia Device Model
- Mapowanie kodów na przyczyny i działania

### D03.07 Wybór, zakup i TCO urządzeń `P3`

`knowledge/hardware/procurement/`

Skill: `ev-evse-hardware-expert`

- Kryteria wyboru, wymagania przetargowe, gwarancje, SLA producenta
- TCO, koszty serwisu, dostępność części

## D04 · vehicle

**Pojazd, bateria i interakcja EV–EVSE** — *Vehicle, battery & EV–EVSE interaction* · priorytet **P2** · katalog `knowledge/vehicle/`

Perspektywa pojazdu — co wpływa na przebieg sesji i kompatybilność.

### D04.01 Bateria i BMS `P2`

`knowledge/vehicle/battery-bms/`

- Chemie ogniw, architektura pakietu, rola BMS
- SOC, SOH, limity temperaturowe, degradacja

### D04.02 Krzywe ładowania i preconditioning `P2`

`knowledge/vehicle/charging-curves/`

- Krzywe mocy według modeli, wpływ temperatury i SOC
- Preconditioning, nawigacja do ładowarki
- Interpretacja „niskiej mocy” w zgłoszeniach klientów

### D04.03 Kompatybilność pojazd–ładowarka `P2`

`knowledge/vehicle/compatibility/`

- Znane problemy kompatybilności (handshake, izolacja, timeouty)
- Testy interoperacyjności, macierze kompatybilności

### D04.04 Identyfikacja pojazdu i autoryzacja `P2`

`knowledge/vehicle/vehicle-identification/`

- Plug & Charge vs Autocharge vs RFID vs aplikacja
- Dane z pojazdu dostępne dla EVSE/CSMS (SOC, departure time, energia)

### D04.05 Telematyka i API producentów pojazdów `P3`

`knowledge/vehicle/oem-telematics/`

- API OEM (SOC, lokalizacja, harmonogramy), agregatory danych pojazdów
- Zastosowania w smart charging i flotach

## D05 · cpms

**CPMS / CSMS i systemy zarządzania** — *CPMS / CSMS & management systems* · priorytet **MVP** · katalog `knowledge/cpms/`

Funkcje, moduły i wzorce architektoniczne systemów zarządzania ładowaniem.

### D05.01 Architektura CPMS `MVP`

`knowledge/cpms/architecture/`

Skill: `ev-cpms-architect`

- Moduły referencyjne i granice odpowiedzialności
- Warstwa komunikacji OCPP (connection management, skalowanie WebSocket)
- Multi-tenancy, white-label, hierarchia organizacji

### D05.02 Zarządzanie flotą urządzeń `MVP`

`knowledge/cpms/asset-management/`

Skill: `ev-cpms-architect`

- Provisioning i onboarding ładowarek
- Zarządzanie konfiguracją i firmware w skali
- Inwentaryzacja, hierarchia lokalizacji, dane statyczne

### D05.03 Sesje, transakcje i autoryzacja `MVP`

`knowledge/cpms/session-management/`

Skill: `ev-cpms-architect`

- Maszyna stanów sesji (w tym przypadki brzegowe i odzyskiwanie)
- Remote start/stop, rezerwacje, lokalna lista autoryzacji, cache
- Obsługa transakcji offline i opóźnionych

### D05.04 Statusy i dostępność `MVP`

`knowledge/cpms/status-availability/`

Skill: `ev-cpms-architect`

- Model statusów (połączenie, EVSE, connector) i ich agregacja
- Offline vs unavailable vs faulted — reguły rozróżniania
- Wyliczanie dostępności (uptime) zgodnie z definicjami regulacyjnymi

### D05.05 Ładowarki własne vs roamingowe / zewnętrzne `MVP`

`knowledge/cpms/external-assets/`

Skill: `ev-cpms-architect`

- Zakres operacji dla urządzeń OCPP vs danych OCPI
- Synchronizacja statusów, lokalizacji, taryf, sesji; konflikty danych
- Wykrywanie braku aktualizacji danych zewnętrznych

### D05.06 Użytkownicy, role i uprawnienia `P2`

`knowledge/cpms/users-permissions/`

Skill: `ev-cpms-architect`

- RBAC/ABAC dla CPO, site hostów, serwisu, klientów flotowych
- Audyt działań operatorów

### D05.07 API i integracje CPMS `P2`

`knowledge/cpms/cpms-apis/`

Skill: `ev-integration-architect`

- API publiczne i partnerskie, webhooks, eventy
- Integracje ERP, CRM, ticketing, BI, płatności

### D05.08 Platforma eMSP `P2`

`knowledge/cpms/emsp-platform/`

Skill: `ev-product-designer`

- Zarządzanie kontraktami i tokenami, aplikacja kierowcy
- Agregacja lokalizacji, ceny dla kierowcy, rozliczenia z CPO

### D05.09 Raportowanie `P3`

`knowledge/cpms/reporting/`

Skill: `ev-cpms-architect`

- Raporty operacyjne, finansowe, regulacyjne
- Raporty dla site hostów i klientów flotowych

## D06 · roaming

**Roaming i interoperacyjność** — *Roaming & interoperability* · priorytet **MVP** · katalog `knowledge/roaming/`

Współpraca między operatorami — umowy, dane, procesy, rozliczenia.

### D06.01 Modele roamingu `MVP`

`knowledge/roaming/models/`

- Peer-to-peer vs hub, wielohubowość, routing
- Porównanie hubów (Hubject, Gireve, e-clearing.net i inne)

### D06.02 Onboarding partnerów `MVP`

`knowledge/roaming/onboarding/`

- Proces techniczny (credentials, wersje, testy) i biznesowy (umowy)
- Checklisty go-live, środowiska testowe

### D06.03 Synchronizacja danych `MVP`

`knowledge/roaming/data-sync/`

- Lokalizacje, EVSE, statusy — opóźnienia, jakość danych, deduplikacja
- Tokeny i whitelisty, autoryzacja real-time vs offline
- Taryfy w roamingu — prezentacja ceny kierowcy

### D06.04 Settlement i reconciliation `MVP`

`knowledge/roaming/settlement/`

- CDR — kompletność, walidacja, korekty, duplikaty
- Uzgadnianie sesji i CDR między stronami, spory
- Clearing i rozliczenia międzyoperatorskie

### D06.05 Umowy roamingowe `P2`

`knowledge/roaming/agreements/`

- Typowe warunki umów, modele cenowe B2B, SLA danych
- Odpowiedzialność za błędy, procedury reklamacyjne

## D07 · operations

**Operacje, utrzymanie i serwis** — *Charging operations & maintenance* · priorytet **MVP** · katalog `knowledge/operations/`

Codzienna praca operatora — monitoring, incydenty, diagnostyka, serwis, KPI.

### D07.01 Monitoring i NOC `MVP`

`knowledge/operations/monitoring/`

Skill: `ev-charging-operations-expert`

- Organizacja NOC, dyżury, poziomy wsparcia (L1/L2/L3)
- Alerty, progi, redukcja fałszywych alarmów
- Wykrywanie utraty komunikacji (Heartbeat, WebSocket, brak danych)

### D07.02 Diagnostyka zdalna `MVP`

`knowledge/operations/diagnostics/`

Skill: `ev-charging-operations-expert`

- Drzewa diagnostyczne typowych problemów
- Kolejność działań (bez odruchowego restartu), zbieranie dowodów
- {'Narzędzia': 'logi, GetDiagnostics/GetLog, triggery, konfiguracja'}

### D07.03 Zarządzanie incydentami i eskalacjami `MVP`

`knowledge/operations/incidents/`

Skill: `ev-charging-operations-expert`

- Klasyfikacja i priorytety, SLA reakcji i naprawy
- Eskalacje do producenta, serwisu, DSO, partnera roamingowego

### D07.04 Serwis terenowy i utrzymanie `P2`

`knowledge/operations/field-service/`

Skill: brak skilla (luka w bazie)

- Dyspozytornia, work orders, przeglądy okresowe
- Części zamienne, logistyka, bezpieczeństwo prac
- Przeglądy i odbiory dozorowe (np. wymagania krajowe)

### D07.05 KPI i SLA operatora `P2`

`knowledge/operations/kpi-sla/`

Skill: `ev-charging-operations-expert`

- Uptime, success rate sesji, MTTR, MTBF, utilization
- Definicje KPI zgodne z regulacjami i umowami

### D07.06 Obsługa klienta (kierowcy) `P2`

`knowledge/operations/customer-support/`

Skill: brak skilla (luka w bazie)

- Hotline 24/7, typowe zgłoszenia, skrypty
- Reklamacje, zwroty, komunikacja w trakcie awarii

## D08 · energy

**Energia, sieć i elastyczność** — *Energy, grid & flexibility* · priorytet **P2** · katalog `knowledge/energy/`

Zarządzanie mocą lokalnie i współpraca z systemem elektroenergetycznym.

### D08.01 Smart charging `P2`

`knowledge/energy/smart-charging/`

- Profile ładowania OCPP (stack levels, purposes, composite schedule)
- {'Strategie': 'równy podział, priorytety, departure time, koszt'}
- Lokalne vs centralne sterowanie, fallback przy utracie łączności

### D08.02 Load balancing i DLM `P2`

`knowledge/energy/load-management/`

- Statyczny i dynamiczny load management, pomiar na przyłączu
- Algorytmy podziału mocy dla AC i DC

### D08.03 EMS, PV, magazyny energii `P2`

`knowledge/energy/ems-der/`

- Integracja z EMS/BMS budynku, HEMS
- PV, BESS, peak shaving, autokonsumpcja

### D08.04 Przyłączenie do sieci `P2`

`knowledge/energy/grid-connection/`

- Moc przyłączeniowa, warunki przyłączenia, czas i koszty
- Ograniczenia DSO, przyłącza elastyczne (flexible connection)

### D08.05 Rynek energii i ceny `P3`

`knowledge/energy/energy-market/`

- Taryfy dystrybucyjne, opłaty mocowe, ceny dynamiczne / spot
- Sprzedaż energii na punkcie ładowania, wybór sprzedawcy

### D08.06 Elastyczność, demand response i V2G/V2X `P3`

`knowledge/energy/flexibility-dr/`

- Demand response, rynki elastyczności, usługi systemowe, agregacja
- V2G, V2H, V2B — standardy, wymagania, modele biznesowe

## D09 · billing

**Taryfy, rozliczenia i płatności** — *Tariffs, billing & payments* · priorytet **P2** · katalog `knowledge/billing/`

Od ceny przez CDR do faktury i płatności.

### D09.01 Modele taryfowe `P2`

`knowledge/billing/tariff-models/`

- kWh, czas, opłata startowa, idle/blocking fee, parking
- Taryfy złożone, ograniczenia czasowe, dynamiczne, abonamenty
- Zaokrąglenia, min/max, prezentacja ceny

### D09.02 Wycena sesji i CDR `P2`

`knowledge/billing/rating-cdr/`

- Silnik wyceny (rating), dane wejściowe, okresy taryfowe
- Generowanie CDR, walidacja, korekty

### D09.03 Płatności `P2`

`knowledge/billing/payments/`

- {'Ad hoc': 'terminale, QR/web, preautoryzacja i jej zwolnienie'}
- RFID, aplikacje, karty flotowe, płatności cykliczne
- PCI DSS, PSD2/SCA, dostawcy płatności

### D09.04 Fakturowanie i podatki `P2`

`knowledge/billing/invoicing-tax/`

- Faktury, noty, korekty, VAT w roamingu i transgranicznie
- Waluty i kursy, e-fakturowanie

### D09.05 Reklamacje i korekty `P3`

`knowledge/billing/disputes/`

- Procesy reklamacyjne, zwroty, chargebacki
- Korelacja reklamacji z danymi sesji i pomiarów

## D10 · metering

**Pomiary i metrologia prawna** — *Metering & legal metrology* · priorytet **P2** · katalog `knowledge/metering/`

Wiarygodność pomiaru energii jako podstawa rozliczeń.

### D10.01 MID i zatwierdzenia typu `P2` ⚠️

`knowledge/metering/mid/`

Skill: `ev-compliance-expert`

- Dyrektywa MID, klasy dokładności, liczniki AC
- Liczniki DC i wymagania (np. normy dla pomiaru DC)

### D10.02 Eichrecht i wymagania krajowe `P2`

`knowledge/metering/eichrecht/`

Skill: `ev-compliance-expert`

- Niemieckie prawo legalizacyjne — wymagania dla CPO i eMSP
- Odpowiedniki i wymagania w innych krajach (w tym PL)

### D10.03 Podpisane wartości pomiarowe `P2`

`knowledge/metering/signed-meter-values/`

Skill: `ev-compliance-expert`

- OCMF, formaty podpisów, transparency software
- Przenoszenie podpisanych danych przez OCPP i OCPI

### D10.04 Jakość danych pomiarowych `P3`

`knowledge/metering/meter-data-quality/`

Skill: `ev-billing-tariff-expert`

- Luki, skoki, reset liczników, rozbieżności z CDR
- Reguły walidacji MeterValues

## D11 · security

**Bezpieczeństwo i cyberbezpieczeństwo** — *Security & cybersecurity* · priorytet **P2** · katalog `knowledge/security/`

Ochrona urządzeń, komunikacji, danych i procesów.

### D11.01 Bezpieczeństwo OCPP `P2`

`knowledge/security/ocpp-security/`

- Security profiles 1–3, Basic Auth, TLS, mTLS
- Zarządzanie certyfikatami stacji, rotacja haseł
- Secure firmware update, podpisy firmware

### D11.02 PKI w ekosystemie EV `P2`

`knowledge/security/pki/`

- V2G PKI, root CA, Plug & Charge ecosystem, certificate pools
- Cykl życia certyfikatów, odwołania, OCSP

### D11.03 Bezpieczeństwo urządzeń i sieci `P3`

`knowledge/security/device-network-security/`

- Hardening, porty serwisowe, fizyczne zabezpieczenia
- Segmentacja sieci, APN prywatne, VPN

### D11.04 Bezpieczeństwo backendu i API `P3`

`knowledge/security/backend-security/`

- Uwierzytelnianie/autoryzacja API, zarządzanie sekretami
- Logowanie, audyt, wykrywanie anomalii

### D11.05 Normy i ramy bezpieczeństwa `P3` ⚠️

`knowledge/security/security-standards/`

- IEC 62443, ISO/IEC 27001
- EN 18031 (RED — wymagania cyber dla urządzeń radiowych)
- Zarządzanie podatnościami i ujawnianiem (CVD)

## D12 · regulations

**Regulacje i compliance** — *Regulations & compliance* · priorytet **P2** · katalog `knowledge/regulations/`

Wymagania prawne UE i krajowe wpływające na produkty i procesy.

### D12.01 AFIR i akty wykonawcze `P2` ⚠️

`knowledge/regulations/eu-afir/`

- Cele rozmieszczenia infrastruktury, terminy
- Płatności ad hoc, przejrzystość cen, dane statyczne i dynamiczne
- Akty delegowane/wykonawcze — standardy techniczne, komunikacja, dane (NAP)

### D12.02 Energia i budynki (UE) `P3` ⚠️

`knowledge/regulations/eu-energy-buildings/`

- EPBD — wymagania dla budynków (pre-cabling, punkty ładowania)
- RED III — elementy dot. inteligentnego ładowania i dostępu do danych baterii
- Rynek energii elektrycznej — dyrektywy i rozporządzenia

### D12.03 Cyfrowe i cyber (UE) `P3` ⚠️

`knowledge/regulations/eu-digital-cyber/`

- NIS2, Cyber Resilience Act, akt delegowany RED
- RODO w kontekście sesji i danych kierowców
- Data Act, European Accessibility Act

### D12.04 Bezpieczeństwo produktów (UE) `P3`

`knowledge/regulations/eu-product-safety/`

- LVD, EMC, RED, oznakowanie CE, deklaracje zgodności
- Rozporządzenie bateryjne (w zakresie magazynów i pojazdów)

### D12.05 Polska `P2` ⚠️

`knowledge/regulations/poland/`

- Ustawa o elektromobilności i paliwach alternatywnych — obowiązki
- Dozór techniczny stacji ładowania (UDT) — odbiory, badania okresowe
- Ewidencja infrastruktury, raportowanie, rola URE
- Przepisy dotyczące cen, informowania konsumentów, fakturowania

### D12.06 Inne kraje `P3`

`knowledge/regulations/other-countries/`

- Niemcy (Eichrecht, Ladesäulenverordnung), Holandia, Francja, Wielka Brytania (regulacje dot. publicznych punktów ładowania)
- Szablon karty kraju — wymagania, organy, dane

### D12.07 Programy wsparcia i dotacje `P3`

`knowledge/regulations/public-funding/`

- Programy UE (np. instrumenty dla infrastruktury paliw alternatywnych)
- Programy krajowe i ich wymagania techniczne/raportowe

## D13 · testing

**Testy, zgodność i certyfikacja** — *Testing, conformance & certification* · priorytet **P2** · katalog `knowledge/testing/`

Jak udowodnić, że implementacja działa i jest zgodna.

### D13.01 Zgodność protokołów `P2`

`knowledge/testing/protocol-conformance/`

Skill: `ev-evse-diagnostics-expert`

- OCTT i certyfikacja OCA, plany testów
- Testy OCPI, środowiska testowe hubów
- ISO 15118 conformance (np. testy CharIN)

### D13.02 Testy interoperacyjności `P3`

`knowledge/testing/interoperability-events/`

Skill: `ev-integration-architect`

- Plugfesty i testivale, wnioski z wydarzeń
- {'Różnica': 'conformance vs interoperability testing'}

### D13.03 Testy integracyjne CPMS–EVSE `P2`

`knowledge/testing/integration-testing/`

Skill: `ev-integration-architect`

- Symulatory ładowarek i pojazdów, narzędzia open-source
- Katalog przypadków testowych i kryteria akceptacji
- Testy regresji po zmianie firmware

### D13.04 Certyfikacja produktów `P3`

`knowledge/testing/product-certification/`

Skill: `ev-compliance-expert`

- Badania bezpieczeństwa, laboratoria, certyfikaty krajowe
- Certyfikacja pomiarów (MID/Eichrecht)

## D14 · it-architecture

**Architektura IT i integracje** — *IT architecture & integrations* · priorytet **P2** · katalog `knowledge/it-architecture/`

Wzorce techniczne dla systemów w branży EV.

### D14.01 Wzorce komunikacji `P2`

`knowledge/it-architecture/communication-patterns/`

Skill: `ev-integration-architect`

- REST, WebSocket, webhooks, gRPC
- Idempotencja, retry, back-off, korelacja żądań

### D14.02 Architektura zdarzeniowa `P2`

`knowledge/it-architecture/event-driven/`

Skill: `ev-integration-architect`

- Message brokers (Kafka, RabbitMQ, MQTT), event sourcing
- Kolejność zdarzeń, deduplikacja, outbox

### D14.03 Przechowywanie danych `P3`

`knowledge/it-architecture/data-storage/`

Skill: `ev-cpms-architect`

- Relacyjne (PostgreSQL), cache (Redis), szeregi czasowe
- Retencja danych, archiwizacja, partycjonowanie

### D14.04 Skalowalność i niezawodność `P3`

`knowledge/it-architecture/scalability-reliability/`

Skill: `ev-cpms-architect`

- Skalowanie połączeń WebSocket, sticky sessions, failover
- Multi-region, disaster recovery

### D14.05 Observability `P3`

`knowledge/it-architecture/observability/`

Skill: `ev-cpms-architect`

- Logi, metryki, tracing komunikacji OCPP/OCPI
- Monitoring syntetyczny, SLO

### D14.06 IAM i API gateway `P3`

`knowledge/it-architecture/identity-gateway/`

Skill: `ev-cpms-architect`

- IAM, SSO, multi-tenant identity
- API gateway, rate limiting, wersjonowanie API

## D15 · data-analytics

**Dane, analityka i AI** — *Data, analytics & AI* · priorytet **P3** · katalog `knowledge/data-analytics/`

Wykorzystanie danych z sieci ładowania do decyzji i automatyzacji.

### D15.01 Analityka operacyjna i biznesowa `P3`

`knowledge/data-analytics/analytics-kpi/`

- Utilization, przychód na punkt, profil sesji, zachowania kierowców
- Benchmarki rynkowe

### D15.02 Prognozowanie i optymalizacja `P3`

`knowledge/data-analytics/forecasting/`

- Prognozy popytu i obciążenia, planowanie rozbudowy
- Optymalizacja cen

### D15.03 Predykcyjne utrzymanie i wykrywanie anomalii `P3`

`knowledge/data-analytics/predictive-maintenance/`

- Sygnały wczesnego ostrzegania z danych OCPP
- Modele anomalii sesji i komunikacji

### D15.04 Dane otwarte i udostępnianie danych `P3` ⚠️

`knowledge/data-analytics/open-data/`

- NAP, DATEX II, wymogi AFIR dot. danych
- Agregatory danych (mapy, nawigacje), jakość danych publicznych

### D15.05 AI i agenci w operacjach EV `P3`

`knowledge/data-analytics/ai-agents/`

- Zastosowania agentów AI w NOC, supportcie, projektowaniu
- Ryzyka, nadzór człowieka, ocena jakości

## D16 · product-ux

**Produkt, UX i doświadczenie klienta** — *Product, UX & customer experience* · priorytet **P3** · katalog `knowledge/product-ux/`

Jak przełożyć wiedzę techniczną na dobre produkty dla różnych użytkowników.

### D16.01 Persony i customer journeys `P3`

`knowledge/product-ux/personas-journeys/`

- Kierowca, operator NOC, technik, site host, fleet manager, administrator
- {'Ścieżki': 'znalezienie, start, ładowanie, płatność, problem'}

### D16.02 UX dla operatora i administratora `P3`

`knowledge/product-ux/operator-ux/`

- Widoki NOC, diagnostyka, masowe operacje
- Wzorce UX dla statusów i alarmów

### D16.03 UX kierowcy `P3`

`knowledge/product-ux/driver-ux/`

- Aplikacje, mapy, informacja o cenie, ekrany ładowarek
- Komunikaty o błędach zrozumiałe dla kierowcy

### D16.04 Dostępność `P3`

`knowledge/product-ux/accessibility/`

- Dostępność fizyczna stanowisk (osoby z niepełnosprawnościami)
- Dostępność cyfrowa (aplikacje, terminale)

### D16.05 Benchmarki funkcjonalne `P3`

`knowledge/product-ux/feature-benchmarks/`

- Porównanie funkcji CPMS/eMSP na rynku
- Katalog funkcji referencyjnych i ich wartość

## D17 · business

**Modele biznesowe i rynek** — *Business models & market* · priorytet **P3** · katalog `knowledge/business/`

Ekonomia i struktura rynku elektromobilności.

### D17.01 Modele biznesowe `P3`

`knowledge/business/business-models/`

- CPO (własność, operacja, CPO-as-a-service), eMSP, hub
- SaaS, white-label, revenue share z site hostem

### D17.02 Ekonomika i finansowanie `P3`

`knowledge/business/unit-economics/`

- Unit economics stacji, CAPEX/OPEX, punkt rentowności
- Finansowanie, leasing, inwestorzy infrastrukturalni

### D17.03 Krajobraz rynku `P3`

`knowledge/business/market-landscape/`

- Główni gracze (CPO, eMSP, CPMS, producenci) per kraj
- Trendy, konsolidacja, dane rynkowe

### D17.04 Partnerstwa i sprzedaż B2B `P3`

`knowledge/business/partnerships/`

- Site host, retail, flota, OEM, energetyka
- Przetargi publiczne i ich wymagania

## D18 · site-deployment

**Rozwój lokalizacji i wdrażanie infrastruktury** — *Site development & deployment* · priorytet **P3** · katalog `knowledge/site-deployment/`

Od wyboru miejsca do uruchomienia stacji.

### D18.01 Wybór lokalizacji `P3`

`knowledge/site-deployment/site-selection/`

- Analiza ruchu, popytu, konkurencji, mocy dostępnej
- Umowy z właścicielami terenu

### D18.02 Pozwolenia i formalności `P3`

`knowledge/site-deployment/permitting/`

- Procedury budowlane i przyłączeniowe, zgłoszenia, dozór

### D18.03 Budowa i instalacja `P3`

`knowledge/site-deployment/construction/`

- Prace budowlane, posadowienie, okablowanie, oznakowanie, ochrona przed uszkodzeniami

### D18.04 Uruchomienie i odbiór `P3`

`knowledge/site-deployment/commissioning/`

- Checklisty uruchomienia, onboarding do CPMS, testy odbiorcze
- Przekazanie do eksploatacji i publikacja w roamingu

## D19 · segments

**Segmenty i konteksty ładowania** — *Charging segments & use contexts* · priorytet **P3** · katalog `knowledge/segments/`

Specyfika różnych zastosowań — wymagania i różnice względem ładowania publicznego.

### D19.01 Ładowanie publiczne (AC, DC, korytarze HPC) `P2`

`knowledge/segments/public/`

- Wymagania, oczekiwania kierowców, specyfika korytarzy TEN-T

### D19.02 Domowe i budynki wielorodzinne `P3`

`knowledge/segments/home-multifamily/`

- Wallboxy domowe, rozliczenia we wspólnotach, zarządzanie mocą budynku

### D19.03 Miejsce pracy i destination `P3`

`knowledge/segments/workplace-destination/`

- Rozliczanie pracowników, refundacja ładowania domowego, hotele, retail

### D19.04 Floty i zajezdnie `P2`

`knowledge/segments/fleet-depot/`

- Harmonogramy, priorytety pojazdów, integracja z systemami flotowymi
- Karty flotowe, raportowanie kosztów

### D19.05 Ciężarówki i autobusy (w tym MCS, pantografy) `P3` ⚠️

`knowledge/segments/heavy-duty-bus/`

- MCS, ładowanie pantografowe, depot vs opportunity charging

### D19.06 Pojazdy lekkie (LEV, jednoślady) `P3`

`knowledge/segments/lev/`

- Złącza i standardy LEV, wymiana baterii

### D19.07 Alternatywne metody ładowania `P3`

`knowledge/segments/alternative-charging/`

- Ładowanie bezprzewodowe (SAE J2954, ISO 15118-20 WPT)
- Battery swapping, ładowarki mobilne, ładowanie dynamiczne

## D20 · sustainability

**Zrównoważony rozwój i ESG** — *Sustainability & ESG* · priorytet **P3** · katalog `knowledge/sustainability/`

Środowiskowy wymiar ładowania — źródła energii, emisje, raportowanie.

### D20.01 Zielona energia i gwarancje pochodzenia `P3`

`knowledge/sustainability/green-energy/`

- Gwarancje pochodzenia, PPA, informowanie o źródle energii

### D20.02 Mechanizmy kredytów emisyjnych w transporcie `P3` ⚠️

`knowledge/sustainability/credits/`

- Krajowe mechanizmy (np. THG-Quote w Niemczech), mechanizmy kredytowe RED III

### D20.03 Raportowanie ESG `P3`

`knowledge/sustainability/reporting-esg/`

- CSRD/ESRS w kontekście operatorów, ślad węglowy infrastruktury

### D20.04 Cykl życia i gospodarka obiegu zamkniętego `P3`

`knowledge/sustainability/circularity/`

- Refurbishment, recykling, wymiana komponentów

## D21 · implementation-intelligence

**EV Implementation Intelligence** — *Implementation intelligence* · priorytet **MVP** · katalog `knowledge/implementation-intelligence/`

Wiedza praktyczna z wdrożeń — kluczowy wyróżnik. Zawsze z modelem, firmware i źródłem obserwacji.

### D21.01 Odstępstwa i osobliwości producentów `MVP`

`knowledge/implementation-intelligence/vendor-quirks/`

Skill: `ev-evse-diagnostics-expert`

- Różnice „standard vs implementacja” per model/firmware
- Niestandardowe DataTransfer, nietypowe sekwencje komunikatów

### D21.02 Macierz kompatybilności `P2`

`knowledge/implementation-intelligence/compatibility-matrix/`

Skill: `ev-integration-architect`

- CPMS × EVSE × firmware × funkcja — status zweryfikowany/obserwowany
- EV × EVSE — znane problemy

### D21.03 Obejścia i sprawdzone konfiguracje `MVP`

`knowledge/implementation-intelligence/workarounds-configs/`

Skill: `ev-evse-diagnostics-expert`

- Rekomendowane ustawienia konfiguracji per model
- Obejścia problemów z oceną ryzyka

### D21.04 Biblioteka przypadków produkcyjnych `P2`

`knowledge/implementation-intelligence/case-library/`

Skill: `ev-charging-operations-expert`

- Zanonimizowane incydenty — objawy, przyczyna, rozwiązanie, lekcje
- Anti-patterns projektowe i operacyjne

## D22 · use-cases

**Katalog przypadków użycia** — *Use case catalogue* · priorytet **MVP** · katalog `knowledge/use-cases/`

Scenariusze end-to-end łączące wiele domen — test wartości całej bazy.

### D22.01 Cykl życia sesji `MVP`

`knowledge/use-cases/session-lifecycle/`

- Remote start z obsługą timeoutów i przyjęcia bez startu
- Sesja offline i późne dosłanie transakcji
- Sesja roamingowa end-to-end (token → sesja → CDR → rozliczenie)

### D22.02 Łączność i dostępność `MVP`

`knowledge/use-cases/connectivity/`

- Wykrywanie utraty Heartbeat i obsługa incydentu
- Ładowarka online, ale sesja nie startuje

### D22.03 Onboarding `MVP`

`knowledge/use-cases/onboarding/`

- Onboarding nowej ładowarki do CPMS
- Onboarding partnera roamingowego

### D22.04 Scenariusze energetyczne `P2`

`knowledge/use-cases/energy-scenarios/`

- DLM na lokalizacji z ograniczonym przyłączem
- Podział mocy DC między złącza

### D22.05 Scenariusze rozliczeniowe `P2`

`knowledge/use-cases/settlement-scenarios/`

- Reconciliation sesji i CDR
- Taryfa z idle fee w roamingu
- Płatność ad hoc zgodna z AFIR

## Rejestr skilli

| Skill | Nazwa | Etap | Domeny |
|-------|-------|------|--------|
| `ev-domain-expert` | EV Domain Expert | MVP | D00, D19, D22 |
| `ev-ocpp-expert` | OCPP Expert | MVP | D01 |
| `ev-ocpi-roaming-expert` | OCPI / Roaming Expert | MVP | D01, D06 |
| `ev-cpms-architect` | CPMS Architect | MVP | D05, D14 |
| `ev-evse-hardware-expert` | EVSE Hardware Expert | MVP | D02, D03 |
| `ev-evse-diagnostics-expert` | EVSE Diagnostics Expert | MVP | D03, D04, D13, D21 |
| `ev-charging-operations-expert` | Charging Operations Expert | MVP | D03, D07, D18, D21 |
| `ev-integration-architect` | EV Integration Architect | P2 | D05, D13, D14, D21 |
| `ev-billing-tariff-expert` | EV Billing & Tariff Expert | P2 | D09, D10 |
| `ev-energy-smart-charging-expert` | Energy & Smart Charging Expert | P2 | D08 |
| `ev-iso15118-pki-expert` | ISO 15118 & PKI Expert | P2 | D01, D11 |
| `ev-compliance-expert` | Compliance Expert | P2 | D10, D12, D13, D20 |
| `ev-product-designer` | EV Product Designer | P2 | D05, D15, D16, D17 |
