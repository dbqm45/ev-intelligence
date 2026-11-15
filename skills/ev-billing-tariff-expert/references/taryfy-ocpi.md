# Taryfy OCPI 2.3.0: struktura, pierwszeństwo, ograniczenia, `step_size`

Źródła: specyfikacja OCPI 2.3.0 `[OCPI230]` i wytyczne EVRF „Tariff simplification … using OCPI v2.3”, wersja 1.0 z
2026-07-09 `[OCPI-TSG]`. Wytyczne dotyczą 2.3.0, ale według autorów większość z nich nadaje się też do 2.2.1
`[OCPI-TSG Preface]`. Zdania **Wniosek** to rekomendacje wyprowadzone z cytowanych faktów.

## Spis treści
1. Obiekt Tariff
2. Który element obowiązuje (pierwszeństwo)
3. Ograniczenia (`TariffRestrictions`)
4. `step_size` w całej sesji
5. Zmiana taryfy, ważność i przypisanie do złącza
6. Wytyczne uproszczenia taryf i rozbieżności ze specyfikacją
7. Przykłady liczbowe ze specyfikacji i błędy w nich
8. Różnice modelu taryfy: OCPI 2.2.1 a 2.3.0

## 1. Obiekt Tariff `[OCPI230 §11.3.1]`
- Budowa: Tariff → lista `TariffElement` → lista `PriceComponent`. Element to grupa składników obowiązujących przy tych
  samych warunkach (ograniczeniach).
- Pola wymagane: `country_code`, `party_id`, `id`, `currency` (ISO-4217), `elements`, `tax_included`, `last_updated`.
- `type` (`TariffType`): `AD_HOC_PAYMENT`, `PROFILE_CHEAP`, `PROFILE_FAST`, `PROFILE_GREEN`, `REGULAR`. Bez `type` taryfa
  dotyczy wszystkich sesji `[OCPI230 §11.3.1]`. Znaczenie wartości `[OCPI230 §11.4.8]`:
  - `REGULAR`: sesja z RFID bez preferencji ładowania albo z preferencją `REGULAR`;
  - `PROFILE_CHEAP` / `_FAST` / `_GREEN`: sesja, dla której ustawiono preferencję ładowania `CHEAP` / `FAST` / `GREEN`;
  - `AD_HOC_PAYMENT`: płatność ad hoc w punkcie (np. terminal kart debetowych lub kredytowych).
- `tax_included`: `YES`, `NO`, `N/A` `[OCPI230 §11.4.9]`. `PriceComponent.price` jest z podatkiem albo bez, zależnie od
  `tax_included`. `PriceComponent.vat`: gdy brak, VAT nie ma zastosowania `[OCPI230 §11.4.2]`.
- `min_price` / `max_price` (`PriceLimit`): sesja kosztuje co najmniej / co najwyżej tyle. Obowiązują **obie** wartości,
  przed i po podatkach, bo podatki mogą być różne dla części sesji.
- Klasa `PriceLimit` ma pola `before_taxes` (number, wymagane: koszt bez podatków) i `after_taxes` (number, opcjonalne:
  koszt z podatkami) `[OCPI230 §11.4.3]`. **Wniosek:** gdy `after_taxes` nie ma, limit po podatkach nie obowiązuje i
  silnik wyceny sprawdza tylko `before_taxes`.
- `preauthorize_amount`: kwota, którą dostawca terminala płatniczego (PTP) powinien zablokować przy płatności kartą.
- `tariff_alt_text` przy obecnych `elements` SHALL zawierać tylko informacje dodatkowe, nie ceny z `elements`
  (eMSP może mieć własne opłaty).
- **Zaokrąglanie cen:** OCPI nie ma pól ani wymagań co do zaokrąglania. Robi się je według prawa, umów między stronami
  i waluty. „The OCPI specification stays out of these matters.”
- Taryfa bezpłatna: jeden element bez ograniczeń z jednym składnikiem `FLAT` o cenie `0.00`. VAT można podać także
  przy cenie zerowej `[OCPI230 §11.3.1.1]`.
- `tariff_alt_url`: strona z opisem taryfy dla człowieka. `energy_mix`: dane o energii dostarczanej w tej taryfie
  `[OCPI230 §11.3.1]`.
