# Sesja end-to-end: transakcja OCPP → Session OCPI → CDR (CSMS jako CPO)

Zakres: jak jedna transakcja OCPP 1.6 (`StartTransaction` / `MeterValues` / `StopTransaction`) albo 2.0.1
(`TransactionEvent` `Started` / `Updated` / `Ended`) staje się obiektem Session OCPI 2.2.1 / 2.3.0 u eMSP, a potem
CDR. Plik skleja fakty z kilku warstw i nie powtarza szczegółów, które są gdzie indziej:
- transport, deduplikacja, mapowanie Locations, START_SESSION ogólnie: `ocpp-ocpi-polaczenie.md`;
- mechanika Sessions, CDRs, Tokens i Commands (PUT/PATCH, credit CDR, `AllowedType`): skill `ev-ocpi-roaming-expert`
  (`references/moduly.md`);
- zdalny start, kolejka offline, ponawianie po stronie OCPP: skill `ev-ocpp-expert` (`references/wzorce.md`);
- przerwane sesje, wycena, płatność ad hoc: skill `ev-billing-tariff-expert` (`references/sesja-przerwana.md`).

Źródła: OCPP 1.6 `[16]` z erratą `[16E]`, OCPP 2.0.1 Ed4 część 2 `[201-P2]`, OCPI 2.3.0 `[OCPI230]`, OCPI 2.2.1
`[OCPI221]`. Zdania **Wniosek** to rekomendacje projektowe wyprowadzone z cytowanych faktów.

Spis:
1. Trzy obiekty i ich identyfikatory
2. Autoryzacja: OCPP Authorize a OCPI Tokens
3. Zdalny start: START_SESSION → RemoteStart / RequestStart
4. Cykl życia Session: mapowanie zdarzeń OCPP
5. Odczyty licznika → `kwh` i `charging_periods`
6. Późna transakcja po offline stacji
7. CDR po zakończeniu sesji
8. Rozbieżności w źródłach
9. Lista kontrolna przeglądu
10. Czego źródła nie określają

## 1. Trzy obiekty i ich identyfikatory
| Obiekt | Kto tworzy | Identyfikator | Źródło |
|---|---|---|---|
| transakcja OCPP 1.6 | stacja zgłasza start, `transactionId` nadaje Central System w `StartTransaction.conf` | `integer`; zalecane unikalne liczby dodatnie, ale gdy `StartTransaction` nie dotarło, stacja używa `-1` | `[16 §6.45]` `[16E §3.54]` `[16E §3.18]` |
| transakcja OCPP 2.0.1 | stacja | `identifierString[0..36]`, unikalny **w obrębie stacji**, zalecany UUID | `[201-P2 §2.48]` `[201-P2 E §1.2]` |
| Session OCPI | CPO; właścicielem danych jest CPO | `id` `CiString(36)`, unikalny w platformie CPO | `[OCPI230 §9]` `[OCPI230 §9.3.1]` |
| CDR OCPI | CPO, po zakończeniu sesji | `id` `CiString(39)` (36 dla zwykłego CDR, dłuższy dla credit CDR), `session_id` wskazuje Session | `[OCPI230 §10]` `[OCPI230 §10.3.1]` |

- Transakcja w 2.0.1 to „the portion of a charging session that is recorded by CSMS”; jej granice wyznaczają
  `TxStartPoint` i `TxStopPoint` `[201-P2 E §1.1]`. W 1.6 sesja ładowania zaczyna się od pierwszej interakcji
  (karta, zdalny start, kabel), transakcja dopiero po spełnieniu warunków ładowania, a sesja kończy się, gdy stacja
  jest znów wolna `[16 §3.6]`.
- Diagram START_SESSION w OCPI pokazuje `Session(id=15)` po `StartTransaction.conf(TransactionId=15)`
  `[OCPI230 §13.1]`. To przykład, nie wymóg.

