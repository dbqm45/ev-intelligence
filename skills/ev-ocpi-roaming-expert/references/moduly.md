# OCPI — moduły: Credentials, Locations, Sessions, CDRs, Tariffs, Tokens, Commands, Payments

Źródła: `[OCPI230]` (znaczniki jak w `SKILL.md`).

## Spis treści
1. Credentials — rejestracja
2. Locations
3. Sessions
4. CDRs i credit CDR
5. Tariffs i `step_size`
6. Tokens i autoryzacja
7. Commands
8. Interfejsy i metody modułów
9. Payments (tylko 2.3.0)

## 1. Credentials — rejestracja `[OCPI230 §7.1.1]`
1. Platformy ustalają poza OCPI, która jest Senderem modułu Credentials.
2. Receiver tworzy `CREDENTIALS_TOKEN_A` i przekazuje go z adresem endpointu versions bezpiecznym kanałem spoza OCPI.
3. Sender z tokenem A pobiera wersje i szczegóły wersji, generuje `CREDENTIALS_TOKEN_B` i wysyła go w **POST** na
   credentials Receivera.
4. Receiver zapisuje token B, pobiera nim wersje i endpointy Sendera, po czym zwraca `CREDENTIALS_TOKEN_C` w odpowiedzi
   na POST.
5. Sender SHALL używać tokenu C w kolejnych żądaniach. Token A „MAY no longer be used”.

Metody na endpoincie credentials `[OCPI230 §7.2]`. Moduł jest symetryczny: każda implementacja go wystawia i woła u
partnera.
| Metoda | Działanie | Kiedy HTTP 405 |
|---|---|---|
| GET | zwraca obiekt credentials do platformy serwera (z danymi firmy) | — |
| POST | rejestracja: serwer pobiera endpointy klienta, generuje nowy token i zwraca poświadczenia | klient już zarejestrowany |
| PUT | aktualizacja: przełącza na wersję tego endpointu, serwer zawsze pobiera endpointy na nowo i generuje nowy token | klient jeszcze niezarejestrowany |
| PATCH | n/a | — |
| DELETE | wyrejestrowanie: poświadczenia nieważne, obie strony kończą automatyczną komunikację | klient niezarejestrowany |
Źródła wierszy: `[OCPI230 §7.2.1]`, `[OCPI230 §7.2.2]`, `[OCPI230 §7.2.3]`, `[OCPI230 §7.2.4]`.

Pozostałe przypadki:
- Nowsza wersja: gdy obie platformy ją wdrożą, jedna wysyła PUT na credentials drugiej w tej wersji. Receiver poznaje
  wersję po użytym endpoincie `[OCPI230 §7.1.2]`.
- Zmiana endpointów bieżącej wersji: ta sama procedura (PUT) dla tej samej wersji `[OCPI230 §7.1.3]`.
- Zmiana poświadczeń lub reset tokenu: PUT nowych poświadczeń na credentials bieżącej wersji. Przy podejrzeniu
  wycieku platforma SHALL zainicjować wymianę tokenu „as soon as possible”. Specyfikacja zaleca („advisable”) odnawiać
  tokeny co najmniej raz w miesiącu, na wypadek niewykrytego wycieku `[OCPI230 §7.1.4]`.
- Błąd przy łączeniu zwrotnym serwera w trakcie rejestracji: serwer „should” dodać kod 3001 do odpowiedzi na POST
  `[OCPI230 §7.1.5]`.
- Brak oczekiwanych endpointów (np. CPO chce CDRs u eMSP): Sender nie wysyła POST, loguje i powiadamia administratora.
  Receiver w tej sytuacji odpowiada kodem 3003 `[OCPI230 §7.1.6]`.
Błędy rejestracji: kody 3001 (nie można użyć API klienta), 3002 (nieobsługiwana wersja), 3003 (brak wspólnych lub
wymaganych endpointów) `[OCPI230 §5.3]`.

## 2. Locations (właściciel danych: CPO) `[OCPI230 §8.1]`
- Zależność: „the Receiver endpoint is dependent on the Tariffs module” `[OCPI230 §8]`. Taryfy złącza wskazuje
  `Connector.tariff_ids` `[OCPI230 §8.3.3]`. **Wniosek:** eMSP z interfejsem Receiver Locations powinien obsłużyć też
  Tariffs, inaczej nie rozwiąże `tariff_ids`.
- Location → EVSE (1:n) → Connector (1:n). Aktualizować można całą Location, jedno EVSE albo jeden Connector.
- Nowa Location: PUT na Receiverze (eMSP). Zmiany: PATCH tylko ze zmienionymi polami. Bez push eMSP robi GET
  „regularly … but not too often”.
