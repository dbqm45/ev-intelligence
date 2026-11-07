# Wymagania produktu wynikające z przepisów i protokołów

Źródła: AFIR `[AFIR]`, ustawa o elektromobilności `[PL-EMOB]` i rozporządzenie `[PL-R1316]`, OCPP 2.0.1 część 2
`[201-P2]`, OCPI 2.3.0 `[OCPI230]`, dyrektywa 2019/882 `[EAA]` i ustawa o dostępności `[PL-DOST]`, EIPA
`[EIPA-STAT]` `[EIPA-OPIS]` `[EIPA-API]`. Każde wymaganie ma znacznik. Zdania **Wniosek** to propozycje projektowe, a nie
wymagania. Czego źródła nie określają (UX, ekonomika, większość danych rynkowych), opisuje sekcja 7.

## Spis treści
1. Ścieżka kierowcy: znalezienie stacji
2. Start sesji i płatność
3. Informacja o cenie i koszcie
4. Problem i pomoc
5. Dostępność
5a. Dane rynkowe: Polska (EIPA)
6. Produkt operatora i partnera
7. Czego źródła nie określają

## 1. Ścieżka kierowcy: znalezienie stacji
- **Publikacja w aplikacji:** Location z `publish = false` SHALL NOT być pokazywana w aplikacji ani na stronie, chyba że
  właścicielowi tokenu z listy `publish_allowed_to`. Także NSP i eMSP, którzy nie są właścicielami tego tokenu, MAY
  pokazać ją tylko temu właścicielowi `[OCPI230 §8.3.1]`.
- **Pola karty stacji** w OCPI: `name`, adres, `coordinates`, `directions`, `parking_type`, `facilities`, `opening_times`,
  `charging_when_closed`, `images`, `energy_mix`, `help_phone` (numer do obsługi klienta CPO), operator, właściciel
  `[OCPI230 §8.3.1]`.
- Lokalizacje prywatne, nieprzeznaczone do ładowania publicznego, SHALL NOT być publikowane przez OCPI `[OCPI230 §8.1]`.
- Dane AFIR dla NAP: statyczne i dynamiczne, w tym status, dostępność i cena ad hoc `[AFIR art. 20]`, z aktualizacją
  dynamicznych do 1 minuty `[AFIR-655 art. 2]`. W Polsce mapa EIPA pokazuje tylko stacje po badaniu UDT
  `[PL-EMOB art. 42 ust. 4a]`.

**Wniosek:** w produkcie eMSP filtr `publish` to wymaganie zgodności, a nie opcja wyświetlania. Test akceptacyjny:
lokalizacja z `publish = false` nie pojawia się na mapie użytkownika bez pasującego tokenu.

## 2. Start sesji i płatność
- Publiczne punkty: ładowanie ad hoc; od 13.04.2024 płatność powszechnie używanym instrumentem (czytnik kart, urządzenie
  zbliżeniowe, a poniżej 50 kW także np. QR); od 1.01.2027 czytnik albo urządzenie zbliżeniowe na punktach ≥ 50 kW na
  TEN-T `[AFIR art. 5 ust. 1]`.
- Przy automatycznym uwierzytelnieniu kierowca zawsze może z niego zrezygnować i ładować ad hoc albo w innej ofercie
  umownej; opcję pokazuje się jasno i wygodnie `[AFIR art. 5 ust. 2]`.
- W Polsce dostawca usługi nie może uzależniać ładowania od wcześniejszego zawarcia umowy pisemnej ani elektronicznej
  `[PL-EMOB art. 7]`.

**Wniosek:** ekran startu Plug & Charge albo autoryzacji automatycznej potrzebuje widocznej ścieżki „zapłać inaczej”,
a rejestracja konta nie może być warunkiem ładowania.

## 3. Informacja o cenie i koszcie
- **Przed sesją (AFIR):** ceny CPO rozsądne, porównywalne, przejrzyste, niedyskryminujące `[AFIR art. 5 ust. 3]`.
  - ≥ 50 kW: cena ad hoc za kWh i ewentualna opłata za zajętość za minutę, pokazane na stacji przed sesją;
  - < 50 kW: wszystkie składniki w kolejności kWh, minuta, sesja, inne `[AFIR art. 5 ust. 4]`.
- **Aplikacja MSP:** przed sesją wszystkie informacje o cenie tej sesji, z rozróżnieniem składników, w tym kosztów
  e-roamingu i opłat MSP; bez dodatkowych opłat za transgraniczny e-roaming `[AFIR art. 5 ust. 5]`.
- **Polska:** dostawca usługi publikuje cenę i warunki na swojej stronie `[PL-EMOB art. 3 ust. 2]`.
- **Ekran stacji (OCPP 2.0.1):** taryfa jako tekst dla człowieka w `personalMessage` (I01); koszt bieżący (I02); koszt
  końcowy `totalCost`, gdzie 0.00 oznacza sesję bezpłatną, a brak pola nie oznacza bezpłatnej (I03.FR.04); komunikaty
  zastępcze offline (I04, I05) `[201-P2 I03.FR.04]`.