**Wniosek:** `Session.id` nadajesz sam, a `transactionId` trzymasz jako atrybut. Identyfikator 2.0.1 jest unikalny
tylko na stacji, a w 1.6 kilka transakcji może przyjść z `-1`. Klucz po stronie OCPP to (stacja, `transactionId`), w 1.6
z regułą dopasowania dla `-1` (sekcja 6).

## 2. Autoryzacja: OCPP Authorize a OCPI Tokens
Fakty OCPP:
- 1.6: stacja SHALL dostarczać energię dopiero po autoryzacji. Gdy `idTag` nie ma na liście lokalnej ani w cache,
  SHALL wysłać `Authorize.req`; gdy jest, MAY `[16 §4.1]`. 2.0.1: to samo w `[201-P2 C01.FR.02]`.
- Central System MUST sprawdzić identyfikator w `StartTransaction.req`, bo stacja mogła go autoryzować lokalnie na
  nieaktualnych danych `[16 §4.8]`; w 2.0.1 CSMS MUST sprawdzić identyfikator w `TransactionEventRequest`
  `[201-P2 E05.FR.01]`.
- Odpowiedź inna niż `Accepted` przy trwającej transakcji: 1.6 — przy `StopTransactionOnInvalidId = true` stacja
  SHOULD zatrzymać transakcję z powodem `DeAuthorized`, przy `false` tylko przerwać energię `[16E §3.17]`. 2.0.1 —
  zależnie od `StopTxOnInvalidId` i `TxStopPoint`: `Ended` z `stoppedReason = DeAuthorized` `[201-P2 E05.FR.10]` albo
  zatrzymanie energii bez końca transakcji.
- 1.6 offline: stacja MAY dopuścić nieznane identyfikatory (`AllowOfflineTxForUnknownId`). Po powrocie łączności SHALL
  wysłać `StartTransaction` dla każdej transakcji autoryzowanej offline `[16 §3.5.4]`.

Fakty OCPI (Tokens, właściciel: eMSP):
| `Token.whitelist` `[OCPI230 §12.4.5]` | Co robi CPO po `Authorize` / starcie ze stacji | `auth_method` w Session/CDR `[OCPI230 §10.4.1]` |
|---|---|---|
| `ALWAYS` | dopuszcza token bez zapytania; real-time niedozwolony | `WHITELIST` |
| `ALLOWED` | wybiera: lista albo real-time | `WHITELIST` albo `AUTH_REQUEST` |
| `ALLOWED_OFFLINE` | real-time; gdy eMSP nie odpowiada, dopuszcza token | `AUTH_REQUEST`; przy dopuszczeniu bez odpowiedzi źródło nie określa (**Wniosek:** `WHITELIST`, bo „no request to the eMSP has been performed”) |
| `NEVER` | zawsze real-time | `AUTH_REQUEST` |

- Real-time: `POST {tokens_endpoint_url}{token_uid}/authorize` z opcjonalnym `LocationReferences`; token nieznany →
  HTTP 404 `[OCPI230 §12.2.2.2]`. Odpowiedź `AuthorizationInfo` może mieć `authorization_reference`, które trafia do
  Session i CDR `[OCPI230 §12.3.1]`. `valid = false` nie zwalnia z real-time, gdy wymaga go `whitelist`
  `[OCPI230 §12.4.5]`.
- eMSP nie musi wysyłać listy tokenów; wtedy CPO musi pytać real-time `[OCPI230 §12.1.3]`.
- Session i CDR: `authorization_reference` SHALL mieć wartość podaną przez eMSP (real-time, StartSession, ReserveNow);
  przy kilku wartościach — ostatnią `[OCPI230 §9.3.1]` `[OCPI230 §10.3.1]`. `auth_method` może się zmienić w trakcie;
  CDR SHALL mieć ostatnią metodę `[OCPI230 §10.3.1]`.

**Wniosek:** CSMS odpowiada na `Authorize` stacji wynikiem z OCPI (lista albo real-time) i zapisuje przy transakcji
`auth_method` i `authorization_reference`. Bez tego nie wypełnisz poprawnie Session ani CDR. Transakcję offline
sprawdzasz ponownie przy `StartTransaction` / `Started`; odmowa eMSP po fakcie kończy się po stronie OCPP
deautoryzacją (patrz wyżej), a w OCPI statusem sesji według sekcji 4.

