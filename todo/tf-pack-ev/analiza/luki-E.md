# Luki pack-ev → ev-intelligence, grupa E

Zakres: pięć skilli pack-ev (`dom-ev-cpms-architecture`, `dom-ev-csms-migration`, `dom-ev-session-lifecycle`,
`dom-ev-asset-operations`, `dom-ev-kpi-analytics`) porównane z `ev-cpms-architect`, `ev-integration-architect`,
`ev-charging-operations-expert`. Sprawdziłem też pliki sąsiednie ev-intelligence, które pokrywają część tematów:
`ev-ocpp-expert`, `ev-ocpi-roaming-expert`, `ev-billing-tariff-expert/references/sesja-przerwana.md`,
`ev-iso15118-pki-expert`, `ev-evse-hardware-expert`.
Analiza tylko do odczytu, stan na 2026-11-15. Niczego nie edytowałem i nie pobierałem z sieci.

Ścieżki skrócone: `PE/` = `/home/user/tf/packs/pack-ev/skills/`, `EI/` = `/home/user/ev-intelligence/`.
Numery linii odnoszą się do pliku, nie do konkatenacji.

## 0. Ustalenia wstępne (ważne dla klasyfikacji)

1. **Wiedza „P” nie ma w ev-intelligence ustalonego miejsca.** `knowledge/implementation-intelligence/` zawiera tylko
   `vendor-quirks/_szablon.yaml`. To rejestr klasy D: obserwacje z wdrożeń, które mają model, firmware, dowód
   (`evidence`) i `confidence` (`EI/docs/PLAN.md:47`, `:255`). Nie ma tu miejsca na wzorce architektury ani na praktykę
   operacyjną bez dowodu.
2. **„Wniosek” jest dozwolony tylko jako wyprowadzenie z cytowanych faktów:**
   - `EI/skills/ev-cpms-architect/SKILL.md:15-18`: „Architektury CPMS nie opisuje żadna norma… Nie dodajesz «dobrych
     praktyk branżowych» bez źródła”;
   - `EI/skills/ev-integration-architect/SKILL.md:17-19`: ogólne wzorce IT (brokery, bazy, API gateway) „nie są
     opracowane”, więc skill nie odpowiada z pamięci;
   - `EI/skills/ev-charging-operations-expert/SKILL.md:15-17`: kolejność kroków to Wnioski z faktów.

   Wynika z tego, że treść P przenosisz tylko wtedy, gdy da się ją przepisać jako **Wniosek** oparty na znaczniku
   `[dok §]`. Czysty wzorzec systemów rozproszonych (outbox, rejestr połączeń z TTL, sticky session) nie ma takiej
   podstawy.
3. **Wiele luk ma wspólny problem: brak źródła w rejestrze.** Nie ma go ani w `sources/*.yaml`, ani w
   `sources/niedostepne.yaml`, dla:
   - 23 CFR 680 (NEVI);
   - Data Act (rozporządzenie (UE) 2023/2854);
   - RODO/GDPR;
   - dyrektywy 2000/84/WE (czas letni);
   - WEEE.

   NIS2, CRA i RODO są wymienione w `EI/docs/DO-ZROBIENIA.md:20-22` jako tematy bez źródeł. Poddomena D07.04 (serwis
   terenowy) ma `skills: []` (`EI/taxonomy/taxonomy.yaml:609-617`), a D12.06 (USA) jest nieopracowana
   (`alarmy.md:63`).
4. **Kopie tekstów lokalnie nie istnieją** (`.cache/ev-kb` brak, `EV_KB_DOCS` pusty). Numerów sekcji w kolumnie
   „źródło” nie dało się sprawdzić w tekście. To wskazanie, gdzie szukać, a nie cytat (CLAUDE.md: numer sekcji
   sprawdzasz w dokumencie).
5. Pack-ev jako źródeł używa bazy fabryki: kopii `mobilityhouse/ocpp`, `.claude/skills/dom-ev-charging/references/*.md`
   (import 2024–2025) i „wiedzy ogólnej autora”. Według CLAUDE.md to źródła wtórne, więc nic z pack-ev nie jest dowodem.
   Każdy fakt F trzeba ponownie zweryfikować w dokumencie OCA, EVRF albo UE.

Legenda klas:
- **F**: fakt sprawdzalny w specyfikacji lub akcie;
- **P**: praktyka lub architektura bez źródła oficjalnego;
- **R**: procedura lub heurystyka, która nie niesie faktów.

---

## 1. dom-ev-cpms-architecture → ev-cpms-architect

Pliki: `PE/dom-ev-cpms-architecture/SKILL.md` (141 l.), `references/brama-i-routing.md` (57),
`references/konteksty-i-tenancy.md` (50). Pack-ev sam przyznaje (`SKILL.md:135-138`, `brama-i-routing.md:3-4`), że
źródło domenowe „nie opisuje wzorców” i że są to „wiedza ogólna inżynierii systemów rozproszonych”. Prawie cała treść
to P.

| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Mapa komponentów: brama OCPP, adapter wersji (ACL), szyna, konteksty domeny, magazyn stanu stacji, OCPI jako osobny kontekst | SKILL.md:19-27 | ev-cpms-architect SKILL.md (Procedura) albo nowy `references/moduly.md`; taksonomia D05.01 „Moduły referencyjne” ma na to miejsce | P | Brak normy. Podstawa dla Wniosku: 201-P1 rozdz. 8 (topologie), 201-P0 rozdz. 2 (niezgodność 1.6/2.x), OCPI230 §8.1.2. Id: `201-P1`, `201-P0`, `OCPI230` |
| Rejestr połączeń `stationId → węzeł` z TTL; nowe połączenie wypiera stare; usuwanie wpisu tylko przy zgodnym `connectionId` | SKILL.md:37-45; brama-i-routing.md:6-16 | ev-cpms-architect ograniczenia.md §1 (jako Wniosek) | P | Wzorzec bez źródła. Do sprawdzenia w 201-P4 (§3–§5), czy OCPP-J mówi coś o drugim połączeniu z tą samą tożsamością. Nie przyjmować z pamięci. Id `201-P4` |
| Routing komend CSMS→stacja przez szynę z kluczem `stationId`; kontrakt komendy (`commandId`, `expiresAt`, wyniki `offline`/`expired`/`timeout`); odrzucona opcja sticky session | SKILL.md:39-42, 96-102; brama-i-routing.md:18-28 | ev-cpms-architect ograniczenia.md §1 | P | Podstawa Wniosku już cytowana w EI: jedno CALL naraz `[201-P4 §4.1.1]` (ograniczenia.md:22); Accepted ≠ transakcja (ev-ocpp-expert wzorce.md). Kontrakt komendy jest bez źródła |
| Warstwowa obrona przed reconnect storm: drenaż przy wdrożeniu, limit handshake/TLS, 503, `Pending` z `interval` jako dławik, test „wszyscy wracają” | SKILL.md:72-80; brama-i-routing.md:37-48 | ev-cpms-architect ograniczenia.md §1–2 (przykład w SKILL.md:53-74 już częściowo to robi) | P | Fakty bazowe już są: backoff `[201-P4 §5.4]`, `Pending`/`interval` `[201-P2 B02.FR.01-07]`. Drenaż i limity TLS to P |
| Tolerancyjny czytelnik dla znanych odchyleń producenta w adapterze, z jawną listą wyjątków | brama-i-routing.md:50-54 | ev-cpms-architect albo ev-evse-diagnostics-expert (rejestr odchyleń) | P | Lista wyjątków pasuje do `knowledge/implementation-intelligence/vendor-quirks/` (klasa D z dowodem). Sam wzorzec P |
| Zdarzenia domenowe: outbox/inbox, `eventId`, czas stacji vs czas odbioru, kolejność per `stationId`, wersjonowanie zdarzeń | SKILL.md:52-55; konteksty-i-tenancy.md:19-23 | ev-cpms-architect ograniczenia.md §4 | P | Fakty częściowo: komunikaty historyczne `[16 §3.7]`, `offline` i `seqNo` `[201-P2 E §1.3.2]`. Outbox i inbox to P (integration-architect SKILL.md:17-19 wprost wyklucza wzorce IT) |
| Mapa kontekstów domeny z własnością danych i zdarzeniami (Asset, Session, Authorization, Pricing, Billing/CDR, Roaming, Energy, NOC) | konteksty-i-tenancy.md:3-17 | ev-cpms-architect (D05.01) | P | Brak normy |
| Multi-tenancy: poziomy izolacji, najemca rozpoznawany z uwierzytelnionego połączenia (URL, certyfikat profilu 3), limity per najemca („hałaśliwy sąsiad”), testy izolacji | SKILL.md:63-67; konteksty-i-tenancy.md:25-36 | ev-cpms-architect ograniczenia.md §7 (dziś jest tylko Wniosek „obiekt ma tenanta”, :124-126) | P | Podstawa: tożsamość z credentials `[201-P4 §3.1.1]`, CredentialsRoles `[OCPI230 §4.1.5]` (już w EI). Wiele ról lub party w jednym credentials: OCPI230 moduł Credentials (§7?) do sprawdzenia. Id `OCPI230` |
| Obserwowalność: minimalny zestaw metryk (połączenia, tempo handshake, percentyle CALL, CALLERROR po producencie, sesje-duchy, opóźnienie komenda→wynik, głębokość kolejki) | SKILL.md:82-93 | ev-cpms-architect albo ev-charging-operations-expert alarmy.md | P | Brak normy. Wzmianka o RODO bez źródła w rejestrze |
| Stan stacji w jednym miejscu; Device Model 2.x i płaska konfiguracja 1.6 za wspólnym interfejsem; stan nadpisywany tylko nowszym znacznikiem | SKILL.md:56-58 | ev-cpms-architect (D05.02 „Zarządzanie konfiguracją”) | P | Fakty o DM są w ev-ocpp-expert (komunikaty-201.md §4, `201-CSV`). Wzorzec P |
| Szablon ADR i lista typowych ADR | konteksty-i-tenancy.md:38-47; SKILL.md:30 | ev-cpms-architect Procedura krok 5 (już ma „Decyzje jako Wniosek”) | R | — |
| Checklista oceny istniejącego CSMS i zasada „lukę opisz scenariuszem awarii” | SKILL.md:69-70, 114-126 | ev-cpms-architect (Kryteria akceptacji, SKILL.md:50-51) | R | — |

