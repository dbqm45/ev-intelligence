# Luki D: pack-ev (regulacje, metrologia, bezpieczeństwo, ISO 15118) w porównaniu z ev-intelligence

Stan: 2026-11-15. Analiza tylko do odczytu: nic nie edytowano i niczego nie pobierano z sieci. Nie otwierano `sources/poufne/`.

**Ścieżki skrócone w tabelach:**
- `pe/` = `/home/user/tf/packs/pack-ev/skills/`
- `ei/` = `/home/user/ev-intelligence/`
- `CE` = `ei/skills/ev-compliance-expert/`
- `PKI` = `ei/skills/ev-iso15118-pki-expert/`

Numery linii to numery w danym pliku.

**Klasy:**
- **F**: fakt, który da się sprawdzić w akcie prawnym, normie albo specyfikacji. Można go przenieść dopiero po sprawdzeniu w źródle oficjalnym.
- **F-N**: fakt normowy, ale źródło jest płatne albo niedostępne (`sources/niedostepne.yaml`). Według CLAUDE.md nie wolno go przenieść.
- **P**: wiedza praktyczna bez źródła oficjalnego. Nie da się jej przenieść jako faktu.
- **R**: procedura albo heurystyka bez faktów. Pasuje do sekcji „Procedura” lub „Pułapki” albo jako **Wniosek** przy faktach z cytatem.

**Ważna uwaga o źródłach pack-ev:** pack-ev cytuje bazę fabryki tf (`.claude/knowledge/<id>/doc.txt`, linie). Nie są to identyfikatory z `ei/sources/*.yaml`, więc żadnego cytatu nie da się przenieść 1:1. Każdy fakt trzeba sprawdzić w tekście oficjalnym i dać mu znacznik `[ID §sekcja]`. Rejestr ei ma dziś dla tego obszaru tylko te identyfikatory:
- `AFIR`, `AFIR-OJ`, `AFIR-655`;
- `MID` (tylko tekst pierwotny);
- `PL-EMOB`, `PL-R1316`;
- `DE-MESSEG-33`, `BNETZA-LSR`;
- `EIPA-OPIS`, `EIPA-API`;
- pakiety OCA: `16`, `S16`, `SWP4`, `201-P2`, `201-P3`, `201-APP`, `201-CSV`, `201-E`, `21-P0`, `21-P2`;
- noty OCA: `OCA-AN-SMV`, `OCA-AN-PNC`, `OCA-WP-AFIR` (pobrany, nieopracowany);
- `OCPI230`, `OCPI221`.

**Brakuje w rejestrze:** NIS2, CRA, Data Act, EPBD, RED III, RED DA 2022/30, 2026/339, MID 2026/706, Zalecenie 2003/361/WE, RODO, 23 CFR 680, NIST HB44 i OCMF.

**Wpisy w `niedostepne.yaml`, które dotyczą tej grupy:**
- ISO 15118, DIN SPEC 70121;
- IEC 62443 / ISO 27001 / EN 18031;
- OCMF i EDL (`niezarejestrowana`);
- MessEV i PTB;
- Prawo o miarach;
- UL 1741 / SAE J3072.

UL 2594, UL 2202, UL 2231, SAE J1772 i J3400 nie są wpisane nigdzie.

**USA w ev-intelligence:** brak całkowity. Jedyne ślady:
- enum złącza `SAE_J3400` w `ei/skills/ev-evse-hardware-expert/references/zlacza-i-moc.md:37`;
- normy IEEE, UL i SAE w `niedostepne.yaml`;
- zdanie „Wymogi spoza UE (np. USA) to domena D12.06, nieopracowana” w `ei/skills/ev-charging-operations-expert/references/alarmy.md:63`.

Taksonomia D12.06 „Inne kraje” wymienia DE, NL, FR i UK, ale nie wymienia USA. Domena D12 należy do `ev-compliance-expert`, więc USA pasuje tam jako nowy plik `CE/references/usa.md`. Wymaga to trzech kroków:
1. decyzji właściciela o zakresie;
2. dopisania USA do tematów D12.06 i uruchomienia `render_taxonomy.py`;
3. nowego rejestru `sources/us-prawo.yaml` (eCFR 23 CFR 680, NIST HB44 3.40).

**NIS2 i CRA w ev-intelligence:** są tylko w taksonomii (D12.03, D11.05 → `ev-compliance-expert`) i w `docs/DO-ZROBIENIA.md:20-23` jako „tematy bez skilla”. Merytorycznie nie ma nic. Cel: nowy plik `CE/references/cyber-i-dane-ue.md`, czyli NIS2, CRA, Data Act i RED DA. EPBD i RED III mogą trafić tam samo albo do D12.02.

---

## 1. dom-ev-regulations-eu → ev-compliance-expert