## 3. Zdalny start: START_SESSION → RemoteStart / RequestStart
- Przepływ jest asynchroniczny: CPO od razu zwraca `CommandResponse` (`result`, `timeout` w sekundach), potem wysyła
  `CommandResult` na `response_url` `[OCPI230 §13.1]` `[OCPI230 §13.3.2]`. Odpowiedź stacji „doesn't always mean that
  the command was executed successfully” `[OCPI230 §13.1]`.
- Przykład z OCPI: `RemoteStartTransaction.conf(Accepted)` → `CommandResult(ACCEPTED)`, a pojazd nie zostaje
  podłączony przed timeoutem i Session nie powstaje `[OCPI230 §13.1]`. `TIMEOUT` = brak odpowiedzi stacji „in a
  reasonable time” `[OCPI230 §13.4.2]`.
- Token z StartSession jest autoryzowany przez eMSP; CPO SHALL NOT sprawdzać go przed wysłaniem do stacji. Gdy stacja
  OCPP sama go weryfikuje: dla `AD_HOC_USER` / `APP_USER` CPO SHALL NOT robić real-time u eMSP, dla `RFID` — nie w
  ciągu 15 minut od StartSession na tym EVSE `[OCPI230 §13.3.5]`. Dane tokenu SHALL trafić do Session i CDR, nawet gdy
  tokenu nie ma w module Tokens `[OCPI230 §13.3.5]`.
- 2.0.1: dla `IdTokenType` typu `Central` stacja SHALL NOT wysyłać `AuthorizeRequest` `[201-P2 C05.FR.01]`;
  `remoteStartId` SHALL pojawić się co najmniej raz w `TransactionEventRequest` `[201-P2 C05.FR.03]`.
- STOP_SESSION niesie `session_id` `[OCPI230 §13.3.6]`. Po stronie OCPP potrzebny jest `transactionId`: 1.6
  `RemoteStopTransaction.req(transactionId)` `[16 §5.12]`, 2.0.1 `RequestStopTransactionRequest` z `transactionId`
  `[201-P2 F03.FR.01]`.
- Korelacja odpowiedzi stacji z poleceniem (1.6 bez identyfikatora, 2.0.1 `remoteStartId`): `wzorce.md` §1–2
  (`ev-ocpp-expert`).

**Wniosek:**
- `authorization_reference` i token z StartSession zapisujesz w rekordzie oczekującego startu. Po `StartTransaction` /
  `Started` przenosisz je do sesji;
- tokeny OCPI `AD_HOC_USER` / `APP_USER` wysyłasz do stacji 2.0.1 jako `Central`, żeby stacja nie pytała o nie CSMS;
- długość: OCPI `Token.uid` ma do 36 znaków `[OCPI230 §12.3.2]`, a `idTag` w 1.6 to `CiString20Type`
  `[16 §7.28]`. Dla stacji 1.6 potrzebujesz mapy tokenów dłuższych niż 20 znaków.

## 4. Cykl życia Session: mapowanie zdarzeń OCPP
Fakty OCPI:
- Nowa Session: CPO robi PUT u eMSP; każda zmiana: PATCH. Sesji nie usuwa się, a stan końcowy to `COMPLETED`
  `[OCPI230 §9.1.1]`. eMSP bez push albo po swojej przerwie robi GET `[OCPI230 §9.1.2]`; GET filtruje po
  `last_updated` (`date_from` włącznie, `date_to` wyłącznie) `[OCPI230 §9.2.1.1]`.
- PATCH SHALL zawierać `last_updated`; `charging_periods` w PATCH są **dopisywane**, a pusta lista nic nie zmienia.
  Zastąpić albo usunąć okresy można tylko PUT-em całej Session `[OCPI230 §9.2.2.3]`. PUT zastępuje cały obiekt, a brak
  `charging_periods` usuwa istniejące `[OCPI230 §9.2.2.2]`.