**Nakładki** (pokryte w EI, nie przenosić):
- stacja inicjuje WebSocket: `EI/…/ev-cpms-architect/references/ograniczenia.md:16`, `[201-P4 §3.1]`;
- backoff z jitterem: ograniczenia.md:23-25, `[201-P4 §5.4]`;
- `Pending`/`Rejected` i interval: ograniczenia.md:37-54;
- Heartbeat i ping: ograniczenia.md:27-28, ev-ocpp-expert wzorce.md §3;
- idempotencja po `messageId`: ev-integration-architect ocpp-ocpi-polaczenie.md:45-46;
- `seqNo` i luki: ograniczenia.md:77-82;
- OCPI jako osobny model: ograniczenia.md:84-93;
- CALLERROR tylko przy błędzie formatu: ev-ocpp-expert wzorce.md (Wniosek §4);
- „Rejected dla ochłonięcia” = błąd: `[201-P2 B03]` w ograniczenia.md:46-50.

---

## 2. dom-ev-csms-migration → ev-integration-architect (`references/migracja-i-rozszerzenia.md`)

Pliki: `PE/dom-ev-csms-migration/SKILL.md` (131), `references/ciaglosc-i-plan.md` (103), `inwentarz-i-wlasnosc.md` (62),
`przelaczenie-stacji.md` (83). EI ma tu mocną bazę z białej księgi OCA (`OCA-WP-MIG`) i z B09/B10. Pack-ev wnosi
głównie ciągłość biznesową i pola schematów.

| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Pola `NetworkConnectionProfileType`: `ocppVersion` (enum OCPP12/15/16/20), `ocppTransport`, `ocppCsmsUrl` ≤512, `messageTimeout`, `securityProfile`, `ocppInterface` (Wired0…Wireless3), opcjonalne `apn`, `vpn`; `OCPP20` dla 2.0.x | przelaczenie-stacji.md:23-28; SKILL.md:56 | migracja-i-rozszerzenia.md §4 pkt 2 (dziś tylko `ocppCsmsUrl`, `securityProfile`: :53-56) | F | Schemat SetNetworkProfileRequest `[201-P3]` i typy danych 201-P2 (rozdz. 2 Datatypes, do sprawdzenia). Id `201-P3`, `201-P2` |
| Statusy odpowiedzi `SetNetworkProfile` (Accepted/Rejected/Failed); `attributeStatus` w SetVariables | przelaczenie-stacji.md:32 | migracja-i-rozszerzenia.md §4 | F | `[201-P3]`. SetVariables już jest w ev-ocpp-expert komunikaty-201.md:76 (nakładka), luka dotyczy tylko SetNetworkProfile. Id `201-P3` |
| Nie nadpisuj aktywnego slotu, przed zmianą odczytaj stan (`GetBaseReport`/`GetVariables`), po zmianie sprawdź Boot, Heartbeat i StatusNotification wszystkich EVSE | przelaczenie-stacji.md:19-36 | migracja-i-rozszerzenia.md §4 | F | Do sprawdzenia w 201-P2 B09 (wymagania o zmianie slotu aktywnego). Kroki weryfikacji wynikają z `[201-P2 B10.FR.10]`, `[201-P2 B01.FR.05]`. Id `201-P2` |
| Co nie przenosi się samo: profile ładowania ustawione przez stary CSMS (odczyt `GetCompositeSchedule`, ustawienie od nowa), lokalna lista i jej wersja (`SendLocalList` albo czyszczenie), rezerwacje i zdalne starty do zakończenia przed falą | SKILL.md:62-71; ciaglosc-i-plan.md:45-49 | migracja-i-rozszerzenia.md §1 (lista „co trzeba przenieść” :21-27 nie ma profili ani listy lokalnej) | F | Trwałość profili po restarcie: 16 (Smart Charging §3.13) i 201-P2 blok K; wersja listy lokalnej: 16 §5.15/§9.4 i 201-P2 blok D (sekcje do sprawdzenia). „Stary CSMS ustawiał” to Wniosek. Id `16`, `201-P2`, `S16`, `201-P3` |
| OCPI przy zmianie platformy: ponowna wymiana credentials pod nowym adresem `versions`, pełny zestaw Tokens od eMSP, zmiana endpointów Commands, stałe `uid`; tylko jedna platforma publikuje naraz, a stara nie wysyła `REMOVED` | ciaglosc-i-plan.md:22-36 | migracja-i-rozszerzenia.md nowa sekcja „Roaming przy migracji” (dziś tylko EVSEID :26 i umowy) | F | Credentials (rejestracja, aktualizacja przez PUT): OCPI230 rozdz. Credentials; Tokens pull: OCPI230 §12; `uid`: OCPI230 §8.3.2. „Jedna platforma publikuje” to Wniosek. Id `OCPI230` |
| Migracja 1.6 → 2.0.1: koegzystencja po podprotokole, mapowanie Start/Stop → TransactionEvent, kto nadaje `transactionId`, 9 → 5 statusów złącza; wersję zmienia firmware i `ocppVersion` w profilu, nie OCPP; rollback wersji wymaga slotu 1.6 | SKILL.md:73-84 | migracja-i-rozszerzenia.md nowa sekcja (EI nie ma osobnego rozdziału o zmianie wersji) | F | `[201-P0 rozdz. 2]`, `[J16 §3.2]`/`[201-P4]` podprotokół, `[201-P1 §7.3]`, statusy `[16 §7.7]`/`[201-P2 §3.23]`, odpowiedniki konfiguracji w ev-ocpp-expert wzorce.md §5. „Dwa projekty osobno” to P. Id `201-P0`, `201-P1`, `201-P2`, `16`, `J16` |
| Data Act art. 23–31 (zmiana dostawcy usług przetwarzania danych, eksport, zniesienie opłat od 12.01.2027) i art. 3–5 (dostęp do danych z produktu); żądanie próbki eksportu | inwentarz-i-wlasnosc.md:39-49; SKILL.md:90-91 | migracja-i-rozszerzenia.md §1 i ev-compliance-expert | F | Rozporządzenie (UE) 2023/2854: **brak w rejestrze i w `niedostepne.yaml`**. Trzeba je zarejestrować w `sources/eu-inne.yaml` (EUR-Lex działa). Kwalifikacja SaaS-owego CSMS to interpretacja prawna, więc dostaje oznaczenie Wniosek albo „poza zakresem” |
| Własność danych: CPO jako administrator a SaaS jako procesor, właściciel tokenów, rejestracja `party_id` poza dostawcą CSMS, PKI dostawcy | inwentarz-i-wlasnosc.md:24-37 | migracja-i-rozszerzenia.md §1 | P | RODO bez źródła w rejestrze. Przydział `party_id` jest do sprawdzenia w OCPI230 (definicja party_id i rejestr) |
| Zależności od dostawcy: wyszukanie `DataTransfer`/`vendorId` w logach, niestandardowe klucze i zmienne, firmware zarządzany, funkcje poza OCPP, terminale, SIM | inwentarz-i-wlasnosc.md:51-61 | migracja-i-rozszerzenia.md §6–7 | P | Podstawa jest już w EI: `[OCA-WP-CUST §1.2.3]`, `[OCA-WP-MIG §6]` (ESCROW). Sama metoda P |
| Transakcje offline na granicy systemów: import zaległych z flagą „sprzed migracji”, granica CDR wyznaczona przez `Ended`, ciągłość identyfikatorów CDR, brak podwójnego CDR | ciaglosc-i-plan.md:7-20 | migracja-i-rozszerzenia.md §4 pkt 4 | P | Fakt bazowy (B10.FR.05) już jest w :59-61. Reszta to Wniosek, oparty na niezmienności CDR `[OCPI230 §10.1.1]` |
| Hub (OICP): konto i `OperatorID` zostają przy operatorze, zmienia się punkt podłączenia | ciaglosc-i-plan.md:36 | migracja-i-rozszerzenia.md | P | Do sprawdzenia w `OICP23-CPO-INTRO`/`OICP23-CPO-SVC`. Dziś „[do uzgodnienia]” |
| Taryfy porównane kalkulatorem przed i po; cena przed sesją bez zmian; terminale ad hoc (parowanie, płatność testowa) | ciaglosc-i-plan.md:38-44 | migracja-i-rozszerzenia.md | P | Podstawa: `[AFIR art. 5 ust. 4-5]` (ev-cpms-architect ograniczenia.md:99-101) |
| Raport uptime za okres migracji (luka = „nieznany”), podwójny monitoring, oznaczenie zmian statusu z przełączenia, publikacja do NAP bez przerwy | ciaglosc-i-plan.md:51-60 | migracja-i-rozszerzenia.md + ev-charging-operations-expert alarmy.md §5 | P | Podstawa: `[AFIR-655 art. 2]` (1 minuta), `[OCPI230 §8.4.26]` UNKNOWN |
| Fale: lab → pilot 1–3 stacje → ~5% → kolejne; kryteria przejścia zapisane przed falą; próg zatrzymania | przelaczenie-stacji.md:52-67; SKILL.md:31-34 | migracja-i-rozszerzenia.md §2 pkt 5 | P | `[OCA-WP-MIG §3.3]` (partie) już jest. Liczby i progi to P |
| Rollback: wyzwalacze, w 1.6 zachowaj stare wartości `GetConfiguration`, sesji nie dzielisz między systemy, tymczasowy most proxy OCPP dla ogona | przelaczenie-stacji.md:69-83 | migracja-i-rozszerzenia.md §3–4 | P | Podstawa: `[201-P2 B10.FR.07-09]`, `[OCA-WP-MIG §4]` |
| Kryteria wyłączenia starego systemu: zero stacji, CDR uzgodnione, eksport, unieważnione poświadczenia, DNS, usunięcie danych | ciaglosc-i-plan.md:86-93 | migracja-i-rozszerzenia.md | P | Brak normy. RODO poza rejestrem |
| Inwentarz floty (kolumny, porównanie z rejestrem aktywów) | inwentarz-i-wlasnosc.md:5-22 | migracja-i-rozszerzenia.md §2 | R | — |
| Rejestr ryzyk (tabela) | ciaglosc-i-plan.md:62-75 | migracja-i-rozszerzenia.md | R | — |
| Komunikacja z partnerami OCPI i hubem | ciaglosc-i-plan.md:77-84 | migracja-i-rozszerzenia.md | R | — |

**Nakładki:**
- kolejność migracji, SIM/APN, QR i partie: migracja-i-rozszerzenia.md:21-38, `[OCA-WP-MIG §2-3]`;
- klucze 1.6 nieustandaryzowane: :40-45;
- B09/B10 (sloty, `NetworkConfigurationPriority`, `Inoperative` przed resetem, stranded asset): :48-70;
- profil 3: :72-78;
- brak współpracy starego CSO: :80-92;
- `ChangeConfiguration` key ≤50/value ≤500 i statusy: ev-ocpp-expert komunikaty-16.md:61;
- profil bezpieczeństwa i InstallCertificate: ev-iso15118-pki-expert.

---

## 3. dom-ev-session-lifecycle → ev-integration-architect / ev-cpms-architect (D05.03) / ev-charging-operations-expert

Pliki: `PE/dom-ev-session-lifecycle/SKILL.md` (160), `references/free-vend-i-stop-failed.md` (106),
`projekt-obslugi-sesji.md` (83), `sekwencje.md` (73). Pack-ev oznacza wiele pozycji „[do weryfikacji]” lub
„[założenie]”. W EI są one już częściowo potwierdzone (patrz Konflikty).

| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Trzy obiekty (transakcja OCPP, Session OCPI, CDR): kto tworzy, właściciel, klucz; Session tylko przy roamingu; nie używać `transactionId` jako `session id` | SKILL.md:24-36 | ev-integration-architect ocpp-ocpi-polaczenie.md nowa sekcja „Sesja end-to-end” (albo ev-cpms-architect ograniczenia.md §4) | F | `[201-P1 §7.3]` (kto nadaje `transactionId`), OCPI230 §9 (Session, id), §10 (CDR). Osobny identyfikator to Wniosek. Id `201-P1`, `OCPI230` |
| Pełna sekwencja end-to-end: START_SESSION → odpowiedź synchroniczna → Remote/RequestStart → wynik na `response_url` → Start → PUT Session → PATCH → Stop → COMPLETED → POST CDR (1.6 i 2.0.1) | sekwencje.md:6-46; SKILL.md:60-63 | ev-integration-architect ocpp-ocpi-polaczenie.md §6/§8 | F | Części są rozproszone w EI: `[OCPI230 §13.1]`, `[OCPI230 §9.1.1]`, `[16 §5.11]`, `[201-P2 F01]`. Brakuje sklejonego diagramu. Id `OCPI230`, `16`, `201-P2` |
| Energia z licznika: `meterStart`/`meterStop` w Wh (1.6), odczyty w zdarzeniach (2.0.1), zapis surowych odczytów z jednostką, MeterValues w trakcie jako podgląd, szacunek oznaczony | SKILL.md:75-81 | ev-cpms-architect ograniczenia.md §4 | F | Jednostka Wh w StartTransaction/StopTransaction: 16 rozdz. 6 (do sprawdzenia) i `[S16]`; `Transaction.End` `[201-P2 §3.66]` (już w billing). MID: id `MID` (eu-inne.yaml). Flaga szacunku to Wniosek |
| Późna transakcja po offline: czas zdarzenia obok czasu odbioru, do CDR idzie czas zdarzenia, Session wysłana od razu jako zakończona (bez ACTIVE) | SKILL.md:106-109; projekt-obslugi-sesji.md:54-57 | ev-integration-architect ocpp-ocpi-polaczenie.md §1/§8 | F | `[16 §3.7]` (historyczne „as any other”). Czy Session wolno utworzyć od razu w `COMPLETED`, trzeba sprawdzić w OCPI230 §9 (statusy, PUT). Id `OCPI230`, `16` |
| Komenda bez odpowiedzi stacji w czasie → wynik `TIMEOUT`/`FAILED` na `response_url`; późniejszy start to zwykła sesja, którą można powiązać po `authorization_reference` | SKILL.md:54-58; projekt-obslugi-sesji.md:58-60 | ev-integration-architect ocpp-ocpi-polaczenie.md §6 | F | `[OCPI230 §13.4.2]` CommandResult (jest w ops diagnostyka.md), `[OCPI230 §13.3.5]` (jest w integracji §6, :85). Luka jest cienka: dopisać regułę |
| Free vend: transakcja z tokenem technicznym; w 1.6 `idTag` wymagany w StartTransaction, w 2.0.1 `idToken` opcjonalny w TransactionEvent; `NoAuthorization`; brak Session i CDR do eMSP; konfiguracja przez klucze autoryzacji i `AuthCtrlr`/`TxCtrlr`; ryzyko wobec ad hoc w AFIR | free-vend-i-stop-failed.md:9-35; SKILL.md:65-69 | ev-cpms-architect ograniczenia.md §4 (z odesłaniem do ev-ocpp-expert) | F | `[S16]` StartTransaction, `[201-P3]` TransactionEvent i IdTokenEnumType (`NoAuthorization` już w ev-ocpp-expert komunikaty-201.md:69, wzorce.md:48); klucze `[16 §9.1]`; zmienne `[201-CSV]` AuthCtrlr; `[AFIR art. 5 ust. 1]`. Czy spec opisuje free vend wprost: do sprawdzenia w 201-P2 blok C |
| Terminal płatniczy (ad hoc) jako ścieżka bez eMSP i OCPI | SKILL.md:51; sekwencje.md:59-62 | ev-billing-tariff-expert (platnosc-ad-hoc.md już jest) | P | Dla 2.1 F jest w EI (`21-P2` C20–C22). Dla 1.6/2.0.1 „[założenie]” |
| Klucze idempotencji per poziom: ramka; transakcja 1.6 z kluczem zapasowym (`connectorId`, `idTag`, `timestamp`, `meterStart`); 2.0.1 (`transactionId`, `seqNo`); Session id; CDR id | SKILL.md:90-99 | ev-integration-architect ocpp-ocpi-polaczenie.md §2/§8 | P | `messageId` `[201-P4 §4.1.4]` już jest. Klucz zapasowy 1.6 bez źródła. `-1` `[16E §3.18]` podważa założenie pack-ev |
| Sesje osierocone: sygnały zamknięcia (nowy Boot, `Available` na złączu, limit bez MeterValues), szacunek, „nie zamykaj przed limitem” | SKILL.md:101-105 | ev-cpms-architect ograniczenia.md §4 (taksonomia D05.03 „przypadki brzegowe i odzyskiwanie”) | P | Fakty graniczne są w billing sesja-przerwana.md:16-25 (`PowerLoss`/`Reboot`, 2.1 E17; 1.6 i 2.0.1 nie opisują wznowienia). Reguły zamknięcia to Wniosek |
| Późny Stop po zamknięciu szacunkiem: zastąp szacunek, jeśli CDR niewysłany, inaczej ścieżka korekty | SKILL.md:110-111 | ev-cpms-architect §4 | P | Korekta przez Credit CDR `[OCPI230 §10.1.1]` jest w EI |
| Maszyna stanów sesji domenowej (`oczekuje_na_start`, `aktywna`, `osierocona`, `zakonczona`, `cdr_wyslany`) i model danych sesji | projekt-obslugi-sesji.md:6-30 | ev-cpms-architect (D05.03 „Maszyna stanów sesji”) | P | Statusy OCPI Session `[OCPI230 §9.4.3]` jako punkt oparcia |
| Tabela decyzji dla nietypowych ramek (duplikat, Stop bez Start → kwarantanna, Update po Ended, nowy Start przy aktywnej, Ended z luką `seqNo`) | projekt-obslugi-sesji.md:32-42 | ev-cpms-architect §4 / ev-ocpp-expert wzorce.md §4 | P | Wniosek „kwarantanna, nie CALLERROR” już jest w ev-ocpp-expert wzorce.md (Wniosek §4). Pozostałe wiersze to P |
| Błędny zegar stacji (np. 1970): korekta z `currentTime` w Heartbeat/Boot, zapis obu czasów | projekt-obslugi-sesji.md:50-52 | ev-cpms-architect §4 | P | Synchronizacja zegara przez Heartbeat `[201-P4 §5.3]` (ograniczenia.md:27-28). Pole `currentTime` do sprawdzenia w `[S16]`/`[201-P3]` |
| Kiosk (terminal lub ekran jako punkt startu), zatrzymanie z kiosku = `Local` | free-vend-i-stop-failed.md:37-47 | ev-billing-tariff-expert | P | Powód `Local` w `[16 §7.36]`/`[201-P3]` |
| `STOP_FAILED` jako stan operatorski: tabela przyczyn, obsługa (TriggerMessage, ponowienie z limitem, profil 0 W, reset po zapisaniu odczytu, zamknięcie administracyjne z wpisem), wpływ na CDR i KPI | free-vend-i-stop-failed.md:49-90; SKILL.md:70-73 | ev-charging-operations-expert diagnostyka.md (nowa gałąź „sesji nie da się zakończyć”) | P | Fakty graniczne są w EI: statusy RemoteStop `[S16]`/`[201-P3]`; TriggerMessage 1.6 bez Start/Stop (dzialania-zdalne.md:39-41); TxStopPoint (ev-ocpp-expert). Sam stan i procedura to P, ale dają się zapisać jako Wniosek |

**Nakładki:**
- `remoteStartId` i korelacja: ev-ocpp-expert wzorce.md §2;
- `ConnectionTimeOut` i `Preparing`: diagnostyka.md:21, `[16 §9.1.6]`;
- CDR niezmienny i Credit CDR: billing sesja-przerwana.md:42-51;
- Session PUT/PATCH/COMPLETED: ev-ocpi-roaming-expert moduly.md:58-63;
- real-time authorization tylko RFID >15 min: ocpp-ocpi-polaczenie.md:80-84, `[OCPI230 §13.1]`;
- `TxStopPoint`: ev-ocpp-expert komunikaty-201.md §5;
- kolejka offline: ev-ocpp-expert wzorce.md §4;
- Plug & Charge: ev-iso15118-pki-expert.

---

## 4. dom-ev-asset-operations → ev-cpms-architect (D05.02, D05.04) / ev-charging-operations-expert (D07)

Pliki: `PE/dom-ev-asset-operations/SKILL.md` (153), `references/cykl-zycia-i-publikacja.md` (84),
`om-i-degradacja.md` (83), `operacje-i-komendy.md` (86), `rejestr-assetow.md` (59). Pack-ev sam zaznacza (SKILL.md:153),
że „stany cyklu życia i praktyki O&M to wiedza branżowa [założenie]”.

| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Status stacji NEVI: `operational`, `under construction`, `planned`, `decommissioned` (680.116(c)(6)); status portu w terminach OCPI 2.2.1 (680.116(c)(8)(vii)) | cykl-zycia-i-publikacja.md:32-36 | ev-cpms-architect model-statusow.md (nowa kolumna) / ev-compliance-expert | F | 23 CFR 680: **brak w rejestrze i w `niedostepne.yaml`**. Wymaga nowego `sources/us-*.yaml` (eCFR; dostępność hosta niesprawdzona) |
| PAUSED a uptime: NEVI wyłącza tylko wymienione przyczyny (680.116(b)) | SKILL.md:102-106; operacje-i-komendy.md:81-86 | ev-charging-operations-expert alarmy.md §5 | F | 23 CFR 680.116(b), jak wyżej (niezarejestrowane) |
| EIPA: numer przed rozpoczęciem działalności, zgłaszanie zmian i wycofania | cykl-zycia-i-publikacja.md:37-38; SKILL.md:58 | ev-cpms-architect ograniczenia.md §6 (dziś tylko AFIR/NAP) | F | `PL-EMOB` art. 42, `EIPA-OPIS`, `EIPA-API` (pl-prawo.yaml, pl-dane.yaml). Id istnieją. Pack-ev nie podaje treści, tylko odsyła |
| Reguły EVSE ID w cyklu życia: zostaje przy wymianie 1:1, firmware, module, kablu, liczniku; zmiana lokalizacji lub operatora = nowe ID; wygaszone nigdy ponownie; rezerwacja na etapie PLANNED; `uid` niezależny od numeru sprzętu; `evse_id` osobno od `uid` | SKILL.md:65-75; cykl-zycia-i-publikacja.md:40-52 | ev-cpms-architect ograniczenia.md §5 albo model-statusow.md | F | `uid` (unikalność w platformie CPO) i `evse_id`: OCPI230 §8.3.2. Zmiana CSO zmienia EVSEID `[OCA-WP-MIG §3.2]` (już w EI). Format EVSE ID odwołuje się do ISO 15118 / eMI3: ISO 15118 jest w `niedostepne.yaml` (płatna). Zakaz ponownego użycia do sprawdzenia w OCPI230; jeśli spec milczy, to P/Wniosek |
| Pola komend serwisowych: `GetDiagnostics`/`GetLog` (`location`, `startTime`, `stopTime`, `retries`, `retryInterval`, `remoteLocation`), `UpdateFirmware` (`retrieveDate`, `installDateTime`, `signature`, `signingCertificate`); statusy UpdateFirmware 2.0.1 (`AcceptedCanceled`, `InvalidCertificate`, `RevokedCertificate`) | operacje-i-komendy.md:31-51 | ev-charging-operations-expert dzialania-zdalne.md (sekcja „TriggerMessage i logi”) | F | `[S16]`, `[201-P3]`, `[SWP4]`. Częściowo w ev-ocpp-expert komunikaty-16/201 i ev-iso15118-pki-expert bezpieczenstwo-ocpp.md:102-107 |
| Legalizacja licznika jako zdarzenie z terminem; okres legalizacji w PL | rejestr-assetow.md:55-59 | — | F | **NIEDOSTEPNE**: „Ustawa Prawo o miarach (PL)…” jest w `sources/niedostepne.yaml` (sekcja dokumenty). Odpowiedź musi to mówić w pierwszym zdaniu. Sam wzorzec „zdarzenie z terminem” to P |
| Rejestr aktywów: typy (moduł mocy, kabel DC, licznik, SIM, terminal, BESS/PV, budowlane), model asset/pozycja/zdarzenie z okresem ważności, atrybuty | SKILL.md:28-38; rejestr-assetow.md:5-24 | ev-cpms-architect (D05.02 „Inwentaryzacja”) | P | Pola Boot jako źródło tożsamości: ev-evse-hardware-expert karta-urzadzenia.md:11-15 (`[S16]`, `[201-P3]`) |
| Maszyna stanów cyklu życia (PLANNED … DECOMMISSIONED) i skutki w CSMS (Boot `Rejected`/`Pending`/`Accepted` per stan, wyciszanie alarmów, „offline w IN_STOCK to nie incydent”) | SKILL.md:40-63; cykl-zycia-i-publikacja.md:6-16; operacje-i-komendy.md:16 | ev-cpms-architect model-statusow.md §3 (dziś planned/removed tylko jako wartości, :38) | P | Podstawa Wniosku: `[201-P2 B02]`/`[B03]`, `[OCPI230 §8.4.26]` |
| Mapowanie stanów cyklu życia na OCPI (COMMISSIONING → INOPERATIVE/PLANNED, MAINTENANCE → INOPERATIVE/OUTOFORDER, PAUSED → INOPERATIVE, DECOMMISSIONED → REMOVED, UNDER_CONSTRUCTION → PLANNED); `StatusSchedule` informacyjny | SKILL.md:41-51; cykl-zycia-i-publikacja.md:18-30 | ev-cpms-architect model-statusow.md §3 | P | Definicje są w EI: `[OCPI230 §8.4.26]`, `[OCPI230 §8.4.24]` (moduly.md:41), REMOVED (moduly.md:30). Mapowanie to Wniosek |
| Uzgadnianie rejestru z BootNotification (inny numer seryjny lub model → alarm i `Pending`; stacja nieznana → `Rejected`; firmware spoza katalogu → `Pending`); rejestr nie nadpisywany automatycznie | rejestr-assetow.md:42-53; SKILL.md:77-83 | ev-cpms-architect ograniczenia.md §2 (onboarding) | P | Podstawa: `[201-P2 B02.FR.01]` (w Pending CSMS pobiera dane), pola Boot (hardware karta) |
| Wymiana sprzętu pod tym samym EVSE (7 kroków; nowy licznik zaczyna od innej wartości) | cykl-zycia-i-publikacja.md:54-61 | ev-cpms-architect | P | — |
| RMA (`IN_REPAIR`), sprzęt z demontażu (reset fabryczny, usunięcie certyfikatów) | cykl-zycia-i-publikacja.md:63-68 | ev-cpms-architect | P | — |
| Repowering | cykl-zycia-i-publikacja.md:70-74 | ev-cpms-architect | P | — |
| Decommissioning w 10 krokach (REMOVED, unieważnienie poświadczeń, reset, SIM, utylizacja, EVSE ID na listę wygaszonych, retencja) | cykl-zycia-i-publikacja.md:76-84 | ev-cpms-architect | P | Częściowo F: REMOVED (EI), unieważnienie certyfikatu (ev-iso15118-pki-expert). WEEE i retencja RODO poza rejestrem |
| Bezpieczeństwo URL w GetLog/UpdateFirmware (krótki czas życia, bez haseł w ścieżce) | operacje-i-komendy.md:58 | ev-charging-operations-expert dzialania-zdalne.md | P | — |
| Uprawnienia do komend (Reset i UpdateFirmware tylko dla roli z uprawnieniem; blokada dla IN_STOCK/DECOMMISSIONED) | operacje-i-komendy.md:52-57 | ev-cpms-architect ograniczenia.md §7 | P | Podstawa: `[201-P2 A §1.2]` (kontrola dostępu w CSMS) już w EI |
| Szablony konfiguracji per (vendor, model, firmware, wersja OCPP) i wykrywanie dryfu (`GetConfiguration`/`GetVariables` po zastosowaniu) | operacje-i-komendy.md:60-66 | ev-cpms-architect (D05.02 „Zarządzanie konfiguracją i firmware w skali”) | P | — |
| Katalog `vendorErrorCode` (vendor, model, firmware → znaczenie, runbook, część); kod nieznany idzie do kolejki | operacje-i-komendy.md:23-25 | **`knowledge/implementation-intelligence/vendor-quirks/`** (jedyne ustalone miejsce na wiedzę D) + ev-charging-operations-expert alarmy.md §4 | P | Znaczenie kodu pochodzi z dokumentacji producenta (klasa B, brak w rejestrze). Wpis wymaga dowodu i `confidence` |
| Priorytet = wpływ × zasięg, grupowanie alarmów po lokalizacji i (model, firmware), deduplikacja, wyciszenie na czas MAINTENANCE | operacje-i-komendy.md:26-29 | ev-charging-operations-expert alarmy.md §1 (dziś priorytety tylko z severity, :20-21) | P | — |
| O&M: przeglądy prewencyjne, korekcyjne i wymuszone, pola zgłoszenia serwisowego, części zamienne | om-i-degradacja.md:6-28 | **brak celu**: D07.04 ma `skills: []`, a `DO-ZROBIENIA.md:20-22` wymaga najpierw źródeł | P | Brak źródeł oficjalnych |
| Analiza degradacji z telemetrii (kohorta model × firmware, sygnały, normalizacja ograniczeń DLM i profili, wykrycie odchylenia, rozstrzygnięcie przyczyny) | om-i-degradacja.md:30-53 | ev-charging-operations-expert (nowy plik references) | P | Kody błędów `[16 §7.6]` są w alarmy.md §4. Measurand temperatury: do sprawdzenia w `[16 §7.31]`/`[201-P2]` |
| Firmware w cyklu życia: katalog dopuszczonych wersji, wdrażanie etapami, porównanie `firmwareVersion` po aktualizacji | om-i-degradacja.md:64-71 | ev-cpms-architect (D05.02) | P | Podstawa: Boot `reason = FirmwareUpdate` (ev-ocpp-expert komunikaty-201.md:66), L01 (ev-iso15118) |
| Runbook: szkielet | operacje-i-komendy.md:68-73 | ev-charging-operations-expert | R | — |
| Eskalacja i SLA: znaczniki czasu do MTTR | operacje-i-komendy.md:75-79 | ev-charging-operations-expert (D07.03) | R | — |
| Predictive maintenance: etapy | om-i-degradacja.md:55-62 | — | R | — |