Pokrycie w ev-intelligence:
- AFIR jest dobrze opracowany. Mapa obowiązków jest w `CE/references/afir-mapa.md`, szczegóły w innych skillach (hardware, billing, smart charging, cpms).
- ev-intelligence ma dodatkowo `AFIR-655` (częstotliwość 1 min i 24 h, DATEX II), którego pack-ev w ogóle nie zna.
- Reszta aktów (NIS2, CRA, Data Act, EPBD, RED III, RED DA) to luka pełna.

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| E1 | NIS2: zakres (średnie i większe, wyjątki z art. 2 ust. 2), CPO w Aneksie I pkt 1 lit. a, podmiot kluczowy a ważny (art. 3) | `pe/dom-ev-regulations-eu/references/akty-nis2-cra-data-act-epbd-red.md:16-23`; `SKILL.md:37` | `CE/references/cyber-i-dane-ue.md` (nowy, D12.03) | F | dyrektywa (UE) 2022/2555, EUR-Lex. **Brak id**, trzeba zarejestrować |
| E2 | NIS2: środki z art. 21 ust. 2 (lista), łańcuch dostaw z art. 21 ust. 3, odpowiedzialność zarządu (art. 20) | `akty…md:24`; `pe/dom-ev-security/references/regulacje-cyber.md:14-16` | jw. | F | 2022/2555. Brak id |
| E3 | NIS2: zgłoszenia z art. 23 (24 h, 72 h, raport pośredni, raport końcowy do miesiąca), definicja poważnego incydentu (ust. 3), powiadomienie odbiorców usług (ust. 1–2), treść wczesnego ostrzeżenia | `akty…md:25-26`; `regulacje-cyber.md:17-19`; `incydent-w-sieci.md:47-54` | jw.; procedura w PKI (pkt 7) jako odesłanie | F | 2022/2555. Brak id |
| E4 | NIS2: kary z art. 34 (10 mln EUR / 2 % i 7 mln EUR / 1,4 %), transpozycja z art. 41 (17.10.2024 i 18.10.2024), listy podmiotów do 17.04.2025 | `akty…md:27-28` | jw. | F | 2022/2555. Brak id. Ustawa PL transponująca NIS2 też niezarejestrowana |
| E5 | Kwalifikacja eMSP i dostawcy CSMS w NIS2 (inny typ podmiotu, usługa zarządzana) | `akty…md:21`; `regulacje-cyber.md:13` | jw., jako „czego źródło nie określa” | R | pytanie otwarte, bez faktu |
| E6 | CRA: zakres (art. 2), produkt ze zdalnym przetwarzaniem danych (art. 3 pkt 1–2), motyw 12 (SaaS podlega NIS2), wyłączenia | `akty…md:37-41`; `SKILL.md:83-84` | `cyber-i-dane-ue.md` | F | rozporządzenie (UE) 2024/2847. Brak id |
| E7 | CRA, art. 13: ocena ryzyka, komponenty obce, obsługa podatności, okres wsparcia ≥ 5 lat (motyw 60 i art. 13) | `akty…md:42`; `regulacje-cyber.md:38-39` | jw. | F | 2024/2847. Brak id |
| E8 | CRA, Aneks I część I i II: brak znanych podatności, bezpieczna konfiguracja domyślna, aktualizacje, SBOM, CVD, adres do zgłoszeń | `akty…md:43`; `pe/dom-ev-security/references/kontrole-i-migracja.md:69-74` | jw. | F | 2024/2847. Brak id |
| E9 | CRA, art. 14 i 16: zgłaszanie aktywnie wykorzystywanej podatności (24 h, 72 h, 14 dni) i poważnego incydentu, jedna platforma do CSIRT i ENISA | `akty…md:44`; `SKILL.md:40`; `incydent-w-sieci.md:51` | jw. | F | 2024/2847. Brak id. **Stosuje się od 11.09.2026, czyli już dziś** |
| E10 | CRA: ocena zgodności (art. 32, moduł A), Aneks III (ładowarka nie jest wymieniona), art. 28–31 (deklaracja, CE), art. 69 (produkty starsze), art. 71 (terminy 11.06.2026, 11.09.2026, 11.12.2027) | `akty…md:45-48`; `SKILL.md:38` | jw. | F | 2024/2847. Brak id |
| E11 | Data Act, art. 1–5 i 7 (produkt skomunikowany, dostęp z projektu, żądanie użytkownika, strona trzecia, wyłączenie MŚP), art. 50 | `akty…md:54-67`; `SKILL.md:41, 85` | `cyber-i-dane-ue.md`, odesłanie do ev-cpms-architect | F | rozporządzenie (UE) 2023/2854. Brak id |
| E12 | Data Act, art. 23–31 (zmiana dostawcy chmury: 2 mies., 30 dni, bez opłat od 12.01.2027) | `akty…md:66`; `SKILL.md:42` | jw. | F | 2023/2854. Brak id |
| E13 | EPBD, art. 14 ust. 1, 2, 4, 6 i 7 (punkty i pre-okablowanie, smart i otwarte protokoły), art. 2 pkt 33–34, art. 16, transpozycja z art. 35 (29.05.2026) | `akty…md:73-83`; `SKILL.md:43` | `CE` (D12.02, nowy plik albo sekcja), odesłanie do ev-energy-smart-charging-expert | F | dyrektywa (UE) 2024/1275, wersja skonsolidowana. Brak id |
| E14 | RED III, art. 20a ust. 1–5 (dane z sieci, dane baterii dla eMSP, punkty niepubliczne), art. 25 ust. 4 (kredyty OZE), transpozycja. Do tego **rozbieżność**: art. 20a ust. 4 odsyła do „AFIR art. 15 ust. 3–4”, a tekst AFIR nie pasuje | `akty…md:89-101` | `CE` (D12.02); rozbieżność do tabeli rozbieżności (wymóg CLAUDE.md) | F | dyrektywa (UE) 2023/2413. Brak id. Druga strona rozbieżności: `AFIR art. 15` (jest w rejestrze) |
| E15 | RED: rozporządzenie delegowane 2022/30 (stosuje się od 01.08.2025) i 2026/339 (uchylenie ze skutkiem od 11.12.2027, motywy 3–5) | `SKILL.md:39, 72`; `regulacje-cyber.md:61-64` | `cyber-i-dane-ue.md` (D12.03 i D11.05) | F | EUR-Lex 2022/30 i 2026/339. Brak id. EN 18031 jest w `niedostepne.yaml` (płatna). **Treści 2022/30 nie czytał nawet pack-ev** |
| E16 | AFIR, art. 2: definicje rozstrzygające zakres (ad hoc pkt 47, digitally-connected pkt 17, smart pkt 65, publicly accessible pkt 45, punkt, stacja, pula, MSP pkt 36, dane statyczne i dynamiczne) | `pe/dom-ev-regulations-eu/references/afir.md:19-35` | `CE/references/afir-mapa.md` (nowa sekcja „Definicje”) | F | **`AFIR art. 2`** (jest) |
| E17 | AFIR, art. 5 ust. 3: zakaz dyskryminacji także między eMSP, zróżnicowanie tylko proporcjonalne. Art. 5 ust. 6: państwa monitorują zgodność | `afir.md:54, 60` | `afir-mapa.md` (operatorzy, MSP) | F | `AFIR art. 5` |
| E18 | AFIR, art. 5 ust. 4, ostatni akapit: akapity 1–2 dla punktów od 13.04.2024 (punkty starsze i akapit 3 to kwestia wykładni) | `afir.md:58`; `SKILL.md:53-54` | `afir-mapa.md`, jako „czego źródło nie określa” | F | `AFIR art. 5` |
| E19 | AFIR, art. 5 ust. 8: daty (nowe po 13.04.2024, odnowione po 14.10.2024) | `SKILL.md:34`; `afir.md:69` | `afir-mapa.md:21` (dziś bez dat) | F | `AFIR art. 5` |
| E20 | AFIR, art. 20 ust. 1 (IDRO do 14.04.2025), ust. 4 (NAP do 31.12.2024), **ust. 5 (wspólny europejski punkt dostępu do 31.12.2026)**, ust. 6–8 (wspólne API, akty wykonawcze) | `afir.md:75-93`; `SKILL.md:35` | `afir-mapa.md:28-30` | F | `AFIR art. 20`, `AFIR-655` |
| E21 | AFIR, art. 21–22 (zmiany Aneksu II, normy dla pkt 2.2–2.4), **art. 24 ust. 2 (przegląd do 31.12.2026)**, art. 26 (stosowanie) | `afir.md:62-63, 112-119` | `afir-mapa.md` | F | `AFIR art. 21`, `art. 24`, `art. 26` |
| E22 | Mapa „zdarzenie → akty” oraz kolumna „dla CPMS / aplikacji / firmware” | `akty…md:105-111`; `SKILL.md:27-44` (ostatnia kolumna) | `CE/SKILL.md`, procedura | R | bez faktów |
| E23 | Progi średniego przedsiębiorstwa (przykład „120 i 150 pracowników = podmiot ważny”) | `akty…md:30-33`; `regulacje-cyber.md:23-26` | `cyber-i-dane-ue.md` | F | Zalecenie Komisji 2003/361/WE. **Niezarejestrowane** (pack-ev też go nie ma) |

Nakładki, których nie trzeba przenosić:
- AFIR art. 5 ust. 1–2 (płatność ad hoc, QR < 50 kW, terminal od 01.01.2027 dla starszych punktów ≥ 50 kW na TEN-T): `ei/skills/ev-evse-hardware-expert/references/wymagania-afir.md:38` i `ei/skills/ev-billing-tariff-expert/references/ceny-afir-ocpp.md:16`.
- AFIR art. 5 ust. 4–5 (cena): `afir-mapa.md:17-26` i ev-billing-tariff-expert.
- AFIR art. 5 ust. 7 i 10, art. 3 (cele mocy, TEN-T): `afir-mapa.md:6-22`.
- AFIR art. 5 ust. 11: `ev-evse-hardware-expert/references/wymagania-afir.md:50`.
- AFIR Aneks II (złącza, daty ISO 15118): `PKI/references/iso15118-w-ocpp.md:120-122` i ev-evse-hardware-expert.
- „AFIR nie wskazuje OCPP ani OCPI”: `ev-evse-hardware-expert/references/wymagania-afir.md:33`.
- AFIR art. 25 (uchylenie 2014/94/UE): `afir-mapa.md:37-38`.

## 2. dom-ev-regulations-pl → ev-compliance-expert (`references/prawo-pl.md`)

Pokrycie jest wysokie. ev-intelligence ma więcej niż pack-ev, bo opracował rozporządzenie Dz.U. 2019 poz. 1316, którego pack-ev nie ma. Luki to drobne przepisy ustawy. Wszystkie da się sprawdzić w `PL-EMOB`, który jest w rejestrze, więc przeniesienie jest tanie.