- **OCPI:** `tariff_alt_text` przy obecnych `elements` SHALL zawierać tylko informacje dodatkowe, nie ceny
  `[OCPI230 §11.3.1]`.

Szczegóły i obliczanie ceny: skill `ev-billing-tariff-expert`.

**Wniosek:** jeden model ceny w produkcie zasila trzy ekrany (stacja, aplikacja, NAP/EIPA). Ekran stacji ≥ 50 kW
pokazuje tylko kWh i minutę, a aplikacja MSP dokłada własne opłaty i koszty roamingu jako osobne pozycje.

## 4. Problem i pomoc
- Na stacji w widocznym miejscu: numer telefonu eksploatującego do zgłaszania awarii, instrukcja ładowania (może być na
  wyświetlaczu), oznaczenie zagrożeń `[PL-R1316 § 11]` `[PL-R1316 § 12]`.
- OCPI: `help_phone` w Location `[OCPI230 §8.3.1]`.
- Komunikaty na stacji (OCPP 2.0.1, blok O) `[201-P2 O01.FR.08]`:
  - CSO ustawia, pobiera, zastępuje i usuwa komunikaty. Komunikatów wbudowanych w firmware nie da się zmienić;
  - komunikaty mają wersje językowe i formaty; jest język preferowany kierowcy, a jako zapas zaleca się angielski
    (O01.FR.08–09); znaczniki języka według RFC 5646 (O01.FR.17);
  - priorytety: `NormalCycle` (w normalnym cyklu), `InFront` (poza cyklem; kilka takich się zmienia), `AlwaysFront`
    (nadpisuje inne i komunikaty stacji; nowy zastępuje stary) (O01.FR.12–16);
  - `startTime` i `endTime` (O01.FR.05–07); komunikaty są trwałe po restarcie (O01.FR.10); limit
    `NumberOfDisplayMessages` (O01.FR.11).
- Komunikaty o błędach z perspektywy operatora i diagnostyka: skill `ev-charging-operations-expert`.

**Wniosek:** w produkcie operatora komunikat o awarii to `AlwaysFront` z czasem końca, a promocja to `NormalCycle`.
Panel ostrzega przed drugim `AlwaysFront`, bo zastąpi pierwszy.

## 5. Dostępność
- Polska: stacje spełniają wymagania m.in. dostępu dla osób niepełnosprawnych `[PL-EMOB art. 13]`. Ochrona przed
  najechaniem nie może utrudniać dostępu `[PL-R1316 § 8]`, a sposób umieszczenia instrukcji uwzględnia potrzeby osób
  niepełnosprawnych `[PL-R1316 § 11]`.
- AFIR: krajowe ramy polityki obejmują środki zapewniające dostępność punktów dla osób starszych, z ograniczoną
  mobilnością i z niepełnosprawnościami według wymagań dyrektywy (UE) 2019/882 `[AFIR art. 14 ust. 2]`.
- **Dyrektywa 2019/882 (EAA), zakres:** produkty wprowadzone do obrotu po 28.06.2025, w tym **terminale płatnicze**
  (urządzenie, którego głównym celem jest płatność instrumentem płatniczym w fizycznym punkcie sprzedaży)
  `[EAA art. 2]` `[EAA art. 3]`; usługi dla konsumentów, w tym **usługi handlu elektronicznego** (na odległość, przez
  strony i aplikacje, na żądanie konsumenta w celu zawarcia umowy) `[EAA art. 2]`. Usługi ładowania nie są wymienione
  wprost.
- **Polska (transpozycja):** ustawa o zapewnianiu spełniania wymagań dostępności `[PL-DOST art. 3]`:
  - obejmuje terminale płatnicze w fizycznym punkcie sprzedaży i usługi handlu elektronicznego;
  - nie dotyczy usług mikroprzedsiębiorców `[PL-DOST art. 4]` ani produktów wprowadzonych do obrotu przed wejściem
    ustawy w życie `[PL-DOST art. 84]`;
  - terminal ma syntezę mowy w języku interfejsu i wejście na przewodowy stereofoniczny zestaw słuchawkowy. Funkcje
    dostępności działają bez wcześniejszej aktywacji. Klawisze mają kontrast i są wyczuwalne dotykiem. Gdy reakcja
    jest wymagana w określonym czasie, terminal informuje o tym więcej niż jednym kanałem zmysłowym i pozwala
    wydłużyć czas `[PL-DOST art. 9]`;
  - w e-commerce dostępne są m.in. identyfikacja, bezpieczeństwo i płatność `[PL-DOST art. 18]`;
  - terminale używane przed wejściem ustawy w życie mogą działać do końca okresu ekonomicznej użyteczności, najwyżej
    20 lat `[PL-DOST art. 85 ust. 3]`.
