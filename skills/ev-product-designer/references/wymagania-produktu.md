# Wymagania produktu wynikające z przepisów i protokołów

Źródła: AFIR `[AFIR]`, ustawa o elektromobilności `[PL-EMOB]` i rozporządzenie `[PL-R1316]`, OCPP 2.0.1 część 2
`[201-P2]`, OCPI 2.3.0 `[OCPI230]`, akt wykonawczy AFIR 2025/655 `[AFIR-655]` z mapowaniem EVRF `[OCPI-NAP-MAP]`,
dyrektywa 2019/882 `[EAA]` i ustawa o dostępności `[PL-DOST]`. Każde wymaganie ma znacznik. Zdania **Wniosek** to
propozycje projektowe, a nie wymagania. Czego źródła nie określają (UX, ekonomika, wykorzystanie stacji), opisuje sekcja 7.

## Spis treści
1. Ścieżka kierowcy: znalezienie stacji
1a. Dane lokalizacji: wartości pól OCPI i dane AFIR dla NAP
2. Start sesji i płatność
3. Informacja o cenie i koszcie
4. Problem i pomoc
5. Dostępność
5a. Dane rynkowe
6. Produkt operatora i partnera
6a. Platforma eMSP: tokeny, karty, zdalny start
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

## 1a. Dane lokalizacji: wartości pól OCPI i dane AFIR dla NAP
**Location** `[OCPI230 §8.3.1]`:
- `publish = false`: tylko tokeny pasujące do wszystkich ustawionych pól jednego wpisu `publish_allowed_to`. Gdy w tej
  samej lokalizacji są EVSE publikowane i niepublikowane, tworzy się dwie Location. Wpis `PublishTokenType` SHALL mieć
  co najmniej `uid`, `visual_number` albo `group_id`; przy `uid` SHALL być `type`, przy `visual_number` SHALL być
  `issuer` `[OCPI230 §8.4.24]`.
- `address` i `city` obowiązkowe, `postal_code` można pominąć tylko gdy lokalizacja nie ma kodu (np. autostrada),
  `country` w ISO 3166-1 alfa-3, `time_zone` obowiązkowa wartość IANA tzdata (np. „Europe/Oslo”).
- `operator` opcjonalny; gdy go brak, bierzesz dane z modułu Credentials według `country_code` i `party_id`.
- `charging_when_closed` domyślnie `true`. `help_phone` to `CiString(25)`.
- `parking_places` (obiekty `Parking`, nowe w 2.3.0) i `related_locations` (dodatkowe punkty dla użytkownika).
- **Współrzędne** `[OCPI230 §8.4.16]`: WGS 84, kropka dziesiętna, 5–7 miejsc po przecinku według wyrażenia regularnego.
  Pięć miejsc to minimum (około 1 m), siedem daje około 1 cm.
- **Godziny** `[OCPI230 §8.4.17]`: `twentyfourseven` obowiązkowe; `regular_hours` tylko przy `twentyfourseven=false` i
  wtedy co najmniej jeden wpis; `exceptional_openings` dodają okresy, `exceptional_closings` nadpisują godziny
  regularne i otwarcia wyjątkowe.
- **`parking_type`** `[OCPI230 §8.4.22]`: `ALONG_MOTORWAY`, `PARKING_GARAGE`, `PARKING_LOT`, `ON_DRIVEWAY`, `ON_STREET`,
  `UNDERGROUND_GARAGE`.
- **`facilities`** `[OCPI230 §8.4.15]`: `HOTEL`, `RESTAURANT`, `CAFE`, `MALL`, `SUPERMARKET`, `SPORT`, `RECREATION_AREA`,
  `NATURE`, `MUSEUM`, `BIKE_SHARING`, `BUS_STOP`, `TAXI_STAND`, `TRAM_STOP`, `METRO_STATION`, `TRAIN_STATION`,
  `AIRPORT`, `PARKING_LOT`, `CARPOOL_PARKING`, `FUEL_STATION`, `WIFI`.

**EVSE** `[OCPI230 §8.3.2]`:
- `floor_level` (`string(4)`, numeracja lokalna w garażu), `physical_reference` (`string(16)`, napis na urządzeniu),
  `directions` wielojęzyczne, `images`.
- `status_schedule`: planowane statusy, informacyjnie do planowania podróży; okres MAY nie mieć końca. Gdy status się
  zmieni, CPO musi wysłać aktualizację pola `status` `[OCPI230 §8.4.27]`.
- `parking_restrictions` (ograniczenia poza typem pojazdu) `[OCPI230 §8.4.21]`: `CUSTOMERS`, `DISABLED`, `EMPLOYEES`,
  `EV_ONLY`, `MOTORCYCLES`, `PLUGGED`, `TAXIS`, `TENANTS`.