| # | luka | źródło pack-ev | cel w ev-intelligence | klasa | źródło oficjalne / id |
|---|---|---|---|---|---|
| P1 | Kary z art. 45 ust. 2 pkt 4: **50 000 zł** (art. 27, 29c) i **100 000 zł** (eksploatacja mimo decyzji z art. 27 ust. 4, 29c ust. 4, 29f ust. 7 i ust. 8 pkt 1–2), za każdą stację | `pe/dom-ev-regulations-pl/references/ustawa-artykuly.md:69`; `SKILL.md:76` | `CE/references/prawo-pl.md:113-120` (tabela kar) | F | `PL-EMOB art. 45` |
| P2 | Art. 29f: kontrola Prezesa UDT, protokół, decyzja o wstrzymaniu, ponowny start jak po badaniu wstępnym | `ustawa-artykuly.md:50` | `prawo-pl.md:92` (dziś „szczegóły nieopracowane”) | F | `PL-EMOB art. 29f` |
| P3 | Odwołania: od Prezesa URE do SOKiK w 14 dni (art. 46), od Prezesa UDT do ministra. Art. 47 (dokąd idą należności z kar). Art. 30–31 (podstawa opłat, KPA) | `ustawa-artykuly.md:51, 73-75` | `prawo-pl.md` §8 | F | `PL-EMOB art. 30`, `art. 31`, `art. 46`, `art. 47` |
| P4 | Art. 41b ust. 2: wniosek o uznanie kodu nadanego w innym państwie UE zamiast numeru EIPA | `SKILL.md:45-47` | `prawo-pl.md` §7 | F | `PL-EMOB art. 41b` |
| P5 | Art. 41 ust. 1–4: oznakowanie stacji i informacja w widocznym miejscu (dziś jest tylko kara za ich brak) | `ustawa-artykuly.md:56` | `prawo-pl.md` §2 i §8 | F | `PL-EMOB art. 41` |
| P6 | Art. 42 ust. 8 i 10 (dane dla każdego zainteresowanego), ust. 11 (wzór zgłoszenia w rozporządzeniu) | `SKILL.md:52`; `ustawa-artykuly.md:60-61` | `prawo-pl.md` §7 | F | `PL-EMOB art. 42`. Rozporządzenie Dz.U. 2022 poz. 1511 jest w `pl-prawo.yaml: not_yet_reviewed` |
| P7 | Art. 10: pojazd z układem pomiarowo-rozliczeniowym, zapłata na warunkach umowy kierowcy ze sprzedawcą | `ustawa-artykuly.md:38` | `prawo-pl.md` §2 albo `metrologia.md` §6 | F | `PL-EMOB art. 10` |
| P8 | Art. 3b–3c: przetarg na stacje OSD, konsultacje URE co 5 lat | `ustawa-artykuly.md:32` | `prawo-pl.md` §4 | F | `PL-EMOB art. 3b`, `art. 3c` |
| P9 | Art. 2 pkt 5 („ładowanie”, także motorowery i rowery) i pkt 17 (punkt ładowania obejmuje miejsce wymiany akumulatora) | `ustawa-artykuly.md:18, 21` | `prawo-pl.md` §1 | F | `PL-EMOB art. 2` |
| P10 | Przepisy przejściowe i daty: art. 86 (art. 42 i 69 od 2019-01-01; art. 3 ust. 1 pkt 8 od 2018-09-01), art. 74, 79, 60 (historyczne), obwieszczenie (zmiany Dz.U. 2024 poz. 1853 i 1881) | `ustawa-artykuly.md:77-86`; `SKILL.md:83-86` | `prawo-pl.md`, nowa krótka sekcja | F | `PL-EMOB art. 86` i obwieszczenie |
| P11 | Porównanie definicji ustawy i AFIR: ogólnodostępna a publicly accessible, stacja z oprogramowaniem a instalacja fizyczna, brak pojęcia MSP w ustawie, „usługa ładowania” | `pe/dom-ev-regulations-pl/references/afir-relacja.md:14-22` | `prawo-pl.md` §9 (tabela ma dziś tylko progi mocy i podmiot) | F | `PL-EMOB art. 2`, `AFIR art. 2` |
| P12 | EIPA: błędny lub brakujący numer EIPA we wniosku o badanie oznacza brak stacji na mapie; układ współrzędnych (ustawa: państwowy system odniesień, OCPI: lat/lon) | `SKILL.md:54-57` | `prawo-pl.md` §7 albo ev-cpms-architect | F | `PL-EMOB art. 42` oraz `EIPA-OPIS` / `EIPA-API` (pack-ev cytuje stronę główną eipa.udt.gov.pl; trzeba sprawdzić w dokumentach z rejestru) |
| P13 | „Czego ustawa nie reguluje” i lista pytań otwartych: czy UDT jest IDRO, kto egzekwuje AFIR w PL, czy firmware to „modernizacja” w rozumieniu art. 16, retencja danych sesji | `afir-relacja.md:44-51`; `ustawa-artykuly.md:88-94` | `prawo-pl.md` §10 („Czego nie opracowano”) | R | brak faktów; tylko lista luk |
| P14 | Tabela „co to znaczy dla CPMS”: kolejka ponowień do EIPA, alarm po godzinie, model danych (numer EIPA, data badania) | `SKILL.md:98-107` | `CE/SKILL.md`, Procedura i Wniosek | R | brak faktów |

Nakładki:
- Role operatora i dostawcy (art. 2, 3, 4, 6, 7, 8) są w `prawo-pl.md:1-55`.
- OSD (art. 3a) jest w `prawo-pl.md:57-61`.
- UDT (art. 15–16) jest w `prawo-pl.md:81-96`.
- EIPA (art. 41b, 42 ust. 5–6, 4a) jest w `prawo-pl.md:98-110`.
- Kary główne i limit 15 % są w `prawo-pl.md:112-125`.
- „Godzina w ustawie a minuta w AFIR” jest w `prawo-pl.md:127-136`.
- Art. 85a jest w `prawo-pl.md:41`.

## 3. dom-ev-regulations-us → ev-compliance-expert (nowy `references/usa.md`)

ev-intelligence nie ma o USA nic, więc wszystkie pozycje to luki. Dwa źródła mają charakter oficjalny i można je zarejestrować:
- **eCFR 23 CFR part 680**, który wydaje FHWA (regulator federalny);
- **NIST Handbook 44, wydanie 2026, sekcja 3.40**: NIST jest agencją federalną, a HB44 to kod wzorcowy, który wiąże dopiero po przyjęciu przez stan.

**Decyzja właściciela:** czy rozszerzyć zakres na USA, bo taksonomia D12.06 dziś USA nie wymienia.

