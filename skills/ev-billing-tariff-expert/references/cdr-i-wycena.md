# CDR, wycena sesji i płatności terminalowe (OCPI 2.3.0)

Źródło: specyfikacja OCPI 2.3.0 `[OCPI230]`. Mechanika wysyłki CDR i credit CDR (POST, niezmienność) jest opisana w
skillu `ev-ocpi-roaming-expert`; tu: z czego składa się koszt i jak go wyliczyć. Zdania **Wniosek** to rekomendacje.

## Spis treści
1. CDR jako dokument rozliczeniowy
2. Pola kosztów i ilości
3. Okresy ładowania (`ChargingPeriod`) i wymiary
4. Dane podpisane (`SignedData`)
5. Moduł Payments: terminal płatniczy
6. Procedura silnika wyceny

## 1. CDR jako dokument rozliczeniowy `[OCPI230 §10.3.1]`
- CDR jest „sealed”: zachowuje dane z chwili **startu** sesji, bo jego główne zastosowanie to fakturowanie. Location,
  EVSE, taryfy i token SHALL być takie, jak przy starcie sesji.
- `id` unikalny w obrębie `country_code`/`party_id`, zwykły CDR do 36 znaków; pole ma 39 znaków, żeby credit CDR mógł
  mieć dopisek do `id` oryginału.
- `tariffs`: lista taryf istotnych dla sesji. W razie potrzeby także taryfa bezpłatna.
- `auth_method`: przy kilku metodach w sesji podaje się ostatnią. `authorization_reference`: ostatnia wartość od eMSP.
- `start_date_time` / `end_date_time` nieznane → CPO zwykle nie może wysłać CDR. Wyjątek tylko przy zgodzie obu stron i
  dopuszczeniu przez prawo lokalne: wtedy wartość `1970-1-1T00:00:00Z`.

## 2. Pola kosztów i ilości `[OCPI230 §10.3.1, §17.8, §17.9]`
| Pole | Wymagane | Znaczenie |
|---|---|---|
| `currency` | tak | ISO 4217 |
| `total_cost` | tak | suma wszystkich kosztów (`Price`) |
| `total_fixed_cost` | nie | koszty stałe (np. opłata startowa) **bez** stałych składników parkowania i rezerwacji |
| `total_energy` | tak | energia w kWh |
| `total_energy_cost` | nie | koszt energii |
| `total_time` | tak | czas całej sesji w godzinach (ładowanie i postój) |
| `total_time_cost` | nie | koszt czasu ładowania |
| `total_parking_time` | nie | czas bez przepływu energii, w godzinach |
| `total_parking_cost` | nie | koszt parkowania, łącznie ze stałymi składnikami parkowania |
| `total_reservation_cost` | nie | koszt rezerwacji, łącznie ze stałymi składnikami rezerwacji |
| `invoice_reference_id` | nie | odnośnik do faktury; pozwala grupować CDR na jednej fakturze |
| `credit`, `credit_reference_id` | nie | credit CDR i `id` korygowanego CDR |
| `home_charging_compensation` | nie | sesja na domowej ładowarce, za której energię kierowca dostaje zwrot |

- Czas ładowania: `total_time - total_parking_time` (uwaga w §10.3.1).
- `Price`: `before_taxes` wymagane, `taxes` jako lista `TaxAmount` (nazwa podatku, `amount` wymagane, opcjonalnie
  procent i numer konta podatkowego) `[OCPI230 §17.8, §17.9]`.

## 3. Okresy ładowania i wymiary `[OCPI230 §10.3.1, §10.4.2, §10.4.3, §10.4.6]`
- CPO SHALL otworzyć nowy `ChargingPeriod` przy każdym zdarzeniu istotnym dla kosztu, czyli gdy zaczyna obowiązywać inny
  składnik ceny. Może dodawać więcej okresów pośrednich.
- Przykłady ze specyfikacji: zmiana ceny energii o 17:00 → nowy okres o 17:00, a w okresie kończącym się o 17:00 energia
  zużyta do 17:00; cena zależna od prądu > 32 A → nowy okres w chwili przekroczenia. Ten moment CPO może wyliczyć
  interpolacją pomiarów, gdy stacja go nie zgłasza.