- `accepted_service_providers`: nazwy eMSP z płatnością umowną akceptowanych na EVSE, dodane dla obowiązku wobec NAP w
  UE; poza tym obowiązkiem pole można pominąć.
- `capabilities` istotne dla kierowcy `[OCPI230 §8.4.3]`: terminal płatniczy opisuje kombinacja `CHIP_CARD_SUPPORT`,
  `CONTACTLESS_CARD_SUPPORT`, `CREDIT_CARD_PAYABLE`, `DEBIT_CARD_PAYABLE`, `PED_TERMINAL`; dalej `RFID_READER`,
  `RESERVABLE`, `REMOTE_START_STOP_CAPABLE`, `TOKEN_GROUP_CAPABLE` (sesję można zacząć jednym tokenem, a zakończyć
  drugim, np. karta i brelok), `UNLOCK_CAPABLE`.
- Plug & Charge na złączu: `ISO_15118_2_PLUG_AND_CHARGE`, `ISO_15118_20_PLUG_AND_CHARGE`. Wartość sygnalizuje, że
  kierowca naprawdę może użyć funkcji; samo wsparcie normy przez sprzęt nie wystarcza `[OCPI230 §8.4.4]`.

**Parking i pojazdy (2.3.0)** `[OCPI230 §8.3.4]`:
- obiekt dodany, by CPO w UE spełnili wymóg AFIR raportowania miejsc postojowych do NAP; odbiorcy inni niż NAP mogą go
  ignorować;
- `vehicle_types` obowiązkowe, `restricted_to_type` i `reservation_required` obowiązkowe; wymiary i masa (`max_vehicle_*`
  w kg i cm, wymiary miejsca), `dangerous_goods_allowed`, `drive_through`, `time_limit` (minuty), `roofed`, `lighting`,
  `refrigeration_outlet`, `standards`, `apds_reference`; przy typie `DISABLED` powinno być co najmniej jedno zdjęcie;
- `EVSEParking` łączy EVSE z miejscem (`parking_id`) i podaje położenie `LEFT`, `RIGHT`, `CENTER` `[OCPI230 §8.4.12]`
  `[OCPI230 §8.4.13]`;
- `VehicleType` `[OCPI230 §8.4.28]`: `MOTORCYCLE` (L), `PERSONAL_VEHICLE` (M1), `PERSONAL_VEHICLE_WITH_TRAILER`,
  `VAN` (N1, wysokość poniżej 275 cm), `SEMI_TRACTOR`, `RIGID`, `TRUCK_WITH_TRAILER`, `BUS`, `DISABLED`. Kody UNECE
  są przybliżone; OCPI celowo używa własnej kategoryzacji.

**AFIR 2025/655, tabela A (dane statyczne stacji)** `[AFIR-655 Annex, tabela A]` i odpowiedniki OCPI według EVRF
`[OCPI-NAP-MAP]`:

| Dana AFIR (poziom) | Format AFIR | OCPI 2.3.0 | Różnica |
|---|---|---|---|
| telefon helpdesku (stacja) | kod kraju, spacja, pełny numer; numer wewnętrzny po myślniku; bez innych myślników, spacji, nawiasów | `help_phone` | OCPI nie narzuca formatu |
| udogodnienia (stacja) | tak/nie: zadaszenie, oświetlenie, gastronomia, toalety, odpoczynek, inne | `facilities`, `Parking` | toalet nie ma w `Facility` |
| kraj (stacja) | ISO 3166-1 alfa-2 | `country` (alfa-3) | inny kod |
| godziny otwarcia, strefa czasowa (stacja) | dni tygodnia i przedziały; strefa według ISO 8601 | `opening_times`, `time_zone` (IANA) | inny format strefy |
| typy pojazdów (stacja) | L, M1, M2/M3, N1, N2/N3, inne | `Parking.vehicle_types` | kategorie OCPI przybliżone |
| wymiary i masa (stacja) | tony i metry, z przyczepą | `max_vehicle_*` | kg i cm |
| liczba miejsc, miejsca dla osób z niepełnosprawnościami (stacja) | liczba całkowita | liczba obiektów `Parking`, typ `DISABLED` | trzeba policzyć |
| czytnik kart, zbliżeniowo (stacja) | tak/nie | `CHIP_CARD_SUPPORT`, `CONTACTLESS_CARD_SUPPORT` w EVSE | poziom EVSE |
| inne ad hoc: QR dynamiczny, strona www, gotówka (stacja) | tak/nie | brak; EVRF: „TBD” | brak pola |

