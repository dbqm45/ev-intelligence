# Analiza luk — grupa A (OCPP, symulacja, certyfikacja, diagnostyka, onboarding)

Stan: 2026-11-15. Analiza tylko do odczytu, bez sieci. Ścieżki pack-ev względem `/home/user/tf/packs/pack-ev/skills/`,
ścieżki ev-intelligence względem `/home/user/ev-intelligence/`. Numery linii z plików źródłowych (nie z wydruków
złączonych).

**Legenda klas.**
- **F**: fakt, który da się sprawdzić w specyfikacji lub normie. Podaję prawdopodobne źródło i `id` z `sources/*.yaml`
  albo informację, że go nie ma (lub że jest w `sources/niedostepne.yaml`).
- **P**: wiedza praktyczna albo zachowanie producentów bez źródła oficjalnego. Według `CLAUDE.md` nie da się tego
  przenieść, chyba że istnieje miejsce na wiedzę klasy D (`knowledge/implementation-intelligence/vendor-quirks/`).
  Szablon `_szablon.yaml` wymaga jednak producenta, modelu, firmware i dowodu, a bez nich wpis ma `confidence: hypothesis`.
- **R**: procedura lub heurystyka („jak pracować”) bez faktów. Można ją przenieść jako **Wniosek** albo procedurę, ale
  każde zdanie z faktem trzeba podeprzeć cytatem.

**Uwaga ogólna o źródłach.** Wszystkie 6 skilli pack-ev opiera się na `dom-ev-charging/references/ocpp.md` (import
2024–2025) i na „wiedzy ogólnej autora”. Zostały oznaczone `[do weryfikacji]`/`[założenie]` i nie mają cytatów z
dokumentów OCA. Z pack-ev **nie da się więc niczego skopiować dosłownie**. Każdą lukę klasy F trzeba opracować od nowa
z dokumentu OCA, a z pack-ev wziąć tylko temat. Lokalnych kopii dokumentów (`.cache/ev-kb/`) w tej sesji nie ma.
Numery sekcji podane niżej jako „prawdopodobne” trzeba więc sprawdzić w tekście (`ev_kb cite`) przed użyciem.

---

## 1. dom-ev-ocpp-16 → cel: `skills/ev-ocpp-expert`

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| O16-1 | **Pełna tabela przejść statusów złącza 1.6** (z → do, wyzwalacz; w specyfikacji kody przejść). ev-intel ma tylko przejście B6 (`[16E §3.20]`) i statusy z enum | `dom-ev-ocpp-16/references/status-i-transakcje.md:19-31` | `ev-ocpp-expert/references/komunikaty-16.md` §2 | F | OCPP 1.6 ed. 2, opis StatusNotification z tabelą przejść (prawdopodobnie §4.9, sprawdzić) + errata `[16E §3.19–3.21]`; id `16`, `16E` (`sources/oca-ocpp.yaml:17-18`). Tabela pack ma oznaczenie [do weryfikacji] i nie ma kodów: trzeba ją zbudować od nowa z tabeli OCA |
| O16-2 | **Typowa kolejność ramek sesji** (RFID: StatusNotification Preparing → Authorize → StartTransaction → Charging → MeterValues → StopTransaction → Finishing → Available; sesja z aplikacji) | `status-i-transakcje.md:35-44` | `ev-ocpp-expert/references/wzorce.md` (nowa sekcja „Przebieg sesji 1.6”) | F (+P) | diagramy sekwencji i opisy w `[16]` rozdz. 3–5 (sekcje ustalić); id `16`. Zdanie „kolejność kroków różni się między producentami” (`:39`) to P |
| O16-3 | **Boot `Pending` / `Rejected` w 1.6**: co wolno stacji i Central System. ev-intel ma tylko „SHOULD NOT be closed” (`komunikaty-16.md:79-80`); odpowiednik 2.0.1 jest w `ev-cpms-architect/references/ograniczenia.md:40-50` | `dom-ev-ocpp-16/SKILL.md:42-46` | `komunikaty-16.md` §3 | F | `[16 §4.2]` BootNotification; id `16` |
| O16-4 | Ponowne łączenie z backoffem po zerwaniu w 1.6 | `SKILL.md:48` | `wzorce.md` §3 | F (do ustalenia) | Nie ustalono, czy 1.6 / OCPP-J 1.6 / SWP4 to określa. 2.0.1: `RetryBackOff*` `[201-P4 §5.4]` (już w ev-cpms-architect i ev-integration-architect). Jeśli 1.6 milczy, trzeba to napisać wprost |
| O16-5 | **Pola `StopTransaction` i energia sesji**: `transactionId`, `meterStop` (Wh), `timestamp`, `reason`, `transactionData`; `idTagInfo` opcjonalne w odpowiedzi (przykład pack `[3,"a7",{}]`); energia = `meterStop − meterStart` (Wniosek) | `SKILL.md:69-70`, `:109-110` | `komunikaty-16.md` §3–4 | F | `[S16]` StopTransaction.json / StopTransactionResponse.json, `[16 §6.x StopTransaction.req/conf]`; id `S16`, `16` |
| O16-6 | 1.6 istnieje w wariancie SOAP/XML i JSON; „1.6J” to JSON/WebSocket | `SKILL.md:12-13` | `wersje-i-status.md` | F | `[16]` wstęp / `[J16]` (sekcje ustalić); id `16`, `J16`. Drobne |
| O16-7 | Idempotencja CSMS po (`chargePointId`, `messageId`) dla 1.6; zapasowy klucz StartTransaction (`connectorId`, `idTag`, `timestamp`, `meterStart`) | `SKILL.md:97-99`; `references/odchylenia-i-offline.md:12` | `wzorce.md` §4 (krótko + odesłanie do ev-integration-architect) | R | Deduplikacja dla 2.0.1 jest w `ev-integration-architect/references/ocpp-ocpi-polaczenie.md:35-45` `[201-P4 §4.1.4]`. Dla 1.6 trzeba sprawdzić, co `[J16 §4.1.3]` mówi o unikalności id. Zapasowy klucz pack sam oznacza jako [założenie] (P), więc się go nie przenosi |
| O16-8 | Szybka odpowiedź, ciężka praca po odpowiedzi, skutki przez outbox | `SKILL.md:100-102` | ev-cpms-architect (poza grupą) | R | Kotwica: jedno CALL naraz `[J16 §4.1.1]` (już w `ramki-i-bledy.md:23-31`) |
| O16-9 | Test na nagranej ramce (odtworzenie, także dwukrotne, jako regresja) | `SKILL.md:103-104` | `ev-evse-diagnostics-expert/references/metoda.md` §5 | R | — |
| O16-10 | Kolejka offline po stronie CSMS: nie wyciągać stanu „teraz” z ostatniej ramki, zapisywać czas odbioru obok czasu z ramki, korygować zegar | `odchylenia-i-offline.md:7-13`; `SKILL.md:120` | `wzorce.md` §4 | R | Kotwica: dostarczanie chronologiczne `[16 §3.7]` (już w `wzorce.md:82-84`) |
| O16-11 | **Katalog „typowych odchyleń” 1.6**: brak Stop po zaniku zasilania, zegar 1970 bez RTC, `connectorId 0` w złym miejscu, dodatkowe pola, nietypowe `status`/`measurand`, ignorowany `interval`, wielokrotny Boot | `odchylenia-i-offline.md:15-26` | `knowledge/implementation-intelligence/vendor-quirks/` | **P** | Brak źródła oficjalnego, brak producenta, modelu, firmware i dowodu. Nie da się z tego zrobić wpisów (`_szablon.yaml:9-15, 29-33`). Najwyżej lista „hipotez do sprawdzenia” w `metoda.md` (R), bez twierdzenia, że to występuje. **Nie przenosić** |
| O16-12 | Zamykanie wiszącej sesji heurystyką (nowy Boot + `Available`), energia oznaczona jako szacowana | `SKILL.md:122-123`; `odchylenia-i-offline.md:16-17` | `wzorce.md` §4 lub ev-charging-operations-expert | R (+F-kotwice) | `[16 §5.14]` (Reset → StopTransaction, w `dzialania-zdalne.md`), `StopTransaction.reason` `PowerLoss`/`Reboot` `[S16]` (`komunikaty-16.md:70`), `[16 §3.7]`. Heurystyka to R |
| O16-13 | Tryb tolerancyjny walidacji (dodatkowe pola) z alertem per model | `odchylenia-i-offline.md:22-23` | ev-integration-architect (ma „odrzucanie i tolerowanie nieznanych pól”) | R | Kotwica: `additionalProperties` w `[S16]` (sprawdzić w schemacie) |
| O16-14 | `MeterValues` to telemetria, a do rozliczenia służy licznik z wymogami prawnymi | `status-i-transakcje.md:46-50` | ev-billing-tariff-expert / ev-compliance-expert (poza grupą) | F | MID (`sources/eu-inne.yaml:8`, id `MID`), `OCA-AN-SMV`. Prawdopodobnie już pokryte w tamtych skillach |

