# Ceny według AFIR i informacja o taryfie i koszcie w OCPP 2.0.1

Źródła: AFIR w wersji skonsolidowanej `[AFIR]` (art. 5), OCPP 2.0.1 Edition 4: część 2, blok I `[201-P2]`, załączniki
części 2 `[201-APP]`. Zdania **Wniosek** to rekomendacje.

## Spis treści
1. AFIR art. 5: płatność ad hoc i ceny
2. OCPP 2.0.1: blok I (Tariff and Cost)
3. Zmienne `TariffCostCtrlr`
4. Czego źródła nie określają

## 1. AFIR art. 5 `[AFIR art. 5]`
- **Ad hoc (ust. 1):** operator punktów publicznych zapewnia ładowanie ad hoc. Na punktach uruchomionych od 13.04.2024
  płatność instrumentem powszechnie używanym w UE, przez co najmniej jedno z: (a) czytnik kart płatniczych, (b)
  urządzenie zbliżeniowe czytające co najmniej karty płatnicze, (c) dla mocy < 50 kW urządzenie z internetem, np.
  generujące kod QR. Od 1.01.2027 punkty ≥ 50 kW na sieci TEN-T i na bezpiecznych parkingach, także sprzed 13.04.2024,
  muszą spełniać (a) albo (b). Jeden terminal może obsługiwać kilka punktów w puli. Przepis nie dotyczy punktów
  bezpłatnych.
- **Automatyczne uwierzytelnienie (ust. 2):** kierowca zawsze może z niego zrezygnować i ładować ad hoc albo w innej
  ofercie umownej dostępnej w punkcie. Operator pokazuje tę opcję wyraźnie.
- **Ceny CPO (ust. 3):** rozsądne, łatwo i jasno porównywalne, przejrzyste i niedyskryminujące. Operator nie dyskryminuje
  cenami między użytkownikami końcowymi a MSP ani między MSP. Różnicowanie poziomu cen jest dozwolone tylko, gdy jest
  proporcjonalne i obiektywnie uzasadnione.
- **Ad hoc ≥ 50 kW (ust. 4):** cena oparta na cenie za kWh. Dodatkowo można pobierać opłatę za zajętość za minutę,
  żeby zniechęcić do długiego zajmowania punktu. Cenę za kWh i opłatę za minutę pokazuje się na stacji tak, żeby
  kierowca znał je przed rozpoczęciem sesji.
- **Ad hoc < 50 kW (ust. 4):** informacja o cenie ad hoc ze wszystkimi składnikami, przed sesją, w kolejności: cena za
  kWh, za minutę, za sesję, inne składniki.
- Pierwszy i drugi akapit ust. 4 (zasady dla ≥ 50 kW) dotyczą punktów uruchomionych od 13.04.2024 `[AFIR art. 5 ust. 4]`.
- **Ceny MSP (ust. 5):** rozsądne, przejrzyste i niedyskryminujące. Przed sesją MSP udostępnia wszystkie informacje o
  cenie tej sesji, z rozróżnieniem składników, w tym kosztów e-roamingu i własnych opłat. Bez dodatkowych opłat za
  transgraniczny e-roaming.
- **Nadzór (ust. 6):** państwa członkowskie monitorują zgodność z ust. 3 i 5.
- Cena ad hoc jest daną dynamiczną publikowaną do NAP `[AFIR art. 20 ust. 2 lit. f]`, aktualizowaną najpóźniej
  1 minutę po zmianie `[AFIR-655 art. 2]` (szczegóły w skillu `ev-cpms-architect`).

**Wniosek:**
- taryfa ad hoc punktu ≥ 50 kW uruchomionego od 13.04.2024 w OCPI to taryfa `AD_HOC_PAYMENT` ze składnikiem `ENERGY` i
  ewentualnie `PARKING_TIME` lub `TIME` jako opłatą za zajętość. Opłaty startowej `FLAT` ust. 4 dla tych punktów nie
  przewiduje;
- różne ceny dla klientów różnych MSP są dopuszczalne tylko z uzasadnieniem proporcjonalnym i obiektywnym (ust. 3).
  Uzasadnienie dokumentujesz;
- informacja o cenie przed startem (ust. 4 i 5) obejmuje w taryfie OCPI także to, co zmienia kwotę mimo tej samej
  stawki: `step_size` większy niż 1 (specyfikacja zaleca podawać go wyraźnie w ofercie `[OCPI230 §11.4.2]`), `min_price`
  i `max_price` `[OCPI230 §11.3.1]`, chwilę, od której liczy się postój (`PARKING_TIME`), okna czasowe z ograniczeń oraz
  to, czy ceny są z podatkiem (`tax_included` `[OCPI230 §11.4.9]`) i w jakiej walucie.