| # | luka | źródło pack-ev | cel | klasa | źródło oficjalne / id |
|---|---|---|---|---|---|
| U1 | § 680.100–680.104: zakres (projekty NEVI i Title 23) i definicje (charging network provider a charging station operator, AFC, DCFC, Plug and Charge, power sharing, cryptographic agility) | `pe/dom-ev-regulations-us/references/nevi-680.md:15-23`; `SKILL.md:19-22` | `CE/references/usa.md` | F | eCFR 23 CFR 680. **Brak id** (nowy `sources/us-prawo.yaml`) |
| U2 | § 680.106(b)–(e): 4 porty, CCS1 i J1772 na stałe, CHAdeMO tylko z funduszy FY2022, 250–920 V, ≥ 150 kW na port, ≥ 6 kW AC L2, dostępność 24/7 | `SKILL.md:31-35`; `nevi-680.md:28-32` | `usa.md` | F | 23 CFR 680. Brak id |
| U3 | § 680.106(f): płatności (karta zbliżeniowa + telefon bezpłatny lub SMS, bez członkostwa, bez ograniczania mocy zależnie od metody płatności) | `SKILL.md:36`; `nevi-680.md:33` | `usa.md`, odesłanie do ev-billing-tariff-expert | F | 23 CFR 680. Brak id |
| U4 | § 680.106(g), (i)–(m): NRTL i ENERGY STAR („must”), UL („should”), utrzymanie 5 lat, EVITP, ADA i wielojęzyczność, minimalizacja danych i PCI DSS („should”), przeznaczenie przychodów | `SKILL.md:37-41`; `nevi-680.md:34-40` | `usa.md` | F | 23 CFR 680. Brak id |
| U5 | § 680.106(h) i § 680.114: strategia cyber (lista tematów „may”), bezpieczna łączność, zdalne aktualizacje, działanie po utracie sieci (e), jedna identyfikacja w wielu sieciach (c), komunikacja z zakładem energetycznym (d) | `SKILL.md:38, 42-44`; `nevi-680.md:55-59`; `regulacje-cyber.md:49-59` | `usa.md`; w PKI tylko odesłanie | F | 23 CFR 680. Brak id |
| U6 | § 680.108: ISO 15118-3, sprzęt zdolny do -2 i -20, OCPP 1.6J lub nowszy, OCPP 2.0.1, OCPI 2.2.1, zmiana dostawcy sieci bez zmiany sprzętu. Terminy 2024-02-28 już minęły | `SKILL.md:46-56`; `nevi-680.md:42-45` | `usa.md`; odesłanie z PKI i ev-ocpp-expert | F | 23 CFR 680. Brak id. ISO 15118 jest F-N |
| U7 | § 680.112: dane kwartalne (8 pozycji), roczne do 1 marca, jednorazowe (AFC), te same identyfikatory co w API | `SKILL.md:69-78`; `nevi-680.md:47-53` | `usa.md`, odesłanie do ev-cpms-architect | F | 23 CFR 680. Brak id |
| U8 | § 680.116(a): cena w $/kWh przed sesją, stała w trakcie sesji, konwersja na $/kWh | `SKILL.md:80-82`; `nevi-680.md:64` | `usa.md` / ev-billing-tariff-expert | F | 23 CFR 680. Brak id |
| U9 | **§ 680.116(b): uptime > 97 %**, wzór µ z 525 600 min, T_outage, T_excluded (wyłączenia i dowód), definicja portu „up”, okno 12 miesięcy liczone co miesiąc | `SKILL.md:58-67, 114-116`; `nevi-680.md:65` | `usa.md`, odesłanie do ev-charging-operations-expert (KPI) | F | 23 CFR 680. Brak id |
| U10 | § 680.116(c): bezpłatne API (pola, status i cena według OCPI 2.2.1) | `SKILL.md:75`; `nevi-680.md:66` | `usa.md` / ev-cpms-architect | F | 23 CFR 680. Brak id. `OCPI221` jest w rejestrze |
| U11 | § 680.118: inne wymogi federalne (2 CFR 200, Buy America, Davis-Bacon, ADA, Title VI, URA, NEPA) | `nevi-680.md:68-71` | `usa.md` | F | 23 CFR 680. Brak id |
| U12 | HB44 3.40: status (od 2023 „permanent”), zakres A.1, wyjątki A.2, A.3 i 5.55, NTEP z NRTL (A.4) | `pe/dom-ev-regulations-us/references/hb44-3-40.md:13-23` | `usa.md` oraz `CE/references/metrologia.md` (sekcja „USA”) | F | NIST HB44 (2026) §3.40. Brak id |
| U13 | HB44 S.1–S.8: wskazania ≥ 15 s, rozdzielczość AC ≤ 0,0001 kWh i DC ≤ 0,001 kWh, cena liczona z ≤ 0,01 kWh, zmiana ceny (S.2.4.3), paragon (S.2.6), utrata zasilania (S.2.3), audit trail kat. 1–3 (S.3.3), pamięć 3 lata (S.3.4), wyłączenie po 2 min (S.2.8), MMQ AC 0,5 kWh i DC 1 kWh (S.8), oznaczenia | `hb44-3-40.md:25-53`; `SKILL.md:86-99` | `metrologia.md` / `usa.md` | F | HB44 §3.40. Brak id |
| U14 | HB44 N i T: punkty testowe, tolerancje 1 % i 2 %, DC Class 5 (5 % do 01.01.2034), odroczenia do 01.01.2028 | `hb44-3-40.md:55-67` | `metrologia.md` | F | HB44 §3.40. Brak id |
| U15 | HB44 UR.1–UR.3 (kabel > 25 ft, nazwa i telefon odpowiedzialnego, cena na urządzeniu) | `hb44-3-40.md:69-74` | `usa.md` | F | HB44 §3.40. Brak id |
| U16 | SAE J1772 i J3400 (NACS), UL 2594, 2202, 2231 | `pe/dom-ev-regulations-us/references/normy-i-stany.md:13-31` | wpis do `sources/niedostepne.yaml` (płatne) | F-N | normy płatne; dziś nie są wpisane nawet do niedostępnych. Fakt „część 680 nie wymienia J3400” sprawdza się w 23 CFR 680 |
| U17 | Prawo stanowe (Kalifornia: CDFA DMS, CEC; przyjęcie HB44 przez stany) | `normy-i-stany.md:33-44` | `niedostepne.yaml` (`niezarejestrowane`) | P | pack-ev nie podaje żadnego faktu, tylko „może” |
| U18 | „Co to znaczy dla CPMS” (identyfikatory, dowody wyłączeń z uptime, „Available” nie dowodzi „up”), „kto co spełnia” (założenie), lista pytań | `SKILL.md:101-111, 124-131`; `hb44-3-40.md:76-82`; `normy-i-stany.md:46-51` | `usa.md` jako Wniosek i Pułapki | R | bez faktów |

## 4. dom-ev-metering-calibration → ev-compliance-expert (`references/metrologia.md`)

ev-intelligence ma:
- MID w tekście pierwotnym (art. 1–3, MI-003);
- MessEG § 33;
- notę OCA o podpisanych wartościach.

ev-intelligence nie ma:
- zmiany MID 2026/706 (MI-011);
- struktury OCMF, bo OCMF jest w `niedostepne.yaml` jako `niezarejestrowana`.

pack-ev pobrał OCMF z repozytorium właściciela standardu (S.A.F.E. e.V., github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format). Według CLAUDE.md to „dokument właściciela standardu”, więc można go zarejestrować. Licencję i SHA-256 trzeba sprawdzić.

| # | luka | źródło pack-ev | cel | klasa | źródło oficjalne / id |
|---|---|---|---|---|---|
| M1 | **MID 2026/706, nowy zał. Va (MI-011, systemy pomiarowe EVSE AC i DC):** klasy A, B, C (2 %, 1 %, 0,5 %), MMQ (AC ≤ 0,1 kWh, DC ≤ 1 kWh), BMPE w trzech zakresach prądu, zakresy AC, kabel nierozłączny albo wymienny, zakłócenia, przerwana transakcja, ocena zgodności (B+F, B+D, G, H1) | `pe/dom-ev-metering-calibration/references/mid-mi-011.md:9-14, 31-46`; `SKILL.md:28`; `pe/dom-ev-regulations-eu/SKILL.md:73` | `metrologia.md`, nowa sekcja „MI-011” | F | dyrektywa (UE) 2026/706, EUR-Lex. **Brak id** (dopisać do `eu-inne.yaml`) |
| M2 | 2026/706, art. 2–4: transpozycja do 10.04.2028, stosowanie od 10.10.2028, przejście do 10.04.2030, certyfikaty najpóźniej do 10.04.2038, jednostki notyfikowane. **Niespójność wewnątrz pack-ev:** „MID z 08.04.2026” w `mid-mi-011.md:23` i `regulations-eu/SKILL.md:73`, ale „2026-04-09” w `dom-ev-knowledge-base/references/rejestr-standardow.json` | `mid-mi-011.md:18-26` | `metrologia.md` | F | 2026/706. Brak id. Datę sprawdzić w art. 2 |
| M3 | MID zał. I: pkt 10.2 i 10.6 w brzmieniu 2026/706 (wynik bez narzędzi, także na urządzeniu konsumenta, powiązany z przyrządem, dowód ingerencji, „transakcja zawarta”). Z tekstu bazowego: 7.6, 8.1–8.4, 11.1–11.2 | `mid-mi-011.md:48-56`; `regulations-eu/SKILL.md:73` | `metrologia.md` §1 | F | Część bazowa: **`MID Annex I`** (jest). Zmiany: 2026/706 (brak id) |
| M4 | 2026/706 zmienia zał. V (MI-003): liczniki prądu stałego (zakresy napięć, rozruch, brak rejestracji bez prądu) | `mid-mi-011.md:13-15` | `metrologia.md:38-40` (**do korekty**, zob. konflikt K1) | F | 2026/706. Brak id |
| M5 | OCMF, układ rekordu i payload: `OCMF\|payload\|podpis`, pola PG, MS, IS, IT, RD, GI, GS, GV, MV, MM, MF, CF, CT, CI, dziedziczenie pól w RD, TX (B, C, X, E, L, R, A, P, S, T), ST (12 stanów), EF, TM (format i stany S, I, U, R), RV jako niezmieniany JSON Number, RI (OBIS) z RU, RT | `pe/dom-ev-metering-calibration/references/ocmf-pola.md:1-58`; `SKILL.md:36-51` | `metrologia.md`, nowa sekcja „OCMF” (D10.03) | F | specyfikacja OCMF (S.A.F.E. e.V., GitHub). **Dziś w `niedostepne.yaml` jako `niezarejestrowana`**; zarejestrować i usunąć wpis |
| M6 | OCMF, podpis i klucz: SA (domyślnie ECDSA-secp256r1-SHA256 i lista krzywych), SE (hex lub base64), SM, SD; klucz publiczny poza protokołem, powiązany z numerem seryjnym; rozszerzenia producenta U–Z, litery A–F zarezerwowane; OBIS 1.4 (Mains, Device, Transaction) | `ocmf-pola.md:60-78` | `metrologia.md` | F | OCMF. Lista krzywych pokrywa się z `OCA-AN-SMV §4.2.1`, który jest w rejestrze |
| M7 | Zalecane przez OCMF klucze OCPP 1.6: `StopTransactionSignatureFormat` (MR, SR), `StopTransactionSignatureContexts`, `MeterValuesSignatureContexts` | `SKILL.md:74`; `ocmf-pola.md:77-78` | `metrologia.md` §4 i tabela rozbieżności (zob. K3) | F | OCMF (zalecenie S.A.F.E., nie OCA) |
| M8 | OCPP 2.0.1 `SignedMeterValueType`: wymagalność pól i maksymalne długości (`signedMeterData` 2500, `encodingMethod` 50, `publicKey` 2500) | `SKILL.md:75` | `metrologia.md:75-78` | F | `201-P3` (jest). pack-ev sprawdzał w bibliotece mobilityhouse/ocpp, czyli źródle wtórnym |
| M9 | Taryfa za czas: zał. Va reguluje tylko energię, opłat za minuty nie (fakt negatywny). Czas z licznika nadaje się do taryfy czasowej tylko przy stanie TM S albo R. Zmiana taryfy oznaczana TX=T | `SKILL.md:81-90` | `metrologia.md` + Wniosek | F | 2026/706 (brak id) i OCMF |
| M10 | Straty kabla: zał. Va pkt 4 (kabel plombowany albo wymienny), OCMF LC (LR, LU, LN, LI) i CL (zerowane przy TX=B); software nie dolicza strat | `SKILL.md:92-97`; `ocmf-pola.md:29-31` | `metrologia.md` | F | 2026/706 i OCMF. Brak id |
| M11 | `meterStart` i `meterStop` w OCPP 1.6 są w Wh i mogą pochodzić z innego rejestru niż podpisany; różnicę ocenia się względem klasy dokładności i MMQ, a nie względem zera | `SKILL.md:110-113, 146` | `metrologia.md` (Pułapki) | F + R | `16` (StopTransaction) i `S16`, oba w rejestrze. Ocena rozjazdu to Wniosek |
| M12 | Legalizacja jako zdarzenie w rejestrze assetów (model zdarzeń: commissioned, verified, replaced, cable, seal, firmware) | `SKILL.md:99-108`; `pe/dom-ev-metering-calibration/references/rejestr-i-sprawy-otwarte.md:5-18` | `CE/SKILL.md` (Procedura) albo ev-charging-operations-expert | R | „propozycja projektowa, nie przepis” |
| M13 | Pułapki przetwarzania: Decimal, zachowanie surowego zapisu, osobna kopia robocza, WORM (wprost oznaczone [założenie]) | `SKILL.md:145-155`; `rejestr-i-sprawy-otwarte.md:46-49` | `metrologia.md` (Pułapki) | R | bez faktów, poza „RV się nie zmienia” z M5 |
| M14 | Eichrecht: Transparenzsoftware, PTB, rejestr kluczy | `SKILL.md:29, 67-68` | `niedostepne.yaml` (MessEV i PTB już są) | P | niedostępne |