**Nakładki (ev-intel już pokrywa, zwykle pełniej i z cytatami):**
- ramki RPC i kody CALLERROR, literówka `OccurenceConstraintViolation`: `ev-ocpp-expert/references/ramki-i-bledy.md`;
- profile 1.6 z kierunkiem: `komunikaty-16.md` §1 (z korektą errata §3.2);
- statusy i `errorCode`: `komunikaty-16.md:32-38`;
- `transactionId` nadaje CS, `meterStart` w Wh: `SKILL.md` ev-ocpp-expert, `komunikaty-16.md:74, 95`;
- `RemoteStart` `Accepted` ≠ start: `wzorce.md` §1;
- kolejka offline i `TransactionMessageAttempts`: `wzorce.md` §4;
- `StopTransaction` dla nieznanej transakcji: przyjąć i dać do kwarantanny (`wzorce.md:106-107`);
- `connectorId 0`: `komunikaty-16.md:39`; dozwolone statusy `connectorId 0`: `ev-cpms-architect/references/model-statusow.md:8` `[16 §7.7]`;
- klucze konfiguracji: `komunikaty-16.md` §5 (pack pisze „repozytorium ich nie wylicza”, ev-intel je wylicza);
- `idTagInfo.status`, `ChangeConfiguration` status: `komunikaty-16.md` §3;
- profile Security Whitepaper: `ev-iso15118-pki-expert/references/bezpieczenstwo-ocpp.md` §2.

---