- `ChargingPeriod`: `start_date_time` (okres kończy się startem następnego, ostatni z końcem sesji), `dimensions` (co
  najmniej jeden), opcjonalnie `tariff_id`. Brak `tariff_id` → w tym okresie żadna taryfa nie jest istotna.
- `CdrDimensionType` w CDR: `ENERGY` (kWh, ujemna przy przewadze oddawania do sieci), `MAX_CURRENT`, `MIN_CURRENT`,
  `MAX_POWER`, `MIN_POWER`, `PARKING_TIME`, `RESERVATION_TIME`, `TIME` (czasy w godzinach). `CURRENT`, `ENERGY_EXPORT`,
  `ENERGY_IMPORT`, `POWER`, `STATE_OF_CHARGE` są tylko dla Sessions.

## 4. Dane podpisane `[OCPI230 §10.4.7, §10.4.8]`
- `SignedData`: `encoding_method` (wymagane), `encoding_method_version`, `public_key` (base64), `signed_values` (co
  najmniej jeden), `url` dla kierowcy do sprawdzenia danych.
- `SignedValue`: `nature` (np. `Start`, `End`, `Intermediate`), `plain_data`, `signed_data` (base64).
- Specyfikacja wymienia przy niemieckim Eichrecht znane kodowania: OCMF, Alfen Eichrecht, EDL40 E-Mobility Extension,
  EDL40 Mennekes. Treść tych formatów i wymagań Eichrecht nie jest opracowana (domena D10.02).

## 5. Moduł Payments `[OCPI230 §16]`
- Właściciel danych: PTP (Payment Terminal Provider). Obiekty: `Terminal` i Financial Advice Confirmation. Jeden
  terminal może obsługiwać wiele lokalizacji lub EVSE; przypisania robi CPO `[OCPI230 §16, §16.2]`.
- Przebieg transakcji `[OCPI230 §16.4]`:
  1. terminal pobiera Location (złącze), z niego `tariff_id`, potem taryfę i pokazuje cenę;
  2. preautoryzacja u PSP na kwotę `preauthorize_amount` z taryfy;
  3. `StartSession` z `authorization_reference` (używany do powiązania faktury);
  4. zatrzymanie: przez pojazd lub stację, `StopSession` od PTP po osiągnięciu limitu preautoryzacji albo przez backend
     CPO (także przy osiągnięciu `max_price`);
  5. CDR. Wypełnione `invoice_reference_id` → fakturę wystawił CPO. Wtedy PTP po pobraniu środków (capture) wysyła
     Financial Advice Confirmation, a CPO uzupełnia fakturę o dane EFT. Puste → fakturę wystawia PTP.
- `InvoiceCreator`: `CPO` (faktura przez `invoice_base_url` + `authorization_reference`) albo `PTP` (faktura na
  terminalu). `CaptureStatusCode`: `SUCCESS`, `PARTIAL_SUCCESS`, `FAILED` `[OCPI230 §16.7]`.

## 6. Procedura silnika wyceny
**Wniosek** (z §10.3.1, §11.3.1, §11.4.2, §11.4.7):
1. Ustal taryfę z chwili startu sesji i jej strefę czasową z Location.
2. Podziel sesję na okresy w każdym punkcie zmiany: godzina i dzień, progi kWh i czasu, prąd lub moc, start i koniec
   postoju.
3. W każdym okresie wybierz osobno dla każdego wymiaru pierwszy pasujący element. Wymiar bez elementu → 0.
4. Zsumuj zużycie wymiaru w sesji i zastosuj `step_size` raz, według ostatniego istotnego składnika. Przy `TIME` i
   `PARKING_TIME` zaokrąglasz tylko parkowanie.
5. Policz koszty składników, potem `min_price` / `max_price` przed i po podatkach.
6. Zaokrąglenie kwot według prawa, umowy i waluty, bo OCPI go nie określa. Zasadę zapisujesz w umowie roamingowej.
7. Wypełnij pola `total_*`, `charging_periods` z `tariff_id` i wyślij CDR. Korekta tylko przez credit CDR.