- Usunięcie EVSE: status MUST = `REMOVED` (PUT/PATCH). Location bez ważnego EVSE „can be considered expired”.
  Obiektów nie da się skasować, bo zależą od nich inne moduły.
- Publikacja `[OCPI230 §8.3.1]`:
  - Location z `publish = false` SHALL NOT być pokazywana w aplikacji ani na stronie, chyba że właścicielowi tokenu z listy
    `publish_allowed_to`. Także NSP i eMSP, którzy nie są właścicielami tokenu, MAY ją pokazać, ale tylko temu
    właścicielowi, gdy dane tokenu podane przez użytkownika pasują do **wszystkich** ustawionych pól jednego wpisu listy;
  - `publish_allowed_to` wolno użyć tylko przy `publish = false`. Gdy jedna lokalizacja ma EVSE publiczne i niepubliczne,
    tworzy się dwie Locations;
  - do startu sesji wolno użyć tylko tokenu, którego właścicielem jest sam eMSP.
- `PublishTokenType`: pola `uid`, `type`, `visual_number`, `issuer`, `group_id`. Co najmniej jedno z `uid`,
  `visual_number`, `group_id` SHALL być ustawione; przy `uid` SHALL być `type`, przy `visual_number` SHALL być `issuer`
  `[OCPI230 §8.4.24]`.
- Prywatne lokalizacje SHALL NOT być publikowane. Lokalizacje niedostępne publicznie ani w roamingu: zaleca się ich
  nie wysyłać (§8.1.1).
- Identyfikatory i długości `[OCPI230 §8.3.1, §8.3.2]`:
| Pole | Typ | Uwagi |
|---|---|---|
| `Location.id` | `CiString(36)` | nie może się zmieniać |
| `EVSE.uid` | `CiString(36)` | identyfikator „techniczny”, unikalny w platformie CPO, nie może się zmieniać; nie służy jako identyfikator czytelny dla człowieka |
| `EVSE.evse_id` | `CiString(48)`, opcjonalne | czytelny identyfikator w formacie dokumentu „E-mobility ID-codes” (evroaming.org); można go usunąć z EVSE o statusie `REMOVED`, gdy `evse_id` ma być użyty ponownie |
| `EVSE.physical_reference` | `string(16)`, opcjonalne | numer lub napis na obudowie do identyfikacji wzrokowej |
  CPO „will typically want to avoid” identyfikatorów sprzętu w `EVSE.uid`: po przeniesieniu urządzenia do innej Location
  złamałby unikalność, bo EVSE nie usuwa się `[OCPI230 §8.3.2]`. Ta uwaga doszła w 2.2.1-d2 `[OCPI230 §18.2]`.
  W `[OCPI221 §8.3.2]` `evse_id` odsyła do eMI3 V1.0 Part 2, a w 2.3.0 do „E-mobility ID-codes”. Samego formatu nie
  opisujemy: żaden z tych dokumentów nie jest w rejestrze.
- Nowe w 2.3.0 w Locations `[OCPI230 §18.1]`:
  - obiekt `Parking` (lista `Location.parking_places`, odwołania `EVSE.parking`), m.in. typ pojazdu `[OCPI230 §8.3.4]`;
  - `EVSE.accepted_service_providers`: nazwy eMSP, których umowy są akceptowane. Pole dodano dla europejskich CPO
    (raportowanie do NAP); gdy wymóg nie obowiązuje, można je pominąć `[OCPI230 §8.3.2]`;
  - `Location.help_phone` (`CiString(25)`): numer pomocy dla kierowcy `[OCPI230 §8.3.1]`;
  - `ConnectorCapability` `ISO_15118_2_PLUG_AND_CHARGE`, `ISO_15118_20_PLUG_AND_CHARGE`. Mają sygnalizować, że kierowca
    może z funkcji skorzystać; samo wsparcie normy przez sprzęt nie wystarcza `[OCPI230 §8.4.4]`;
  - typy złączy, m.in. `MCS`, `SAE_J3400` (brak ich w `[OCPI221 §8.4.5]`); `TESLA_S` jest mechanicznie zgodny z J3400
    `[OCPI230 §8.4.6]`.
- Statusy EVSE `[OCPI230 §8.4.26]`:
| Wartość | Znaczenie |
|---|---|
| `AVAILABLE` | może rozpocząć nową sesję |
| `BLOCKED` | niedostępne z powodu fizycznej przeszkody (np. auto) |
| `CHARGING` | w użyciu |
| `INOPERATIVE` | jeszcze nieaktywne albo czasowo niedostępne, ale nie zepsute |
| `OUTOFORDER` | niesprawne, części mogą być uszkodzone |
| `PLANNED` | planowane, wkrótce działające |
| `REMOVED` | wycofane |
| `RESERVED` | zarezerwowane dla konkretnego kierowcy |
| `UNKNOWN` | brak informacji o statusie (**także offline**) |