## 2. dom-ev-ocpp-2x → cel: `skills/ev-ocpp-expert`

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| O2-1 | **Struktura Device Model**: komponent → zmienna → atrybuty, adresowanie parą komponent+zmienna, wynik `Get/SetVariables` per zmienna (częściowy sukces). ev-intel ma enum atrybutów i statusy (`komunikaty-201.md:75-78`), ale bez opisu modelu | `dom-ev-ocpp-2x/references/device-model-i-transakcje.md:3-9` | `komunikaty-201.md` §4 | F | `[201-P1]` (rozdział o Device Model) i `[201-P2 B05–B06]`; sekcje ustalić; id `201-P1`, `201-P2` |
| O2-2 | **`GetBaseReport`/`GetReport` → `NotifyReport` asynchronicznie, w porcjach**; odpowiedź tylko potwierdza przyjęcie; użycie do inwentaryzacji po Boot | `device-model-i-transakcje.md:11-14` | `komunikaty-201.md` §1/§4 | F | `[201-P2 B07, B08]`, pola porcjowania w `[201-P3]` NotifyReportRequest (sprawdzić w schemacie); id `201-P2`, `201-P3`. Użycie przy onboardingu: Wniosek (zbieżny z `ev-cpms-architect/references/ograniczenia.md:53`) |
| O2-3 | **Mapowanie `connectorStatus` 2.0.1 ↔ 9 stanów 1.6** (`Occupied` → `Preparing`/`Charging`/`Suspended*`/`Finishing`, rozstrzygane `chargingState`/transakcją) | `device-model-i-transakcje.md:24-33`; `SKILL.md:79-80` | `ev-ocpp-expert` (tabela różnic w SKILL.md albo `wzorce.md` §5) | F → Wniosek | Definicje `[16 §7.7]`, `[201-P2 §3.23]`, `chargingState` `[201-P3]` (id `16`, `201-P2`, `201-P3`). OCA mapowania nie publikuje (sprawdzić `OCA-WP-MIG`). Zapisać jako Wniosek, tak jak `wzorce.md` §5 |
| O2-4 | Polityka luk i duplikatów `seqNo`: przyjąć, oznaczyć jako niekompletne, timer na uzupełnienie, alarm po `Ended`; duplikat obsłużyć idempotentnie | `SKILL.md:38-42`; `device-model-i-transakcje.md:16-22` | `wzorce.md` §4 | R | ev-intel ma Wniosek „dane niepełne” (`wzorce.md:108`). Kotwica `[201-P2 E §1.3.2]`. Uwaga na K6 |
| O2-5 | Klucz sesji w bazie (stacja, `transactionId`) niezależnie od wersji | `SKILL.md:33-34, 81-82` | `wzorce.md` / ev-cpms-architect | R | — |
| O2-6 | Procedura CSMS dla floty mieszanej 1.6 + 2.x: adapter per wersja, warstwa antykorupcyjna, wspólny model domeny, rejestr wersji i edycji, testy kontraktowe per wersja | `SKILL.md:72-84` | ev-cpms-architect / ev-integration-architect (poza grupą); w ev-ocpp-expert tylko odesłanie | R | Kotwice już są: `[J16 §3.2]`, `[201-P4 §3.1.2]`, `[201-P0 rozdz. 2]` |
| O2-7 | Zapis wersji **i edycji** w rejestrze urządzeń; wymaganie „OCPP 2.1” rozbić na funkcje i sprawdzić, które są certyfikowane | `SKILL.md:15`; `references/ocpp-21.md:17-20` | `wersje-i-status.md` | R | Edycje są już w `[OCA-DL]`. Certyfikacja 2.1: strona OCA niezarejestrowana (patrz CERT-2) |

**Nakładki:**
- brak zgodności wstecz, `TransactionEvent`, `transactionId` od stacji: `SKILL.md` ev-ocpp-expert;
- podprotokoły 2.0.1/2.1: `wersje-i-status.md`;
- profile 1–3 i PKI: `ev-iso15118-pki-expert/references/bezpieczenstwo-ocpp.md`;
- ISO 15118 przez OCPP: `ev-iso15118-pki-expert/references/iso15118-w-ocpp.md`;
- `triggerReason` (pack: [do weryfikacji]): `komunikaty-201.md:50-55`;
- 2.1: daty, IEC 63584-210, edycje (pack: „wtórne”), ramki `SEND`/`CALLRESULTERROR`, 27 nowych akcji: `wersje-i-status.md`, `ramki-i-bledy.md`, `komunikaty-201.md` §6.

---

## 3. dom-ev-simulation-testing → cel: `ev-integration-architect` (taksonomia D13.03 „Symulatory ładowarek…”) i częściowo `ev-evse-diagnostics-expert`

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| SIM-1 | Piramida testów CSMS (5 poziomów: jednostkowe, kontraktowe, symulator, ładowarka w labie, pilotaż) i zasada „łap na najniższym poziomie” | `dom-ev-simulation-testing/SKILL.md:18-28` | ev-integration-architect `references/migracja-i-rozszerzenia.md` §9 (D13.03) | R | — |
| SIM-2 | **Katalog scenariuszy awarii z oczekiwaniem wobec CSMS** (zerwanie w trakcie sesji, odtworzenie kolejki offline, duplikat CALL, zły zegar, brak Stop, utrata zasilania, reconnect storm) | `SKILL.md:56-65` | `ev-ocpp-expert/references/wzorce.md` (krok 7 procedury „kryteria akceptacji”) + ev-integration-architect | R (+F-kotwice) | Każde oczekiwanie da się podeprzeć zarejestrowanymi źródłami: `[16 §3.7]`, `[16 §3.7.1]`, `[16E §3.18]`, `[J16 §4.1.1]`, `[201-P4 §4.1.4]`, `[201-P2 E13]`, `[201-P4 §5.4]` |
| SIM-3 | Test obciążeniowy bramy: metryki (połączenia, handshake/s, p50/p95/p99 per akcja, CALLERROR, CPU/FD generatora), plan z rampą, stan ustalony | `references/obciazenie-i-storm.md:6-22` | ev-cpms-architect (poza grupą) | R | — |
| SIM-4 | Warianty reconnect storm (peak, rampa z jitterem, częściowy, z zaległościami); `Pending` jako sposób rozłożenia ruchu | `obciazenie-i-storm.md:24-34` | ev-cpms-architect / ev-integration-architect | R (+F) | `[201-P4 §5.4]` RetryBackOff, `[201-P2 B02.FR.07]` `interval` przy Pending (zarejestrowane, już w `ograniczenia.md:23-25, 49-50`); dla 1.6 patrz O16-4 |
| SIM-5 | Testy kontraktowe OCPI, atrapa partnera, sandbox huba | `references/kontrakt-ocpi-i-regresja.md:3-15` | ev-ocpi-roaming-expert / ev-integration-architect (tam „Testy OCPI … nie są opracowane”, `migracja-i-rozszerzenia.md:133`) | R | Pola: `evrf-ocpi.yaml` (id `OCPI230`). Sandboxy hubów: brak źródła |
| SIM-6 | Regresja na nagranych logach: anonimizacja stałymi pseudonimami, odtwarzanie ramek `cp>csms`, porównanie stanu domeny | `kontrakt-ocpi-i-regresja.md:17-28` | `ev-evse-diagnostics-expert/references/metoda.md` §1/§5 | R (+F) | Zdanie „anonimizacja jest wymogiem RODO” (`:21`) wymaga RODO (rozp. 2016/679). **Nie ma go w rejestrze ani w `niedostepne.yaml`**: trzeba zarejestrować albo wpisać do niedostępnych |
| SIM-7 | Narzędzia OSS (EVerest, SteVe) | `kontrakt-ocpi-i-regresja.md:30-34` | — | **P** | Źródła wtórne. Taksonomia D13.03 wymienia „narzędzia open-source”, ale według `CLAUDE.md` biblioteka OSS to tylko wskazówka. Nie przenosić jako faktu |
| SIM-8 | Pułapki testów (generator jako wąskie gardło, peak ≠ storm, logi bez anonimizacji, test na produkcji, kod 0 ≠ poprawny stan domeny) | `SKILL.md:77-84` | ev-integration-architect | R | — |

