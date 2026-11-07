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

## Push i pull `[OCPI230 §4.1.3]`
Push opcjonalny, **pull wymagany**, żeby odbiorca mógł się zsynchronizować po utracie połączenia. Dla produkcji push
jest „strongly advised”. Pull list: interwał „think in hours, not minutes”, z losowym rozrzutem (splay).

## Żądania i obiekty należące do klienta `[OCPI230 §4.1.4–4.1.6]`
- Metody: GET, POST, PUT, PATCH, DELETE. `Content-Type: application/json` SHALL przy żądaniach z treścią.
- Obiekty należące do klienta (np. Tariff należący do CPO): URL `{base-ocpi-url}/{end-point}/{country-code}/{party-id}/{object-id}`.
  POST nie jest obsługiwany, nowy obiekt wysyła się przez PUT.
- `country_code` / `party_id` niezgodne z CredentialsRoles z rejestracji → serwer może odpowiedzieć HTTP 404.
  `object-id` w URL różny od `id` w obiekcie → zalecany `status_code` 2001.

## Paginacja (każdy GET listy) `[OCPI230 §4.1.4.1]`
- Parametry żądania: `date_from` (włącznie, po `last_updated`), `date_to` (wyłącznie), `offset` (domyślnie 0), `limit`.
- Nagłówki odpowiedzi: `Link` (następna strona, jeśli to nie ostatnia), `X-Total-Count`, `X-Limit` (górny limit
  serwera, a nie liczba zwróconych obiektów).
- Najlepsza praktyka: najstarsze obiekty najpierw. Wzrost `X-Total-Count` w trakcie przeglądania nie wymaga ponowień.
  Spadek (np. przy `date_to`) → ponów poprzedni GET z `offset` mniejszym o 1.

## Format odpowiedzi `[OCPI230 §4.1.7]`
Obiekt JSON z polami: `data` (obiekt / lista / string), `status_code` (4 cyfry, wymagane), `status_message` (opcjonalne),
`timestamp` (wymagane). Gdy specyfikacja nie określa `data`, odbiorca akceptuje brak `data` i dowolną wartość, a nadawca
zostawia pole puste (np. PUT Session, PATCH charging periods).

## Routing przez hub `[OCPI230 §4.1.9.2]`
- Nagłówki `OCPI-to-party-id`, `OCPI-to-country-code`, `OCPI-from-party-id`, `OCPI-from-country-code` SHALL być
  zaimplementowane dla każdego żądania i odpowiedzi modułów funkcjonalnych (Tokens, Locations, CDRs…). Nie zawsze muszą
  występować (zob. Open Routing Request, §4.1.9.4).
- Moduły konfiguracyjne (Credentials, Versions, Hub Client Info): routing headers SHALL NOT be used.
- Pozostałe mechanizmy hubów: Broadcast Push (§4.1.9.3), GET All via Hubs (§4.1.9.5), tabela wymaganych nagłówków
  dla scenariuszy (§4.1.9.6), znaczniki czasu obiektów przez huby (§4.1.9.8).

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

## Odpowiedniki sekcji w OCPI 2.2.1 `[OCPI221]`
| Temat | 2.3.0 | 2.2.1 |
|---|---|---|
| Authorization header | §4.1.2 | §4.1.2 |
| Pull and Push | §4.1.3 | §4.1.3 |
| GET / paginacja | §4.1.4.1 | §4.1.4.1 |
| Response format | §4.1.7 | §4.1.7 |
| Message Routing Headers | §4.1.9.2 | §4.1.8.2 |
| Unique message IDs | §4.2 | §4.2 |
| Offline behaviour | §4.4 | §4.4 |
Porównanie 2026-11-07: kluczowe zdania (Base64 w Authorization, „SHOULD NOT be queued”, X-Correlation-ID, kody 4xxx)
występują w obu dokumentach w identycznym brzmieniu. Pozostałe zdania przed cytowaniem dla 2.2.1 sprawdzasz w `[OCPI221]`.
