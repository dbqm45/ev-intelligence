# USA: NEVI (23 CFR 680) i NIST Handbook 44 § 3.40

Źródła: 23 CFR Part 680 w eCFR, stan na 2026-11-24 `[US-23CFR680]`; NIST Handbook 44, wydanie 2026, sekcja 3.40
`[NIST-HB44 §3.40]`. eCFR to kompilacja redakcyjna; jego noty o statusie prawnym nie udało się pobrać (strony
„Reader Aids” zablokowane), więc moc prawna tekstu eCFR jest **niesprawdzona** (`sources/us-prawo.yaml`). Zdania
**Wniosek** to interpretacja, nie opinia prawna. Lokalizatory paragrafów HB44 (np. `S.1.3.2`) narzędzie `ev_kb check`
zgłasza jako NIESPRAWDZONE — sprawdzono je ręcznie w tekście sekcji 3.40.

**Normy płatne.** 23 CFR 680 przywołuje ISO 15118-2, -3, -4, -5 i -20, SAE J1772, normy UL, PCI DSS i ENERGY STAR, ale
nie zawiera sekcji o włączeniu norm przez odesłanie (incorporation by reference). Treści tych norm baza nie opisuje
(`sources/niedostepne.yaml`); poniżej jest tylko to, co mówi sam tekst rozporządzenia.

## 1. Zakres i adresaci
- Część 680 ustala minimalne standardy dla projektów finansowanych z programu NEVI Formula Program i dla publicznie
  dostępnych ładowarek budowanych ze środków z tytułu 23 U.S.C., także gdy projekt jest traktowany jako projekt na
  drodze federalnej (Federal-aid highway) `[US-23CFR680 §680.100]` `[US-23CFR680 §680.102]`.
- Większość obowiązków adresuje „States or other direct recipients”; wprost do „charging station operators” kierowane są
  m.in. platformy wielojęzyczne i ochrona danych klientów `[US-23CFR680 §680.106(k)]` `[US-23CFR680 §680.106(l)]`.
- Definicje ról: *charging station operator* to właściciel ładowarek i urządzeń, który zachowuje odpowiedzialność za
  eksploatację i utrzymanie mimo podwykonawców; *charging network provider* to podmiot obsługujący sieć komunikacji
  zdalnie zarządzającą ładowarkami; obie role może pełnić jeden podmiot `[US-23CFR680 §680.104]`.
- *Charging port* ładuje jeden pojazd naraz, nawet z kilkoma złączami `[US-23CFR680 §680.104]`.
- **Wniosek:** dla CPO i CPMS wymogi z części 680 przychodzą przez umowę ze stanem (odbiorcą środków); sam tekst nie
  nakłada kar na operatora — sankcji część 680 nie określa.

## 2. Terminy
- Podstawa: 88 FR 12752, 28.02.2023; wszystkie sekcje §§ 680.100–680.118 mają w eCFR jedną wersję z 2023-03-30
  `[US-23CFR680]`. Daty wejścia w życie rozporządzenia tekst eCFR nie podaje (preambuła w Federal Register niepobrana).
- Do 28.02.2024: oprogramowanie ładowarki zgodne z ISO 15118-2 i zdolne do Plug and Charge, ładowarki zgodne z OCPP 2.0.1,
  sieci zdolne do komunikacji z innymi sieciami według OCPI 2.2.1 `[US-23CFR680 §680.108]`.
- Cena w $/kWh: jeśli cena nie była oparta na $/kWh, wymóg trzeba spełnić w ciągu roku od 28.02.2023
  `[US-23CFR680 §680.116(a)]`.
- Dane roczne i jednorazowe od 2024, do 1 marca `[US-23CFR680 §680.112(b)]` `[US-23CFR680 §680.112(c)]`.
- Utrzymanie ładowarek zgodnie z częścią 680 przez co najmniej 5 lat od pierwszego uruchomienia
  `[US-23CFR680 §680.106(i)]`.

## 3. Stacja: porty, moc, złącza, dostępność
- Stacja przy wyznaczonych korytarzach (AFC): co najmniej cztery porty DCFC podłączone do sieci, równoczesne ładowanie
  czterech pojazdów; w innych lokalizacjach cztery porty DCFC lub AC Level 2 `[US-23CFR680 §680.106(b)]`.
