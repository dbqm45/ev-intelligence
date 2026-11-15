# OCPI — transport, routing, kody statusu, offline

Źródła: `[OCPI230]`, odpowiedniki w `[OCPI221]` (tabela na końcu). Znaczniki jak w `SKILL.md`.

## Bezpieczeństwo i Authorization `[OCPI230 §4.1.1–4.1.2]`
- Ochrona na poziomie HTTP: TLS i uwierzytelnianie tokenem. Certyfikaty klienta nie są wymagane, tylko certyfikat
  serwera.
- Każde żądanie MUST zawierać `Authorization: Token <encoded token>`. Encoded token to UTF-8 → Base64 (RFC 4648)
  „credentials tokenu”. Przykład: `example-token` → `ZXhhbXBsZS10b2tlbgo=`.
- „Credentials tokens” (moduł Credentials) to coś innego niż Tokens kierowców (moduł Tokens).
- Wiele implementacji 2.1.1 i 2.2 nie koduje tokenu Base64. Od 2.2-d2 kodowanie jest wymagane, a zgodność ze starymi
  implementacjami wymaga prób albo flag konfiguracyjnych.
- Brak nagłówka albo nieznany token → HTTP 401. Ważny `CREDENTIALS_TOKEN_A` użyty poza modułami credentials i versions
  → HTTP 401.
- Credentials token musi jednoznacznie identyfikować stronę żądającą: serwer po nagłówku wiąże żądanie z kontem
  partnera.
- W obiekcie Credentials pole `token` ma typ `string(64)`. Powinno zawierać tylko drukowalne znaki ASCII bez spacji,
  od U+0021 do U+007E `[OCPI230 §7.3.1]`. Kodowanie Base64 §4.1.2 opisuje dla wartości nagłówka `Authorization`.
  Tak samo w `[OCPI221 §7.3.1]`.

## Push i pull `[OCPI230 §4.1.3]`
Push opcjonalny, **pull wymagany**, żeby odbiorca mógł się zsynchronizować po utracie połączenia. Dla produkcji push
jest „strongly advised”. Pull list: interwał „think in hours, not minutes”, z losowym rozrzutem (splay).

## Żądania i obiekty należące do klienta `[OCPI230 §4.1.4–4.1.6]`
- Metody: GET, POST, PUT, PATCH, DELETE. `Content-Type: application/json` SHALL przy żądaniach z treścią.
- PUT `[OCPI230 §4.1.4.2]`: niesie wszystkie wymagane pola obiektu. Pominięte pola opcjonalne wracają do wartości
  domyślnej z protokołu albo do NULL.
- PATCH `[OCPI230 §4.1.4.3]`: tylko identyfikator obiektu (jeśli potrzebny) i zmieniane pola. Pominięte pola, wymagane
  i opcjonalne, zostają bez zmian. Po nieudanym PATCH klient „is expected to” zrobić GET i sprawdzić stan obiektu
  u partnera. Gdy obiektu nie ma, klient „should do a PUT”.
- Obiekty należące do klienta (np. Tariff należący do CPO): URL `{base-ocpi-url}/{end-point}/{country-code}/{party-id}/{object-id}`.
  POST nie jest obsługiwany, nowy obiekt wysyła się przez PUT. Pary `country_code`/`party_id` serwer zna z
  CredentialsRoles z rejestracji `[OCPI230 §4.1.5]`.
- `country_code` / `party_id` niezgodne z CredentialsRoles z rejestracji → serwer może odpowiedzieć HTTP 404.
  `object-id` w URL różny od `id` w obiekcie → zalecany `status_code` 2001 `[OCPI230 §4.1.5.1]`.
- GET na interfejsie Sender: właściciela obiektu poznaje się po `country_code` i `party_id` w samym obiekcie. Obiekty
  spoza CredentialsRoles z rejestracji „may be ignored” `[OCPI230 §4.1.6]`.

**Wniosek:** po błędzie PATCH nie ponawiaj go od razu. Zgodnie z §4.1.4.3 najpierw GET, a przy braku obiektu PUT
całego obiektu.

## Paginacja (każdy GET listy) `[OCPI230 §4.1.4.1]`
- Parametry żądania: `date_from` (włącznie, po `last_updated`), `date_to` (wyłącznie), `offset` (domyślnie 0), `limit`.
- Nagłówki odpowiedzi: `Link` (następna strona, jeśli to nie ostatnia), `X-Total-Count`, `X-Limit` (górny limit
  serwera, a nie liczba zwróconych obiektów).