**Nakładki:**
- statusy OCPI i nieusuwanie EVSE: ev-ocpi-roaming-expert moduly.md:30-53;
- pola BootNotification: ev-evse-hardware-expert karta-urzadzenia.md;
- Reset, ChangeAvailability i UnlockConnector (pola i statusy): dzialania-zdalne.md, ev-ocpp-expert komunikaty-16.md:61-69 i komunikaty-201.md:73-76;
- errorCode 1.6: alarmy.md §4;
- podpisany firmware 1.6/2.0.1 (pack-ev ma „[do weryfikacji]”): EI ma `[SWP4]` SignedUpdateFirmware (komunikaty-16.md:27) i L01;
- NIS2/CRA to tylko odesłanie w pack-ev.

---

## 5. dom-ev-kpi-analytics → ev-charging-operations-expert (D07.05, `references/alarmy.md` §5)

Pliki: `PE/dom-ev-kpi-analytics/SKILL.md` (158), `references/kpi-sesji-i-finanse.md` (69),
`model-danych-i-pulapki.md` (78), `uptime-i-regulacje.md` (70), `scripts/uptime_kpi.py` (220). EI ma dziś tylko
`alarmy.md:56-63`:
- AFIR i 2025/655 nie mają wymogu uptime;
- Wniosek: KPI definiujesz w SLA i liczysz z tych samych zdarzeń co dane do NAP;
- wymogi USA (D12.06) nieopracowane.

| luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|
| Wzór NEVI `µ = ((525 600 − (T_outage − T_excluded)) / 525 600) × 100`, wynik **powyżej** 97 % dla każdego portu osobno, liczony co miesiąc za poprzednie 12; lista wyłączeń (utility, vehicle, planowana konserwacja, wandalizm, klęski, godziny poza pracą) z obowiązkiem wykazania | SKILL.md:34-41; uptime-i-regulacje.md:6-16 | ev-charging-operations-expert alarmy.md §5 / ev-compliance-expert (D12.06) | F | 23 CFR 680.116(b): **brak w rejestrze i w `niedostepne.yaml`**; trzeba zarejestrować |
| „Port up” wymaga faktycznej dostawy energii z mocą minimalną (680.106(d)); `Available` nie wystarcza | SKILL.md:43-48; uptime-i-regulacje.md:8-9 | jw. | F | 23 CFR 680.106(d), 680.116(b), niezarejestrowane |
| Raportowanie NEVI: kwartalnie (680.112(a): uptime, `T_outage`, `T_excluded` za 3 miesiące, czas każdej awarii, kody błędów sesji, kWh, moc szczytowa, metoda płatności), rocznie koszty, 680.114(a)(4) historyczny uptime | SKILL.md:56-58; uptime-i-regulacje.md:18-27 | jw. | F | 23 CFR 680.112, 680.114, niezarejestrowane |
| Polska: dostępność punktu przekazywana do EIPA natychmiast po zmianie stanu, ceny w ciągu godziny; brak progu uptime | SKILL.md:61-62; uptime-i-regulacje.md:67-68 | alarmy.md §5 (dziś tylko AFIR) | F | `PL-EMOB` art. 42 (id istnieje; ustępu nie sprawdziłem w tekście). Także `EIPA-API` |
| Definicja AFIR „availability of data” (art. 2) dotyczy istnienia danych, nie dostępności ładowarki | uptime-i-regulacje.md:65-66 | alarmy.md §5 | F | `[AFIR art. 2]` (id `AFIR`). Numer punktu (9) do sprawdzenia w wersji skonsolidowanej |
| DST w raportach: doby 23 i 25 h (PL 2026-03-29 i 2026-10-25); strefa IANA, nie stałe przesunięcie | model-danych-i-pulapki.md:33-41; SKILL.md:122-123 | alarmy.md §5 | F | Daty zmiany czasu: dyrektywa 2000/84/WE, **brak w rejestrze**. Reszta to P |
| Trzy definicje uptime obok siebie: surowa, NEVI, SLA z wyłączeniami także w mianowniku | SKILL.md:27-35 | alarmy.md §5 | P | Surowa i SLA to definicje umowne. NEVI jak wyżej |
| Decyzje definicji: offline = przestój, czas nieznany na początku okna, `PAUSED`, `Unavailable` operatora, `Available` z kolejnymi nieudanymi startami, `BLOCKED` | SKILL.md:49-55; uptime-i-regulacje.md:40-52 | alarmy.md §5 | P | Wniosek z `[AFIR-655 Annex, tabela F]` (non-operational) i model-statusow.md §3 (offline → non-operational) |
| Raport per jednostka, kraj i model: wymiar z historią ważności, ważenie minutami, liczba portów poniżej progu | uptime-i-regulacje.md:54-60 | alarmy.md §5 | P | — |
| Lejek sesji i session success rate: autoryzacja osobno, sesje bez energii z przyczyną, `STOP_FAILED` osobno | kpi-sesji-i-finanse.md:5-20 | alarmy.md §5 (taksonomia D07.05 wymienia „success rate sesji”) | P | Statusy autoryzacji są w EI (`[16 §7.2]`, `[201-P3]`) |
| Utilization w trzech wersjach (zajętość, ładowanie, energetyczna), mianownik z godzin pracy, jednostka EVSE, cięcie sesji na granicy okresu | kpi-sesji-i-finanse.md:22-33 | alarmy.md §5 | P | EVSE = jeden pojazd naraz `[201-P1 §1.2.1]` `[OCPI230 §2.6]` (już w ev-cpms-architect SKILL.md:41-42) |
| kWh (źródło ustalone raz), sesje na EVSE i dzień (dni eksploatacji), długość sesji z medianą | kpi-sesji-i-finanse.md:35-42 | alarmy.md §5 | P | — |
| Przychód na EVSE i marża na kWh (netto, korekty CDR, bez CAPEX) | kpi-sesji-i-finanse.md:44-52 | ev-billing-tariff-expert albo pominąć | P | Ekonomika stacji jest w `niedostepne.yaml` („Dane rynkowe i ekonomika stacji”, D15.02/D17) |
| MTTR i MTBF: epizod przestoju, cenzurowanie okna, mediana | kpi-sesji-i-finanse.md:54-60 | alarmy.md §5 (D07.05 wymienia MTTR i MTBF) | P | — |
| NPS | kpi-sesji-i-finanse.md:62-65 | — (poza domeną EV; nie przenosić) | P | — |
| Model danych KPI: `status_event` tylko do dopisywania, klucz naturalny i `ON CONFLICT`, `outage_exclusion` z dowodem, `kpi_snapshot`, `status_interval` jako widok | model-danych-i-pulapki.md:6-31 | ev-cpms-architect (D05.09 Raportowanie) | P | Wzorzec IT, który ev-integration-architect SKILL.md:17-19 wyklucza |
| Zdarzenia z opóźnieniem: przeliczanie wsteczne, `data_cutoff_ts`, zamrożone raporty | model-danych-i-pulapki.md:43-48; SKILL.md:124-125 | alarmy.md §5 | P | Fakt bazowy `[16 §3.7]` (historyczne) |
| Tożsamość portu: stały `port_id` z aliasami `evse_id`; agregacja złączy do portu | model-danych-i-pulapki.md:50-57 | alarmy.md §5 | P | — |
| Porty nowe (krócej niż rok) a stała 525 600 | model-danych-i-pulapki.md:59-66 | alarmy.md §5 | P | NEVI, jak wyżej |
| Progi z przeglądów branżowych („15–20 % utilization”) nie są celem | kpi-sesji-i-finanse.md:67-69; SKILL.md:98-99 | alarmy.md §5 (jedno zdanie) | R | Zgodne z `niedostepne.yaml` „Dane rynkowe” |
| Agregacja przez sumy liczników i mianowników, nigdy średnia procentów; przykład liczbowy | model-danych-i-pulapki.md:68-78; SKILL.md:131-132 | alarmy.md §5 | R | — |
| Procedura: nazwij odbiorcę liczby, zapisz i wersjonuj definicję, licz z danych raportu regulacyjnego | SKILL.md:17-25 | alarmy.md §5 (Wniosek :61-63 jest zbieżny) | R | — |