Z tabeli B `[AFIR-655 Annex, tabela B]`: ID punktu z kodem operatora od IDRO (w OCPI `evse_id`), lista MSP z płatnością
umowną akceptowanych na **stacji** (w OCPI `accepted_service_providers` na **EVSE**), Plug & Charge na **punkcie**
(w OCPI na **złączu**, §8.4.4). Mapowanie EVRF wskazuje dla Plug & Charge pole `Capabilities` EVSE `[OCPI-NAP-MAP]`,
a wartości Plug & Charge są w enumie złącza `[OCPI230 §8.4.4]`. **Rozstrzygnięcie:** wiąże specyfikacja OCPI.
Identyfikatory i formaty kodów: skill `ev-domain-expert` (`references/identyfikatory-i-role.md`).

**Wniosek:** formularz lokalizacji w panelu CPO zbiera dane w jednostkach i kodach OCPI, a eksport do NAP przelicza
(alfa-3 na alfa-2, kg na tony, cm na metry, EVSE na stację). Test: dla każdej stacji eksport zawiera liczbę miejsc
i listę akceptowanych MSP jako sumę z jej EVSE.

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

## 5a. Dane rynkowe
Liczby infrastruktury i floty (PL, UE, DE) oraz struktura cen: `references/rynek-dane.md`.

## 6. Produkt operatora i partnera
- Statusy, alarmy, działania zdalne i KPI dostępności: skille `ev-cpms-architect` i `ev-charging-operations-expert`.
- Dane rozliczeniowe dla partnerów: CDR z polami kosztów i czasu (`total_time`, `total_parking_time`)
  `[OCPI230 §10.3.1]`; skill `ev-billing-tariff-expert`.
- Pola CDR do raportów `[OCPI230 §10.3.1]`: obowiązkowe `total_cost`, `total_energy` (kWh), `total_time` (godziny, z
  czasem bez ładowania); opcjonalne `total_fixed_cost`, `total_energy_cost`, `total_time_cost`, `total_parking_time`
  (godziny bez przepływu energii), `total_parking_cost`, `total_reservation_cost`, `invoice_reference_id`, `credit` z
  `credit_reference_id` (CDR korygujący), `home_charging_compensation`.
- Dane dla regulatora i rejestrów: EIPA w PL, NAP w UE (skill `ev-compliance-expert`).

**Wniosek:** wskaźniki wykorzystania (np. godziny ładowania i postoju na punkt) można liczyć z pól CDR
`total_time` i `total_parking_time`. OCPI ich nie definiuje jako KPI, więc definicję wskaźnika zapisujesz w produkcie
jawnie. Raport przychodu odejmuje CDR z `credit = true` od CDR, do którego się odnoszą.

## 6a. Platforma eMSP: tokeny, karty, zdalny start
Właścicielem danych Tokens jest MSP; CPO buduje z nich pamięć podręczną i wie, do którego eMSP wysłać CDR `[OCPI230 §12]`.
- **Wydanie i zmiana karty:** nowy token eMSP wysyła PUT-em do CPO, zmiany PUT-em albo PATCH-em. Gdy eMSP nie jest
  pewien stanu tokenu u CPO, MAY sprawdzić go GET-em `[OCPI230 §12.1.1]`. PATCH SHALL zawierać `last_updated`
  `[OCPI230 §12.2.1.3]`.
- **Zablokowanie (zgubienie, koniec umowy):** tokenu nie da się usunąć; eMSP wysyła go z `valid = false` `[OCPI230 §12.1.1]`.
- **Pull:** CPO pobiera pełną listę dla synchronizacji (np. przy starcie albo co X godzin), nie przy każdej
  autoryzacji `[OCPI230 §12.1.2]`.
- **`whitelist`** `[OCPI230 §12.4.5]`:
  - `ALWAYS`: autoryzacja real-time niedozwolona, CPO zawsze dopuszcza token;
  - `ALLOWED`: CPO wybiera; `ALLOWED_OFFLINE`: real-time, a bez odpowiedzi eMSP dopuszcza token;
  - `NEVER`: tylko real-time.
  Ważność tokenu nie wpływa na `whitelist`; przy `valid = false` i `whitelist` wymagającym real-time CPO SHALL zapytać
  eMSP. Tokeny `APP_USER` i `AD_HOC_USER` zaleca się wysyłać z `NEVER` `[OCPI230 §12.4.4]`. Real-time wymaga od eMSP
  POST Authorize, a bez niego wszystkie tokeny muszą mieć `ALWAYS` `[OCPI230 §12.1.3]`.