- Statusy `[OCPI230 §9.4.3]`: `PENDING` — stan początkowy, nie wszystkie warunki spełnione, sesja może nigdy nie
  ruszyć; `ACTIVE` — kabel podłączony poprawnie i pojazd albo kierowca autoryzowany, energia płynie albo nie;
  `COMPLETED` — zakończona, bez dalszych zmian; `INVALID` — uznana za nieważną, nie będzie rozliczona; `RESERVATION`.
- `start_date_time`: w `PENDING` czas utworzenia sesji na stacji; przy przejściu do `ACTIVE` SHALL zostać zmieniony na
  chwilę przejścia. `end_date_time` może być późniejszy niż koniec ładowania (np. opłata za postój) `[OCPI230 §9.3.1]`.
- `kwh` jest wymagane (card. 1); `total_cost` pominięty nie oznacza sesji darmowej `[OCPI230 §9.3.1]`. Tak samo
  OCPP 2.0.1: brak `totalCost` w `TransactionEventResponse` nie oznacza darmowej transakcji `[201-P2 §1.60.2]`.

**Wniosek** (mapowanie; OCPI nie wiąże statusów z komunikatami OCPP):
| Zdarzenie OCPP | Session OCPI |
|---|---|
| `Authorize` zaakceptowane albo START_SESSION przyjęte, transakcji jeszcze nie ma | opcjonalnie PUT `PENDING` (`start_date_time` = czas utworzenia) |
| 2.0.1 `Started` przed autoryzacją (np. `TxStartPoint = EVConnected`) | PUT `PENDING` |
| 1.6 `StartTransaction.req`; 2.0.1 pierwsze `TransactionEvent` z autoryzowanym `idToken` | PUT albo PATCH `ACTIVE`, `start_date_time` = `timestamp` ze stacji (`[16 §6.45]`, `[201-P2 §1.60.1]`) |
| 1.6 `MeterValues` z `transactionId`; 2.0.1 `Updated` z `meterValue` | PATCH: `kwh`, nowe `charging_periods`, `total_cost`, `last_updated` |
| 1.6 `StopTransaction.req`; 2.0.1 `Ended` | PATCH `COMPLETED`, `end_date_time`, końcowe `kwh` |
| odmowa tokenu po fakcie, sesja bez podstawy do rozliczenia | `INVALID` (decyzja CPO z eMSP) |

- `last_updated` ustawiasz na czas zmiany w systemie CPO. Gdy wstawisz historyczny czas ze stacji, eMSP pobierający
  GET-em od `date_from` po swojej przerwie tej sesji nie dostanie `[OCPI230 §9.2.1.1]`.
- Nieudanego PUT/PATCH nie kolejkujesz (`[OCPI230 §4.4]`, `ocpp-ocpi-polaczenie.md` §1). Gdy nie wiesz, co ma eMSP,
  robisz GET u eMSP `[OCPI230 §9.1.1]` i wysyłasz PUT całej sesji. Uzasadnienie PUT zamiast powtórzonego PATCH:
  `moduly.md` §3 (`ev-ocpi-roaming-expert`).
- W 2.0.1 wybór `TxStopPoint` decyduje, czy postój po naładowaniu jest w transakcji. Dla ładowania jak w 1.6:
  `TxStartPoint = PowerPathClosed`, `TxStopPoint = EVConnected, Authorized` `[201-P2 E §1.1.2]`.