## 3. Sessions (właściciel danych: CPO) `[OCPI230 §9]`
- Push: nową Session CPO wysyła przez PUT, zmiany przez PATCH. Sesji nie usuwa się, a stan końcowy to `COMPLETED`.
  Pull: eMSP robi GET, także po swojej przerwie (§9.1.1–9.1.2).
- Walidacja w push: CPO niepewny stanu lub istnienia Session u eMSP robi GET na Sessions eMSP
  (`/{country_code}/{party_id}/{session_id}`), np. po błędzie przy PATCH `[OCPI230 §9.1.1, §9.2.2.1]`. **Wniosek:** po
  błędzie PATCH: GET, porównanie, a w razie rozbieżności PUT całej Session.
- `SessionStatus` `[OCPI230 §9.4.3]`:
  - `PENDING` (stan początkowy, „might never become an active session”);
  - `ACTIVE` (spełnione warunki: komunikacja EV–EVSE, autoryzacja; energia płynie albo może płynąć);
  - `COMPLETED` (zakończona, bez dalszych zmian);
  - `INVALID` (nieważna, nie będzie rozliczona);
  - `RESERVATION` (sesja z rezerwacji, ładowanie jeszcze nie ruszyło).
- PUT na istniejącą Session zastępuje cały obiekt. `charging_periods` zastępuje się w całości. Brak pola albo pusta
  lista usuwa istniejące okresy `[OCPI230 §9.2.2.2]`.
- PATCH `[OCPI230 §9.2.2.3]`:
  - SHALL zawierać `last_updated`; pola pominięte pozostają bez zmian;
  - działa tylko na całej Session: nie wolno dokładać segmentów URL, by PATCH-ować obiekty wewnętrzne;
  - `charging_periods` w PATCH to żądanie **dopisania** okresów. Brak pola albo pusta lista nic nie zmienia;
  - zastąpić lub usunąć okresy można tylko PUT-em całej Session.
  **Wniosek:** ponowione (np. po timeoucie) PATCH z tymi samymi okresami dopisze je drugi raz. Specyfikacja nie
  przewiduje deduplikacji. Bezpieczniej ponawiać PUT-em całej Session.
  Te same reguły PUT i PATCH są w `[OCPI221 §9.2.2.3]`.
- Pola czasu i okresy w Session `[OCPI230 §9.3.1]`:
  - `last_updated` (wymagane): czas ostatniej zmiany albo utworzenia. Po nim filtruje GET listy;
  - `start_date_time`: w stanie `PENDING` czas utworzenia sesji na stacji; przy przejściu na `ACTIVE` SHALL zostać
    zaktualizowany na moment aktywacji;
  - `charging_periods` w Session jest opcjonalne (`*`), w CDR wymagane (`+`) `[OCPI230 §10.3.1]`;
  - ile okresów wysyłać, decyduje CPO. Specyfikacja zaleca tyle, by eMSP mógł pokazać kierowcy postęp, i okres przy
    każdej zmianie istotnej dla taryfy. Przykłady: nowy okres co minutę przy AC to za dużo (180 na 3 h), co 30 minut
    przy DC to za mało (jeden na 30 min).
- `total_cost` to cena, którą eMSP zapłaci CPO. `0.00` oznacza bezpłatnie, a brak pola nie oznacza, że sesja była
  bezpłatna `[OCPI230 §9.3.1]`.
- GET listy u CPO (Sender): `date_from` jest wymagany, `date_to` nie. Filtr po `last_updated`: `date_from` włącznie,
  `date_to` wyłącznie `[OCPI230 §9.2.1.1]`.
- Rezerwacja `[OCPI230 §9.1.4]`: przy rezerwacji Sender SHALL utworzyć nową Session (w push CPO SHALL ją wysłać). Gdy rezerwacja kończy się
  ładowaniem tym samym tokenem, status przechodzi na `ACTIVE`; gdy nie, SHALL przejść na `COMPLETED`. CDR może
  powstać bez energii, tylko za koszt rezerwacji. `evse_uid` i `connector_id` mogą mieć wartość `#NA`, gdy EVSE lub
  złącze nie jest jeszcze przydzielone `[OCPI230 §9.3.1]`.
  Rozbieżność: §9.1.4 pisze „status = RESERVED”, a `SessionStatus` nie ma tej wartości, tylko `RESERVATION`
  `[OCPI230 §9.4.3]` (`RESERVED` jest statusem EVSE, §8.4.26). To samo w `[OCPI221 §9.1.4]`. Rozstrzygnięcie: enum,
  czyli `RESERVATION`.
