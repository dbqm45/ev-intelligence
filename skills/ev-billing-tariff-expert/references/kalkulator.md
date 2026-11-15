# Kalkulator ceny sesji z taryfy OCPI (`scripts/ocpi_tariff_calc.py`)

Źródła: specyfikacja OCPI 2.3.0 `[OCPI230]`, OCPI 2.2.1-d2 `[OCPI221]` i wytyczne EVRF `[OCPI-TSG]`. Zdania **Wniosek**
to rekomendacje wyprowadzone z cytowanych faktów. Zdania „zachowanie narzędzia” opisują wybór skryptu tam, gdzie
specyfikacja czegoś nie określa.

## Spis treści
1. Do czego służy
2. Uruchomienie
3. Wejście
4. Wyjście i kody wyjścia
5. Reguły wyceny
6. Podatki i limity cen
7. Czego narzędzie nie liczy
8. Błędy w przykładach specyfikacji

## 1. Do czego służy
- Liczy koszt sesji z taryfy OCPI dla okresów ładowania (`charging_periods`) i porównuje wynik z kosztami w CDR.
- Obsługuje dwa modele cen: 2.3.0 (`tax_included`, `PriceLimit`, `Price` z `before_taxes` i `taxes`) i 2.2.1
  (`Price` z `excl_vat` i `incl_vat`).
- Tylko biblioteka standardowa Pythona, bez sieci. Strefy czasowe z `zoneinfo` (na Windowsie potrzebny pakiet `tzdata`).

**Wniosek:** CDR zawiera taryfy w wersji z chwili startu sesji `[OCPI230 §10.3.1]`, więc koszt z CDR da się odtworzyć
później: taryfę bierzesz z pola `tariffs` tego CDR.

## 2. Uruchomienie
```bash
python3 skills/ev-billing-tariff-expert/scripts/ocpi_tariff_calc.py <taryfa.json> <okresy.json> \
    [--cdr <cdr.json>] [--ocpi auto|2.3.0|2.2.1] [--tz Europe/Warsaw] [--tolerance 0.01] [--json]
```
- `--tz`: strefa z `Location.time_zone`. Restrykcje czasu i daty są w czasie lokalnym lokacji `[OCPI230 §11.4.7]`.
  Domyślnie UTC.
- `--ocpi auto` (domyślnie) ustala model z danych (pkt 3).
- `--tolerance`: dopuszczalna różnica kwot i czasów przy porównaniu z CDR. To próg narzędzia, nie wartość z OCPI.
- Testy: `python3 -m unittest tests.test_ocpi_tariff_calc`.

## 3. Wejście
- Taryfa: obiekt `Tariff`, także w kopercie odpowiedzi OCPI (`data`, `status_code`). Lista taryf jest dozwolona, gdy
  ma jedną taryfę albo gdy okresy wskazują jedną z nich polem `tariff_id` `[OCPI230 §10.4.6]`.
- Okresy: obiekt z `start_date_time`, `end_date_time` i `charging_periods`. Może to być sam CDR.
- Wymiary okresu (`CdrDimension`): `ENERGY` w kWh, `TIME` i `PARKING_TIME` w godzinach, `MIN_CURRENT`/`MAX_CURRENT`
  w A, `MIN_POWER`/`MAX_POWER` w kW `[OCPI230 §10.4.3]`.
- Wybór modelu przy `auto`:

| Znacznik w danych | Model |
|---|---|
| `tax_included` w taryfie albo `before_taxes`/`after_taxes`/`taxes` w limitach lub kosztach | 2.3.0 |
| `excl_vat`/`incl_vat` w limitach lub kosztach | 2.2.1 |
| znaczniki obu modeli | błąd wejścia (kod 2) |
| brak znaczników | 2.2.1 z ostrzeżeniem |

Uzasadnienie ostatniego wiersza: w 2.3.0 pole `tax_included` jest wymagane `[OCPI230 §11.3.1]`, a w 2.2.1 go nie ma
`[OCPI221 §11.3.1]`. Przykład CDR w 2.3.0 ma taryfę bez `tax_included` `[OCPI230 §10.3.1.1]`. Zachowanie narzędzia:
model wynika wtedy z kosztów CDR (`before_taxes`), a brak `tax_included` czyta jako `NO` z ostrzeżeniem.

## 4. Wyjście i kody wyjścia
- Pola kosztów jak w CDR: `total_cost`, `total_fixed_cost`, `total_energy_cost`, `total_time_cost`,
  `total_parking_cost` `[OCPI230 §10.3.1]`. Wymiar bez ceny ma `null`.