Nakładki:
- MID art. 3 (to państwo decyduje o obowiązku liczników) jest w `metrologia.md:21-26`.
- MessEG § 33 jest w `metrologia.md:42-51`.
- Transport podpisanych wartości według OCA (1.6 i 2.x, `SampledDataSignReadings`) jest w `metrologia.md:53-92`.
- OCPI `SignedData` (`encoding_method_version`, `plain_data`) jest w `ei/skills/ev-billing-tariff-expert/references/cdr-i-wycena.md:58-60`.
- Enum 1.6 `format` (Raw, SignedData) jest w `ei/skills/ev-ocpp-expert/references/komunikaty-16.md:90`.
- HB44 w tym skillu dubluje U13 i U14, więc nie liczę go osobno.

## 5. dom-ev-security → ev-iso15118-pki-expert (D11) i ev-compliance-expert (NIS2, CRA, NEVI)

Część prawna dubluje E1–E10 i U5, więc nie liczę jej drugi raz. Reszta to w większości wiedza praktyczna bez źródła, którą pack-ev sam oznacza jako „wiedza ogólna branży, [do weryfikacji]”. W ev-intelligence D11.03 (urządzenia i sieć) oraz D11.04 (backend i API) nie mają żadnej treści.

| # | luka | źródło pack-ev | cel | klasa | źródło oficjalne / id |
|---|---|---|---|---|---|
| S1 | Model zagrożeń (11 zagrożeń: fałszywa stacja, fałszywy CSMS, przejęcie sesji, klon RFID, nadużycie zdalnego startu, manipulacja odczytem, firmware, komendy masowe, token OCPI, CDR, skimming, dostęp serwisowy) | `pe/dom-ev-security/SKILL.md:37-49`; `pe/dom-ev-security/references/model-zagrozen.md:20-35` | nie da się przenieść jako faktów. Kontrole z kotwicą mają już źródło w PKI: A00 (profile, CN i O, unikalność), L01 (podpis firmware), M05 (root CSMS) | P | brak. Kotwice tylko w `201-P2` (A00, L01) |
| S2 | Aktywa i granice zaufania; ocena ryzyka osobno dla pojedynczej stacji i dla floty | `SKILL.md:28-33`; `model-zagrozen.md:6-15, 48-52` | `PKI/SKILL.md` (Procedura) | R | bez faktów. Zatwierdzenie środków przez zarząd to fakt z NIS2 art. 20 (E2) |
| S3 | Migracja profili OCPP falami (inwentarz, unikalne hasła, TLS obok `ws://`, kohorty, wyłączenie `ws://` przy zerowym ruchu) | `SKILL.md:51-61`; `kontrole-i-migracja.md:5-17` | `PKI/references/bezpieczenstwo-ocpp.md` §2, jako Wniosek przy A00.FR.004–005 | R | Kotwice: `201-P2 A00.FR.004`, `A00.FR.005` (są w PKI), `SetNetworkProfile.securityProfile` (`201-P2 B09` / `201-P3`) |
| S4 | Zmiana hasła stacji: pack-ev twierdzi, że „CSMS przyjmuje stare i nowe hasło przez okno przejściowe”; do tego rotacja certyfikatów i decommissioning | `kontrole-i-migracja.md:19-24` | `bezpieczenstwo-ocpp.md` §4 | F (A01) + P (okno przejściowe) | `201-P2 A01` (przypadek „Update Charging Station Password”; dziś PKI go nie opisuje). Twierdzenie o oknie trzeba porównać z A01 |
| S5 | Separacja uprawnień w CSMS, próg komend masowych, zasada dwóch osób, tryb zamrożenia, MFA | `SKILL.md:63-73`; `kontrole-i-migracja.md:37-45` | nie da się przenieść. Ogólny fakt (kontrola dostępu i MFA) jest w NIS2 art. 21 ust. 2 (E2) | P | brak |
| S6 | Reguły detekcji (duplikat `chargePointId`, nowy numer seryjny przy znanym EVSE, sesje bez energii, token w dwóch krajach) | `SKILL.md:75-85`; `kontrole-i-migracja.md:47-60` | nie da się przenieść. Typy `SecurityEventNotification` są już w ev-charging-operations-expert | P | brak |
| S7 | Firmware: fale 5 % i 25 %, rollback, ochrona przed cofnięciem wersji, HSM, potwierdzenie wersji w `BootNotification` | `kontrole-i-migracja.md:26-35` | nie da się przenieść. L01 jest w PKI §8 | P | brak (L01 to nakładka) |
| S8 | OCPI: osobny token na partnera, rotacja `PUT credentials`, cykl miesięczny, procedura po wycieku | `kontrole-i-migracja.md:62-67` | ev-ocpi-roaming-expert (poza grupą) | P (+F dla `PUT credentials`) | `OCPI230` (moduł credentials). „Cykl miesięczny” nie ma źródła |
| S9 | Skutek masowy dla sieci energetycznej (wyłączenie, skok mocy, efekt odbicia, fale 2–5 %, losowe opóźnienia) | `model-zagrozen.md:37-46` | nie da się przenieść. Zachowanie offline z `TxDefaultProfile` jest w ev-energy-smart-charging-expert | P | brak |
| S10 | Proces PSIRT i SBOM (inwentarz, skan w CI, wymagania wobec dostawców) | `kontrole-i-migracja.md:69-74` | `cyber-i-dane-ue.md`, jako Wniosek przy E8 | R | kotwica: CRA Aneks I cz. II (E8) |
| S11 | Runbook incydentu (role, pierwsze 60 minut, izolacja bez kasowania logów, komunikacja z OSD i partnerami, przywracanie falami, przegląd po incydencie) | `pe/dom-ev-security/references/incydent-w-sieci.md:6-66` | `PKI/SKILL.md` albo `CE`, procedura z kotwicami NIS2 art. 23 i CRA art. 14 | R | kotwice: E3, E9; `201-P2 N01` (GetLog SecurityLog, już w ev-charging-operations-expert) |
| S12 | Tabela „kto czego pilnuje” (CPO, dostawca CSMS, producent × NIS2, CRA, NEVI, RED) | `regulacje-cyber.md:66-71` | `cyber-i-dane-ue.md` | R | oznaczona [założenie] |
| S13 | RODO (zgłoszenie naruszenia), ETSI EN 303 645, ISO 27001, IEC 62443 | `incydent-w-sieci.md:44-45`; `regulacje-cyber.md:73-75` | `niedostepne.yaml`: dopisać RODO (`niezarejestrowane`) i ETSI EN 303 645 (dostępność do sprawdzenia). IEC 62443 i ISO 27001 już są | F | RODO (rozporządzenie (UE) 2016/679): brak id |