**Nakładki:** brak istotnych. ev-intel ma tylko ogólne „Test każdego modelu stacji” `[OCA-WP-MIG §3.1]` i certyfikację z
symulowanym CSMS `[OCA-WP-CUST §1.5.2]` (`migracja-i-rozszerzenia.md:30, 115`).

---

## 4. dom-ev-certification-testing → cel: `ev-evse-diagnostics-expert` (D13.01) i `ev-integration-architect` (D21.02, D13.03)

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| CERT-1 | Cztery warstwy zgodności (certyfikat OCA / wewnętrzna certyfikacja CPO / ISO 15118 / zgodność regulacyjna): kto co potwierdza, a czego nie | `dom-ev-certification-testing/SKILL.md:23-32` | `metoda.md` §3 | R (+F) | `OCA-CERT`, `OCA-LIST`, `201-P5` (zarejestrowane) |
| CERT-2 | 1.6, 2.0.1 i 2.1 to osobne certyfikaty; profile certyfikacji 1.6 | `SKILL.md:38-39` | `metoda.md` §3 | F | Strony certyfikacji OCA dla 1.6 i 2.1 są **niezarejestrowane** (`OCA-CERT` dotyczy tylko 2.0.1, `oca-ocpp.yaml:65-67`) i **nie ma ich w `niedostepne.yaml`** |
| CERT-3 | OCTT: narzędzie OCA symuluje drugą stronę; wynik zależy od wersji narzędzia i edycji testów | `SKILL.md:26, 41-43` | `metoda.md` §5 | F | Dokumentacja OCTT (OCA) **niezarejestrowana, brak w niedostepne.yaml**; taksonomia D13.01 wymienia OCTT. Przypadki testowe 2.0.1 są w `201-P6` |
| CERT-4 | Żądać raportu z testu (pominięte przypadki, konfiguracja), nie samego logo | `SKILL.md:42` | `metoda.md` §3 | F/R | Dostępność raportu dla kupującego: źródło OCA nieustalone. Sama zasada to R |
| CERT-5 | Wewnętrzny program certyfikacji CPO: fazy 0–5, macierz model × firmware × OCPP × kraj, statusy typu per kraj (`laboratorium`→`pilot`→`dopuszczony`→`wycofany`), firmware referencyjny | `SKILL.md:47-89`; `references/program-certyfikacji-cpo.md:7-25` | ev-integration-architect `migracja-i-rozszerzenia.md` §9 (macierz kompatybilności, D21.02) | R | ev-intel ma tylko zasadę „trzy źródła: certyfikat+PICS, TC z części 6, rejestr odchyleń” (`:135-136`) |
| CERT-6 | Zakres regresji przy zmianie (firmware z/bez zmian OCPP, licznik/terminal, edycja OCPP, nowy kraj, nowa wersja CSMS) | `program-certyfikacji-cpo.md:27-36`; `SKILL.md:84-87` | ev-integration-architect (D13.03 „Testy regresji po zmianie firmware”) | R | — |
| CERT-7 | Kryteria wyjścia i lista dowodów; raport z pierwszą linią `Werdykt:` | `SKILL.md:80-89`; `program-certyfikacji-cpo.md:38-43` | `metoda.md` §6 | R | Progi pack oznacza jako [założenie] (P), więc się ich nie przenosi |
| CERT-8 | Grupy testów (boot, autoryzacja, sesje, pomiar/OCMF, smart charging, firmware, offline, błędy, płatności, bezpieczeństwo, wymogi kraju) | `SKILL.md:59-74` | ev-integration-architect | R | **Wniosek:** zmapować grupy na `TC_*` z `[201-P6]` i arkusz testów `[PICS-CS]` (zarejestrowane). OCMF jest w `niedostepne.yaml` |
| CERT-9 | ISO 15118 conformance, DIN 70121 jako fallback, testivale, interoperacyjność z modelami aut | `SKILL.md:91-98` | ev-iso15118-pki-expert (poza grupą) | F (niedostępne) | ISO 15118 (-4/-5) i DIN SPEC 70121: `niedostepne.yaml` (normy płatne). Testivale (CharIN): niezarejestrowane. Odpowiedź musi zaczynać się od informacji o niedostępności |
| CERT-10 | Mapa zgodności regulacyjnej produktu: CE/RED, EN 18031, CRA, MID/MI-011, Eichrecht, UDT/EIPA, UL 2594/2202, NRTL, NIST HB44 3.40, NEVI | `SKILL.md:100-108` | ev-compliance-expert (poza grupą) | F | Zarejestrowane: `MID`, `DE-MESSEG-33`, `PL-EMOB`, `PL-R1316`. EN 18031: `niedostepne.yaml`. **RED 2014/53/UE, CRA: niezarejestrowane, brak w niedostepne**. USA (UL, NRTL, HB44, NEVI): brak w rejestrze i w niedostępnych |
| CERT-11 | **Karta producenta/modelu** (tożsamość z Boot, wersje firmware × OCPP × profil, certyfikat „deklarowany”, funkcje: deklaracja vs wynik testu, klucze konfiguracji per model, status per kraj, serwis), zasady wpisów, cykl życia, „czego nie wpisywać” | `references/karta-producenta.md:19-108` | rozszerzenie `knowledge/implementation-intelligence/vendor-quirks/_szablon.yaml` + `metoda.md` §6 (D21.03 „Rekomendowane ustawienia konfiguracji per model”) | R | ev-intel ma wpis per obserwacja, bez karty modelu. Pola kontakt/SLA dotyczą `confidentiality` |
| CERT-12 | Role (CPO, producent, dostawca CSMS, osoba podpisująca) | `program-certyfikacji-cpo.md:54-58` | ev-integration-architect | R | — |

