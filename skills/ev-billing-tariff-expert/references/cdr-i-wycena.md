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
7. Rozbieżności w dokumentach

## 1. CDR jako dokument rozliczeniowy `[OCPI230 §10.3.1]`
- CDR jest „sealed”: zachowuje dane z chwili **startu** sesji, bo jego główne zastosowanie to fakturowanie. Location,
  EVSE, taryfy i token SHALL być takie, jak przy starcie sesji.
- `id` unikalny w obrębie `country_code`/`party_id`, zwykły CDR do 36 znaków; pole ma 39 znaków, żeby credit CDR mógł
  mieć dopisek do `id` oryginału.
- `start_date_time`: start sesji, a przy CDR za rezerwację (przed startem sesji) start rezerwacji. `end_date_time`: koniec
  sesji; ładowanie mogło skończyć się wcześniej (np. postój).
- `session_id` wolno pominąć tylko, gdy CPO nie wdrożył modułu Sessions albo CDR dotyczy rezerwacji, która nie stała się
  sesją.
- `cdr_location` (`CdrLocation`): tylko właściwe EVSE i złącze. Przy CDR za rezerwację bez sesji `evse_uid`, `evse_id` i
  `connector_id` mogą mieć wartość `#NA`, a pola typu złącza są dowolne, a odbiorca powinien („should”) je ignorować `[OCPI230 §10.4.4]`.
- `tariffs`: lista taryf istotnych dla sesji. W razie potrzeby także taryfa bezpłatna.
- `auth_method` (`AuthMethod`): `AUTH_REQUEST` (zapytanie do eMSP), `COMMAND` (np. `StartSession`, `ReserveNow`),
  `WHITELIST` (bez zapytania do eMSP) `[OCPI230 §10.4.1]`. Przy kilku metodach w sesji podaje się ostatnią (np.
  rezerwacja `COMMAND`, potem start tokenem z białej listy: `WHITELIST`).
- `authorization_reference`: ta sama wartość, którą eMSP podał w autoryzacji, `StartSession` albo `ReserveNow`; przy
  kilku wartościach ostatnia.
- `meter_id`: identyfikator licznika w punkcie. `remark`: tekst dla człowieka, np. powód zatrzymania. `last_updated`:
  czas ostatniej zmiany albo utworzenia.
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
| `invoice_reference_id` | nie | odnośnik do faktury (do 39 znaków); pozwala grupować CDR na jednej fakturze |
| `credit`, `credit_reference_id` | nie | credit CDR i `id` korygowanego CDR (do 39 znaków). Oba pola naraz, bo filtr po polu logicznym jest szybszy niż porównanie napisów |
| `home_charging_compensation` | nie | sesja na domowej ładowarce, za której energię kierowca dostaje zwrot |

- Czas ładowania: `total_time - total_parking_time` (uwaga w §10.3.1).
- `Price`: `before_taxes` wymagane, `taxes` jako lista `TaxAmount` (nazwa podatku, `amount` wymagane, opcjonalnie
  procent i numer konta podatkowego) `[OCPI230 §17.8, §17.9]`. W `taxes` są podatki istotne dla odbiorcy Session lub
  CDR. W OCPI 2.2.1 `Price` ma inne pola: `excl_vat` (wymagane) i `incl_vat` `[OCPI221 §16.5]`.
- Credit CDR zawiera wszystkie dane oryginału, a tylko wartości w `total_cost` są ujemne `[OCPI230 §10.1.1]`. **Wniosek:**
  w 2.3.0 ujemne są `before_taxes` i każde `taxes[].amount` w `total_cost`. Pozostałe pola `total_*` zostają jak w
  oryginale.