## 2. OCPP 2.0.1: blok I `[201-P2 I]`
- OCPP przekazuje taryfę jako **tekst dla człowieka**, nie strukturę. Uzasadnienie OCA: skoro CSO nie umie zamienić
  swojej taryfy na czytelny tekst, nie da rady tego zrobić stacja `[201-P2 I §1.1]`.
- Wszystkie taryfy i koszty są w walucie ze zmiennej `Currency` `[201-P2 I §1]`.
- I01: taryfę kierowcy CSMS MAY wysłać w `IdTokenInfo.personalMessage` w `AuthorizeResponse` (I01.FR.01), tylko gdy
  stacja obsługuje taryfy lub DisplayMessage (I01.FR.02). Stacja SHALL ją pokazać (I01.FR.03).
- I02 (koszt bieżący): CSMS SHALL wysyłać `CostUpdatedRequest` w stosownych odstępach albo zwracać koszt bieżący w
  `TransactionEventResponse` (I02.FR.01). Stacja odpowiada `CostUpdatedResponse` i pokazuje koszt (I02.FR.02–04).
  `CostUpdatedRequest.totalCost` (wymagane) to koszt z podatkami; `transactionId` wymagane `[201-P2 §1.11.1]`.
- I03 (koszt końcowy): po `TransactionEventRequest(eventType = Ended)` CSMS, gdy zna koszt, SHALL podać go w `totalCost`
  w `TransactionEventResponse` (I03.FR.01–02). Stacja online SHALL go pokazać (I03.FR.03).
  - **Transakcja bezpłatna: CSMS SHALL ustawić `totalCost = 0.00`. Brak `totalCost` nie oznacza, że transakcja była
    bezpłatna** (I03.FR.04). To samo w opisie pola w `TransactionEventResponse`.
  - Przy `TxStopPoint` z `ParkingBayOccupancy` stacja SHOULD NOT pokazywać kosztu, bo kierowca już odjechał (I03.FR.05).
- I04: gdy brak taryfy dla kierowcy (np. stacja offline), stacja SHALL pokazać `TariffFallbackMessage` (I04.FR.01).
- I05: gdy stacja offline nie może pobrać kosztu zakończonej transakcji, SHALL pokazać komunikat zastępczy
  `TotalCostFallbackMessage` (I05.FR.01–02).
- I06: na `TransactionEventRequest(eventType = Updated)` CSMS SHALL sprawdzić, czy jest nowa informacja o taryfie, i
  podać ją w `updatedPersonalMessage`. Stacja SHALL ją pokazać (I06.FR.01–03).

## 3. Zmienne `TariffCostCtrlr` w 2.0.1 `[201-APP §3.1.17]`
`Available` i `Enabled` (instancje `Cost` i `Tariff`), `TariffFallbackMessage`, `TotalCostFallbackMessage`, `Currency`
(ISO 4217).

Plik CSV Device Model v1.5 `[201-CSV]` zawiera dla `TariffCostCtrlr` także zmienne, których nie ma w opisie załączników
2.0.1, np. `Enabled[RunningCost]`, `Interval`, `MaxElements`, `ConditionsSupported`, `HandleFailedTariff` i opis „supports
the TariffType structure”. **Wniosek:** to zmienne do struktury taryf, której część 2 OCPP 2.0.1 nie zawiera (zob. §1.1
bloku I). Dla 2.0.1 przyjmujesz listę z załączników. Strukturalnych taryf z OCPP 2.1 skill jeszcze nie opracował.

## 4. Czego źródła nie określają
- OCPI i OCPP nie określają zaokrąglania kwot `[OCPI230 §11.3.1]`. Decydują prawo, umowy i waluta.
- Przeliczanie walut: taryfa i CDR mają po jednej walucie (`currency`) `[OCPI230 §11.3.1, §10.3.1]`, a reguł
  przeliczania specyfikacja nie podaje. Kurs i moment przeliczenia to sprawa umowy między stronami.
- Przepisy USA o cenach na stacjach (23 CFR 680, program NEVI) nie są w rejestrze źródeł. Pytanie o nie → mówisz, że
  baza ich nie obejmuje.
- VAT w roamingu i transgranicznie, faktury i noty korygujące (D09.04), PCI DSS i PSD2/SCA (D09.03) oraz metrologia
  prawna MID i Eichrecht (D10) wymagają innych źródeł (prawo UE i krajowe, normy). Nie są opracowane.
- Prawo konsumenckie zabraniające zmiany taryfy w trakcie sesji: specyfikacja OCPI tylko o nim wspomina
  `[OCPI230 §11.3.1]`. Konkretnych przepisów krajowych baza nie zawiera.