**Nakładki:**
- certyfikat nie rozstrzyga przy innym firmware: `metoda.md:128-130`;
- profile certyfikacji 2.0.1 i pola listy certyfikatów: `metoda.md` §3;
- PICS: `[PICS-CS]`;
- „deklaracja ≠ dowód”: `ev-evse-diagnostics-expert/SKILL.md:69`.

---

## 5. dom-ev-diagnostics → cel: `ev-evse-diagnostics-expert` (metoda, skrypt) i `ev-charging-operations-expert/references/diagnostyka.md` (drzewa, poza grupą)

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| DIAG-1 | Drzewo 1 „offline” rozpisane warstwami: DNS/TCP → TLS → upgrade WebSocket → Boot → Heartbeat → wzorzec rozłączeń (idle timeout balancera/NAT, APN) | `dom-ev-diagnostics/references/drzewa-1-2.md:8-45` | `ev-charging-operations-expert/references/diagnostyka.md` §4 | R (+F/P) | F już są: `[J16 §3.2]` (404, podprotokół), `[201-P2 A §1.3]` (zegar a TLS), `[201-P4 §5.4]`. NAT/APN/idle timeout: P (bez źródła) |
| DIAG-2 | Drzewo 2, uzupełnienia: „czy ramka w ogóle wyszła z CSMS” (routing między instancjami), wcześniejsze niezakończone CALL blokuje komendę, lista lokalna po powrocie z offline | `drzewa-1-2.md:58-80` | `diagnostyka.md` §1 | R | Kotwica `[J16 §4.1.1]` (już w `ramki-i-bledy.md`) |
| DIAG-3 | Drzewo 3 „wisząca sesja / brak CDR”: tabela dowodów, przyczyny, zamknięcie szacunkowe, korekta przez CDR kredytowy | `drzewa-3-5.md:9-42` | `diagnostyka.md` (nowa sekcja) / `metoda.md` | R (+F) | `[16 §3.7]`, `[16E §3.18]`, `[201-P2 E13]`, `TxStopPoint` `[201-P2 §2.6.6]`, CDR kredytowy w `[OCPI230 §10]` (sekcję sprawdzić). Nakłada się na `ev-billing-tariff-expert` (`sesja-przerwana.md`) |
| DIAG-4 | **Drzewo 4 „rozjazd energii” licznik ↔ CSMS ↔ CDR**: ×1000 = jednostka, zły `measurand`/`context`, licznik malejący, zegar a granice sesji, zaokrąglenia | `drzewa-3-5.md:44-78` | `diagnostyka.md` (nowa sekcja; w ev-intel brak drzewa energii) | F + R | `meterStart` Wh `[16 §6.45]`, domyślne `unit` Wh `[16 §7.43]`, `measurand`/`context` `[S16]` (już w `komunikaty-16.md` §4), `total_energy` w CDR `[OCPI230 §10.x]` (id `OCPI230`, sekcję ustalić), zaokrąglenia/`step_size` w ev-billing. Struktura drzewa to R |
| DIAG-5 | Drzewo 5, uzupełnienia: wykrywanie flapowania statusów; znaczenie `vendorErrorCode` wymaga dokumentacji producenta; `Faulted` z `NoError` jako odchylenie | `drzewa-3-5.md:80-114` | `ev-charging-operations-expert/references/alarmy.md`, `metoda.md` | P (+F) | Pola `vendorErrorCode`, `info` `[S16]` (już w `komunikaty-16.md:33`). Znaczenie kodów to źródło klasy B (producent), nie A. „Faulted z NoError” to P: wpis w vendor-quirks tylko z modelem i firmware |
| DIAG-6 | Polityka komend zdalnych: plan, akceptacja człowieka, najpierw odczyt, `UnlockConnector` przy aktywnej sesji | `SKILL.md:78-87`; `drzewa-3-5.md:108-114` | `ev-charging-operations-expert/references/dzialania-zdalne.md` | R | Kotwice: skutki Reset `[16 §5.14]`, `[201-P2 B11–B12]` (już są); `UnlockConnector` `OngoingAuthorizedTransaction` `[201-P3]` (`komunikaty-201.md:73`) |
| DIAG-7 | Format logu ramek JSON Lines `{ts, cp, dir, frame}`, czas odbioru po stronie bramy | `references/log-i-skrypt.md:3-17` | `metoda.md` §1–2 (razem ze skryptem, patrz sekcja 7) | R | — |
| DIAG-8 | RODO dla logów (minimalny zakres, retencja, zakaz wklejania do narzędzi zewnętrznych) | `log-i-skrypt.md:15-16` | `metoda.md` §1 | F | RODO **niezarejestrowane, brak w niedostepne.yaml** (jak SIM-6) |
| DIAG-9 | **Raport diagnozy**: 9 sekcji, oś czasu z plik:linia, wykluczone hipotezy, kroki naprawy, skutki dla rozliczeń; jakość dowodu (bezpośredni / pośredni / założenie) | `references/raport-diagnozy.md:3-31, 55-60` | `metoda.md` §6 (werdykt i poziom pewności) | R | Spójne z werdyktem ev-intel (zgodne / niezgodne / nierozstrzygnięte) |
| DIAG-10 | Pułapki: Heartbeat ≠ „wszystko działa”, brak ramki we *własnym* logu (inna instancja), za wczesna jedna przyczyna, ukryte obejście | `SKILL.md:102-110` | `metoda.md` / `diagnostyka.md` | R | — |

