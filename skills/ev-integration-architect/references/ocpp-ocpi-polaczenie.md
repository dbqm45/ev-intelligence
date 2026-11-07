# Łączenie OCPP i OCPI: zasady transportu, mapowanie obiektów, synchronizacja

Źródła: OCPP-J 1.6 `[J16]`, OCPP 1.6 `[16]`, OCPP 2.0.1 części 2 i 4 `[201-P2]` `[201-P4]`, OCPI 2.3.0 `[OCPI230]`,
nota aplikacyjna OCA `[OCA-AN-MC]`. Zdania **Wniosek** to rekomendacje projektowe.

## Spis treści
1. Dwa protokoły, przeciwne założenia
2. OCPP-J: kolejność, identyfikatory, ponowne łączenie
3. OCPI: identyfikatory, obiekty klienta, brak kolejkowania
4. Mapowanie stacji OCPP na OCPI Locations
5. Wiele złączy na jednym EVSE w OCPP 1.x
6. Polecenia i autoryzacja: OCPI START_SESSION → OCPP
7. Profile ładowania z OCPI do OCPP
8. Szkielet bramy OCPP–OCPI

## 1. Dwa protokoły, przeciwne założenia
| Temat | OCPP (stacja ↔ CSMS) | OCPI (platforma ↔ platforma) |
|---|---|---|
| Awaria łączności | stacja MUST kolejkować komunikaty transakcyjne i wysłać je chronologicznie `[16 §3.7]`; 2.0.1: ponawianie do limitu prób (E13) `[201-P2 E13]` | komunikatów SHOULD NOT kolejkować ani ponawiać; po powrocie odbiorca pobiera stan przez GET, np. CDR z okresu przerwy, statusy z Locations `[OCPI230 §4.4]` |
| Nieznane pola | schematy JSON mają `additionalProperties: false`; jedynym miejscem na dodatkowe pola jest `customData` (2.0.1) `[OCA-WP-CUST §1.2.2]` | platforma SHALL NOT odrzucać pól nieopisanych w specyfikacji `[OCPI230 §4.1.8]` |
| Korelacja | `messageId` łączy CALL z odpowiedzią `[201-P4 §4.1.4]` | `X-Request-ID` per żądanie, `X-Correlation-ID` przez cały łańcuch, także przez hub `[OCPI230 §4.2]` |
| Równoległość | jedno niepotwierdzone CALL na połączenie: 1.6 SHOULD NOT `[J16 §4.1.1]`, 2.0.1 SHALL NOT `[201-P4 §4.1.1]` | HTTP; żądania niezależne |
| Kto inicjuje połączenie | stacja otwiera WebSocket do CSMS (rozwiązuje NAT) `[201-P4 §5.5]` | obie strony wywołują swoje endpointy po rejestracji credentials `[OCPI230 §4.1.3]` |

**Wniosek:** brama OCPP–OCPI nie może przenosić logiki ponowień z OCPP na OCPI. Po stronie OCPP przyjmujesz i
zapisujesz zaległe komunikaty stacji. Po stronie OCPI wysyłasz stan bieżący, a po przerwie partner się z tobą
synchronizuje (GET z `date_from`). Twoja strona robi to samo wobec partnera.

## 2. OCPP-J: kolejność, identyfikatory, ponowne łączenie
- Jedno oczekujące CALL na połączenie: nie wysyłasz kolejnego, dopóki poprzednie nie dostanie odpowiedzi albo nie minie
  timeout. CALL z obu stron mogą się minąć `[J16 §4.1.1]` `[201-P4 §4.1.1]`. W 2.0.1 reguła dotyczy pojedynczego
  połączenia: CSMS może w tym czasie wysyłać do innych stacji `[201-P4 §4.1.1]`.
- Timeout wybiera implementacja. Zaleca się uwzględnić rodzaj sieci, bo sieci komórkowe mają dłuższe czasy odpowiedzi
  `[J16 §4.1.1]`.
- `messageId` (do 36 znaków):
  - 1.6: unikalny wśród CALL tego nadawcy na tym samym połączeniu WebSocket `[J16 §4.1.3]`;
  - 2.0.1: unikalny na **każdym** połączeniu z tym samym identyfikatorem stacji. Ponowienie po timeoucie MAY użyć tego
    samego `messageId` `[201-P4 §4.1.4]`.
- Ponowne łączenie w 2.0.1: rosnący odstęp z losowością (`RetryBackOffWaitMinimum`, `RetryBackOffRandomRange`,
  podwajanie do `RetryBackOffRepeatTimes`), żeby restart CSMS nie wywołał lawiny połączeń. Po ponownym połączeniu
  stacja SHOULD NOT wysyłać `BootNotification`, jeśli nic się nie zmieniło `[201-P4 §5.4]`.
- Local Controller SHALL działać tak, żeby ani stacja, ani CSMS nie zauważyły różnicy względem połączenia
  bezpośredniego `[201-P4 §6.1]`.

**Wniosek:** w CSMS deduplikujesz CALL od stacji po (identyfikator stacji, `messageId`). W 2.0.1 ponowienie może mieć
ten sam identyfikator, więc drugą kopię rozpoznasz po nim.

## 3. OCPI: identyfikatory, obiekty klienta, brak kolejkowania
- Obiekty klienta (np. taryfy, lokalizacje CPO u eMSP): adres `{base}/{module}/{country_code}/{party_id}/{id}`, nowe
  obiekty przez PUT (POST nie jest obsługiwany). Inny `country_code` / `party_id` niż w CredentialsRoles → serwer może
  zwrócić 404. `id` w URL różny od `id` w obiekcie → zalecany kod OCPI 2001 `[OCPI230 §4.1.5]`.