- **Odpowiedź autoryzacji** `[OCPI230 §12.4.1]`: `ALLOWED`, `BLOCKED`, `EXPIRED`, `NO_CREDIT` (konto bez wystarczających
  środków), `NOT_ALLOWED` (ważny, ale nie w tej lokalizacji). eMSP SHALL NOT oceniać, czy ładowanie jest możliwe, na
  podstawie godzin otwarcia czy statusu EVSE, bo mogą być nieaktualne `[OCPI230 §12.1.3]`.
- **Karta i brelok:** `group_id` łączy tokeny; start jednym, stop drugim działa na EVSE z `TOKEN_GROUP_CAPABLE`
  `[OCPI230 §12.3.2]` `[OCPI230 §8.4.3]`. Język interfejsu kierowcy: `Token.language` (ISO 639-1); bez niego CPO wybiera
  sam `[OCPI230 §12.3.2]`.
- **Świeżość danych w aplikacji:** push wysyła zmiany „(semi) real-time”; push nie jest wymagany, pull jest wymagany,
  żeby odbiorca mógł się zsynchronizować po utracie połączenia `[OCPI230 §4.1.3]`. Dla NAP aktualizacja danych
  dynamicznych do 1 minuty `[AFIR-655 art. 2]`.
- **Zdalny start:** polecenia są asynchroniczne. CPO odpowiada `CommandResponse` (`NOT_SUPPORTED`, `REJECTED`,
  `ACCEPTED`, `UNKNOWN_SESSION`) `[OCPI230 §13.4.1]`, a wynik ze stacji przychodzi później jako `CommandResult`:
  `ACCEPTED`, `CANCELED_RESERVATION`, `EVSE_OCCUPIED`, `EVSE_INOPERATIVE`, `FAILED`, `NOT_SUPPORTED`, `REJECTED`,
  `TIMEOUT`, `UNKNOWN_RESERVATION` `[OCPI230 §13.1]` `[OCPI230 §13.4.2]`. `UNLOCK_CONNECTOR` jest tylko dla helpdesku
  `[OCPI230 §13.4.3]`. Gdy EVSE ma `START_SESSION_CONNECTOR_REQUIRED`, MSP musi podać `connector_id`
  `[OCPI230 §8.4.3]`. Szczegóły i przypadki brzegowe: skill `ev-ocpi-roaming-expert`.

**Wniosek:**
- zgłoszenie „zgubiona karta” w aplikacji robi PATCH `valid = false` u każdego CPO. Ekran mówi „karta zablokowana”
  dopiero po potwierdzeniu odbioru. Przy `whitelist = ALWAYS` CPO nie pyta eMSP, więc blokada działa dopiero od
  przetworzenia aktualizacji tokenu. Specyfikacja nie rozstrzyga, jak CPO traktuje `valid = false` przy `ALWAYS`
  („CPO shall always allow any use of this Token”, a ważność „has no influence” na `whitelist`) `[OCPI230 §12.4.5]`,
  więc razem z `valid = false` zmieniasz `whitelist` na `NEVER`;
- czy zablokowanie tokenu przerywa trwającą sesję, specyfikacja nie mówi. Polecenie do zatrzymania to `STOP_SESSION`
  `[OCPI230 §13.4.3]`;
- dla abonamentu przedpłaconego tokeny mają `whitelist = NEVER`, żeby eMSP mógł zwrócić `NO_CREDIT`;
- ekran startu zdalnego ma osobny stan dla `CommandResponse` i dla `CommandResult`, a każdy `CommandResult` ma własny
  komunikat dla kierowcy.

## 7. Czego źródła nie określają
Bez źródeł oficjalnych w bazie (piszesz to wprost, nie uzupełniasz z pamięci):
- wzorce UX, persony i ścieżki klienta jako praktyka projektowa (D16.01–D16.03): powyższe sekcje dają tylko wymagania;
- benchmarki funkcji CPMS i eMSP (D16.05);
- wymagania aplikacji eMSP spoza protokołu: deduplikacja stacji z wielu źródeł, próg nieświeżości statusu, abonamenty,
  retencja danych tokenów (RODO nie ma w rejestrze), integracja z CarPlay i Android Auto;
- ekonomika stacji (CAPEX, OPEX, czas zwrotu), finansowanie, przychody i marże (D17);
- wykorzystanie stacji, prognozy popytu, predykcyjne utrzymanie, AI w operacjach (D15.02, D15.03, D15.05);
- normy zharmonizowane do dyrektywy 2019/882.

Dane rynkowe, które są w bazie (liczba punktów, flota, struktura cen z 2024 r.): `references/rynek-dane.md`.