Nakładki:
- Profile 1–3, TLS, Basic Auth, CN i O, unieważnianie i podpis firmware są w `PKI/references/bezpieczenstwo-ocpp.md`.
- `SecurityEventNotification` (lista zdarzeń) jest w `ei/skills/ev-charging-operations-expert/references/alarmy.md:37-39`.
- `GetLog` `SecurityLog` jest w `ei/skills/ev-charging-operations-expert/references/dzialania-zdalne.md:44-45`.
- Profil 1 tylko w sieci zaufanej jest w `bezpieczenstwo-ocpp.md:30`. Jest to zgodne z `pe/dom-ev-security/SKILL.md:54-60`.

## 6. dom-ev-iso15118 → ev-iso15118-pki-expert

Większość treści pochodzi z implementacji josev (SwitchEV/iso15118, Apache 2.0, „ranga W”). Według CLAUDE.md to źródło wtórne: wskazówka, nie dowód. Normy ISO 15118 i DIN 70121 są w `niedostepne.yaml` (płatne). ev-intelligence świadomie ich nie opisuje (`PKI/SKILL.md:16-20`, `iso15118-w-ocpp.md:20-23`), więc rozmowy pojazd–stacja nie można przenieść. Można przenieść tylko to, co dotyczy OCPP: schematy i Device Model, sprawdzone w `201-P3` i `201-APP`.

| # | luka | źródło pack-ev | cel | klasa | źródło oficjalne / id |
|---|---|---|---|---|---|
| I1 | Stos: CP 5 %, SLAC (PLC), SDP (UDP 15118, bajty Security i Transport), V2GTP (typy ładunku), EXI, SupportedAppProtocol (namespace, Priority, kody odpowiedzi) | `pe/dom-ev-iso15118/SKILL.md:26-62`; `pe/dom-ev-iso15118/references/sesja-i-timeouty.md:110-118` | **nie przenosić** (PKI mówi „wymaga normy”) | F-N | ISO 15118-2, -3, -20, DIN 70121 (`niedostepne.yaml`) |
| I2 | Porównanie DIN 70121, ISO 15118-2 i -20 (energia, autoryzacja, certyfikaty, TLS, pętle, harmonogram) | `SKILL.md:33-47` | nie przenosić | F-N | jw. |
| I3 | Kolejność komunikatów DC i AC dla DIN, -2 i -20; identyfikatory usług -20; tryby energii; DCEVErrorCode; stany izolacji | `SKILL.md:64-86`; `sesja-i-timeouty.md:65-107` | nie przenosić | F-N | jw. |
| I4 | Timeouty (wartości z josev, „nie z normy”) | `SKILL.md:88-91`; `sesja-i-timeouty.md:15-51` | nie przenosić. Wyjątek: ChargeParameterDiscovery 2 s → 60 s, już w `iso15118-w-ocpp.md:55-56` (`201-P2 M §1`) | F-N | jw. |
| I5 | Pola `CertificateInstallationReq` i `Res` (-2 i -20), szyfrowany klucz kontraktu (DH), `RetryCounter`, brak `CertificateUpdate` w -20 | `pe/dom-ev-iso15118/references/pki-i-ocpp.md:43-68` | nie przenosić | F-N | jw. |
| I6 | Drzewa PKI z `create_certs.sh` (ważności testowe 60, 90, 730, 3650 dni; `pathLen 0`, `CA=false`, kolejność łańcucha SECC) | `SKILL.md:98-108`; `pki-i-ocpp.md:15-40` | nie przenosić. 4 PKI według OCPP są już w `iso15118-w-ocpp.md:25-33` | P | skrypt testowy. Polityki CharIN, Hubject i Gireve są niezarejestrowane |
| I7 | OCPP 2.0.1, pola i limity: `Authorize.certificate` (≤ 5500), `iso15118CertificateHashData` (≤ 4; `hashAlgorithm` SHA256, 384, 512; `responderURL`), `Get15118EVCertificate` (`iso15118SchemaVersion`, `exiRequest` ≤ 5600, `exiResponse`), `CertificateSigned.certificateChain` ≤ 10000, `SignCertificate.certificateType`, `GetCertificateStatus.ocspRequestData`, `TriggerMessage` z Sign*Certificate | `SKILL.md:116-122`; `pki-i-ocpp.md:70-91` | `PKI/references/iso15118-w-ocpp.md` §3–5 | F | **`201-P3`** (jest) i `201-P2` M01–M06 |
| I8 | Pełny `AuthorizeCertificateStatusEnum`: pack-ev wymienia też `SignatureError` i `NoCertificateAvailable`, których brak w tabeli PKI | `pki-i-ocpp.md:84` | `iso15118-w-ocpp.md:75-81` | F | `201-P3`, `201-P2 C07` |
| I9 | Zmienne komponentu `ISO15118Ctrlr` (włączenie PnC, instalacja kontraktu, walidacja centralna i offline, OCSP); pack-ev sam oznacza nazwy jako [do weryfikacji] | `pki-i-ocpp.md:92-94` | `iso15118-w-ocpp.md` §6 | F | `201-APP`, `201-CSV` (są) |
| I10 | `NotifyEVChargingNeeds`: wartości trybu energii i `departureTime` | `pki-i-ocpp.md:90` | ev-energy-smart-charging-expert (sprawdzić pokrycie) albo PKI §4 | F | `201-P3` |
| I11 | Czy `TransactionEvent` niesie wynegocjowaną wersję ISO 15118 (pack-ev: [do weryfikacji]) | `sesja-i-timeouty.md:123-124` | `iso15118-w-ocpp.md` (Pułapki) | F | `201-P3` (schemat TransactionEvent), `201-APP` |
| I12 | Typowe awarie krok po kroku (SDP a link-local i Docker, `unable to get local issuer`, RTC, OCSP timeout, instalacja dłuższa niż 5 s) | `pki-i-ocpp.md:131-143` | nie przenosić jako faktów | P | josev README / praktyka |
| I13 | Checklista logowania (wersja protokołu na sesję, czas `Get15118EVCertificate`), nie logować EXI z materiałem kluczowym, monitorowanie ważności SECC i rootów | `SKILL.md:157-162`; `pki-i-ocpp.md:51-52, 146-152` | `PKI/SKILL.md` (Pułapki, Wniosek) | R | kotwice: M06 (OCSP raz w tygodniu), A02/A03 |
| I14 | Fallback do samego PWM po `sdpRetryCycles`; EIM a PnC (AuthEnum `ExternalPayment`/`Contract`, `EIM`/`PnC`); brak automatycznego powrotu do EIM w tej samej sesji | `pki-i-ocpp.md:120-128, 146-150` | nie przenosić (C08 w PKI to nakładka) | F-N | ISO 15118 (niedostępna) |

Nakładki:
- Cztery PKI według OCPP i tabela typów certyfikatów są w `iso15118-w-ocpp.md:25-45`.
- M01/M02 (`Get15118EVCertificate`, Install i Update), M03–M06 i OCSP raz w tygodniu są w `iso15118-w-ocpp.md:47-66`.
- C07 (online i offline, `CentralContractValidationAllowed`) i C08 są w `iso15118-w-ocpp.md:68-89`.
- Plug & Charge w 1.6 przez `DataTransfer` jest w `iso15118-w-ocpp.md:91-109`. Tu ev-intelligence jest **lepszy**, bo pack-ev tego nie sprawdził.
- AFIR Aneks II (daty ISO 15118) jest w `iso15118-w-ocpp.md:118-122`.
- OCPI `ISO_15118_*_PLUG_AND_CHARGE` jest w `iso15118-w-ocpp.md:118-119`.