## 5. Odczyty licznika → `kwh` i `charging_periods`
| | OCPP 1.6 | OCPP 2.0.1 | OCPI |
|---|---|---|---|
| jednostka | `meterStart` / `meterStop` w Wh `[16 §6.45]` `[16 §6.49]`; wartość bez pól dodatkowych = rejestr energii czynnej pobranej w Wh `[16 §4.7]` | domyślnie `Energy.Active.Import.Register` w Wh `[201-P2 §2.41]` `[201-P2 §2.49]` | `kwh` w Session, `total_energy` w kWh w CDR `[OCPI230 §9.3.1]` `[OCPI230 §10.3.1]`; wymiar `ENERGY` w kWh `[OCPI230 §10.4.3]` |
| start / koniec | `meterStart`, `meterStop`; w `transactionData` zaleca się wartości `Transaction.Begin` i `Transaction.End` `[16E §3.14]` | `Started` z `context = Transaction.Begin` `[201-P2 E01.FR.09]`; `Ended` z `TxEndedMeasurands` `[201-P2 J §2.1]`; konteksty `[201-P2 §3.66]` | — |
| w trakcie | `MeterValues` co `MeterValueSampleInterval` `[16 §3.16.1]`; przy interwale > 0 stacja SHALL je wysyłać `[16E §3.15]`; `transactionId` = transakcja trwająca w chwili próbki `[16E §3.16]` | `Updated` co `SampledDataTxUpdatedInterval`; dane transakcji nigdy w `MeterValuesRequest` `[201-P2 J §2.1]` | PATCH z nowymi `charging_periods` |
| rejestr | zaleca się wysyłać stan rejestru zamiast zaczynać każdą transakcję od 0 `[16E §3.9]` | — | — |

- Każdy `ChargingPeriod` ma `start_date_time`; kończy go początek następnego, ostatni — koniec sesji
  `[OCPI230 §10.4.6]`. Liczbę okresów w Session wybiera CPO: na tyle dużo, żeby eMSP pokazał postęp, i z okresami w
  chwilach zmian taryfy `[OCPI230 §9.3.1]`. W CDR nowy okres SHALL zaczynać się przy każdym zdarzeniu istotnym dla
  kosztu; moment przekroczenia progu CPO może wyliczyć z interpolacji odczytów `[OCPI230 §10.3.1]`.
- Wymiary `CURRENT`, `ENERGY_EXPORT`, `ENERGY_IMPORT`, `POWER`, `STATE_OF_CHARGE` są tylko dla Session
  `[OCPI230 §10.4.3]`.

**Wniosek:** `kwh` = (ostatni odczyt rejestru − odczyt startowy) / 1000. Okres `ENERGY` to przyrost w tym okresie, a
nie stan rejestru. Odczyty z różnych `location` / `phase` (`[16 §3.16.3]`) filtrujesz do jednego licznika złącza
(`Outlet`, bez fazy), inaczej zsumujesz energię kilka razy.

## 6. Późna transakcja po offline stacji
Fakty OCPP:
- 1.6: komunikaty transakcyjne MUST być kolejkowane offline i dostarczone chronologicznie; CS nie wie, że komunikat
  jest historyczny, poza starym `timestamp`, i SHOULD przetworzyć go „as any other” `[16 §3.7]`. Po wyczerpaniu prób
  stacja SHOULD porzucić komunikat `[16 §3.7.1]`.
- 1.6: gdy stacja nie dostała `transactionId`, SHALL wysyłać komunikaty tej transakcji z `transactionId = -1`, a CS
  SHALL odpowiadać, jakby identyfikator był ważny `[16E §3.18]`.
- 2.0.1: `transactionId` nadaje stacja, więc transakcja offline ma go od początku `[201-P2 E §1.2]`. Zdarzenia z czasu
  offline mają `offline = true` `[201-P2 E04.FR.03]`, a `seqNo` rośnie o 1 na EVSE i pozwala sprawdzić kompletność
  (`Started` z `a`, `Ended` z `o`, każde `n` pomiędzy) `[201-P2 E §1.3.2]`.
- 2.0.1: przy braku pamięci stacja offline MAY porzucić komunikaty `Updated`, zaczynając od pośrednich
  `[201-P2 E12.FR.04]` `[201-P2 E12.FR.05]`.
- 2.0.1: `GetTransactionStatus` pokazuje, czy transakcja trwa i czy w kolejce są jeszcze jej komunikaty
  `[201-P2 E14]` `[201-P2 E14.FR.04]`.

Fakty OCPI:
- `PENDING` jest „the initial state” `[OCPI230 §9.4.3]`. Czy sesję można utworzyć od razu w `COMPLETED`, specyfikacja
  nie mówi.