- Cena zależna od rynku (np. bieżące ceny energii) nie ma w Tariff własnych pól. Przykład specyfikacji: taryfa
  `PROFILE_CHEAP` z ceną w `elements` i `tariff_alt_url` do strony z rzeczywistą ceną bieżącą `[OCPI230 §11.3.1.1]`.
- Taryfy różnej dla karty kredytowej i debetowej OCPI nie wyrazi („cannot be modeled with OCPI”). Specyfikacja proponuje
  wyższą opłatę w taryfie, rabat w CDR i wyjaśnienie w `tariff_alt_text` `[OCPI230 §11.3.1.1]`.
- Jedna waluta na taryfę (`currency`, wymagane) i jedna na CDR, a wszystkie kwoty CDR są w tej walucie
  `[OCPI230 §11.3.1, §10.3.1]`. Przeliczania walut specyfikacja nie opisuje.

## 2. Który element obowiązuje `[OCPI230 §11.3.1, §11.4.5]`
- Dla każdego wymiaru (`ENERGY`, `TIME`, `PARKING_TIME`, `FLAT`) szukasz **osobno**: obowiązuje pierwszy element na
  liście, który ma składnik tego wymiaru i którego ograniczenia pasują w danej chwili.
- W danej chwili aktywny jest najwyżej jeden składnik na wymiar, ale kilka wymiarów naraz (np. `ENERGY` i `TIME`).
- Brak pasującego elementu i brak elementu bez ograniczeń dla wymiaru → **ten wymiar nic nie kosztuje**.
- Zalecenie: dodaj „domyślny” element bez ograniczeń **po** wszystkich innych elementach danego wymiaru. Działa jako
  zapas, gdy nic innego nie pasuje.

**Wniosek:** walidator taryf przy imporcie zgłasza wymiary, które w jakimś przedziale czasu nie mają ceny. Przykład:
element 17:00–22:00 i element weekendowy bez elementu domyślnego oznaczają darmową energię w dni robocze poza 17–22.

## 3. Ograniczenia `[OCPI230 §11.4.7]`
- Ograniczenia w jednym elemencie łączą się logicznym AND: element jest aktywny tylko, gdy pasują wszystkie podane pola.
- `start_time` / `end_time`: czas lokalny według `time_zone` z Location, format `HH:MM`. Gdy `end_time < start_time`,
  okres przechodzi na następny dzień. „To stop at end of the day use: 00:00.”
- Czy `end_time` jest wyłączny, tekst nie mówi: `start_time` to „valid from”, `end_time` to „valid until this time of the
  day”, a słowa „inclusive/exclusive” stoją tylko przy datach, kWh i czasie trwania. **Wniosek:** przyjmij przedział
  [`start_time`, `end_time`), spójnie z `end_date` i `max_*`, i zapisz to w umowie roamingowej.
- `start_date` włącznie, `end_date` wyłącznie (czas lokalny).
- `min_kwh` włącznie, `max_kwh` wyłącznie (energia zużyta w sesji).
- `min_current` / `max_current` (suma po fazach, A) i `min_power` / `max_power` (kW) dotyczą wartości chwilowej, nie
  całej sesji. Element MUST przestać obowiązywać, gdy prąd lub moc przekroczy próg.
  - `min_current` / `min_power`: aktywny przy wartości „more than, or equal to”, czyli **włącznie**.
  - `max_current` / `max_power`: aktywny przy wartości „less than”, nieaktywny przy „higher”. Równości tekst nie
    nazywa. **Wniosek:** przy równej wartości warunek aktywacji („less than”) nie jest spełniony, więc max jest
    **wyłączny**. W taryfie złożonej ze specyfikacji (`max_current: 32` przed `min_current: 32`) przy dokładnie 32 A
    obowiązuje element z `min_current` `[OCPI230 §11.3.1.1]`.