- Przykład CDR ze specyfikacji: taryfa `TIME` 2,00 €/h, VAT 10%, `step_size` 300; jeden okres `TIME` 1,973 h; `total_cost`
  i `total_time_cost`: `before_taxes` 4,00, VAT 0,40 `[OCPI230 §10.3.1.1]`. **Wniosek (obliczenie):** 1,973 h to
  7102,8 s, po zaokrągleniu do 300 s 7200 s = 2 h × 2,00 € = 4,00 €. Bez `step_size` wyszłoby 3,946 €.

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
- OICP 2.3 dla porównania: z `eRoamingChargeDetailRecord` usunięto `MeteringSignature`, a w jego miejsce weszły
  `SignedMeteringValues` i `CalibrationLawVerificationInfo` `[OICP23-RN #eRoamingChargeDetailRecord]`. Szczegóły OICP:
  skill `ev-ocpi-roaming-expert`.

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

### Obiekt `Terminal` `[OCPI230 §16.6.1]`
Jeden fizyczny terminal. Służy głównie do powiązania punktów (lokalizacje, EVSE) z terminalem i do danych płatności.
| Pole | Wymagane | Znaczenie |
|---|---|---|
| `terminal_id` | tak | identyfikator terminala; w żądaniu aktywacji opcjonalny, nadaje go PTP `[OCPI230 §16.5.1.7]` |
| `customer_reference` | nie | powiązanie terminala z CSMS; może pochodzić z zamówienia |
| `party_id`, `country_code` | nie | alternatywa dla `customer_reference` |
| `address`, `city`, `postal_code`, `state`, `country`, `coordinates` | nie | miejsce terminala; `country` w ISO 3166-1 alpha-3 |
| `invoice_base_url` | nie | adres bazowy faktury do pobrania |
| `invoice_creator` | nie | kto wystawia fakturę kierowcy (`InvoiceCreator`) |
| `reference` | nie | wartość nadana przez PTP do powiązania (np. numer seryjny) |
| `location_ids`, `evse_uids` | nie (`*`) | przypisane lokalizacje i EVSE |
| `last_updated` | tak | czas ostatniej zmiany albo utworzenia |

- Przypisania wysyła CPO przez PATCH. Gdy są oba pola, terminal obsługuje **sumę** EVSE z obu `[OCPI230 §16.5.1.5]`.
  Endpointy modułu opisuje skill `ev-ocpi-roaming-expert`.

### Obiekt Financial Advice Confirmation `[OCPI230 §16.6.2]`
| Pole | Wymagane | Znaczenie |
|---|---|---|
| `id` | tak | identyfikator potwierdzenia |
| `authorization_reference` | tak | ta sama referencja, którą PTP podał w `Commands.StartSession` |
| `total_costs` | tak | kwota naprawdę pobrana u PSP (capture), cena konsumencka z VAT (`Price`) |
| `currency` | tak | ISO 4217 |
| `eft_data` | tak (`+`) | dane płatności elektronicznej do faktury (lista napisów do 255 znaków) |
| `capture_status_code` | tak | `CaptureStatusCode` |
| `capture_status_message` | nie | komunikat o błędzie |
| `last_updated` | tak | czas ostatniej zmiany albo utworzenia |

- Obiekt jest potrzebny tylko wtedy, gdy fakturę wystawia CPO `[OCPI230 §16]`. Dane EFT są obowiązkowe na fakturze ze
  względów prawnych i regulacyjnych `[OCPI230 §16.6.2]`; jakie to przepisy, specyfikacja nie podaje.
- `PARTIAL_SUCCESS`: zatwierdzono tylko część kwoty albo zmieniono warunki płatności, np. przy braku środków
  `[OCPI230 §16.7.2]`. Co dalej z brakującą kwotą, specyfikacja nie określa.

### Aktywacja terminala `[OCPI230 §16.3]`
- Potrzebna zwykle dla terminala zintegrowanego ze stacją: CPO zamawia stację z terminalem u producenta, producent daje
  CPO referencję, CPO wysyła z nią żądanie aktywacji do PTP. PTP przypisuje referencję do terminala, aktywuje go i
  tworzy obiekt Terminal po stronie CPO.