- Każdy port DCFC ma co najmniej jedno trwale przyłączone złącze CCS Type 1; złącza CHAdeMO tylko ze środków FY2022;
  port AC Level 2 ma trwale przyłączone złącze J1772 `[US-23CFR680 §680.106(c)]`.
- DCFC: napięcie wyjściowe 250–920 V DC; przy AFC moc ciągła co najmniej 150 kW na każdym porcie jednocześnie; podział mocy
  dozwolony, jeśli każdy port nadal spełnia żądanie pojazdu do 150 kW. AC Level 2: co najmniej 6 kW na port jednocześnie
  `[US-23CFR680 §680.106(d)]`.
- Stacja przy AFC dostępna 24/7 przez cały rok; pozostałe co najmniej w godzinach działalności gospodarza; przerwy na
  konserwację i wyłączenia z § 680.116(b)(3) nie są zakazane `[US-23CFR680 §680.106(e)]`.
- Certyfikacja ładowarek przez NRTL (OSHA), AC Level 2 z ENERGY STAR; normy UL „should” `[US-23CFR680 §680.106(g)]`.

## 4. Uptime (minimalna dostępność portu)
- Każdy port ma średni roczny uptime **większy niż 97 %** `[US-23CFR680 §680.116(b)]`.
- Port jest „up”, gdy sprzęt i oprogramowanie są online i dostępne (lub w użyciu) **oraz** port dostarcza energię zgodnie z
  minimalną mocą z § 680.106(d) `[US-23CFR680 §680.116(b)(1)]`.
- Liczony co miesiąc za poprzednie 12 miesięcy `[US-23CFR680 §680.116(b)(2)]`, wzorem
  µ = ((525 600 − (T_outage − T_excluded)) / 525 600) × 100, gdzie T_outage i T_excluded to minuty awarii w poprzednim roku
  `[US-23CFR680 §680.116(b)(3)]`.
- T_excluded: awarie poza kontrolą operatora, **jeśli operator wykaże**, że port byłby inaczej sprawny — przerwy w dostawie
  energii przez zakład energetyczny, błąd pojazdu, zaplanowana konserwacja, wandalizm, klęski żywiołowe; wyłączone są też
  godziny poza godzinami działania stacji `[US-23CFR680 §680.116(b)(3)]`.
- Raport kwartalny zawiera uptime, T_outage i T_excluded za każdy z 3 poprzednich miesięcy oraz czas każdej awarii w
  minutach `[US-23CFR680 §680.112(a)]`.
- Czego tekst nie określa: jak liczyć minuty dla portu uruchomionego w trakcie roku (mianownik jest stały: 525 600), jak
  dokumentować wyłączenie, ani ile może trwać „scheduled maintenance”.
- **Wniosek:** CPMS powinien rejestrować stan portu z minutową rozdzielczością, przyczynę każdej awarii (kod błędu,
  źródło: sieć, pojazd, serwis, wandalizm) i dowód sprawności portu — bez tego T_excluded nie da się uzasadnić. Port,
  który działa, ale nie spełnia minimalnej mocy z § 680.106(d), nie jest „up”.

## 5. Płatności i ceny
- Jeśli ładowanie nie jest trwale bezpłatne: bezpieczna płatność dostępna dla osób z niepełnosprawnościami, co najmniej
  zbliżeniowa akceptująca główne karty debetowe i kredytowe **oraz** automatyczny bezpłatny numer telefonu albo SMS do
  rozpoczęcia sesji i zapłaty; bez wymogu członkostwa; bez ograniczania mocy ze względu na metodę płatności lub
  członkostwo; dostęp dla osób o ograniczonej znajomości angielskiego `[US-23CFR680 §680.106(f)]`.
- Płatność zbliżeniowa w definicji obejmuje karty debetowe, kredytowe, smartcard, aplikację mobilną i inne urządzenia
  przez RFID i NFC `[US-23CFR680 §680.104]`.
- Cena wyświetlana **przed** rozpoczęciem transakcji, oparta na $/kWh; cena wyświetlana i przekazywana przez sieć to cena
  bieżąca; **cena z początku sesji nie może się zmienić w trakcie sesji**; struktura cen z innymi opłatami jasno pokazana
  i wyjaśniona `[US-23CFR680 §680.116(a)]`.