- Charging Preferences `[OCPI230 §9.1.3, §9.2.1.2]`:
  - eMSP w trakcie sesji wysyła PUT na `{sessions_endpoint_url}/{session_id}/charging_preferences` (interfejs Sender,
    u CPO). Sufiks `/charging_preferences` jest wymagany;
  - wsparcie EVSE: `CHARGING_PREFERENCES_CAPABLE` w `EVSE.capabilities` `[OCPI230 §8.4.3]`;
  - `ChargingPreferences`: `profile_type` (wymagane: `CHEAP`, `FAST`, `GREEN`, `REGULAR`), `departure_time`,
    `energy_need` (kWh), `discharge_allowed` (domyślnie `false`). Dla każdego obsługiwanego `ProfileType` MUST
    istnieć taryfa `[OCPI230 §9.3.2, §9.4.2]`;
  - odpowiedź `ChargingPreferencesResponse`: `ACCEPTED` (bez gwarancji spełnienia), `DEPARTURE_REQUIRED`,
    `ENERGY_NEED_REQUIRED`, `NOT_POSSIBLE`, `PROFILE_TYPE_NOT_SUPPORTED`. EVSE bez tej capability: odbiorca „should”
    odpowiedzieć HTTP 404 i kodem 2001 `[OCPI230 §9.4.1]`.

## 4. CDRs i credit CDR (właściciel danych: CPO) `[OCPI230 §10]`
- CDR to „the only billing-relevant object”, wysyłany po zakończeniu sesji. Wysyłka „as soon as possible” to dobra
  praktyka, ale dozwolona jest też wysyłka np. raz w miesiącu po uzgodnieniu stron.
- Push: **POST** na CDRs endpoint eMSP. CPO może wysłać CDR tylko do właściwego eMSP. CDR może dotyczyć lokalizacji
  niepublikowanej (np. ładowarki domowej) (§10.1, §10.1.2).
- Wysłanego CDR nie wolno zmienić ani zastąpić. Korekta odbywa się przez **credit CDR** (§10.1.1):
  - inne `id` (np. z dopiskiem „-C”);
  - `credit = true`, `credit_reference_id` = `id` oryginału;
  - dane jak w oryginale, tylko `total_cost` z wartościami ujemnymi;
  - potem nowy CDR z nowym `id`, bez pól `credit` i `credit_reference_id`.
  Jak daleko wstecz można wysłać credit CDR, OCPI nie określa: decydują umowy i prawo lokalne.
- Pull: eMSP robi GET, także po swojej przerwie. CPO może zwrócić tylko CDR istotne dla pytającego (§10.1.3).
- Push jest modelem preferowanym, bo eMSP dostaje CDR prawie w czasie rzeczywistym `[OCPI230 §10.2]`.
- CDR powinien mieć dość wymiarów (`dimensions`), by eMSP sprawdził `total_cost`. Specyfikacja radzi wysyłać tyle, by
  eMSP policzył własne ceny dla klientów, bo jego model cenowy może się różnić od taryfy CPO `[OCPI230 §10.1.2]`.
- POST `[OCPI230 §10.2.2.2]`:
  - ciało: „the full and final CDR object”;
  - odpowiedź: nagłówek `Location` (wymagany) z URL utworzonego CDR u eMSP. Struktury URL OCPI nie definiuje;
  - CPO, który chce obejrzeć wysłany CDR, robi GET właśnie na ten URL `[OCPI230 §10.1.2, §10.2.2.1]`.
- GET listy u CPO `[OCPI230 §10.2.1, §10.2.1.1]`:
  - `date_from` i `date_to` są opcjonalne (inaczej niż w Sessions, gdzie `date_from` jest wymagany). Filtr po
    `last_updated`: `date_from` włącznie, `date_to` wyłącznie; odpowiedź paginowana;
  - `last_updated` CDR to w tej wersji OCPI tylko czas utworzenia (CDR się nie zmienia).
- Identyfikatory `[OCPI230 §10.3.1]`:
  - `id` to `CiString(39)`, SHALL być unikalne w parze `country_code`/`party_id`. Zwykły CDR SHALL mieć `id` najwyżej
    36 znaków; zapas 3 znaków jest na dopisek credit CDR;
  - `credit_reference_id` (`CiString(39)`) jest wymagane przy `credit = true`. Flaga obok referencji jest celowa: zapytanie
    po boolu jest szybsze niż porównanie napisów;
  - CDR jest „zapieczętowany”: Location, EVSE, Tariffs i Token SHALL być takie jak w chwili startu sesji.
  To samo `id` i te same reguły POST są w `[OCPI221 §10.3.1, §10.2.2.2]`. Pola CDR i wycena:
  `ev-billing-tariff-expert/references/cdr-i-wycena.md`.