- Locations, EVSE i Connectors nie da się usunąć, bo zależą od nich inne moduły (np. sesje). EVSE oznacza się
  `REMOVED` `[OCPI230 §8.1]`.
- Lokalizacji prywatnych, nieprzeznaczonych do ładowania publicznego, SHALL NOT się publikować `[OCPI230 §8.1]`.
- Push jest zalecany w normalnej pracy; GET (pull) przy pierwszym połączeniu i przy niepewności co do stanu (pełna
  synchronizacja) `[OCPI230 §8.2]`.
- Mechanikę credentials, nagłówków i paginacji opisuje skill `ev-ocpi-roaming-expert`.

## 4. Mapowanie stacji OCPP na OCPI Locations `[OCPI230 §8.1.2]`
- OCPP 2.0 ma trzy poziomy: Charge Point → EVSE → Connector. OCPI: Location → EVSE → Connector.
- Dwie opcje: jedna Location dla grupy stacji w tym samym miejscu (**zalecana**) albo Location na stację. Kierowcę
  interesuje liczba dostępnych EVSE w miejscu, a nie liczba stacji.
- Z definicji EVSE ładuje jeden pojazd naraz.

## 5. Wiele złączy na jednym EVSE w OCPP 1.x
- OCPP 1.2, 1.5 i 1.6 zakładają model dwupoziomowy (stacja → złącza), w którym każde złącze ładuje niezależnie
  `[OCA-AN-MC §2]`.
- Zalecenie OCA: każde złącze jak osobne („wirtualne”) EVSE, a zmiany dostępności wynikające z blokady wzajemnej
  zgłaszane statusami `[OCA-AN-MC §4]`:
  - początek autoryzacji → wszystkie złącza EVSE `Preparing`;
  - gdy wiadomo, które złącze jest używane (np. włożono kabel) → pozostałe `Unavailable`;
  - koniec transakcji i odłączenie → wszystkie `Available`;
  - uszkodzone jedno złącze → `Faulted` tylko ono; uszkodzone EVSE → wszystkie `Faulted`.
- Dotyczy złączy zarządzanych osobno (z detekcją użycia lub blokadą). CSMS powinien obsługiwać też stacje z innym
  rozwiązaniem `[OCA-AN-MC §4]`.
- OCPI: dla stacji OCPP 1.x CPO SHOULD pokazać złącza jednego EVSE jako osobne EVSE, żeby działał StartSession
  `[OCPI230 §8.3.2]`. Jeśli stacja ma wiele złączy na EVSE, CPO ustawia możliwość `START_SESSION_CONNECTOR_REQUIRED`;
  `[OCPI230 §8.4.3]`. OCPI 2.2.1 dodał do Commands opcjonalne pole `connector_id` dla OCPP 1.x `[OCPI230 §18.3]`.

## 6. Polecenia i autoryzacja: OCPI START_SESSION → OCPP
- CPO SHOULD NOT sprawdzać tokenu z `START_SESSION` przed wysłaniem polecenia do stacji; zakłada, że eMSP wysyła tylko
  ważne tokeny `[OCPI230 §13.1]`.
- Jeśli stacja wykona `Authorize` (OCPP), CPO robi autoryzację real-time u eMSP tylko dla tokenu RFID i tylko wtedy,
  gdy `START_SESSION` dla tego tokenu przyszło ponad 15 minut wcześniej `[OCPI230 §13.1]`.
- `authorization_reference` z `START_SESSION` trafia do sesji i CDR `[OCPI230 §13.3.5]`.
- Mapowanie na zdalny start i jego korelację (`remoteStartId` w 2.0.1, brak identyfikatora w 1.6) opisuje skill
  `ev-ocpp-expert` (references `wzorce.md`).

## 7. Profile ładowania z OCPI do OCPP
- Struktury modułu ChargingProfiles bazują na OCPP 1.6 i 2.0, żeby ułatwić konwersję `[OCPI230 §14]`. Przepływ jest
  asynchroniczny: odpowiedź od razu, wynik z EVSE później na `response_url` `[OCPI230 §14.3]`.
- Szczegóły i ostrzeżenie o wielu nadawcach profili: skill `ev-energy-smart-charging-expert`.

## 8. Szkielet bramy OCPP–OCPI
**Wniosek** (z sekcji 1–7):
1. Model wewnętrzny trzypoziomowy (stacja → EVSE → złącze) z mapą na OCPI (Location → EVSE → Connector). Stacje 1.x z
   wieloma złączami na EVSE mapujesz według noty OCA.
2. Zdarzenia OCPP (status, transakcja) zapisujesz najpierw u siebie, potem publikujesz w OCPI jako push stanu, bez
   kolejki ponowień.
3. Identyfikatory: `messageId` OCPP do deduplikacji i logów; `X-Request-ID` i `X-Correlation-ID` OCPI w logach całego
   łańcucha; w logach zapisujesz też oba identyfikatory.
4. Polecenia z OCPI: odpowiedź synchroniczna od razu (przyjęte / odrzucone), wynik ze stacji asynchronicznie, z
   timeoutem podanym partnerowi.
5. Po awarii: OCPP przyjmuje zaległe komunikaty stacji, OCPI daje partnerowi pobrać stan (GET), a twoja strona pobiera
   stan od partnera.