- Stan lub inny odbiorca środków publikuje m.in. sposób ustalania cen ładowania w zamówieniu `[US-23CFR680 §680.106(a)]`.
- Porównanie z AFIR (`afir-mapa.md`): AFIR wymaga ładowania ad hoc i płatności kartą lub zbliżeniowo, a od 1.1.2027 przy
  ≥ 50 kW na TEN-T lub na bezpiecznym i chronionym parkingu czytnika kart albo urządzenia zbliżeniowego `[AFIR art. 5 ust. 1]`; przy ≥ 50 kW cena ad hoc za kWh,
  ewentualnie opłata za minutę zajętości, pokazana przed sesją `[AFIR art. 5 ust. 4]`. NEVI dodaje wymóg telefonu albo
  SMS i zakaz zmiany ceny w trakcie sesji `[US-23CFR680 §680.106(f)]` `[US-23CFR680 §680.116(a)]`.

## 6. Interoperacyjność i sieć (OCPP, OCPI, ISO 15118)
- Ładowarka–pojazd: zgodność z ISO 15118-3, sprzęt zdolny do ISO 15118-2 i ISO 15118-20; do 28.02.2024 oprogramowanie
  zgodne z ISO 15118-2 i zdolne do Plug and Charge; testy zgodności „should” według ISO 15118-4 i -5
  `[US-23CFR680 §680.108(a)]`. Treść norm ISO 15118 jest płatna i nieopracowana.
- Ładowarka–sieć: OCPP 1.6J lub wyższy, do 28.02.2024 OCPP 2.0.1 `[US-23CFR680 §680.108(b)]`. Sieć–sieć: OCPI 2.2.1 do
  28.02.2024 `[US-23CFR680 §680.108(c)]`. Zmiana dostawcy sieci bez zmian sprzętu `[US-23CFR680 §680.108(d)]`.
- Ładowarka: bezpieczna komunikacja z siecią, zdalne bezpieczne aktualizacje oprogramowania; sieć wykonuje, a ładowarka
  wspiera zdalny monitoring, diagnostykę, sterowanie i smart charge management `[US-23CFR680 §680.114(a)]`.
- Ładowarki i sieci bezpiecznie mierzą, przesyłają, przechowują i raportują energię i moc, bieżący status portu, bieżącą
  cenę dla klienta i historyczny uptime portu `[US-23CFR680 §680.114(a)]`.
- Jedna metoda identyfikacji kierowcy na stacjach wielu sieci `[US-23CFR680 §680.114(c)]`; komunikacja z zakładami
  energetycznymi i lokalnymi systemami zarządzania energią `[US-23CFR680 §680.114(d)]`.
- Przy utracie łączności z siecią ładowarka nadal rozpoczyna i kończy sesje z minimalną mocą `[US-23CFR680 §680.114(e)]`.
- Strategie cyberbezpieczeństwa (m.in. „cryptographic agility and support of multiple PKIs”, ciągłość działania przy
  przerwie komunikacji) są przykładowe („may include”) `[US-23CFR680 §680.106(h)]`.
- **Wniosek:** OCPP 1.6J po 28.02.2024 nie spełnia § 680.108(b); praca offline z § 680.114(e) wymaga lokalnej
  autoryzacji i buforowania transakcji w ładowarce. Szczegóły protokołów — skille OCPP i OCPI.

## 7. Dane: raporty dla FHWA i API dla stron trzecich
- Kwartalnie (format ustala FHWA): identyfikator stacji i portu (te same co w API), początek i koniec sesji i kody błędów
  nieudanych sesji, energia (kWh) na sesję, szczytowa moc sesji (kW), metoda płatności, uptime, czas awarii
  `[US-23CFR680 §680.112(a)]`.
- Rocznie: koszt konserwacji i napraw na stację `[US-23CFR680 §680.112(b)]`; jednorazowo (AFC): operatorzy, moc DER,
  koszty nieruchomości, sprzętu i przyłączenia `[US-23CFR680 §680.112(c)]`. Dane publikowane są zagregowane i
  zanonimizowane `[US-23CFR680 §680.112(a)]`.
- Bezpłatnie przez API dla deweloperów: identyfikator, adres, współrzędne w stopniach dziesiętnych, operator, dostawca
  sieci, status stacji, dostęp i godziny, dane portów (złącza, poziom, moc, dostęp z przyczepą), **status portu w
  bieżącym czasie i bieżąca cena w kategoriach OCPI 2.2.1**, akceptowane metody płatności `[US-23CFR680 §680.116(c)]`.