## 5. Tariffs i `step_size` `[OCPI230 §11.4.2, §11.4.6]`
- `PriceComponent`: `type` (`TariffDimensionType`), `price`, opcjonalnie `vat`, `step_size`.
- `step_size`: zużycie zaokrągla się **w górę** do najmniejszej wielokrotności `step_size`. Przykład ze specyfikacji:
  `TIME` z `step_size` 300 i 6 minut ładowania → rozliczone 10 minut.
- Mnożniki: `ENERGY` 1 Wh, `TIME` i `PARKING_TIME` 1 s, `FLAT` bez jednostki. `TIME` to czas ładowania,
  `PARKING_TIME` to czas bez ładowania.
- W OCPI 3.0 pola `step_size` nie ma. Przygotowując się do 3.0, EVRF zaleca ustawiać `step_size = 1`. Lokalne przepisy
  mogą regulować `step_size`.
- Przejście między elementami taryfy z różnym `step_size`: przykład w §11.4.2.1. Pełne zasady wyliczania kosztu:
  opis obiektu CDR (§10.3.1).
Wytyczne uproszczenia taryf dla 2.3.0: `[OCPI-TSG]` (nieopracowane w tym skillu).

## 6. Tokens i autoryzacja `[OCPI230 §12.1.3, §12.4.5]`
- Właściciel danych: eMSP. Push: nowy Token eMSP wysyła PUT-em na Tokens CPO, zmiany PUT-em albo PATCH-em. Niepewny
  stanu tokenu u CPO eMSP robi GET u CPO `[OCPI230 §12.1.1]`.
- Pull: CPO pobiera GET-em pełną listę od eMSP przy starcie systemu, przy utracie synchronizacji albo co X godzin (gdy
  eMSP nie ma push). Nie służy do pracy w czasie rzeczywistym: pobieranie listy przy każdej autoryzacji „will put to much
  strain on systems” `[OCPI230 §12.1.2]`.
- Autoryzacja real-time: eMSP implementuje POST Authorize i ustawia `Token.whitelist = NEVER` dla tokenów, które mają
  być autoryzowane w czasie rzeczywistym. Jeśli wszystkie tokeny mają `ALWAYS`, POST Authorize nie jest potrzebny.
- Uwagi specyfikacji:
  - real-time dla RFID wydłuża autoryzację, więc opóźnienia trzeba minimalizować;
  - zapytanie może dotyczyć lokalizacji niepublikowanej (zwykle wynik `ALLOWED`);
  - eMSP SHALL NOT odmawiać na podstawie godzin otwarcia czy statusu EVSE, bo te dane mogą być nieaktualne.
- `WhitelistType`:
  - `ALWAYS` — tylko whitelist, real-time niedozwolone;
  - `ALLOWED` — CPO wybiera;
  - `ALLOWED_OFFLINE` — normalnie real-time, ale przy braku łączności z eMSP CPO dopuszcza token;
  - `NEVER` — tylko real-time.
- `valid = false` nie zwalnia z real-time, gdy wymaga tego `whitelist`: CPO SHALL wykonać zapytanie, bo stan tokenu mógł
  się zmienić.
- Obiekt `Token` `[OCPI230 §12.3.2]`: `country_code`, `party_id`, `uid` (`CiString(36)`), `type`, `contract_id`,
  `visual_number`, `issuer`, `group_id` (`CiString(36)`), `valid`, `whitelist`, `language`, `default_profile_type`,
  `energy_contract`, `last_updated`.
  - para `uid` + `type` „should be unique” w systemie eMSP. **Wniosek:** ten sam `uid` może istnieć w kilku typach,
    więc klucz w pamięci CPO to para, nie samo `uid`;
  - `group_id` łączy tokeny (start jednym, stop drugim). OCPP 1.5/1.6 obsługuje `parentId` do 20 znaków, więc
    specyfikacja radzi nie przekraczać 20, dopóki kierowca może ładować na takich stacjach.
- Usuwania nie ma: unieważnienie to `valid = false` wysłane PUT-em albo PATCH-em `[OCPI230 §12.1.1]`. Receiver Tokens
  nie ma DELETE („Tokens cannot be removed”) `[OCPI230 §12.2.1]`.
- Parametr `?type=`: opcjonalny w GET i PUT u CPO oraz w POST authorize; domyślnie `RFID` `[OCPI230 §12.2.1.1,
  §12.2.1.2, §12.2.2.2]`.