- 2.3.0: `{"before_taxes", "taxes": [{"name": "VAT", "percentage", "amount"}], "after_taxes"}`. Klasa `Price` ma tylko
  `before_taxes` i `taxes` `[OCPI230 §17.8]`, a `TaxAmount` ma `name`, `account_number`, `percentage`, `amount`
  `[OCPI230 §17.9]`. **`after_taxes` w wyniku to pole pomocnicze narzędzia.** Przed wpisaniem do CDR je usuwasz.
- 2.2.1: `{"excl_vat", "incl_vat"}` `[OCPI221 §16.5]`.
- `total_energy` (kWh), `total_time` (cała sesja w h), `total_parking_time` (suma `PARKING_TIME`, czas faktyczny,
  nie po `step_size`) `[OCPI230 §10.3.1]`.
- `lines`: rozbicie na okres, wymiar i numer elementu, wolumen przed i po `step_size`, cena, koszt. `warnings`:
  założenia i pominięcia.
- `--cdr`: lista `cdr_diffs` (pole, wyliczone, w CDR). W 2.3.0 porównuje `before_taxes` i sumę `taxes.amount`, gdy CDR
  podaje `taxes`.
- Kod wyjścia: 0 (policzone i zgodne z CDR), 1 (rozbieżność z CDR większa niż `--tolerance`), 2 (błąd wejścia, np.
  zły JSON, nieznana strefa, `tax_included` spoza `YES`/`NO`/`N/A`, CDR w innym modelu niż obliczenie).

## 5. Reguły wyceny
| Reguła | Źródło | W narzędziu |
|---|---|---|
| dla każdego wymiaru osobno pierwszy element z jego składnikiem i pasującymi restrykcjami; brak → wymiar nic nie kosztuje | `[OCPI230 §11.3.1, §11.4.5]` | tak |
| restrykcje łączy AND | `[OCPI230 §11.4.7]` | tak |
| CPO zaczyna nowy okres, gdy aktywny staje się inny składnik; okres kończy się startem następnego | `[OCPI230 §10.3.1, §10.4.6]` | restrykcje liczone na początku okresu |
| `start_date` włącznie, `end_date` wyłącznie; `min_kwh` włącznie, `max_kwh` wyłącznie; `min_duration` włącznie, `max_duration` wyłącznie | `[OCPI230 §11.4.7]` | tak; energia i czas trwania liczone do początku okresu |
| `min_current`/`min_power` aktywne przy „more than, or equal to”, `max_current`/`max_power` przy „less than” | `[OCPI230 §11.4.7]` | tak (32 A pasuje do `min_current: 32`, nie do `max_current: 32`) |
| `end_time < start_time` przechodzi na następny dzień; `00:00` jako koniec dnia | `[OCPI230 §11.4.7]` | tak |
| `day_of_week: []` znaczy „w żaden dzień”; `0` nie znaczy „brak restrykcji” | `[OCPI-TSG cz. 2 pkt 5, pkt 6]` | tak |
| `step_size`: w górę do wielokrotności; mnożnik 1 Wh / 1 s; `FLAT` bez mnożnika | `[OCPI230 §11.4.2, §11.4.6]` | tak |
| `step_size` raz na sesję dla `ENERGY` i raz łącznie dla `TIME` z `PARKING_TIME`; liczy się suma sesji; krok ostatniego istotnego składnika; przy `TIME` i `PARKING_TIME` zaokrągla się tylko parkowanie | `[OCPI230 §10.3.1]` | tak |
| nadwyżka z zaokrąglenia czasu trafia do ostatniego okresu ze składnikiem czasowym; dla `ENERGY` specyfikacja tego nie mówi | `[OCPI230 §11.4.2.1]` („The extra 7 minutes are then added to the last period with a Price Component with a time-based dimension”), `[OCPI230 §10.3.1]` („24 minutes after 17:00 will be billed”) | tak; dla `ENERGY` też ostatni okres z jej składnikiem |

Czego specyfikacja nie określa (zachowanie narzędzia):
- Czy `end_time` jest wyłączny. Tekst mówi tylko „valid until this time of the day” `[OCPI230 §11.4.7]`. Narzędzie
  traktuje go jako wyłączny.
- Do którego dnia tygodnia należy część okna po północy. Narzędzie sprawdza `day_of_week` w dniu lokalnym startu okresu.
- Którą wartość prądu lub mocy okresu porównać z restrykcją. Narzędzie bierze `MIN_*` dla `min_*` i `MAX_*` dla `max_*`,
  potem średnią `CURRENT`/`POWER` (wartości tylko dla Sessions `[OCPI230 §10.4.3]`), potem drugą skrajną. Moc wylicza
  też jako `ENERGY`/`TIME`. Bez danych pomija element z ostrzeżeniem.