- Najlepsza praktyka: najstarsze obiekty najpierw. Wzrost `X-Total-Count` w trakcie przeglądania nie wymaga ponowień.
  Spadek (np. przy `date_to`) → ponów poprzedni GET z `offset` mniejszym o 1.
- `date_from` włącznie, `date_to` wyłącznie: kolejne zapytanie bierze `date_from` równe `date_to` poprzedniego i
  przedziały się nie nakładają.
- `X-Total-Count` liczy obiekty pasujące do zapytania (z `date_from`/`date_to`, bez `limit`/`offset`), które są dostępne
  dla **tego** klienta. Serwer nie musi zwracać klientowi wszystkich obiektów, np. CDR należących do innych.
- `Link` zawiera też filtry z pierwotnego żądania. Serwer może zwrócić mniej obiektów niż `limit`.
- Niepoprawny JSON albo niepoprawny obiekt OCPI (np. brak pól) w odpowiedzi: klient nie ma jak zgłosić tego serwerowi.
  Zalecane: zalogować błąd i skontaktować się z administratorem serwera. Z listy z obiektami poprawnymi i błędnymi
  klient „should at least process” poprawne.
- Pełny pull (GET List): pola niepodane można traktować jak null, a starsze dane nieobecne w odpowiedzi „is considered
  no longer valid”. Przy paginacji „nową prawdą” są wszystkie strony razem `[OCPI230 §8.2.1.1]` (Locations). Zdanie
  o nieważności starszych danych powtarzają też Sessions `[OCPI230 §9.2.1.1]`, CDRs `[OCPI230 §10.2.1.1]`,
  Tariffs `[OCPI230 §11.2.1.1]`, Tokens `[OCPI230 §12.2.2.1]` i Hub Client Info `[OCPI230 §15.3.2.3]`.

## Format odpowiedzi `[OCPI230 §4.1.7]`
Obiekt JSON z polami: `data` (obiekt / lista / string), `status_code` (4 cyfry, wymagane), `status_message` (opcjonalne),
`timestamp` (wymagane). Gdy specyfikacja nie określa `data`, odbiorca akceptuje brak `data` i dowolną wartość, a nadawca
zostawia pole puste (np. PUT Session, PATCH charging periods).

## Nieopisane pola i `OpenEnum` `[OCPI230 §4.1.8]` `[OCPI230 §17.3]`
- Platforma OCPI SHALL NOT odrzucać treści żądania ani odpowiedzi z powodu nazw pól JSON, których specyfikacja nie
  opisuje. Rozszerzając OCPI o własne pola, implementujący SHOULD wybierać sensowne, nieużywane nazwy i SHOULD NOT
  stosować przedrostków `x-` ani `custom` (duch RFC 6648) `[OCPI230 §4.1.8]`.
- `enum` to zamknięty zbiór wartości. `OpenEnum` ma znane wartości, ale zostawia miejsce na inne, np. nowe typy złączy.
  W JSON oba są stringami `[OCPI230 §17.2–17.3]`. Typy `OpenEnum` w 2.3.0 to m.in. `ModuleID`, `VersionNumber`,
  `Capability`, `ConnectorCapability`, `ConnectorType`, `TokenType`, `CommandType`.
- `[OCPI221]` nie ma odpowiednika §4.1.8 ani typu `OpenEnum` (sprawdzone wyszukiwaniem w tekście). `ModuleID` jest tam
  zwykłym `enum` `[OCPI221 §6.2.4]`.

**Wniosek:** walidator Receivera w 2.3.0 nie odrzuca obiektu z nieznanym polem ani z nieznaną wartością pola typu
`OpenEnum`. Nieznaną wartość zapisuje i loguje. Specyfikacja nie określa, co robić z wartością, której odbiorca nie
rozumie.

## Routing przez hub `[OCPI230 §4.1.9.2]`
- Nagłówki `OCPI-to-party-id`, `OCPI-to-country-code`, `OCPI-from-party-id`, `OCPI-from-country-code` SHALL być
  zaimplementowane dla każdego żądania i odpowiedzi modułów funkcjonalnych (Tokens, Locations, CDRs…). Nie zawsze muszą
  występować (zob. Open Routing Request, §4.1.9.4).
- Moduły konfiguracyjne (Credentials, Versions, Hub Client Info): routing headers SHALL NOT be used.

### Broadcast Push `[OCPI230 §4.1.9.3]`
- Klient wysyła push (POST, PUT, PATCH) do huba, a hub rozsyła go do wszystkich połączonych klientów o „opposite role”
  z danym modułem (np. CPO → wszyscy eMSP i NSP; eMSP → wszyscy CPO). Rola „Other” jest traktowana jak eMSP:
  Broadcast Push od CPO trafia też do „Other”, a od „Other” tylko do CPO.