---

## 7. Podsumowanie liczbowe

| Skill pack-ev | F | w tym F-N | P | R | razem |
|---|---|---|---|---|---|
| dom-ev-regulations-eu | 21 | 0 (EN 18031 w E15 częściowo) | 0 | 2 | 23 |
| dom-ev-regulations-pl | 12 | 0 | 0 | 2 | 14 |
| dom-ev-regulations-us | 16 | 1 (U16) | 1 | 1 | 18 |
| dom-ev-metering-calibration | 11 | 0 | 1 | 2 | 14 |
| dom-ev-security | 1 | 0 | 7 | 5 | 13 (S4 i S8 to F+P, liczone jako P) |
| dom-ev-iso15118 | 11 | 6 (I1–I5, I14) | 2 | 1 | 14 |
| **razem** | **72** | **7** | **11** | **13** | **96** |

Liczba F w podziale na dostępność źródła:
- **F ze źródłem już w rejestrze** (tanie przeniesienie): 26, plus fragment A01 w S4.
  - AFIR: E16–E21;
  - PL-EMOB, EIPA-OPIS i EIPA-API: P1–P12;
  - MID (część bazowa M3);
  - `16`, `201-P3`, `201-P2`, `201-APP`: M8, M11, I7–I11.
- **F, które wymagają najpierw rejestracji źródła:** 39. Akty do zarejestrowania:
  - NIS2, CRA, Data Act, EPBD, RED III, 2022/30, 2026/339, 2003/361/WE: E1–E15, E23;
  - 23 CFR 680, HB44: U1–U15;
  - 2026/706, OCMF: M1–M10;
  - RODO: S13.
- **F-N (nie do przeniesienia):** 7.

## 8. Daty w pack-ev, które mogą być nieaktualne

pack-ev liczy terminy od „dziś = 2026-10-20”: `pe/dom-ev-regulations-eu/SKILL.md:20`, `afir.md:89` („za 2 miesiące od dziś”), `pe/dom-ev-regulations-us/SKILL.md:54`. Te sformułowania trzeba przepisać na daty bezwzględne.

| Data | Co | Gdzie w pack-ev | Ryzyko |
|---|---|---|---|
| 11.09.2026 | CRA art. 14 (zgłaszanie) | `regulations-eu/SKILL.md:40`; `regulacje-cyber.md:42` | **już obowiązuje**; ev-intelligence nie ma o tym nic |
| 11.06.2026 | CRA rozdz. IV | `akty…md:47` | minęła |
| 12.09.2026 | Data Act art. 3 ust. 1 | `regulations-eu/SKILL.md:41, 85` | minęła |
| 29.05.2026 | transpozycja EPBD | `akty…md:83` | minęła; potrzebne prawo krajowe (PL niesprawdzone) |
| 31.12.2026 | AFIR art. 20 ust. 5 (wspólny europejski punkt dostępu) i art. 24 ust. 2 (przegląd) | `afir.md:62-63, 89, 118` | **za 6 tygodni**; po przeglądzie możliwe zmiany AFIR |
| 01.01.2027 | AFIR art. 5 ust. 1 akapit 3 (terminal dla starszych punktów ≥ 50 kW na TEN-T); Aneks II pkt 2.1.2–2.1.3 (ISO 15118-20) | `regulations-eu/SKILL.md:30, 36` | najbliższy termin dla CPO |
| 12.01.2027 | Data Act: zmiana dostawcy chmury bez opłat | `regulations-eu/SKILL.md:42` | wkrótce |
| 11.12.2027 | CRA w całości; uchylenie RED DA 2022/30 (rozporządzenie 2026/339) | `regulations-eu/SKILL.md:38-39, 72` | 2026/339 nie jest w rejestrze; datę sprawdzić w akcie |
| 08.04.2026 albo 09.04.2026 | data odniesienia MID w 2026/706 | `mid-mi-011.md:23` a `rejestr-standardow.json` | niespójność wewnątrz pack-ev |
| 10.04.2028, 10.10.2028, 10.04.2030, 10.04.2038 | terminy 2026/706 | `mid-mi-011.md:18-26` | do sprawdzenia w art. 2–4 |
| 2024-02-28 | NEVI § 680.108 (ISO 15118-2 i PnC, OCPP 2.0.1, OCPI 2.2.1) | `regulations-us/SKILL.md:49-56` | minęła. eCFR sprawdzono 2026-10-20; przed rejestracją sprawdzić aktualny eCFR i Federal Register pod kątem zmian w części 680 i programie NEVI. Nie zakładam, co się zmieniło |
| HB44 „wydanie 2026” | NIST publikuje kolejne wydania | `regulations-us/SKILL.md:14` | przy rejestracji sprawdzić, czy nie ma nowszego wydania |
| 2028-01-01 / 2034-01-01 | HB44: odroczenia dla DC sprzed 2025, Class 5 | `hb44-3-40.md:42, 64` | do sprawdzenia w wydaniu, które zostanie zarejestrowane |
| stan prawny 26.08.2026 | tekst jednolity ustawy o elektromobilności | `regulations-pl/SKILL.md:14` | ev-intelligence sprawdził API ELI 2026-11-07 i nie znalazł dalszych zmian (`pl-prawo.yaml:15`) |

## 9. Skrypty

| Katalog | Co robi | Odpowiednik w ev-intelligence | Zależności | Testy | Docelowy skill |
|---|---|---|---|---|---|
| `pe/dom-ev-metering-calibration/scripts/ocmf_check.py` (258 linii) | Walidator **struktury** rekordu OCMF: format `OCMF\|payload\|podpis`, pola obowiązkowe, wartości z tabel (TX, RU, RT, ST, stan TM), paginacja PG, kodowanie SD (hex/base64), odczyt B…E, monotoniczność, ST i EF, energia rejestru (koniec − początek) na `Decimal`, dziedziczenie pól, `--json`. **Nie weryfikuje podpisu ECDSA** (zawsze `signature-not-verified`). Kody wyjścia 0, 1, 2 | **brak**. `ei/skills/ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py` sprawdza ramki OCPP, nie OCMF. `tools/ev_kb.py:326` zna OCMF tylko jako hasło źródła niedostępnego | tylko biblioteka standardowa (argparse, base64, binascii, datetime, json, re, decimal, pathlib); sieć: brak | `pe/../tests/test_ocmf_check.py` (193 linie, 55 asercji `check()`, własny `main()`, nie unittest). `ROOT` szuka `.claude/hooks`, a `SCRIPT` to `.claude/skills/…`, czyli układ instalacji tf | `ev-compliance-expert/scripts/` (D10.03 podpisane wartości) |

Przeniesienie `ocmf_check.py` wymaga:
1. rejestracji OCMF w `sources/` (dziś wpis w `niedostepne.yaml`), bo reguły walidatora to fakty ze specyfikacji;
2. przepisania testu na `unittest` z `ROOT = Path(__file__).parent.parent`, jak w `ei/tests/test_ocpp_frame_check.py` (do tego `sys.dont_write_bytecode = True`);
3. zmiany ścieżek w docstringu i SKILL (z `.claude/skills/...` na `skills/ev-compliance-expert/scripts/...`);
4. dopisania do `metrologia.md` cytatów `[OCMF §…]` dla tabel TX, ST i TM.

Skrypt jest stdlib i offline, więc spełnia warunki bramki `skill_check.py`, w której unit testy są krokiem bramki.

Pozostałe skille z mojej grupy (eu, pl, us, security, iso15118) **nie mają katalogu `scripts/`**.

Poza grupą, ale istotne dla dat: `pe/dom-ev-knowledge-base/scripts/standards_check.py` z rejestrem `references/rejestr-standardow.json` (daty NIS2, CRA, Data Act, EPBD, RED, MID, NEVI, HB44). ev-intelligence nie ma takiego mechanizmu przeglądu dat. Do decyzji w grupie, która analizuje dom-ev-knowledge-base.