- Czy `FLAT` liczy się raz na sesję. Narzędzie liczy go raz, w pierwszym okresie, w którym pasuje.
- Zaokrąglanie cen. OCPI go nie reguluje: „The OCPI specification stays out of these matters” `[OCPI230 §11.3.1]`.
  Narzędzie liczy na `Decimal` i zaokrągla tylko wynik do 4 miejsc (ROUND_HALF_UP). Liczby w OCPI mają domyślnie
  4 miejsca po przecinku `[OCPI230 §17.7]`.
- Próg przed `step_size`. Wolumeny w CDR mają 4 miejsca, więc 40 min to 0,6667 h = 2400,12 s. Narzędzie zaokrągla sumę
  do 1 s (czas) i 0,01 Wh (energia), żeby niedokładność zapisu nie dawała dodatkowego kroku.

## 6. Podatki i limity cen
| `tax_included` `[OCPI230 §11.4.9]` | Narzędzie |
|---|---|
| `NO` | `before_taxes` = cena × wolumen; VAT = `before_taxes` × `vat` %. Składnik bez `vat`: VAT nie ma zastosowania `[OCPI230 §11.4.2]`. Inne podatki doliczane poza taryfą (przykład północnoamerykański `[OCPI230 §11.3.1.1]`) narzędzie pomija z ostrzeżeniem |
| `YES` z `vat` | `after_taxes` = cena × wolumen, `before_taxes` = `after_taxes` / (1 + `vat` %) |
| `YES` bez `vat` | `before_taxes` = `null` z ostrzeżeniem: z taryfy nie da się go wyliczyć |
| `N/A` | brak podatków; `vat` pominięty z ostrzeżeniem |

- W 2.2.1 `price` jest bez VAT, a brak `vat` to co innego niż `0.0` `[OCPI221 §11.4.2]`.
- `TaxAmount` narzędzie grupuje według stawki `vat` (`name: "VAT"`, `percentage`).
- `min_price` i `max_price` obowiązują osobno przed i po podatkach `[OCPI230 §11.3.1]`. W 2.3.0 to `PriceLimit`
  z wymaganym `before_taxes` i opcjonalnym `after_taxes` `[OCPI230 §11.4.3]`, w 2.2.1 to `Price` `[OCPI221 §11.3.1]`.
  Gdy limitu po podatkach nie ma, narzędzie stosuje tylko limit przed podatkami.
- Jak rozłożyć podatki po zadziałaniu limitu, OCPI nie określa. Narzędzie podaje wtedy jedną pozycję `VAT` z różnicą
  i ostrzega.

## 7. Czego narzędzie nie liczy
- Rezerwacji: elementy z `reservation` i wymiar `RESERVATION_TIME` pomija z ostrzeżeniem, a `total_reservation_cost`
  nie liczy. Zasady rezerwacji: `[OCPI230 §11.4.4, §11.4.7]`.
- Kilku taryf w jednej sesji. Okres z innym `tariff_id` daje ostrzeżenie, a liczony jest jedną taryfą.
  `step_size` nie przechodzi między taryfami `[OCPI230 §10.3.1]`.
- Rozdziału `FLAT` na parkowanie. Cały `FLAT` trafia do `total_fixed_cost`, a OCPI wyłącza z niego stałe opłaty za
  parkowanie i rezerwację `[OCPI230 §10.3.1]`.
- Ważności taryfy: `start_date_time`/`end_date_time` tylko sprawdza i ostrzega `[OCPI230 §11.3.1]`.
- Podatków spoza `vat` (np. podatek od sprzedaży w USA i Kanadzie).

## 8. Błędy w przykładach specyfikacji
Testy sprawdzają regułę z tekstu, nie arytmetykę przykładu.

| Przykład | Specyfikacja | Z reguł i cen taryfy | Rozstrzygnięcie |
|---|---|---|---|
| złożona taryfa, sobota, 114 min × 1,25 €/h | 2,28; razem 12,28 / 13,861 `[OCPI230 §11.3.1.1]` | 2,375; razem 12,375 / 13,975 | błąd arytmetyczny przykładu |
| „switching to Free-of-Charge Tariff Element” | 0,80, w tabeli 12 min × 1,20 €/h i parkowanie po 2,40 €/h `[OCPI230 §11.4.2.1]` | 19:40–20:00 obowiązuje element 17:00–20:00: 12 min × 2,40 + 15 min × 1,00 = 0,73 | tabela i suma błędne; tak samo w `[OCPI221 §11.4.2.1]` |
| taryfa `PROFILE_CHEAP`, 20,45 kWh, `step_size` 100 | tekst: energia 5,13 / 5,64, razem 5,63 / 6,24; tabela: 5,11 / 5,62 i 5,61 / 6,22 `[OCPI230 §11.3.1.1]` | 20,5 kWh: 5,125 / 5,6375, razem 5,625 / 6,2375 | tabela 2.3.0 pomija `step_size`; tabela 2.2.1 ma 5,13 `[OCPI221 §11.3.1.1]` |