**Nakładki:**
- dowody przed zmianą: `metoda.md` §1;
- autoryzacja i `idTagInfo`: `diagnostyka.md` §1;
- `Pending` 2.0.1: `ograniczenia.md` §2;
- `Faulted`/`errorCode`/Inoperative: `diagnostyka.md` §1, `alarmy.md`;
- `GetDiagnostics`/`GetLog`: `metoda.md:99`;
- wiele stacji offline naraz: `diagnostyka.md` §4;
- skutki Reset: `dzialania-zdalne.md`.

---

## 6. dom-ev-charger-onboarding → cel: `ev-integration-architect` (D13.03, D21.02), `ev-evse-hardware-expert` (karta urządzenia), `ev-evse-diagnostics-expert`

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| ONB-1 | Procedura 9 kroków wprowadzenia typu (dokumentacja → identyfikatory → połączenie → bramka Boot → konfiguracja → testy → logi → odchylenia → pilot) | `dom-ev-charger-onboarding/SKILL.md:24-37` | ev-integration-architect (nowa sekcja) | R | — |
| ONB-2 | Bramka Boot: dopasowanie (vendor, model, firmware) do karty, `Pending` na czas konfiguracji, `Accepted` tylko dla stacji z listy pilotażowej | `SKILL.md:47-57` | `ev-cpms-architect/references/ograniczenia.md:53` (Wniosek prawie identyczny dla 2.0.1) | R (+F) | 2.0.1 `[201-P2 B02]` jest już. Dla 1.6 brak: patrz O16-3 `[16 §4.2]` |
| ONB-3 | **`Accepted` na `ChangeConfiguration`/`SetVariables` ≠ zastosowanie**; `RebootRequired` → restart → ponowny odczyt jako dowód; zapis po jednym kluczu | `SKILL.md:59-68, 121` | `ev-ocpp-expert/references/wzorce.md` (nowa sekcja „Zmiana konfiguracji”) | F + Wniosek | `ChangeConfiguration` `[16 §5.3]` (numer sprawdzić) i `[S16]`; `SetVariables` `[201-P2 B05]`, `RebootRequired` `[201-P3]`; zarejestrowane (`16`, `S16`, `201-P2`, `201-P3`) |
| ONB-4 | Macierz testów akceptacyjnych T1–T14 (oczekiwanie, dowód) i kryteria przejścia (krytyczne T1, T3, T5–T9) | `references/macierz-testow.md:6-32` | ev-integration-architect §9 / `metoda.md` §5 | R | **Wniosek:** każdy T zmapować na `TC_*` `[201-P6]` i `[PICS-CS]`; oczekiwania (np. T2, T3) poprawić według K2 i K9 |
| ONB-5 | Pilot na jednej stacji, rollout partiami (5%/25%/reszta), plan wycofania (poprzedni firmware, `Rejected` w bramce) | `SKILL.md:99-108`; `macierz-testow.md:34-39` | ev-integration-architect (migracja) | R | Progi pack oznacza jako [założenie] (P), więc się ich nie przenosi |
| ONB-6 | Karta onboardingu typu (OCPP i edycja, profil, EVSE/złącza, moc, licznik, łączność, firmware/podpis, status) | `references/karta-onboardingu.md:6-37` | `ev-evse-hardware-expert/references/karta-urzadzenia.md` (nakłada się w polach z Boot/NotifyReport) | R | — |
| ONB-7 | Obejście zawsze za flagą ograniczoną do (producent, model, firmware), domyślnie wyłączoną | `SKILL.md:85-97` | `_szablon.yaml` → `workaround` (dodać pola `flag`, `scope`) | R | — |
| ONB-8 | „W 2.0.1 podpisany firmware wymagany” | `karta-onboardingu.md:22` | `ev-iso15118-pki-expert/references/bezpieczenstwo-ocpp.md` §8 | F (sporne) | `[201-P2 blok L]` (L01 i ewentualny wariant niepodpisany: sprawdzić); id `201-P2`. Patrz K11 |

**Nakładki:**
- pola tożsamości z Boot: `karta-urzadzenia.md` §1;
- porównanie `NotifyReport` z kartą producenta (D21): `karta-urzadzenia.md` §3;
- `Pending` jako onboarding: `ograniczenia.md:53`;
- certyfikat nie zastępuje testu: `migracja-i-rozszerzenia.md:30-31`.

---

## 7. Skrypty