- Czego tekst nie określa: częstotliwości aktualizacji danych w API ani formatu raportu kwartalnego (odesłanie do FHWA).
- Porównanie z AFIR (`afir-mapa.md`): dane statyczne i dynamiczne określa AFIR `[AFIR art. 20 ust. 2]` z
  rozporządzeniem wykonawczym 2025/655 `[AFIR-655]`. NEVI kieruje dane do deweloperów stron trzecich przez API i
  odsyła do pojęć OCPI 2.2.1; krajowego punktu dostępu tekst części 680 nie przewiduje `[US-23CFR680 §680.116(c)]`.

## 8. Obsługa klienta i dane osobowe
- Kierowcy mają mechanizmy zgłaszania awarii i usterek; operator stacji zapewnia dostęp do platform wielojęzycznych;
  zgodność z ADA `[US-23CFR680 §680.106(k)]`.
- Operator zbiera, przetwarza i przechowuje tylko dane osobowe ściśle niezbędne do usługi; PCI DSS „should”
  `[US-23CFR680 §680.106(l)]`. Treść PCI DSS nieopracowana.
- Kwalifikacje elektryków (EVITP albo program praktyk) `[US-23CFR680 §680.106(j)]`; ADA i przepisy federalne
  `[US-23CFR680 §680.118]`.

## 9. NIST Handbook 44 § 3.40 — pomiar i rozliczenie
- Zakres: urządzenia mierzące energię dla pojazdów, gdy ilość jest podstawą sprzedaży lub opłaty `[NIST-HB44 A.1]`. Nie
  dotyczy m.in. EVSE, w których ilość nie wpływa na opłatę, ani sprzedaży hurtowej `[NIST-HB44 A.2]`. Obowiązuje też
  Section 1.10 General Code (nieopracowany) `[NIST-HB44 A.3]`; NTEP przyjmuje do oceny typu tylko EVSE z certyfikatem
  bezpieczeństwa NRTL `[NIST-HB44 A.4]`. Od 1.1.2023 kod jest stały, nie tymczasowy `[NIST-HB44 §3.40]`.
- EVSE typu obliczeniowego wskazuje energię, cenę jednostkową i cenę całkowitą; przy wielu cenach w sesji — czas
  początku i końca, energię, cenę i kwotę każdej fazy; przy opłatach czasowych — czas, cenę i kwotę oraz sumę
  `[NIST-HB44 S.1.1]`.
- Wskazanie widoczne co najmniej 15 s; energia oddzielona od opłat czasowych (np. parkowanie) `[NIST-HB44 S.1.2]`.
- Jednostki: kWh i ich części dziesiętne `[NIST-HB44 S.1.3.1]`; najmniejsza działka nie większa niż 0,0001 kWh (AC) i
  0,001 kWh (DC) `[NIST-HB44 S.1.3.2]`; cena końcowa liczona z ilości nie większych niż 0,01 kWh `[NIST-HB44 S.2.5.1]`.
- Utrata zasilania: dane do zakończenia transakcji dostępne przy EVSE, konsoli, przez internet na miejscu albo bezpłatny
  telefon (na parkingach długoterminowych co najmniej 8 h), inaczej transakcja bez opłaty za energię
  `[NIST-HB44 S.2.3.1]`; transakcja kończy się albo trwa, jeśli EVSE rozpozna ten sam pojazd; paragon pokazuje przerwę
  z datą i godziną `[NIST-HB44 S.2.3.2]`.
- Cena jednostkowa na każdej stronie urządzenia, maksymalna moc i rodzaj prądu dla każdej ceny `[NIST-HB44 S.2.4.1]`
  `[NIST-HB44 S.2.4.2]`. Wybór ceny przed dostawą; **zmiana ceny w trakcie dostawy zabroniona, chyba że klient przed
  sprzedażą zaakceptował zmienną strukturę cen** `[NIST-HB44 S.2.4.3]`.
- Paragon (papierowy lub elektroniczny) po każdej transakcji: energia z jednostką, kwota za energię, cena jednostkowa (i
  fazy przy wielu cenach), maksymalna moc i rodzaj prądu, opłaty dodatkowe z czasem i ceną, suma, unikalny numer EVSE,
  nazwa i lokalizacja firmy `[NIST-HB44 S.2.6]` `[NIST-HB44 UR.3.3]`.