- Nagłówki: w `OCPI-to-` klient podaje `party-id` i `country-code` **huba**. Hub rozsyła ze swoimi danymi w `OCPI-from-`,
  a odbiorca odpowiada z danymi huba w `OCPI-to-` (tabela „Party to Party Broadcast Push”, §4.1.9.6).
- GET SHALL NOT być używany z Broadcast Push. Gdy nadawca nie zna odbiorcy GET, MUST użyć Open Routing Request.
- Broadcast Push SHALL być używany tylko dla danych przeznaczonych dla wszystkich (np. Tokens, Locations). Nie dla
  CDRs i Sessions: dotyczą jednej strony i mogą podlegać RODO lub innym przepisom.
- Przy Client Owned Objects URL zachowuje `party-id` i `country-code` pierwotnego nadawcy.
- Obowiązek przekazania klientowi błędów 2xxx/3xxx od serwera nie dotyczy Broadcast Push `[OCPI230 §5.4]`.

### Open Routing Request `[OCPI230 §4.1.9.4]`
- Nadawca pomija nagłówki `OCPI-to-` (w tabeli §4.1.9.6: MUST be omitted). Hub sam wybiera odbiorcę z treści żądania
  albo rozsyła, gdy odbiorcy nie da się ustalić.
- Dotyczy GET (nie GET All), POST, PUT, PATCH i DELETE. To nie jest Broadcast Push, który działa tylko dla push.

### GET All via Hubs `[OCPI230 §4.1.9.5]` `[OCPI230 §4.1.9.7]`
- Receiver robi GET na interfejsie Sender modułu u huba, z danymi huba w `OCPI-to-`. Hub łączy obiekty od różnych stron.
- Właściciela obiektu klient poznaje po `country_code` i `party_id` w obiekcie.
- W odpowiedzi hub podaje siebie w `OCPI-from-`, a nadawcę w `OCPI-to-` §4.1.9.7.

### Nagłówki w scenariuszach `[OCPI230 §4.1.9.6]`
| Scenariusz | `OCPI-to-` w żądaniu | `OCPI-from-` w żądaniu | Odpowiedź |
|---|---|---|---|
| Bezpośrednio, bez huba | strona odbierająca | strona żądająca | odwrócone |
| Przez hub (każdy odcinek) | strona odbierająca | strona żądająca | odwrócone |
| Broadcast Push: nadawca → hub | hub | strona żądająca | hub odpowiada: `to` = nadawca, `from` = hub |
| Broadcast Push: hub → odbiorca | strona odbierająca | hub | `to` = hub, `from` = odbiorca |
| Open Routing: nadawca → hub | brak | strona żądająca | `to` = nadawca, `from` = odbiorca |
| Open Routing: hub → odbiorca | strona odbierająca | strona żądająca | `to` = nadawca, `from` = odbiorca |
Nagłówki wskazują strony (party), nie platformy. Lista nie jest zamknięta: kombinacje są możliwe.

### Znaczniki czasu `[OCPI230 §4.1.9.8]`
Hub SHALL NOT zmieniać pól `last_updated` obiektów, które przez niego przechodzą.

## Identyfikatory komunikatów `[OCPI230 §4.2]`
- `X-Request-ID`: każde żądanie SHALL mieć unikalny, a odpowiedź ten sam.
- `X-Correlation-ID`: każde żądanie i odpowiedź SHALL mieć, a odpowiedzi niosą ten sam.
- Zalecane GUID/UUID. Hub przekazując żądanie SHALL nadać **nowy** `X-Request-ID` i zachować `X-Correlation-ID`.

## Zachowanie offline `[OCPI230 §4.4]`
„OCPI messages SHOULD NOT be queued.” Nieudany lub przeterminowany POST/PUT/PATCH nie jest kolejkowany ani ponawiany.
Po odzyskaniu połączenia to serwer docelowy pobiera bieżący stan GET-em ze źródła, np. CDR za okres przerwy (filtr
od ostatniego otrzymanego CDR) i statusy EVSE przez GET Locations.

**Wniosek:** odbiorca utrzymuje znacznik „ostatnia udana synchronizacja” per partner i moduł i po przerwie robi pull
z `date_from` równym temu znacznikowi.

## Kody statusu `[OCPI230 §5]`
- HTTP: niepoprawny JSON → 400 MUST. Poprawny JSON do istniejącego zasobu → błąd HTTP MUST NOT. GET nieistniejącego
  zasobu → 404 SHOULD. Poprawny obiekt → 200 (aktualizacja) albo 201 (nowy).