| Skrypt | Co robi | Odpowiednik w ev-intelligence | Zależności | Testy | Gdzie pasuje |
|---|---|---|---|---|---|
| `dom-ev-diagnostics/scripts/ocpp_log_analyze.py` (243 l.) | Analiza sekwencji i czasu w logu JSON Lines: `call-no-response`, `callerror`, `duplicate-message-id`, `open-transaction`, `unknown-transaction`, `seqno-gap/duplicate`, `meter-decrease`, `clock-skew`, `reboot`, `invalid-line`; wynik tekst/`--json`; kod 0/2 | **Brak.** `ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py` sprawdza tylko schemat ramek, a `metoda.md:108-109` wprost mówi, że „skrypt nie sprawdza sekwencji … czasów”. Analizator wypełnia tę lukę | tylko stdlib (argparse, datetime, json, sys); sieć: brak | `packs/pack-ev/tests/test_ocpp_log_analyze.py` (155 l., styl `main()`+`check()`, nie unittest) | `skills/ev-evse-diagnostics-expert/scripts/`. **Werdykt: przenieść po dostosowaniu.** Do zrobienia: (1) test przepisać na unittest w `tests/` (bramka uruchamia `unittest discover tests`); (2) ścieżki: test szuka `ROOT/.claude/hooks` i `.claude/skills/dom-ev-diagnostics/…`; (3) docstring z cytatami reguł (`seqNo` +1 `[201-P2 E §1.3.2]`, Wh `[16 §6.45]`, `transactionId = -1` `[16E §3.18]`); (4) poprawki: `transactionId -1` zgłaszany jako `unknown-transaction` (`:136-140`), a powinien mieć własne ustalenie; ramki 2.1 typu 5/6 lądują jako `invalid-line` (`:101`); domyślny `--timeout 30` opisać jako próg narzędzia, a nie wartość ze specyfikacji (K1); (5) wspólny format wejścia z `ocpp_frame_check.py` (ten czyta dowolne linie z ramką) albo opcja odczytu obu formatów |
| `dom-ev-simulation-testing/scripts/charge_sim.py` (217 l.) | Symulator stacji 1.6J (jedno złącze, tylko `ws://`): scenariusze `session`/`boot`, awarie `offline-replay`, `duplicate-message`, `clock-skew`, `drop-stop`; log JSON Lines dla analizatora; na każde CALL od CSMS odpowiada CALLERROR `NotSupported`; kod 0/1/2 | **Brak** (`tools/` to narzędzia bazy wiedzy, `scripts/` to release). ev-intel nie ma symulatora | stdlib + `ocpp_ws.py`; sieć: tylko adres `ws://` z wywołania | `tests/test_charge_sim.py` (165 l., stub CSMS na `ocpp_ws.serve`, styl `main()`); `tests/test_mini_csms.py` korzysta z `examples/mini-csms-ocpp16`, którego nie ma w pack-ev ani w `/home/user/tf/examples` | `skills/ev-integration-architect/scripts/` (D13.03), z odesłaniem z `ev-ocpp-expert`. **Werdykt: przenieść warunkowo.** Najpierw poprawić kolejność: `Charging` jest wysyłane **przed** `StartTransaction` (`charge_sim.py:142-144`, K9). Pola payloadów potwierdzić w `[S16]`. Test przepisać na unittest. Zaznaczyć, że to symulator stacji (testuje CSMS), a metoda ev-intel (`metoda.md:149`) potrzebuje odwrotnego: symulatora CSMS do testu stacji |
| `dom-ev-simulation-testing/scripts/ocpp_ws.py` (218 l.) | Minimalny klient i serwer WebSocket RFC 6455 na asyncio (bez TLS, bez rozszerzeń), negocjacja podprotokołu | Brak | stdlib (asyncio, base64, hashlib, os, struct); sieć: adres z wywołania | `tests/test_ocpp_ws.py` (110 l., styl `main()`) | Razem z `charge_sim.py` (biblioteka pomocnicza). **Werdykt: przenieść tylko z poprawką K7.** Serwer bez wspólnego podprotokołu odpowiada `HTTP 400` (`ocpp_ws.py:12, 200-205`), a OCPP-J 1.6 wymaga dokończenia handshake bez nagłówka i natychmiastowego zamknięcia `[J16 §3.2]`. RFC 6455 (IETF) nie jest zarejestrowane: przed cytowaniem dodać do rejestru albo opisywać tylko zachowanie OCPP-J |

Scenariusze ewaluacji pack-ev (`packs/pack-ev/tests/skill_evals/`):
- 3–4 scenariusze na skill plus `holdout/dom-ev-ocpp-16.json` (5).
- Tematy warte przeniesienia jako nowe scenariusze ev-intel (treść sprawdzeń trzeba napisać od nowa z cytowanymi faktami):
  - `stop-nieznany-transactionid`, `status-kabel-bez-autoryzacji` (O16-1);
  - `kwh-vs-wh-rozjazd` (DIAG-4);
  - `firmware-inne-statusy-flota` (ONB/CERT);
  - `certyfikat-oca-a-nasz-csms` (CERT-1).
- Holdout pack-ev: według `docs/SKILLS-WORKFLOW.md` holdout pisze inny agent niż autor skilli. Autor zmian nie powinien
  go czytać, więc przeniesienie musi zrobić osoba lub agent spoza autorstwa.

---

## 8. Konflikty (różne twierdzenia o tym samym)

