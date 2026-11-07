# Taryfy OCPI 2.3.0: struktura, pierwszeństwo, ograniczenia, `step_size`

Źródła: specyfikacja OCPI 2.3.0 `[OCPI230]` i wytyczne EVRF „Tariff simplification … using OCPI v2.3”, wersja 1.0 z
2026-07-09 `[OCPI-TSG]`. Wytyczne dotyczą 2.3.0, ale według autorów większość z nich nadaje się też do 2.2.1
`[OCPI-TSG Preface]`. Zdania **Wniosek** to rekomendacje wyprowadzone z cytowanych faktów.

## Spis treści
1. Obiekt Tariff
2. Który element obowiązuje (pierwszeństwo)
3. Ograniczenia (`TariffRestrictions`)
4. `step_size` w całej sesji
5. Zmiana taryfy i jej ważność
6. Wytyczne uproszczenia taryf i rozbieżności ze specyfikacją

## 1. Obiekt Tariff `[OCPI230 §11.3.1]`
- Budowa: Tariff → lista `TariffElement` → lista `PriceComponent`. Element to grupa składników obowiązujących przy tych
  samych warunkach (ograniczeniach).
- Pola wymagane: `country_code`, `party_id`, `id`, `currency` (ISO-4217), `elements`, `tax_included`, `last_updated`.
- `type` (`TariffType`): `AD_HOC_PAYMENT`, `PROFILE_CHEAP`, `PROFILE_FAST`, `PROFILE_GREEN`, `REGULAR`. Bez `type` taryfa
  dotyczy wszystkich sesji `[OCPI230 §11.4.8]`.
- `tax_included`: `YES`, `NO`, `N/A` `[OCPI230 §11.4.9]`. `PriceComponent.price` jest z podatkiem albo bez, zależnie od
  `tax_included`. `PriceComponent.vat`: gdy brak, VAT nie ma zastosowania `[OCPI230 §11.4.2]`.
- `min_price` / `max_price` (`PriceLimit`): sesja kosztuje co najmniej / co najwyżej tyle. Obowiązują **obie** wartości,
  przed i po podatkach, bo podatki mogą być różne dla części sesji.
- `preauthorize_amount`: kwota, którą dostawca terminala płatniczego (PTP) powinien zablokować przy płatności kartą.
- `tariff_alt_text` przy obecnych `elements` SHALL zawierać tylko informacje dodatkowe, nie ceny z `elements`
  (eMSP może mieć własne opłaty).
- **Zaokrąglanie cen:** OCPI nie ma pól ani wymagań co do zaokrąglania. Robi się je według prawa, umów między stronami
  i waluty. „The OCPI specification stays out of these matters.”
- Taryfa bezpłatna: jeden element bez ograniczeń z jednym składnikiem `FLAT` o cenie `0.00`.

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
- Ograniczenia w jednym elemencie łączą się logicznym AND.
- `start_time` / `end_time`: czas lokalny według `time_zone` z Location, format `HH:MM`. Gdy `end_time < start_time`,
  okres przechodzi na następny dzień. „To stop at end of the day use: 00:00.”
- `start_date` włącznie, `end_date` wyłącznie (czas lokalny).
- `min_kwh` włącznie, `max_kwh` wyłącznie (energia zużyta w sesji).
- `min_current` / `max_current` (suma po fazach, A) i `min_power` / `max_power` (kW) dotyczą wartości chwilowej, nie
  całej sesji. Element MUST przestać obowiązywać, gdy prąd lub moc przekroczy próg.
- `min_duration` włącznie, `max_duration` wyłącznie, w sekundach od początku sesji.
- `day_of_week`: lista dni.
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

## 5. Zmiana taryfy i ważność `[OCPI230 §11.3.1]`
- `start_date_time` / `end_date_time` (UTC): od kiedy taryfa obowiązuje i po kiedy przestaje.
- OCPI **nie zabrania** zmiany taryfy w trakcie sesji. Typowo zmienia się ją dopiero po sesji. W wielu krajach prawo
  konsumenckie zabrania zmiany w trakcie: kierowca akceptuje taryfę obowiązującą przy starcie.
- CDR zawiera taryfy w wersji z chwili startu sesji `[OCPI230 §10.3.1]`.

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
| zmiana obowiązującej taryfy | możliwa: PUT z nową treścią, DELETE; także w trakcie sesji `[OCPI230 §11.1.1, §11.3.1]` | nigdy; nowa taryfa z nowym `id` `[OCPI-TSG cz. 2 pkt 8]` | wytyczne nie zmieniają normy 2.3.0; w OCPI 3.0 według wytycznych to obowiązek |
| metoda zmiany | interfejs odbiorcy taryf ma GET, PUT, DELETE `[OCPI230 §11.2.2]` | pisze o „PATCH/DELETE endpoints” `[OCPI-TSG cz. 2 pkt 8]` | normą jest specyfikacja: w 2.3.0 taryfę zmienia się przez PUT |
| konflikt elementów | obowiązuje pierwszy pasujący `[OCPI230 §11.3.1]` | MSP może odrzucić taryfę `[OCPI-TSG cz. 2 pkt 11]` | odrzucenie to decyzja umowna, nie wymóg OCPI |