- `TokenType` `[OCPI230 §12.4.4]`: `AD_HOC_USER` (jednorazowy, generowany przez serwer lub aplikację), `APP_USER`
  (stały dla użytkownika aplikacji), `EMAID`, `OTHER`, `RFID`. W 2.3.0 to `OpenEnum`. `[OCPI221 §12.4.4]` ma zamknięty
  `enum` bez `EMAID`. Uwagi specyfikacji:
  - `AD_HOC_USER` i `APP_USER`: RECOMMENDED wysyłać z `whitelist = NEVER`, bo whitelist nic im nie daje;
  - `EMAID` (ISO 15118): RECOMMENDED w ogóle ich nie wysyłać. CPO poznaje wystawcę ze stacji i pyta go real-time;
  - zarządzanie certyfikatami kontraktu ISO 15118 jest poza OCPI 2.3.0. PKI: skill `ev-iso15118-pki-expert`.
- Tokenów `AD_HOC_USER` i `APP_USER` eMSP nie musi wcześniej wysyłać modułem Tokens, gdy idą tylko w komendach. CPO nie
  musi ich zapisywać ani zwracać w GET, ale dane tokenu SHALL trafić do Session i CDR `[OCPI230 §13.3.5]`.
- Real-time `POST {tokens_endpoint_url}{token_uid}/authorize[?type=]` `[OCPI230 §12.2.2.2]`:
  - ciało: opcjonalne `LocationReferences` (`location_id`, `evse_uids`) `[OCPI230 §12.4.3]`;
  - token nieznany: HTTP 404 i kod 2004, bez pola `data`;
  - za mało informacji (brak `LocationReferences`), by rozstrzygnąć: kod 2002;
  - token znany: `AuthorizationInfo` z `allowed`, `token`, opcjonalnie `location` (tylko EVSE, na których wolno
    ładować), `authorization_reference` (trafia do Session i CDR), `info` `[OCPI230 §12.3.1]`;
  - `AllowedType`: `ALLOWED`, `BLOCKED`, `EXPIRED`, `NO_CREDIT`, `NOT_ALLOWED` (token ważny, ale nie w tej lokalizacji)
    `[OCPI230 §12.4.1]`.
- Kody statusu OCPI z tego obszaru `[OCPI230 §5.2]`, identyczne w `[OCPI221 §5.2]`:
| Kod | Znaczenie |
|---|---|
| 2001 | brakujące lub błędne parametry, np. brak `last_updated` w PATCH |
| 2002 | za mało informacji, np. żądanie autoryzacji z za małą ilością danych |
| 2003 | nieznana Location, np. `START_SESSION` z nieznaną lokalizacją |
| 2004 | nieznany Token, np. autoryzacja real-time nieznanego tokenu |
  Zakres 2900–2999 jest zarezerwowany na własne kody błędów klienta.

## 7. Commands `[OCPI230 §13]`
- Moduł jest asynchroniczny (§13.1):
  1. Sender (zwykle eMSP) wysyła polecenie;
  2. Receiver (zwykle CPO) odpowiada `CommandResponse`: czy może przekazać polecenie do stacji;
  3. wynik ze stacji Receiver wysyła później jako `CommandResult` w POST na `response_url`.
  Do `response_url` Sender może dodać własny unikalny identyfikator, żeby powiązać wynik z poleceniem.
- `CommandResponse` (§13.3.2): `result` (`NOT_SUPPORTED`, `REJECTED`, `ACCEPTED`, `UNKNOWN_SESSION`), `timeout`
  (sekundy, wymagane), `message`. OCPI nie przewiduje ponowień, więc po `timeout` eMSP może założyć, że wynik nie przyjdzie.
- `CommandResult.result` (§13.4.2): `ACCEPTED`, `CANCELED_RESERVATION`, `EVSE_OCCUPIED`, `EVSE_INOPERATIVE`, `FAILED`,
  `NOT_SUPPORTED`, `REJECTED`, `TIMEOUT`, `UNKNOWN_RESERVATION`.
- Typy (§13.4.3): `CANCEL_RESERVATION`, `RESERVE_NOW`, `START_SESSION`, `STOP_SESSION`, `UNLOCK_CONNECTOR`.
  `UNLOCK_CONNECTOR` jest tylko dla operatora lub eMSP, nigdy bezpośrednio od kierowcy.
- Przykłady w §13.1:
  - `ACCEPTED` w obu krokach, ale brak sesji, bo EV nie został podłączony przed timeoutem (Figure 28);
  - stacja odrzuca start bez wpiętego kabla → `CommandResult` `FAILED` (Figure 29);
  - nieznana Location → `status_code` 2003 i `REJECTED` (Figure 32).