- `min_duration` włącznie, `max_duration` wyłącznie, w sekundach od początku sesji.
- `day_of_week`: lista dni (krotność `*`). Brak pola: ograniczenia nie ma, bo AND obejmuje tylko podane pola. Wytyczne:
  dla wszystkich dni nie tworzy się ograniczenia, a `day_of_week: []` znaczy „w żaden dzień” `[OCPI-TSG cz. 2 pkt 5]`.
  Okno `start_time` `00:00` i `end_time` `00:00` oznacza cały dzień `[OCPI-TSG cz. 2 pkt 5]`.
- `reservation`: element opisuje koszt rezerwacji. Dozwolone tylko wymiary `FLAT` i `TIME` (czas rezerwacji).
  Typy: `RESERVATION` i `RESERVATION_EXPIRES` (kierowca nie zaczął ładować przed wygaśnięciem). Gdy taryfa ma oba z
  składnikiem `TIME`, koszt czasu wygasłej rezerwacji liczy się z elementu `RESERVATION_EXPIRES` `[OCPI230 §11.4.4]`.

## 4. `step_size` w całej sesji `[OCPI230 §10.3.1, §11.4.2]`
- Zużycie zaokrągla się w górę do najmniejszej wielokrotności `step_size`. Mnożnik: `ENERGY` 1 Wh, `TIME` i
  `PARKING_TIME` 1 s; `FLAT` nie ma mnożnika `[OCPI230 §11.4.2]`.
- `step_size` stosuje się **raz na sesję**: raz dla `ENERGY` i raz łącznie dla `TIME` z `PARKING_TIME` `[OCPI230 §10.3.1]`.
- Liczy się **suma** zużycia w sesji, nie ostatni okres. Bierzesz `step_size` ostatniego istotnego składnika.
- Przy przejściu między elementami tego samego wymiaru (np. tańsza i droższa energia) `step_size` wcześniejszego
  elementu się nie stosuje. Nie stosuje się go też przy zmianie taryfy w trakcie sesji (np. inny profil preferencji).
- Przy `TIME` i `PARKING_TIME` w jednej sesji zaokrągla się tylko czas parkowania.
- Nadwyżka z zaokrąglenia trafia do **ostatniego** okresu z danym wymiarem i jest wyceniana jego ceną: w przykładzie
  czasowym zaokrąglone 2 minuty liczy się po stawce po 17:00 `[OCPI230 §10.3.1]`, a w przykładzie z darmowym postojem
  po 20:00 „the extra 7 minutes are then added to the last period” z wymiarem czasowym `[OCPI230 §11.4.2.1]`. O
  rozkładaniu nadwyżki proporcjonalnie na okresy specyfikacja nie mówi.

Przykłady ze specyfikacji `[OCPI230 §10.3.1]`:
| Taryfa | Zużycie | Wynik |
|---|---|---|
| energia 0,20 €/kWh przed 17:00, 0,27 €/kWh po, `step_size` 500 | 4,3 kWh + 1,1 kWh | łącznie 5,4 → 5,5 kWh; nie zaokrągla się 1,1 do 1,5 |
| czas 5 €/h przed 17:00, 7 €/h po, `step_size` 10 min | 6 + 22 min | łącznie 28 → 30 min, więc po 17:00 rozlicza się 24 min (nie 30, co dałoby 36) |
| ładowanie 1 €/h, parkowanie 2 €/h, `step_size` 10 min | 21 min ładowania, 16 min parkowania | parkowanie → 20 min, razem 41 min; czasu ładowania się nie zaokrągla |
| `TIME` i parkowanie, `step_size` 5 min | 21 min ładowania, 7 min parkowania | ładowanie 21 min (nie 25), parkowanie 10 min |

**Wniosek (obliczenie):** w przykładzie czasowym koszt to 6/60 × 5 € + 24/60 × 7 € = 0,50 € + 2,80 € = 3,30 €.

- OCPI 3.0 nie ma `step_size`. Strony przygotowujące się do 3.0 powinny ustawiać `step_size = 1` `[OCPI230 §11.4.2]`.
  Wytyczne EVRF: „Always use step_size 1”, a zaokrąglenia uzgadniać w umowie roamingowej `[OCPI-TSG cz. 2 pkt 1]`.
- Lokalne przepisy mogą regulować `step_size` (przykład z NL w specyfikacji) `[OCPI230 §11.4.2]`.