- Bez `start_date_time` / `end_date_time` CPO zwykle nie może wysłać CDR. Wyjątek: obie strony to akceptują, a prawo
  lokalne pozwala; wtedy brakujące czasy ustawia się na `1970-1-1T00:00:00Z` `[OCPI230 §10.3.1]`.

**Wniosek:**
- czasy w Session i CDR bierzesz z `timestamp` stacji; czas odbioru zapisujesz osobno i używasz go w `last_updated`;
- spóźnioną transakcję, która przychodzi od razu z `Ended` / `StopTransaction`, wysyłasz jako Session od razu w
  `COMPLETED` (PUT). Wysłanie najpierw `ACTIVE` byłoby nieprawdą o stanie bieżącym. Uzgodnij to z eMSP (sekcja 10);
- CDR z transakcji 2.0.1 tworzysz po kompletnym ciągu `seqNo` albo po `GetTransactionStatus` z `messagesInQueue =
  false`. Luka w `Updated` przy pełnym `Ended` nie blokuje rozliczenia, jeśli `Ended` ma `Transaction.Begin` i
  `Transaction.End`;
- w 1.6 komunikaty z `-1` dopasowujesz po (stacja, `connectorId`, czas, `meterStop` ≥ znane `meterStart`) i trzymasz
  w kwarantannie, dopóki nie przypiszesz ich jednoznacznie. `StopTransaction(-1)` bez przyjętego `StartTransaction`
  nie ma `meterStart`, więc bez `transactionData` z `Transaction.Begin` nie wyliczysz `kwh`.

## 7. CDR po zakończeniu sesji
- CDR jest „the only billing-relevant object”, wysyłany po zakończeniu sesji. Wysyłka „as soon as possible” to dobra
  praktyka, ale strony mogą uzgodnić np. raz w miesiącu `[OCPI230 §10]`.
- Wysłanego CDR nie wolno zmienić ani zastąpić `[OCPI230 §10.1]`. Korekta to credit CDR (`credit = true`,
  `credit_reference_id`, ujemne `total_cost`) i nowy CDR `[OCPI230 §10.1.1]`. Szczegóły: `moduly.md` §4,
  `sesja-przerwana.md` §3.
- CDR zachowuje Location, EVSE, Tariffs i Token w stanie z początku sesji `[OCPI230 §10.3.1]`.
- Wymagane: `charging_periods` (co najmniej jeden), `total_energy`, `total_time`, `total_cost`; `session_id` wolno
  pominąć tylko bez modułu Sessions albo przy samej rezerwacji `[OCPI230 §10.3.1]`.
- Push: POST na CDRs endpoint eMSP `[OCPI230 §10.1.2]`; po przerwie eMSP pobiera CDR GET-em `[OCPI230 §4.4]`.

**Wniosek:** `COMPLETED` w Session wysyłasz od razu po `Ended` / `StopTransaction`. CDR — dopiero gdy dane są pełne
(sekcja 6) i wycena zamknięta, bo potem zmienisz go już tylko credit CDR-em. `charging_periods` w CDR budujesz od nowa
z pełnych odczytów, a nie kopiujesz z okresów wysłanych PATCH-em w trakcie.

## 8. Rozbieżności w źródłach
| Temat | Tekst A | Tekst B | Rozstrzygnięcie |
|---|---|---|---|
| jednostka `ENERGY` w przykładach Session | definicja: „defined in kWh” `[OCPI230 §10.4.3]` | przykład PATCH: `"kwh": 15.00` i okres `ENERGY` `"volume": 2200` `[OCPI230 §9.2.2.3]`; przykład zakończonej sesji: `kwh` 41.12 i okresy 120 + 41000 `[OCPI230 §9.3.1.1]`. Przykład poprawiono w 2.2.1-d2, „so that the total energy matches” `[OCPI230 §18.2]`, ale zgadza się tylko przy wolumenach w Wh. To samo w `[OCPI221 §9.2.2.3]` | wiąże definicja typu (kWh). Przykłady są ilustracją; nie kopiuj ich jako wzorca jednostek |
| wynik odrzuconego zdalnego startu | `CommandResultType`: `REJECTED` = „rejected by the Charge Point”, `FAILED` = „execution … failed” `[OCPI230 §13.4.2]` | przykład: `RemoteStartTransaction.conf(Rejected)` → `CommandResult(FAILED)`; dla `ReserveNow.conf(Rejected)` → `REJECTED` `[OCPI230 §13.1]` | enum wskazuje `REJECTED`. Uzgodnij z eMSP, bo przykład podaje `FAILED` |
| kompletność po `seqNo` w 2.0.1 | CSMS może sprawdzić komplet: każde `n` między `a` i `o` `[201-P2 E §1.3.2]` | stacja offline przy braku pamięci MAY porzucić `Updated` `[201-P2 E12.FR.04]` | źródło nie rozstrzyga. Wniosek w sekcji 6: luka w `Updated` nie musi blokować rozliczenia |