**Nakładki:**
- brak progu uptime w AFIR: alarmy.md:57-59 i SKILL.md:76-78;
- dane dynamiczne AFIR i 1 minuta: `[AFIR-655 art. 2]`;
- statusy OCPP i OCPI (tabela źródeł, uptime-i-regulacje.md:29-38): ev-cpms-architect model-statusow.md §1;
- `UNKNOWN` także offline: `[OCPI230 §8.4.26]`.

---

## 6. Skrypty

W grupie tylko jeden pack-ev skill ma katalog `scripts/`:
- `dom-ev-cpms-architecture`, `dom-ev-csms-migration`, `dom-ev-session-lifecycle` i `dom-ev-asset-operations` mają
  tylko `SKILL.md` i `references/`;
- skrypty, do których odsyłają (`ocpi_tariff_calc.py`, `composite_schedule.py`, `ocpp_log_analyze.py`,
  `ev_id_check.py`), należą do innych skilli pack-ev, poza tą grupą.

### `PE/dom-ev-kpi-analytics/scripts/uptime_kpi.py` (220 linii)

**Co robi.** Na wejściu bierze JSON: `window`, `events [{ts, port, status, reason?}]`, `exclusions`, `sessions`. Dla
każdego portu wylicza przedziały statusów i z nich:
- uptime surowy, NEVI i SLA;
- przestoje, wyłączenia, MTTR i MTBF;
- skuteczność sesji (z `ok`/`failed` podanych na wejściu).

Szczegóły działania:
- `--unknown outage|exclude` rozstrzyga stan na początku okna;
- `--up-status`/`--down-status` mapują statusy spoza listy (np. `PAUSED`);
- zwraca ostrzeżenia, m.in. `unknown-start` i `nevi-window`;
- kody wyjścia: 0 (wszystkie porty ≥ próg), 1 (co najmniej jeden poniżej), 2 (błąd wejścia);
- `--json` daje wynik maszynowy.

**Zależności.** Tylko biblioteka standardowa (`argparse`, `datetime`, `json`, `sys`, `pathlib`), bez sieci. To zgodne
z regułą EI „bez zależności”.

**Testy.** `PE/../tests/test_uptime_kpi.py` (199 linii, 34 asercje `check(...)`). To skrypt z `main()`, a nie
`unittest`. `ROOT` szuka katalogu `.claude/hooks`, `SCRIPT` wskazuje `.claude/skills/dom-ev-kpi-analytics/...`.
Bramka EI uruchamia `python3 -m unittest discover tests`, więc test trzeba przepisać na `unittest.TestCase`, tak jak
`EI/tests/test_ocpp_frame_check.py` (`ROOT = Path(__file__).resolve().parent.parent`).

Inne testy pack-ev dla tej grupy:
- scenariusze `tests/skill_evals/dom-ev-{cpms-architecture,csms-migration,session-lifecycle,asset-operations,kpi-analytics}.json`
  (odpowiednio 3, 3, 4, 3 i 4 scenariusze);
- wpisy w `tests/skill_gate/pack-ev.json`;
- pytania w `tests/ev_exam/operacje.json` (pole `zrodlo` wskazuje te skille).

**Odpowiednik w EI.** Brak. `EI/tools/` ma tylko narzędzia bazy (`ev_kb*.py`, `skill_check.py`, `skill_eval.py` i
podobne). Jedyny skrypt skilla to `skills/ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py`, a on robi coś
innego.

**Docelowy skill.** `ev-charging-operations-expert/scripts/uptime_kpi.py`. To D07.05 (KPI i SLA), a SKILL.md tego
skilla już obejmuje „raport uptime”.

**Blokery przeniesienia:**
1. Stałe i reguły NEVI w kodzie i docstringu (525 600 min, próg 97 %, lista wyłączeń `utility`, `vehicle`,
   `maintenance`, `vandalism`, `disaster`, `outside_hours`) to fakty z 23 CFR 680.116(b). Tego źródła nie ma w
   rejestrze. Są dwie drogi:
   - (a) najpierw zarejestrować 23 CFR 680 (eCFR) z SHA-256 i licencją;
   - (b) przenieść wersję bez trybu NEVI: tylko surowy i SLA, z listą przyczyn wyłączeń podawaną przez użytkownika.
2. Zbiory statusów `UP` i `DOWN` mieszają 1.6 i 2.0.1. To fakty sprawdzalne (`[16 §7.7]`, `[201-P2 §3.23]`). Ich
   przypisanie do up/down to Wniosek zgodny z model-statusow.md §3 i powinien to mówić w docstringu.
3. Ścieżki `.claude/skills/...` w docstringu i odwołania do `dom-ev-*` trzeba zmienić.
4. `SKILL.md` celu musi dostać sekcję o skrypcie (jak ev-evse-diagnostics-expert SKILL.md:40, :79), a `references/`
   musi zgadzać się z plikami.

**Werdykt.** Warto przenieść: nie ma odpowiednika, kod jest stdlib, test istnieje. Warunek: konwersja testu na
`unittest` i decyzja o trybie NEVI (najpierw rejestracja źródła).

Scenariusze warte przeniesienia do `evals/skill_evals/` (po przepisaniu na format EI z `checks.all` i sąsiadem `ev-*`):
- `komenda-do-innej-instancji` i `reconnect-storm` → ev-cpms-architect, tylko jeśli treść przejdzie jako Wniosek;
- `przelaczenie-stacji-2x` i `ciaglosc-roamingu` → ev-integration-architect;
- `offline-po-powrocie-stare-transakcje`, `free-vend-i-stop-failed` i `brak-odpowiedzi-na-remotestart` →
  ev-integration-architect albo ev-cpms-architect;
- `wygaszenie-i-ponowne-uzycie-evse-id` → ev-cpms-architect;
- `session-success-nieudane-autoryzacje` i `utilization-srednia-srednich` → ev-charging-operations-expert;
- `uptime-raport-vs-regulator` → ev-charging-operations-expert, dopiero po rejestracji NEVI. Nie koliduje z EI
  `raport-uptime-dla-inwestora`, bo tamten dotyczy UE i AFIR.

---

## 7. Konflikty (różne twierdzenia o tym samym)