- Uzasadnienie: PTP musi wcześniej wykonać konfigurację, np. uzyskać unikalny identyfikator dla adresu instalacji.
- Przypisanie terminala: PTP tworzy obiekt, CPO go pobiera albo dostaje, przypisuje lokalizacje i wysyła przypisanie
  do PTP `[OCPI230 §16.2]`. Dezaktywacja: np. przy awarii terminala albo zmianie adresu `[OCPI230 §16.5.1.8]`.

### Terminal w danych lokalizacji `[OCPI230 §8.4.3]`
Przy płatności ad hoc terminalem EVSE ma w `capabilities` kombinację: `CHIP_CARD_SUPPORT`, `CONTACTLESS_CARD_SUPPORT`,
`CREDIT_CARD_PAYABLE`, `DEBIT_CARD_PAYABLE`, `PED_TERMINAL` (klawiatura PIN).

### Kwota preautoryzacji
- W 2.3.0 PTP blokuje u PSP kwotę z `preauthorize_amount` taryfy `[OCPI230 §16.4]`.
- W module Direct Payment dla 2.2.1 kwotą blokady jest `max_price`, które musi być w taryfie (typ `Price`), a
  `Connector.tariff_ids` musi mieć co najmniej jedną taryfę `[OCPI-DP §6.1.1, §6.2.1]`.
- **Wniosek:** kwotę blokady bierzesz z wersji taryfy z chwili startu, bo taką taryfę zawiera CDR `[OCPI230 §10.3.1]`.
  Gdy taryfa ma `max_price`, a `preauthorize_amount` jest od niego niższe, sesję zatrzyma limit blokady (`StopSession`
  od PTP), zanim zadziała `max_price`.

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

**Wniosek: kontrole spójności CDR przy odbiorze** (reguły własne, nie wymagania OCPI; z §10.1, §10.3.1, §10.4.6):
- klucz CDR to (`country_code`, `party_id`, `id`). Ponowny odbiór tej samej treści traktujesz jak już przyjęty. Inna
  treść pod tym samym kluczem to anomalia, bo wysłanego CDR nie wolno zmienić. Jaki kod odpowiedzi zwrócić na duplikat,
  OCPI nie określa;
- jedna waluta: `currency` CDR i waluty taryf z `tariffs`;
- `total_time` zgodny z `end_date_time - start_date_time`, a czas ładowania `total_time - total_parking_time`;
- suma `ENERGY` z `charging_periods` zgodna z `total_energy`;
- credit CDR: `credit_reference_id` wskazuje znany CDR, a `total_cost` to ujemne wartości oryginału.

## 7. Rozbieżności w dokumentach
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| pola `Price` w module Payments | `Price` ma `before_taxes` i `taxes` `[OCPI230 §17.8]` | przykłady Financial Advice Confirmation mają `total_costs` z `excl_vat` i `incl_vat` `[OCPI230 §16.6.2]` | wiąże definicja typu (§17.8). Przykłady mają postać z modułu Direct Payment dla 2.2.1, gdzie `Price` to `excl_vat`/`incl_vat` `[OCPI-DP §5.2.3]` `[OCPI221 §16.5]` |
| przykład FAC z `FAILED` | `eft_data` ma krotność `+` (wymagane) `[OCPI230 §16.6.2]` | przykład nieudanego capture nie ma `eft_data` `[OCPI230 §16.6.2]` | wiąże tabela pól. **Wniosek:** odbiorca toleruje brak `eft_data` przy `FAILED`, nadawca je wysyła |
| taryfa w przykładzie CDR | `tax_included` wymagane w Tariff `[OCPI230 §11.3.1]` | taryfa w przykładzie CDR nie ma `tax_included` `[OCPI230 §10.3.1.1]` | wiąże tabela pól Tariff |
| CDR przy ad hoc | „no CDR is sent to an eMSP” `[OCPI230 §11.3.1.1]` | w module Payments CDR dostaje PTP `[OCPI230 §16.4]` | nie ma sprzeczności: eMSP nie uczestniczy, ale CDR powstaje i trafia do PTP |