## 9. Lista kontrolna przeglądu
**Wniosek** (pytania wynikające z sekcji 1–8):
1. Czy `Session.id` jest nadawany przez CPO i unikalny w platformie, a nie przepisany z `transactionId`?
2. Czy przy transakcji zapisujesz `auth_method`, `authorization_reference` i dane tokenu (także z StartSession bez
   modułu Tokens)?
3. Czy CSMS uwzględnia `Token.whitelist` (`NEVER`, `ALLOWED_OFFLINE`) i regułę 15 minut dla RFID po StartSession?
4. Czy `CommandResult(ACCEPTED)` nie jest traktowany jako start sesji, a Session powstaje dopiero po
   `StartTransaction` / `Started`?
5. Czy PATCH zawsze ma `last_updated`, a korekta `charging_periods` idzie PUT-em całej sesji?
6. Czy `last_updated` to czas zmiany u CPO, a `start_date_time` / `end_date_time` to czasy ze stacji?
7. Czy energia jest liczona z rejestru (koniec − start), w kWh, z jednego licznika złącza?
8. Czy CDR czeka na komplet danych (`seqNo`, `GetTransactionStatus`, kolejka 1.6) i czy istnieje ścieżka credit CDR?
9. Czy 1.6 `transactionId = -1` jest przyjmowany (odpowiedź jak dla ważnego) i dopasowywany w kwarantannie?
10. Czy STOP_SESSION da się wykonać, gdy CSMS zna tylko `-1` albo nie zna `transactionId`?

## 10. Czego źródła nie określają
- Mapowania statusów Session na komunikaty OCPP: OCPI opisuje stany, OCPP komunikaty, tabela w sekcji 4 to Wniosek.
- Czy Session wolno utworzyć od razu jako `COMPLETED` (spóźniona transakcja) i czy eMSP musi taką przyjąć
  `[OCPI230 §9.4.3]`.
- `auth_method` dla tokenu dopuszczonego bez odpowiedzi eMSP (`ALLOWED_OFFLINE`) albo autoryzowanego offline na stacji.
- Mapowania `TokenType` OCPI na `IdTokenEnumType` OCPP i tokenów dłuższych niż 20 znaków na `idTag` 1.6.
- Którego `transactionId` użyć w zdalnym stopie 1.6, gdy stacja zna transakcję tylko jako `-1`.
- Czy `end_date_time` sesji to koniec transakcji OCPP, czy chwila zwolnienia złącza (`[16 §3.6]` rozróżnia sesję i
  transakcję, OCPI tylko dopuszcza koniec ładowania przed końcem sesji `[OCPI230 §9.3.1]`).
- Termin wysłania CDR i credit CDR: zależy od umów `[OCPI230 §10]` `[OCPI230 §10.1.1]`.

Sprawdzone fragmenty OCPI 2.2.1 brzmią tak samo jak w 2.3.0: PUT/PATCH i stan końcowy Session `[OCPI221 §9.1.1]`
`[OCPI221 §9.2.2.2]` `[OCPI221 §9.2.2.3]`, statusy `[OCPI221 §9.4.3]`, reguła 15 minut `[OCPI221 §13.3.5]`.