| # | pack-ev | ev-intelligence | Rozstrzygnięcie |
|---|---|---|---|
| 1 | Nazwa zmiennej priorytetu profili „[do weryfikacji]… schematy JSON jej nie zawierają; sprawdź w Device Model producenta” — `PE/dom-ev-csms-migration/SKILL.md:59-60`, `przelaczenie-stacji.md:30-31` | `OCPPCommCtrlr.NetworkConfigurationPriority`, próby `NetworkProfileConnectionAttempts` `[201-P2 B10.FR.03]` — `EI/skills/ev-integration-architect/references/migracja-i-rozszerzenia.md:57-58` | Racja po stronie EI: zmienna standardowa (201-P2 B10, `201-APP`/`201-CSV`). Pack-ev jest tu przestarzały |
| 2 | Stacja „gdy się nie połączy — wraca na stary” profil; stary profil to ścieżka powrotu — `przelaczenie-stacji.md:38-39`, `SKILL.md:42-43` | Powrót to tylko SHOULD (B10.FR.07), alternatywa B10.FR.08; biała księga OCA mówi „requirement” — `migracja-i-rozszerzenia.md:65-67`, `:142`; `SKILL.md:76-77` | Racja po stronie EI (spec: zalecenie). Pack-ev łagodzi to „przetestuj w pilocie”, ale formułuje jako zachowanie stacji |
| 3 | Przełączenie floty przez `Reset OnIdle` „nie przerywa ładowania” jako bezpieczna metoda — `przelaczenie-stacji.md:33-34` | Przed resetem `Inoperative` i opróżnienie kolejki transakcyjnej, inaczej nowy CSMS dostanie zakończenia nieznanych transakcji (B10.FR.05) — `migracja-i-rozszerzenia.md:59-61`, `SKILL.md:74-75` | Nie jest to sprzeczność wprost, ale pack-ev pomija wymóg kolejki. Przy przenoszeniu obowiązuje wersja EI |
| 4 | „Profil nie może się obniżyć w trakcie migracji (z 2 do 1 — nie)” jako reguła — `przelaczenie-stacji.md:42`; checklista `SKILL.md:117` | 2.0.1 dopuszcza obniżenie 3 → 2 przy `AllowSecurityProfileDowngrade` `[201-P2 A00.FR.005]` — `EI/skills/ev-iso15118-pki-expert/SKILL.md:39-40`. OCA opisuje dostęp serwisowy producenta „z profilem 1 bez TLS”, gdy stary CSO nie współpracuje `[OCA-WP-MIG §6]` — `migracja-i-rozszerzenia.md:86-87` | Jako polityka operatora reguła pack-ev jest dopuszczalna (Wniosek). Jako fakt o protokole jest nieprawdziwa |
| 5 | „Tożsamość publiczna się nie zmienia: EVSE ID, `party_id`, Location ID, `evse.uid` te same przed i po” — `PE/dom-ev-csms-migration/SKILL.md:47-48`, `ciaglosc-i-plan.md:22` | „Dla roamingu zmienia się zewnętrzny identyfikator EVSE (EVSEID) przy nowym CSO” `[OCA-WP-MIG §3.2]` — `migracja-i-rozszerzenia.md:25-26`, `SKILL.md:78` | Różny zakres. Pack-ev zakłada ten sam CPO i nowy CSMS, OCA mówi o zmianie CSO. Pack-ev asset-operations sam to przyznaje (`dom-ev-asset-operations/SKILL.md:72`: zmiana operatora = nowe ID). Przy scalaniu trzeba wprost rozdzielić oba przypadki |
| 6 | W 1.6 transakcja offline nie ma `transactionId`; „sposób tymczasowej identyfikacji zależy od producenta [do weryfikacji]”, dopasowanie po (`connectorId`, `idTag`, `timestamp`, `meterStart`) — `PE/dom-ev-session-lifecycle/references/projekt-obslugi-sesji.md:47-49`, `SKILL.md:94` | Stacja wysyła `transactionId = -1`, a CSMS SHALL przyjąć `[16E §3.18]` — `EI/skills/ev-cpms-architect/references/ograniczenia.md:76-77`, `:81-82`; ev-ocpp-expert wzorce.md §4 | Racja po stronie EI (errata OCA). Klucz zapasowy pack-ev może zostać co najwyżej jako Wniosek do dopasowania po `-1` |
| 7 | Dane dynamiczne AFIR wg art. 20 ust. 2 „do 2025-04-14”, źródło: tekst pierwotny `eli/reg/2023/1804/oj` — `PE/dom-ev-kpi-analytics/references/uptime-i-regulacje.md:63`, `SKILL.md:153-154` | Cytowana wersja skonsolidowana 2026-01-08, w której art. 20 ust. 2 zastąpiono aktem M2 (2025/671) — `EI/sources/eu-afir.yaml:2, 17-20`; `ograniczenia.md:105-106` | Rozbieżność wersji. Obowiązuje wersja skonsolidowana z EI. Daty i listę danych z pack-ev trzeba sprawdzić ponownie w AFIR (M2) |
| 8 | `UpdateFirmware` 1.6 bez pól podpisu, a podpisany wariant „w rozszerzeniu bezpieczeństwa [do weryfikacji, poza bazą]” — `PE/dom-ev-asset-operations/references/om-i-degradacja.md:75-77` | `SignedUpdateFirmware` w dodatku bezpieczeństwa `[SWP4]` — `EI/skills/ev-ocpp-expert/references/komunikaty-16.md:27` | Nie ma sprzeczności co do faktu. EI ma źródło, więc „[do weryfikacji]” z pack-ev jest zbędne |
| 9 | Wersja OCPI: pack-ev opiera się na OCPI 2.2.1-d2 („nazwy CommandResult [do weryfikacji] w OCPI 2.2.1”) — `PE/dom-ev-session-lifecycle/SKILL.md:58`; `dom-ev-asset-operations/SKILL.md:149-150` | EI cytuje OCPI 2.3.0 (`OCPI230`). `CommandResult` jest sprawdzony `[OCPI230 §13.4.2]` — `EI/skills/ev-charging-operations-expert/references/diagnostyka.md:58` | Przy przenoszeniu cytujesz `OCPI230`. 2.2.1 tylko wtedy, gdy tekst dotyczy różnic (`OCPI221`, `OCPI221-CH`) |

Drobna rozbieżność bez skutków: pack-ev `uptime-i-regulacje.md:65-66` podaje „AFIR art. 2 pkt 9”. EI cytuje art. 2
bez punktu, a `eu-afir.yaml:20` mówi, że w art. 2 tekstów różni się tylko numeracja przypisów. Punkt trzeba sprawdzić
w tekście.

---

## 8. Podsumowanie liczbowe

| skill pack-ev | F | P | R | razem |
|---|---|---|---|---|
| dom-ev-cpms-architecture | 0 | 10 | 2 | 12 |
| dom-ev-csms-migration | 7 | 9 | 3 | 19 |
| dom-ev-session-lifecycle | 6 | 9 | 0 | 15 |
| dom-ev-asset-operations | 6 | 16 | 3 | 25 |
| dom-ev-kpi-analytics | 6 | 13 | 3 | 22 |
| **razem** | **25** | **57** | **11** | **93** |

Status źródeł dla 25 luk F:
- **Id jest w rejestrze (17):**
  - 6 w migracji (`201-P2`, `201-P3`, `16`, `OCPI230`, `201-P0`, `J16`);
  - 6 w sesji;
  - 3 w aktywach (EIPA, EVSE ID, pola komend);
  - 2 w KPI (AFIR art. 2 i PL-EMOB art. 42).
- **Źródła nie ma w rejestrze ani w `niedostepne.yaml` (7):**
  - 23 CFR 680 (2 w aktywach, 3 w KPI);
  - Data Act 2023/2854;
  - dyrektywa 2000/84/WE.
- **NIEDOSTEPNE (1):** Prawo o miarach (legalizacja licznika).

Zgodnie z regułami EI pozycje P można przenieść tylko jako **Wniosek** oparty na przytoczonych faktach. Dla
D07.04 (O&M, części) celu brak, dopóki nie będzie źródeł (DO-ZROBIENIA.md:20-22).