- `StartSession` `[OCPI230 §13.3.5]`: `response_url`, `token` (autoryzowany przez eMSP), `location_id`, opcjonalnie
  `evse_uid` (wymagany, gdy jest `connector_id`), `connector_id` (wymagany przy capability
  `START_SESSION_CONNECTOR_REQUIRED` na EVSE, `[OCPI230 §8.4.3]`), `authorization_reference`. Bez `evse_uid` stacja
  sama wybiera EVSE (nie każda to obsługuje). eMSP SHALL używać tylko własnych tokenów.
- `ReserveNow` `[OCPI230 §13.3.4]`: `response_url`, `token`, `expiry_date`, `reservation_id`, `location_id`, opcjonalnie
  `evse_uid` i `authorization_reference`. Ten sam `reservation_id` w tej samej Location zastępuje rezerwację. Udana
  rezerwacja tworzy Session; niewykorzystana MAY kosztować i dać CDR. CPO SHALL NOT przekazywać `reservation_id` eMSP
  wprost do stacji: sam zapewnia unikalny identyfikator rezerwacji na stacji.
- Anulowanie rezerwacji przez CPO `[OCPI230 §13.1]`: CPO wysyła `CommandResult` `CANCELED_RESERVATION` na ten sam
  `response_url`, który dostał w `RESERVE_NOW` (Figure 35). Specyfikacja: „not to be taken lightly”, tylko gdy CPO jest do
  tego zmuszony, np. awaria punktu albo roboty drogowe.
- `START_SESSION`: CPO „should not check the Token” przed wysłaniem do stacji i zakłada, że eMSP wysyła tylko ważne
  tokeny. Jeśli stacja zrobi OCPP Authorize, CPO robi real-time tylko wtedy, gdy to token RFID, a `START_SESSION` dla
  niego przyszło ponad 15 minut wcześniej (§13.1).

## 8. Interfejsy i metody modułów
Metody niewymienione mają w specyfikacji „n/a”. Rejestr endpointów i role: `references/wersje-i-role.md`. Paginacja:
`references/transport.md`.
| Moduł | Interfejs (typowo) | URL | Metody |
|---|---|---|---|
| `credentials` | symetryczny | `{credentials_endpoint_url}` | GET, POST, PUT, DELETE `[OCPI230 §7.2]` |
| `locations` | Sender (CPO) | `{locations_endpoint_url}` z `date_from`, `date_to`, `offset`, `limit`; obiekt: `/{location_id}[/{evse_uid}][/{connector_id}]` | GET (lista lub obiekt) `[OCPI230 §8.2.1]` |
| `locations` | Receiver (eMSP, NSP) | `/{country_code}/{party_id}/{location_id}[/{evse_uid}][/{connector_id}]` | GET, PUT, PATCH; bez POST (PUT) i DELETE (PATCH na `REMOVED`) `[OCPI230 §8.2.2]` |
| `sessions` | Sender (CPO) | lista z `date_from` (wymagany); `/{session_id}/charging_preferences` | GET, PUT `[OCPI230 §9.2.1]` |
| `sessions` | Receiver (eMSP, SCSP) | `/{country_code}/{party_id}/{session_id}` | GET, PUT, PATCH `[OCPI230 §9.2.2]` |
| `cdrs` | Sender (CPO) | lista z `date_from`, `date_to`, `offset`, `limit` | GET `[OCPI230 §10.2.1]` |
| `cdrs` | Receiver (eMSP) | `{cdr_endpoint_url}`; URL utworzonego CDR wraca w nagłówku `Location` | GET, POST; bez PUT, PATCH, DELETE `[OCPI230 §10.2.2, §10.2.2.2]` |
| `tariffs` | Sender (CPO) | lista | GET `[OCPI230 §11.2.1]` |
| `tariffs` | Receiver (eMSP, NSP) | `/{country_code}/{party_id}/{tariff_id}` | GET, PUT, DELETE (taryfa już nieużywana) `[OCPI230 §11.2.2]` |
| `tokens` | Receiver (CPO) | `/{country_code}/{party_id}/{token_uid}[?type={type}]` | GET, PUT, PATCH; bez DELETE `[OCPI230 §12.2.1]` |
| `tokens` | Sender (eMSP) | lista; `{token_uid}/authorize[?type={type}]` | GET, POST (real-time) `[OCPI230 §12.2.2]` |
| `commands` | Receiver (CPO) | `{commands_endpoint_url}{command}` | POST `[OCPI230 §13.2.1]` |
| `commands` | Sender (eMSP) | `response_url` z żądania; struktury OCPI nie definiuje | POST (`CommandResult`) `[OCPI230 §13.2.2]` |
- Obiekty Locations, Sessions, Tariffs i Tokens to Client Owned Objects: URL Receivera zawiera `{country_code}` i
  `{party_id}` `[OCPI230 §8.2.2, §9.2.2, §11.2.2, §12.2.1]`. Przy PUT te segmenty SHALL równać się polom pchanego
  obiektu `[OCPI230 §9.2.2.2, §12.2.1.2]`.
