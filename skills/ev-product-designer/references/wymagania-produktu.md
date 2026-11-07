# Wymagania produktu wynikające z przepisów i protokołów

Źródła: AFIR `[AFIR]`, ustawa o elektromobilności `[PL-EMOB]` i rozporządzenie `[PL-R1316]`, OCPP 2.0.1 część 2
`[201-P2]`, OCPI 2.3.0 `[OCPI230]`. Każde wymaganie ma znacznik. Zdania **Wniosek** to propozycje projektowe, a nie
wymagania. Czego źródła nie określają (UX, ekonomika, rynek), opisuje sekcja 7.

## Spis treści
1. Ścieżka kierowcy: znalezienie stacji
2. Start sesji i płatność
3. Informacja o cenie i koszcie
4. Problem i pomoc
5. Dostępność
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
  mobilnością i z niepełnosprawnościami według wymagań dyrektywy (UE) 2019/882 `[AFIR art. 14 ust. 2]`. Treść tej
  dyrektywy (European Accessibility Act) nie jest opracowana.

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
- statystyki rynku, wykorzystanie stacji, prognozy popytu, predykcyjne utrzymanie, AI w operacjach (D15.01–D15.03,
  D15.05);
- dyrektywa (UE) 2019/882 o dostępności.

Do takich tematów potrzebne są dane własne użytkownika albo nowe źródła (np. statystyki instytucji UE lub krajowych
regulatorów), które najpierw trafiają do `sources/*.yaml`.