Testy i scenariusze pack-ev dla tych skilli:
- **dom-ev-regulations-eu (5):** `afir-adhoc-terminal-cena`, `afir-dane-nap-api`, `cra-firmware-terminy`, `nis2-cpo-zakres`, `nevi-uptime-poza-zakresem`.
- **dom-ev-regulations-pl (5):** `udt-eipa-przed-startem`, `eipa-dane-terminy`, `afir-platnosc-karta-kara`, `taryfa-ocpi-vat`, `nevi-uptime-usa`.
- **dom-ev-regulations-us (4):** `nevi-uptime-wzor`, `nevi-protokoly-cena`, `hb44-kwh-paragon`, `preautoryzacja-terminal`.
- **dom-ev-metering-calibration (3):** `ocmf-przed-rozliczeniem`, `mi-011-terminy`, `korekta-cdr-kredytowy`.
- **dom-ev-security (4):** `reset-calej-floty-i-profile`, `incydent-nis2-zegar-24-72`, `klon-rfid-i-sesje-bez-energii`, `szczegoly-profilu-3-w-ocpp`.
- **dom-ev-iso15118 (3):** `sap-wybor-protokolu-din`, `certyfikat-kontraktu-przez-ocpp`, `seqno-offline-ocpp`.
- **`tests/ev_exam/regulacje.json` (13 pytań):** m.in. `nis2-terminy-zgloszen`, `cra-art14-terminy`, `nevi-uptime-wzor`, `red-da-2022-30-uchylenie`, `data-act-chmura-i-produkty`, `hb44-rozdzielczosc-ac`.
- `test_kb_ev.py:38` wymaga obszaru `regulations-us`.

Scenariusze NIS2, CRA, NEVI, HB44 i MI-011 to kandydaci do `evals/skill_evals/ev-compliance-expert.json`. Trzeba je dodać dopiero po wpisaniu źródeł; dziś ev-intelligence ma tylko `dev2/ev-compliance-expert.json: nis2-technicznie-od-czego-zaczac` jako granicę.

## 10. Konflikty i rozbieżności

| # | Temat | pack-ev | ev-intelligence | Ocena i rozstrzygnięcie |
|---|---|---|---|---|
| K1 | Pomiar DC w MID | 2026/706 dodaje MI-011 (systemy EVSE AC i DC) oraz liczniki DC w zał. V (`pe/dom-ev-metering-calibration/references/mid-mi-011.md:9-15`) | „Dyrektywa nie mówi wprost o licznikach prądu stałego… stosowanie MI-003 do DC wymaga potwierdzenia w prawie krajowym” (`CE/references/metrologia.md:38-40`); MID zarejestrowany tylko w tekście pierwotnym (`ei/sources/eu-inne.yaml:12`) | **ev-intelligence jest nieaktualny** wobec 2026/706. Rozstrzygnięcie: zarejestrować 2026/706 i przepisać §2 z oboma cytatami (tekst pierwotny a zmiana) |
| K2 | `SignedMeterValueType` w 2.0.1 | „wszystkie cztery pola obowiązkowe” (`pe/dom-ev-metering-calibration/SKILL.md:75`), źródło: biblioteka mobilityhouse | `signingMethod` „pusty, jeśli zawarty w danych”, `publicKey` „pusty albo Base64” (`CE/references/metrologia.md:75-77`, `[OCA-AN-SMV §3.2.1–3.2.2]`) | Prawdopodobnie oba są prawdziwe: pola wymagane w schemacie, ale mogą być pustym ciągiem. Sprawdzić `201-P3` i opisać wymagalność w schemacie razem z dopuszczalną pustą wartością według noty |
| K3 | Klucze konfiguracji podpisanych wartości w 1.6 | `StopTransactionSignatureFormat`, `StopTransactionSignatureContexts`, `MeterValuesSignatureContexts`, czyli zalecenie S.A.F.E. (`SKILL.md:74`; `ocmf-pola.md:77-78`) | `MeterPublicKey[ConnectorID]`, `PublicKeyWithSignedMeterValue`, `SampledDataSignReadings`… według noty OCA (`metrologia.md:79-85`) | Dwa różne zestawy od dwóch właścicieli: OCMF/S.A.F.E. i OCA. Nie jest to sprzeczność, ale wymaga wiersza w tabeli rozbieżności. Pierwszeństwo ma właściciel protokołu (OCA) |
| K4 | Nazwa typu certyfikatu SECC | `certificateType` = `V2GCertificate` (`pe/dom-ev-iso15118/references/pki-i-ocpp.md:85`) | `V2GChargingStationCertificate` (`PKI/references/iso15118-w-ocpp.md:39`, `[201-P2 M §2]`) | Prawdopodobnie inne pola: enum `CertificateSigningUse` w schemacie a nazwa w tabeli tekstu. Sprawdzić w `201-P3` i dopisać do rozbieżności, jeśli tekst i schemat się różnią (wymóg CLAUDE.md) |
| K5 | Plug & Charge w OCPP 1.6 | `vendorId` „[do weryfikacji]”, „dokument nie jest w bazie” (`pki-i-ocpp.md:102-108`; `pe/dom-ev-iso15118/SKILL.md:123-124`) | `vendorId = org.openchargealliance.iso15118pnc`, `messageId`, `ISO15118PnCEnabled` (`iso15118-w-ocpp.md:91-109`, `[OCA-AN-PNC §2.1–2.2]`) | Brak sprzeczności. pack-ev jest przestarzały; zostaje wersja ev-intelligence |
| K6 | Rozporządzenie o wymaganiach technicznych stacji (PL) | „Rozporządzeń wykonawczych nie ma w bazie… [do weryfikacji]” (`pe/dom-ev-regulations-pl/SKILL.md:17-18`; `ustawa-artykuly.md:49`) | opracowane `[PL-R1316]` (`CE/references/prawo-pl.md:62-79`) | ev-intelligence jest lepszy; pack-ev ma lukę |
| K7 | Kara z art. 45 ust. 1 pkt 4 | 20 000, 50 000 i 100 000 zł zależnie od przepisu (`ustawa-artykuly.md:69`; `SKILL.md:75-76`) | tylko 20 000 zł (`CE/references/prawo-pl.md:118`) | ev-intelligence jest niepełny. Sprawdzić art. 45 ust. 2 pkt 4 w `PL-EMOB` i uzupełnić (P1) |
| K8 | Części ISO 15118 w AFIR Aneks II pkt 2.1.1 | „EN ISO 15118-1…-5” (`pe/dom-ev-regulations-eu/references/afir.md:100`); ale „-1..4” w `pe/dom-ev-knowledge-base/references/rejestr-standardow.json` (wpis `iso-15118-2`) | „EN ISO 15118-1…-5” (`PKI/references/iso15118-w-ocpp.md:120`) | Niespójność wewnątrz pack-ev; ev-intelligence jest zgodny z `pe/afir.md`. Przy weryfikacji sprawdzić `AFIR Annex II pkt 2.1.1` |
| K9 | Klasy A, B, C | MI-011: A 2 %, B 1 %, C 0,5 % (`mid-mi-011.md:33`) | MI-003: producent określa klasę A, B albo C, bez procentów (`metrologia.md:31-36`) | Nie ma sprzeczności, bo to inne załączniki. Grozi jednak pomyleniem MI-003 z MI-011; w treści rozdzielić wprost |
| K10 | MMQ | MI-011: AC ≤ 0,1 kWh, DC ≤ 1 kWh (`mid-mi-011.md:35`); HB44 S.8: AC ≤ 0,5 kWh, DC ≤ 1,0 kWh (`hb44-3-40.md:53`) | brak | Inne reżimy (UE i USA). Pułapka: nie przenosić liczb między reżimami (pack-ev sam to pisze, `regulations-us/SKILL.md:131`) |
| K11 | Zmiana hasła stacji | „CSMS przyjmuje stare i nowe hasło przez okno przejściowe” (`pe/dom-ev-security/references/kontrole-i-migracja.md:20`) | brak; PKI nie opisuje A01 | Potencjalny konflikt z `201-P2 A01`. Sprawdzić przed użyciem; dziś to praktyka bez źródła |
| K12 | Profil 1 | „tylko laboratorium i sieć zamknięta”, „profil 2 jako minimum produkcyjne” (`pe/dom-ev-security/SKILL.md:54-56`) | „tylko w zaufanych sieciach (np. VPN); w terenie zdecydowanie zaleca się profil z TLS” (`PKI/references/bezpieczenstwo-ocpp.md:30-31`, `[201-P2 A §1.3]`) | Zgodne co do sensu; zostaje sformułowanie z cytatem z ev-intelligence |
| K13 | AFIR a częstotliwość danych | pack-ev nie zna `AFIR-655` („czy przyjęto akt o wspólnym API: [do weryfikacji]”, `afir.md:91`) | `AFIR-655 art. 2`: dane statyczne do 24 h, dynamiczne do 1 min (`afir-mapa.md:29-30`) | ev-intelligence jest lepszy; pack-ev ma lukę |