- **Wymagania ogólne dla produktów** `[EAA Annex I]`: informacja więcej niż jednym kanałem zmysłowym, alternatywa dla
  koloru i sygnałów dźwiękowych, unikanie dużego zasięgu i siły, alternatywa dla biometrii, wystarczający i elastyczny
  czas na interakcję. Dla terminali samoobsługowych dyrektywa wymaga zamiany tekstu na mowę i słuchawek osobistych.
- **Wyjątki:** wymagania obowiązują, o ile nie zmieniają zasadniczo charakteru produktu i nie stanowią
  nieproporcjonalnego obciążenia. Ocenę podmiot dokumentuje i przechowuje 5 lat `[EAA art. 14]`.
- **Rozbieżność:** dyrektywa wymaga „personal headsets” `[EAA Annex I]`, a ustawa polska mówi o „przewodowym
  stereofonicznym zestawie słuchawkowym” `[PL-DOST art. 9]`. **Rozstrzygnięcie:** w PL obowiązuje brzmienie ustawy.
- **Wniosek:** terminal kartowy w ładowarce wprowadzonej do obrotu po 28.06.2025 to terminal płatniczy w rozumieniu
  EAA i ustawy, więc jego interfejs (wyświetlacz, klawisze, dźwięk) projektujesz według art. 9 ustawy. To, czy
  aplikacja MSP jest usługą handlu elektronicznego, zależy od tego, czy w niej zawierasz umowę. To interpretacja, nie
  opinia prawna. Normy zharmonizowane do EAA nie są opracowane.

## 5a. Dane rynkowe: Polska (EIPA)
Liczby z publicznej statystyki EIPA, stan na koniec roku; migawka strony z 7.11.2026 `[EIPA-STAT]`:

| Data | Lokalizacje | Stacje | Punkty ładowania |
|---|---|---|---|
| 31.12.2021 | 1537 | 1883 | 3582 |
| 31.12.2022 | 2020 | 2514 | 4819 |
| 31.12.2023 | 3026 | 3721 | 7089 |
| 31.12.2024 | 4630 | 5573 | 10596 |
| 31.12.2025 | 6186 | 7427 | 14930 |
| 07.11.2026 | 6693 | 8297 | 16563 |

- Model danych EIPA: baza (Charging Pool) → stacja → punkt ładowania → złącza. Dozorem UDT objęte są stacje
  `[EIPA-OPIS]`. Do EIPA trafiają ceny i metody płatności takie, jak dla użytkownika bez umowy ze sprzedawcą
  `[EIPA-OPIS]`.
- API dla operatorów (REST 2.1): bazy, stacje, punkty, złącza, ceny i status punktu, słowniki metod płatności i
  uwierzytelnienia `[EIPA-API]`.
- Strona statystyk nie definiuje kolumn poza nagłówkami i nie podaje wykorzystania stacji, przychodów ani liczby
  pojazdów.

**Wniosek:** w latach 2021–2025 liczba punktów w EIPA wzrosła ok. 4,2 razy (3582 → 14930). Do liczenia wskaźnika „kW
na pojazd” (AFIR art. 3) potrzebne są jeszcze dane o rejestracjach, których baza nie ma.

## 6. Produkt operatora i partnera
- Statusy, alarmy, działania zdalne i KPI dostępności: skille `ev-cpms-architect` i `ev-charging-operations-expert`.
- Dane rozliczeniowe dla partnerów: CDR z polami kosztów i czasu (`total_time`, `total_parking_time`)
  `[OCPI230 §10.3.1]`; skill `ev-billing-tariff-expert`.
- Dane dla regulatora i rejestrów: EIPA w PL, NAP w UE (skill `ev-compliance-expert`).

**Wniosek:** wskaźniki wykorzystania (np. godziny ładowania i postoju na punkt) można liczyć z pól CDR
`total_time` i `total_parking_time`. OCPI ich nie definiuje jako KPI, więc definicję wskaźnika zapisujesz w produkcie
jawnie.

## 7. Czego źródła nie określają
Bez źródeł oficjalnych w bazie (piszesz to wprost, nie uzupełniasz z pamięci):
- wzorce UX, persony i ścieżki klienta jako praktyka projektowa (D16.01–D16.03): powyższe sekcje dają tylko wymagania;
- benchmarki funkcji CPMS i eMSP (D16.05);
- modele biznesowe, ekonomika stacji (CAPEX, OPEX, czas zwrotu), finansowanie, krajobraz rynku (D17);
- statystyki rynku poza liczbą infrastruktury w PL (rejestracje pojazdów, dane UE i innych krajów), wykorzystanie
  stacji, prognozy popytu, predykcyjne utrzymanie, AI w operacjach (D15.01–D15.03, D15.05);
- normy zharmonizowane do dyrektywy 2019/882.

Kandydaci na źródła (hosty zablokowane w sesji, `sources/niedostepne.yaml`): EAFO, Eurostat, rejestr BNetzA, IEA,
CEPiK w dane.gov.pl. Pełne dane EIPA dla czytelników wymagają rejestracji konta.