## 5. Zmiana taryfy, ważność i przypisanie do złącza `[OCPI230 §11.3.1]`
- `start_date_time` / `end_date_time` (UTC): od kiedy taryfa obowiązuje i po kiedy przestaje.
- OCPI **nie zabrania** zmiany taryfy w trakcie sesji. Typowo zmienia się ją dopiero po sesji. W wielu krajach prawo
  konsumenckie zabrania zmiany w trakcie: kierowca akceptuje taryfę obowiązującą przy starcie.
- CDR zawiera taryfy w wersji z chwili startu sesji `[OCPI230 §10.3.1]`.
- `Connector.tariff_ids` `[OCPI230 §8.3.3]`:
  - kilka taryf jest dozwolonych, ale jednocześnie aktywna może być tylko jedna danego `Tariff.type`. Taryfy tego samego
    typu muszą mieć rozłączne okresy `start_date_time`–`end_date_time`;
  - przy preferencjach ładowania powinno się („should”) podać taryfę dla każdego możliwego `ProfileType`;
  - dla ładowania bezpłatnego pole powinno („should”) wskazywać zdefiniowaną taryfę bezpłatną.
- Wymiana taryfy: złącze może wskazywać starą (z `end_date_time`) i nową taryfę naraz, a starą można usunąć później
  `[OCPI230 §11.3.1.1]`. Przed DELETE taryfy RECOMMENDED jest sprawdzić, że żadne złącze jej nie wskazuje w `tariff_ids`
  `[OCPI230 §11.2.2.3]`.

## 6. Wytyczne uproszczenia taryf `[OCPI-TSG]`
Najważniejsze (cz. 2 = wytyczne techniczne):
- taryfy udostępniać przez OCPI, a zmiany **przed** ich obowiązywaniem; taryfy ad hoc z typem `AD_HOC_PAYMENT`, żeby
  trafiły do NAP `[OCPI-TSG cz. 1 pkt 1, „Ad Hoc tariffs”]`;
- ograniczenia tylko tam, gdzie zmienia się cena (pkt 2); element bez ograniczeń nie przed elementem z ograniczeniami,
  bo ten drugi nigdy nie zadziała (pkt 3); przy kilku elementach jeden składnik na element (pkt 4);
- `0` w ograniczeniu nie znaczy „brak ograniczenia”. `max_duration: 0` oznacza, że składnik nigdy nie obowiązuje;
  `day_of_week: []` oznacza „w żaden dzień” (pkt 5–6);
- nie zmieniać taryfy, która już obowiązywała; nową taryfę tworzyć z nowym `id` i przepinać złącza; ustawiać
  `end_date_time` starej (pkt 7–9);
- unikać ograniczeń prądu, mocy i krzyżowych (czas dla energii, kWh dla czasu), bo kierowca ich nie kontroluje (pkt 10);
- konfliktowe elementy (ten sam typ, te same ograniczenia, inna cena) MSP może odrzucić (pkt 11);
- „pierwsze X minut gratis” przez `PARKING_TIME` + `min_duration` znaczy technicznie „opłata, gdy sesja przekroczy X”
  (pkt 13); taryfę wysłać przed przypisaniem jej `id` do złącza (pkt 15); `PARKING_TIME` tylko przy innej cenie niż
  `TIME` (pkt 16); `start_date`/`end_date` w ograniczeniach tylko dla wyjątków, np. świąt (pkt 17).