- Wskazanie zera i ilości na urządzeniu; DC EVSE uruchomione przed 1.1.2025 zwolnione do 1.1.2028 `[NIST-HB44 S.2.7]`.
  Autoryzacja wygasa po 2 minutach bez aktywacji `[NIST-HB44 S.2.8]`.
- Zabezpieczenie parametrów plombą albo dziennikiem zdarzeń; kategoria 3 (zdalna konfiguracja): licznik zdarzeń 000–999,
  ID parametru, data i czas, nowa wartość, pojemność 10 × liczba parametrów, nie więcej niż 1 000 rekordów
  `[NIST-HB44 S.3.3]`. Dane niezmienialne i dostępne, pamięć co najmniej 3 lata bez wymiennej baterii
  `[NIST-HB44 S.3.4]`. Licznik sumaryczny bez kasowania `[NIST-HB44 S.7]`.
- Minimalna mierzona ilość (MMQ) nie większa niż 0,5 kWh (AC) i 1,0 kWh (DC) `[NIST-HB44 S.8]`; oznakowanie m.in. napięcie,
  prąd, rodzaj prądu, MMQ `[NIST-HB44 S.5.2]`; DC EVSE sprzed 2025 z tolerancją T.2.2(a) oznaczony „Class 5”
  `[NIST-HB44 S.5.2.1]`.
- Badanie w punkcie przyłączenia kabla do pojazdu; straty w kablu „should” być korygowane automatycznie
  `[NIST-HB44 N.2]`; test porównuje energię **i koszt** transakcji ze wzorcem `[NIST-HB44 N.3]`.
- Tolerancje (dla błędów w obie strony `[NIST-HB44 T.1]`): AC — odbiorcza 1,0 %, eksploatacyjna 2,0 %
  `[NIST-HB44 T.2.1]`; DC sprzed 1.1.2025 oznaczone Class 5 — 5,0 % do 1.1.2034, pozostałe DC 1,0 % / 2,0 %
  `[NIST-HB44 T.2.2]`; powtarzalność: rozrzut nie większy niż 25 % tolerancji eksploatacyjnej `[NIST-HB44 T.3]`.
- Na EVSE bez obsługi: nazwa, adres i telefon lokalnej osoby odpowiedzialnej `[NIST-HB44 UR.2.5]`; cena jednostkowa
  widoczna na urządzeniu `[NIST-HB44 UR.3.1]`.
- Rozbieżność w tekście T.2.2: po lit. (b) stoi zdanie „All DC EVSE placed into service prior to January 1, 2025 are exempt
  from this requirement until January 1, 2028.” — tekst nie mówi, czy dotyczy lit. (a), (b) czy obu
  `[NIST-HB44 T.2.2]`. Metadane PDF mają tytuł „Tentative Code”, tekst — status stały; rozstrzyga tekst
  `[NIST-HB44 §3.40]`.
- Czego sekcja 3.40 nie określa: w których stanach HB44 jest wiążący (przyjęcie w prawie stanowym nie było sprawdzane),
  treści General Code (G-S.1, G-S.5.5, G-S.8.2) i Section 5.55.

## 10. NEVI a HB44 — wspólne punkty dla CPMS
- Zmiana ceny: NEVI — cena z początku sesji nie zmienia się `[US-23CFR680 §680.116(a)]`; HB44 — zmiana dozwolona po
  wcześniejszej akceptacji klienta `[NIST-HB44 S.2.4.3]`. **Wniosek:** na stacji NEVI stosujesz ostrzejszy wymóg
  NEVI; taryfy z fazami cen (HB44 S.1.1(a)) nie nadają się do sesji na takiej stacji. Relacji obu aktów tekst nie
  określa.
- Paragon HB44 wymaga unikalnego numeru EVSE `[NIST-HB44 S.2.6]`, a raport NEVI — identyfikatorów stacji i portu
  zgodnych z API `[US-23CFR680 §680.112(a)]`. **Wniosek:** jeden słownik identyfikatorów (EVSE, port, OCPI) w CPMS.
- Metrologia UE (MID, MI-003) — `metrologia.md`. Sekcja 3.40 HB44 nie odsyła do MID ani OIML `[NIST-HB44 §3.40]`;
  **Wniosek:** „Class 5” i tolerancje HB44 nie przekładają się wprost na klasy MID.