| # | pack-ev | ev-intelligence | rozstrzygnięcie |
|---|---|---|---|
| K1 | „typowy timeout ~30 s”: `dom-ev-ocpp-16/SKILL.md:31`, `dom-ev-diagnostics/references/drzewa-1-2.md:4-5`; domyślne `--timeout 30` (`log-i-skrypt.md:27`) | timeout „implementation-dependent”, specyfikacja nie podaje liczby; w 2.0.1 `OCPPCommCtrlr.MessageTimeout`: `ev-ocpp-expert/references/ramki-i-bledy.md:27-29` `[J16 §4.1.1]` `[201-P4 §4.1.1]` | ev-intel (specyfikacja). 30 s może zostać tylko jako parametr narzędzia |
| K2 | „Heartbeat co `interval`”; w testach T2 „co interval”; „cisza = połączenie martwe”: `dom-ev-ocpp-16/SKILL.md:47`, `dom-ev-charger-onboarding/references/macierz-testow.md:10`, `drzewa-1-2.md:22` | `HeartbeatInterval` to interwał **bezczynności**; przy JSON Heartbeat „not mandatory”, stacja MAY go pominąć po innym PDU, CS SHOULD uznać dostępność po każdym PDU: `ev-ocpp-expert/SKILL.md:106-107`, `references/wzorce.md:56-60` `[16 §4.6]` `[16 §9.1.10]` | ev-intel. T2 i drzewo 1 przeformułować („brak jakiegokolwiek PDU”) |
| K3 | Security Whitepaper „edycja 2”, nazwy 11 komunikatów [do weryfikacji]: `dom-ev-ocpp-16/SKILL.md:87-90`, `references/komunikaty-i-profile.md:20-21` | Security Whitepaper **Edition 4** (2026-02-05), 11 akcji wymienionych z nazwy: `ev-ocpp-expert/references/wersje-i-status.md:12`, `komunikaty-16.md:27`; `sources/oca-ocpp.yaml:23-27` | ev-intel (aktualne wydanie OCA) |
| K4 | `DataTransfer` „poza profilami”, przypisanie do Core „do weryfikacji”: `komunikaty-i-profile.md:14, 17` | `DataTransfer` w Core w obu kierunkach (tabela §3.3 po korekcie): `komunikaty-16.md:21` `[16 §3.3]` `[16E §3.2–3.3]` | ev-intel (errata) |
| K5 | Stacja offline bez `transactionId` używa „własnego tymczasowego identyfikatora lokalnie [do weryfikacji]”; „sposób identyfikacji offline do weryfikacji”: `dom-ev-ocpp-16/SKILL.md:116-117`, `odchylenia-i-offline.md:13` | stacja SHALL wysyłać `transactionId = -1`, CS SHALL odpowiadać jak dla ważnego: `ev-ocpp-expert/SKILL.md:100-101`, `wzorce.md:88-89` `[16E §3.18]` | ev-intel (errata). Skutek dla analizatora: `ocpp_log_analyze.py:136-140` zgłasza to jako `unknown-transaction` |
| K6 | `seqNo` „rosnący w obrębie jednej transakcji (nie globalnie, nie per stacja)”: `dom-ev-ocpp-2x/SKILL.md:31-32`, `device-model-i-transakcje.md:16` | `seqNo` to licznik **per EVSE**; 0 na starcie to SHOULD, licznik ciągły dozwolony, SHALL +1 po każdym `TransactionEvent`: `ev-ocpp-expert/SKILL.md:113-114`, `komunikaty-201.md:45-47` `[201-P2 E §1.3.2, §1.3.2.1]` | ev-intel. Analizator (śledzenie w obrębie transakcji, +1) pozostaje zgodny, ale nie może zakładać startu od 0 |
| K7 | Serwer bez wspólnego podprotokołu odpowiada `HTTP 400`: `dom-ev-simulation-testing/scripts/ocpp_ws.py:12, 200-205`; „odrzuć połączenie”: `dom-ev-ocpp-2x/SKILL.md:74`; „nie powinien potwierdzać [do weryfikacji]”: `dom-ev-ocpp-16/SKILL.md:40-41` | CSMS MUST dokończyć handshake **bez** nagłówka `Sec-WebSocket-Protocol` i natychmiast zamknąć połączenie: `ev-ocpp-expert/references/wersje-i-status.md:48-50` `[J16 §3.2]` | ev-intel. `ocpp_ws.py` poprawić przed przeniesieniem |
| K8 | Dla błędów po stronie CSMS „raczej CALLERROR `InternalError` z backoffem po stronie ładowarki”: `dom-ev-ocpp-16/references/odchylenia-i-offline.md:28-31` | CALLERROR na komunikat transakcyjny tylko przy realnym błędzie formatu; stacja ponawia do `TransactionMessageAttempts` i **porzuca** komunikat (utrata danych): `ev-ocpp-expert/SKILL.md:97-99`, `wzorce.md:86-87, 106-107` `[16 §3.7.1]` `[201-P2 E13]` | Oba to wnioski; ev-intel jest oparty na cytowanym mechanizmie porzucania. Rekomendację pack odrzucić albo dopisać ryzyko utraty danych |
| K9 | Symulator wysyła `StatusNotification Charging` **przed** `StartTransaction` (`charge_sim.py:142-144`; opis `dom-ev-simulation-testing/SKILL.md:50-51`) | — (ev-intel nie opisuje kolejności). W samym pack-ev odwrotnie: `status-i-transakcje.md:23, 36-37` (`StartTransaction` → `Charging`) | Niespójność wewnętrzna pack-ev. Rozstrzygnąć z tabeli przejść i diagramów `[16]` (O16-1, O16-2) |
| K10 | Fakty 2.1 (data, IEC 63584-210, edycje Ed4/Ed2) „wtórne, do weryfikacji”; podprotokół 2.1 nieznany: `dom-ev-ocpp-2x/SKILL.md:26, 61-70`, `references/ocpp-21.md:3-7` | Sprawdzone w `[OCA-N1]`, `[OCA-N2]`, `[OCA-DL]`; `ocpp2.1` `[21-P4 §3.1.2]`: `wersje-i-status.md:5-27, 47` | ev-intel (pack jest nieaktualny) |
| K11 | „W 2.0.1 podpisany firmware wymagany (wg `ocpp.md`)”: `dom-ev-charger-onboarding/references/karta-onboardingu.md:22` | Opisuje „Bezpieczna aktualizacja firmware (L01)” bez stwierdzenia, że podpis jest obowiązkowy: `ev-iso15118-pki-expert/references/bezpieczenstwo-ocpp.md:98-110` `[201-P2 L01]` | Nierozstrzygnięte. Sprawdzić blok L w `[201-P2]` (L01 i ewentualny przypadek niepodpisany) przed przeniesieniem |
| K12 | Dozwolone statusy dla `connectorId 0` „ograniczone [do weryfikacji]”: `status-i-transakcje.md:33-34` | tylko `Available`/`Unavailable`/`Faulted`: `ev-cpms-architect/references/model-statusow.md:8` `[16 §7.7]` | Brak sprzeczności treści; ev-intel rozstrzyga |

---

## 9. Podsumowanie liczbowe

- Luki: **59** (O16: 14, O2: 7, SIM: 8, CERT: 12, DIAG: 10, ONB: 8).
- Według klas: **F 19**, **R 37**, **P 3** (O16-11 katalog odchyleń, SIM-7 narzędzia OSS, DIAG-5 znaczenie kodów
  producenta / `Faulted+NoError`).
- Luki F z dokumentem w rejestrze: O16-1, O16-2, O16-3, O16-5, O16-6, O16-14, O2-1, O2-2, O2-3, DIAG-4, ONB-3, ONB-8.
- Luki F bez dokumentu w rejestrze ani wpisu w `niedostepne.yaml` (trzeba zgłosić człowiekowi i dopisać):
  - strony certyfikacji OCA 1.6/2.1 i OCTT (CERT-2, CERT-3, CERT-4);
  - RED 2014/53/UE, CRA, przepisy USA (CERT-10);
  - RODO (SIM-6, DIAG-8);
  - RFC 6455 (skrypt `ocpp_ws.py`);
  - O16-4 (1.6 backoff), gdzie źródło trzeba dopiero ustalić.
- Luki F tylko z norm płatnych (już w `niedostepne.yaml`): CERT-9 (ISO 15118-4/-5, DIN SPEC 70121), OCMF w CERT-8.