### Rozbieżności specyfikacji i wytycznych
| Temat | Specyfikacja | Wytyczne | Rozstrzygnięcie |
|---|---|---|---|
| koniec dnia | „To stop at end of the day use: 00:00” `[OCPI230 §11.4.7]` | bez `end_time`, nie 23:59 ani 00:00 `[OCPI-TSG cz. 2 pkt 14]` | **Wniosek:** wysyłając, pomijasz `end_time`; odbierając, `00:00` czytasz jako koniec dnia (norma) |
| okres przez północ | dozwolony (`end_time < start_time`) `[OCPI230 §11.4.7]` | nie używać; podzielić na dwa składniki `[OCPI-TSG cz. 2 pkt 14]` | **Wniosek:** odbiorca musi go obsłużyć, nadawca go unika |
| północ i `day_of_week` | okres „wraps around to the next day”; do którego dnia tygodnia należy część po północy, tekst nie mówi `[OCPI230 §11.4.7]` | to mylące „especially when combined with a day_of_week restriction” `[OCPI-TSG cz. 2 pkt 14]` | specyfikacja nie określa. **Wniosek:** taryfę z takim oknem i `day_of_week` przy imporcie oznaczasz do wyjaśnienia z CPO |
| zmiana obowiązującej taryfy | możliwa: PUT z nową treścią, DELETE; także w trakcie sesji `[OCPI230 §11.1.1, §11.3.1]` | nigdy; nowa taryfa z nowym `id` `[OCPI-TSG cz. 2 pkt 8]` | wytyczne nie zmieniają normy 2.3.0; w OCPI 3.0 według wytycznych to obowiązek |
| metoda zmiany | interfejs odbiorcy taryf ma GET, PUT, DELETE `[OCPI230 §11.2.2]` | pisze o „PATCH/DELETE endpoints” `[OCPI-TSG cz. 2 pkt 8]` | normą jest specyfikacja: w 2.3.0 taryfę zmienia się przez PUT |
| konflikt elementów | obowiązuje pierwszy pasujący `[OCPI230 §11.3.1]` | MSP może odrzucić taryfę `[OCPI-TSG cz. 2 pkt 11]` | odrzucenie to decyzja umowna, nie wymóg OCPI |

## 7. Przykłady liczbowe ze specyfikacji i błędy w nich
Przykłady z `[OCPI230 §11.3.1.1]`, `[OCPI230 §11.4.2.1]` i `[OCPI230 §11.4.7]` (kwoty netto / brutto w EUR):
| Przykład | Wynik w specyfikacji |
|---|---|
| `ENERGY` 0,25/kWh, VAT 10%, 20 kWh | 5,00 / 5,50 |
| + `FLAT` 0,50 (VAT 20%) | 5,50 / 6,10: VAT liczony osobno dla każdego składnika |
| `min_price` 0,50 / 0,55 | 20 kWh: 5,00 / 5,50; poniżej 2 kWh: 0,50 / 0,55. To nie opłata startowa |
| `max_price` 10 / 11, `FLAT` 0,50 + `ENERGY` 0,25 | 50 kWh: 10,00 / 11,00 (limit); 30 kWh: 8,00 / 8,85 |
| + `PARKING_TIME` 2,00/h, krok 900 s, 40 min postoju | 7,00 / 7,90: płatne 45 min postoju |
| złożona: `FLAT` 2,50 (VAT 15%), `TIME` 1,00/h (VAT 20%), postój 5,00/h (VAT 10%), pon. 09:30, 165 min, 16 A, 42 min postoju | 9,00 / 10,30 (2,50 + 2,75 + 3,75). Ładowania się nie zaokrągla, bo po nim jest postój |
| `max_power`: 0,20/kWh < 16 kW, 0,35/kWh < 32 kW, 0,50/kWh bez ograniczeń; 1 kWh przy 6 kW, 40 kWh przy 48 kW, 0,5 kWh przy 4 kW | 20,30 netto: ograniczenie dotyczy chwili, nie sesji `[OCPI230 §11.4.7]` |
| `max_duration`: 30 min gratis, 0,25/kWh do 60 min, potem 0,40/kWh; 40 min, 5 kWh + 1,2 kWh | 0,30 netto `[OCPI230 §11.4.7]` |
| tabela przełączania elementów: `TIME` 1,20/h krok 1800 s do 17:00, 2,40/h krok 900 s od 17:00, postój 1,00/h krok 900 s do 20:00 | start 16:55, 10 min ładowania + 2 min postoju: 0,55; start 16:35, 35 min ładowania: 1,30 (25 min po 1,20 + 20 min po 2,40) `[OCPI230 §11.4.2.1]` |
| ad hoc `TIME` 1,90/h, VAT 5,2%, krok 300 s, 2,5 h | 4,75 / 5,00 |
| Ameryka Północna: `tax_included` `NO`, bez `vat`, C$ 2,00/h, 2,5 h | C$ 5,00 plus podatki według lokalnych przepisów; z `YES` i C$ 2,10/h: C$ 5,25 z podatkami |

