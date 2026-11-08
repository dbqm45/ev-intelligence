# OCPI — moduły: Credentials, Locations, Sessions, CDRs, Tariffs, Tokens, Commands

Źródła: `[OCPI230]` (znaczniki jak w `SKILL.md`).

## Spis treści
1. Credentials — rejestracja
2. Locations
3. Sessions
4. CDRs i credit CDR
5. Tariffs i `step_size`
6. Tokens i autoryzacja
7. Commands

## 1. Credentials — rejestracja `[OCPI230 §7.1.1]`
1. Platformy ustalają poza OCPI, która jest Senderem modułu Credentials.
2. Receiver tworzy `CREDENTIALS_TOKEN_A` i przekazuje go z adresem endpointu versions bezpiecznym kanałem spoza OCPI.
3. Sender z tokenem A pobiera wersje i szczegóły wersji, generuje `CREDENTIALS_TOKEN_B` i wysyła go w **POST** na
   credentials Receivera.
4. Receiver zapisuje token B, pobiera nim wersje i endpointy Sendera, po czym zwraca `CREDENTIALS_TOKEN_C` w odpowiedzi
   na POST.
5. Sender SHALL używać tokenu C w kolejnych żądaniach. Token A „MAY no longer be used”.
Pozostałe przypadki (nowsza wersja, zmiana endpointów, reset tokenu, błędy, brak wymaganych endpointów): §7.1.2–7.1.6.
Błędy rejestracji: kody 3001 (nie można użyć API klienta), 3002 (nieobsługiwana wersja), 3003 (brak wspólnych lub
wymaganych endpointów) `[OCPI230 §5.3]`.

## 2. Locations (właściciel danych: CPO) `[OCPI230 §8.1]`
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
- `SessionStatus` `[OCPI230 §9.4.3]`:
  - `PENDING` (stan początkowy, „might never become an active session”);
  - `ACTIVE` (spełnione warunki: komunikacja EV–EVSE, autoryzacja; energia płynie albo może płynąć);
  - `COMPLETED` (zakończona, bez dalszych zmian);
  - `INVALID` (nieważna, nie będzie rozliczona);
  - `RESERVATION` (sesja z rezerwacji, ładowanie jeszcze nie ruszyło).

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
- `START_SESSION`: CPO „should not check the Token” przed wysłaniem do stacji i zakłada, że eMSP wysyła tylko ważne
  tokeny. Jeśli stacja zrobi OCPP Authorize, CPO robi real-time tylko wtedy, gdy to token RFID, a `START_SESSION` dla
  niego przyszło ponad 15 minut wcześniej (§13.1).