- OCPI `status_code`:
| Kod | Znaczenie |
|---|---|
| 1000 | sukces (19xx: własne kody sukcesu) |
| 2000 / 2001 / 2002 / 2003 / 2004 | błąd klienta / niepoprawne lub brakujące parametry / za mało informacji / nieznana Location / nieznany Token (29xx: własne) |
| 3000 / 3001 / 3002 / 3003 | błąd serwera / nie można użyć API klienta (np. podczas rejestracji) / nieobsługiwana wersja / brak wspólnych endpointów (39xx: własne) |
| 4000 / 4001 / 4002 / 4003 | błąd huba / nieznany odbiorca / timeout przekazanego żądania / odbiorca niepołączony (49xx: własne) |
Błędy 2xxx i 3xxx od serwera hub SHALL przekazać do klienta (poza Broadcast Push).

### Objaw → pierwsza hipoteza (Wniosek z cytowanych wymagań)
| Objaw | Hipoteza do sprawdzenia | Podstawa |
|---|---|---|
| 401 na module funkcjonalnym zaraz po rejestracji | użyty `CREDENTIALS_TOKEN_A` zamiast C albo token bez Base64 | `[OCPI230 §4.1.2]` `[OCPI230 §7.1.1]` |
| 405 na POST credentials | strona już zarejestrowana; aktualizacja przez PUT | `[OCPI230 §7.2.2]` |
| 405 na PUT lub DELETE credentials | strona jeszcze niezarejestrowana | `[OCPI230 §7.2.3]` `[OCPI230 §7.2.4]` |
| 3001 w odpowiedzi na POST credentials | serwer nie mógł połączyć się z API klienta | `[OCPI230 §7.1.5]` |
| 3003 przy rejestracji | Receiver nie znalazł oczekiwanych endpointów | `[OCPI230 §7.1.6]` |
| 404 na PUT/GET obiektu klienta | `country_code`/`party_id` w URL spoza CredentialsRoles | `[OCPI230 §4.1.5.1]` |
| 2001 na PUT | `object-id` w URL różny od `id` w obiekcie | `[OCPI230 §4.1.5.1]` |
| Pull zwraca mniej obiektów niż `limit` | limit serwera (`X-Limit`); idź po `Link` | `[OCPI230 §4.1.4.1]` |
| 4001 / 4003 od huba | nieznany adres w `OCPI-to-` / odbiorca niepołączony | `[OCPI230 §5.4]` |
Test z partnerem: każdą hipotezę sprawdzasz w obu kierunkach (Sender i Receiver) i zapisujesz HTTP, `status_code` i
nagłówki, nie tylko „200”. To procedura, nie wymaganie specyfikacji.

## Odpowiedniki sekcji w OCPI 2.2.1 `[OCPI221]`
| Temat | 2.3.0 | 2.2.1 |
|---|---|---|
| Authorization header | §4.1.2 | §4.1.2 |
| Pull and Push | §4.1.3 | §4.1.3 |
| GET / paginacja | §4.1.4.1 | §4.1.4.1 |
| PUT / PATCH | §4.1.4.2–4.1.4.3 | §4.1.4.2–4.1.4.3 |
| Client Owned Object Push / Pull | §4.1.5–4.1.6 | §4.1.5–4.1.6 |
| Response format | §4.1.7 | §4.1.7 |
| Non-specified JSON fields | §4.1.8 | brak |
| Message Routing Headers | §4.1.9.2 | §4.1.8.2 |
| Broadcast Push / Open Routing / GET All | §4.1.9.3–4.1.9.5 | §4.1.8.3–4.1.8.5 |
| Nagłówki w scenariuszach / GET All / last_updated | §4.1.9.6–4.1.9.8 | §4.1.8.6–4.1.8.8 |
| OpenEnum | §17.3 | brak (`enum`) |
| Unique message IDs | §4.2 | §4.2 |
| Offline behaviour | §4.4 | §4.4 |
Porównanie 2026-11-07: kluczowe zdania (Base64 w Authorization, „SHOULD NOT be queued”, X-Correlation-ID, kody 4xxx)
występują w obu dokumentach w identycznym brzmieniu. Porównanie 2026-11-15: identyczne są też zdania o PUT/PATCH,
`X-Total-Count`, przetwarzaniu poprawnych obiektów, Broadcast Push (w tym rola „Other”), Open Routing, `last_updated`
przez hub i „pages together is the new truth”. Pozostałe zdania przed cytowaniem dla 2.2.1 sprawdzasz w `[OCPI221]`.