Kwoty brutto w przykładach mają do trzech miejsc po przecinku (np. 2,875, 13,861) `[OCPI230 §11.3.1.1]`. **Wniosek:**
silnik liczy kwoty bez zaokrągleń pośrednich, a zaokrąglenie robi według reguły z umowy, bo OCPI jej nie podaje.

### Błędy w przykładach (sprawdzone przeliczeniem z JSON przykładu)
| Przykład | Specyfikacja | Przeliczenie (**Wniosek**) | Rozstrzygnięcie |
|---|---|---|---|
| złożona, sobota 13:30, 114 min przy 43 A, 71 min postoju `[OCPI230 §11.3.1.1]` | ładowanie 2,28; razem 12,28 / 13,861 | element `min_current: 32` na weekend ma 1,25/h: 114 min = 2,375; razem 12,375 / 13,975 (postój 75 min = 7,50 się zgadza) | liczba w tekście błędna; to samo w `[OCPI221 §11.3.1.1]` |
| przełączanie na element bez postoju, start 19:40, 12 min ładowania, 20 min postoju `[OCPI230 §11.4.2.1]` | 12 min po 1,20/h (0,20) + 15 min po 2,40/h (0,60) = 0,80 | 19:40–19:52 to element 17:00–20:00: 12 min po 2,40/h = 0,48; postój 19:52–20:00 = 8 min po 1,00/h, zaokrąglone do 15 min = 0,25; razem 0,73 | tabela przeczy JSON; reguła nadwyżki z tekstu jest poprawna. To samo w `[OCPI221 §11.4.2.1]` |
| `PROFILE_CHEAP`, krok 100 Wh, 20,45 kWh `[OCPI230 §11.3.1.1]` | tekst: energia 5,13, razem 5,63 / 6,24; tabela: 20,45 kWh, 5,11, razem 5,61 / 6,22 | 20,45 → 20,5 kWh × 0,25 = 5,125 | wiąże tekst; tabela 2.2.1 podaje 5,13 / 5,63 `[OCPI221 §11.3.1.1]` |
| ad hoc, wiele języków `[OCPI230 §11.3.1.1]` | `tariff_alt_text`: „2.00 euro p/hour including VAT.” obok `elements` | — | przeczy zasadzie, że przy `elements` tekst SHALL zawierać tylko dodatkowe informacje, nie ceny z `elements` `[OCPI230 §11.3.1]`. Wiąże zasada |

**Wniosek:** liczb z przykładów nie kopiujesz do testów bez przeliczenia. Przykłady liczbowe z innych źródeł niż PDF
specyfikacji (np. pliki JSON w repozytorium OCPI) nie są w rejestrze źródeł.

## 8. Różnice modelu taryfy: OCPI 2.2.1 a 2.3.0
| Pole | OCPI 2.2.1 `[OCPI221 §11.3.1, §11.4.2]` | OCPI 2.3.0 `[OCPI230 §11.3.1, §11.4.2]` |
|---|---|---|
| `PriceComponent.price` | „Price per unit (excl. VAT)” | z podatkiem albo bez, według `tax_included` |
| `PriceComponent.vat` | brak = VAT nie dotyczy; „Not providing a VAT is different from 0% VAT” | brak = VAT nie dotyczy |
| `tax_included` | nie ma | wymagane (`YES`, `NO`, `N/A`) |
| `min_price` / `max_price` | typ `Price`: `excl_vat` (wymagane), `incl_vat` `[OCPI221 §16.5]` | typ `PriceLimit`: `before_taxes`, `after_taxes` `[OCPI230 §11.4.3]` |
| `preauthorize_amount` | nie ma | jest |

- Zmiana podatków to w changelogu 2.3.0 „Support for North American taxes” `[OCPI230 §18.1]`.
- `OCPI221` to dokument 2.2.1-d2 (w środku oznaczony „2.2.1-d3-pre1”). Pierwotnego wydania 2.2.1 nie ma w rejestrze
  źródeł, więc różnic między nim a d2 baza nie sprawdza.