- Przed DELETE taryfy RECOMMENDED sprawdzić, że żaden `Connector.tariff_ids` jej nie wskazuje `[OCPI230 §11.2.2.3]`.
- `response_url` warto robić unikalnym dla każdego żądania (np. id w segmencie), żeby rozróżnić równoległe komendy
  `[OCPI230 §13.2.2.1]`.

## 9. Payments (tylko 2.3.0) `[OCPI230 §16]`
Moduł `payments`, właściciel danych: PTP (Payment Terminal Provider). W `[OCPI221]` go nie ma: rozdział 16 to tam
typy danych. Przebieg transakcji, pola `Terminal` i Financial Advice Confirmation, `preauthorize_amount` i
wystawca faktury: `ev-billing-tariff-expert/references/cdr-i-wycena.md` §5. Tu tylko interfejsy.
- Role: PTP jest Senderem Payments i Commands oraz Receiverem CDRs, Locations, Sessions i Tariffs. CPO jest Receiverem
  Payments `[OCPI230 §2.3.1]`.
- Interfejs Sender (PTP) `[OCPI230 §16.5.1.1–16.5.1.10]`:
| Wywołanie (od CPO) | URL | Działanie |
|---|---|---|
| GET listy | `{payments_terminals_endpoint_url}` z `date_from`, `date_to`, `offset`, `limit` (opcjonalne) | terminale wg `last_updated`, paginowane |
| GET | `…/{terminal_id}` | jeden terminal, np. do walidacji |
| PATCH | `…/{terminal_id}` | przypisanie `location_ids` i/lub `evse_uids` (suma EVSE z obu) |
| PUT | `…/{terminal_id}` | aktualizacja danych terminala |
| POST | `{payments_terminals_endpoint_url}/activate` | aktywacja; `terminal_id` opcjonalny, nadaje go PTP |
| POST | `{payments_terminals_endpoint_url}/{terminal_id}/deactivate` | dezaktywacja (awaria, zmiana adresu) |
| GET listy | `{payments_financial_advice_confirmation_endpoint_url}` z `date_from`, `date_to`, `offset`, `limit` | potwierdzenia wg `last_updated` |
| GET | `…/{financial_advice_confirmation_id}` | jedno potwierdzenie |
- PUT i PATCH CPO na terminal to „information Push message”: wysłane obiekty nie należą do CPO
  `[OCPI230 §16.5.1.5, §16.5.1.6]`. **Wniosek:** to odwrotnie niż w innych modułach, gdzie zapisuje właściciel danych.
  Tu CPO zapisuje dane PTP, więc PTP musi przyjmować zapisy na interfejsie Sender.
- Po żądaniu aktywacji PTP „should” utworzyć obiekt Terminal u CPO przez POST `[OCPI230 §16.5.1.7]`.
- Interfejs Receiver (CPO) `[OCPI230 §16.5.2.1–16.5.2.6]`:
  - Terminals: GET po `terminal_id` (PTP sprawdza stan), POST nowego terminala. Bez wcześniejszej aktywacji POST nie
    powinien mieć `location_ids`, bo przypisuje CPO. Wystarczy sam `terminal_id`;
  - Financial Advice Confirmation: GET po id i POST nowego potwierdzenia. PTP SHALL użyć tego samego
    `authorization_reference` co w `Commands.StartSession`, by CPO powiązał potwierdzenie z sesją.
  Struktury URL Receivera tekst nie podaje, są tylko przykłady (`…/payments/terminals/`,
  `…/payments/financial-advice-confirmations/`).
- Czego specyfikacja nie określa lub co jest niespójne:
  - `ModuleID` w `[OCPI230 §6.2.4]` nie zawiera `payments`, choć §16 podaje „Module Identifier: payments”. `ModuleID`
    to `OpenEnum`, więc wartość da się wysłać. Rozstrzygnięcie: identyfikator z §16;
  - Sender ma dwa adresy (terminale i potwierdzenia), a `Endpoint` w Versions ma jeden `url` na parę `identifier` +
    `role` `[OCPI230 §6.2.2]`. Jak je zarejestrować, specyfikacja nie określa. Trzeba to uzgodnić z partnerem;
  - opisy `date_from`/`date_to` w GET terminali i potwierdzeń mówią „Only return Sessions” (pozostałość kopiowania);
    obowiązuje zdanie nad tabelą, o Terminals i potwierdzeniach `[OCPI230 §16.5.1.3, §16.5.1.9]`;
  - przykłady mają w URL wersję 2.2.1 `[OCPI230 §16.5.1.3]`.
