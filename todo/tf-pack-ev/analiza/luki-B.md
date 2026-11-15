# Analiza luk, grupa B: pack-ev (roaming, taryfy, rozliczenia, płatności, eMSP, ID, role) → ev-intelligence

Stan: 2026-11-15. Analiza tylko do odczytu, bez sieci. Ścieżki pack-ev są względne wobec `/home/user/tf/packs/pack-ev/skills/`
(testy: `/home/user/tf/packs/pack-ev/tests/`), a ścieżki ev-intelligence wobec `/home/user/ev-intelligence/`.

## Ustalenia ogólne (ważne przed jakimkolwiek przeniesieniem)

1. **Pack-ev nie cytuje sekcji.** Źródła pack-ev to „github.com/ocpi/ocpi, tagi `2.2.1`, `v2.2.1-d2`, `v2.3.0`, pliki
   `mod_*.asciidoc`”, „baza fabryki `.claude/knowledge/...`” i import `dom-ev-charging` z lat 2024–2025. Nie ma znaczników
   `[id §sekcja]`. Każdy fakt przed przeniesieniem trzeba więc ponownie znaleźć w dokumencie z rejestru (zwykle `OCPI230`,
   `OCPI221`, `OICP23-*`) i opisać numerem sekcji z tekstu. Lokalnych kopii dokumentów nie ma: ani `.cache/ev-kb`
   w ev-intelligence, ani `.claude/knowledge` w tf. Numery sekcji w kolumnie „źródło oficjalne” są więc **przypuszczalne**
   i trzeba je sprawdzić w tekście.
2. **Repozytorium github.com/ocpi/ocpi i pliki przykładów `examples/*.json`** (np. `tariff_14_step_size`, `tariff_4_complex`)
   **nie są zarejestrowane** w `sources/evrf-ocpi.yaml`. Rejestr ma tylko PDF-y z evroaming.org. Część przykładów liczbowych
   pack-ev opiera się na tych JSON-ach. Trzeba je zarejestrować (tag i commit, SHA-256) albo odnaleźć te same przykłady
   w PDF `OCPI230`.
3. **„OCPI 2.2.1 pierwotne” (tag `2.2.1`) nie jest w rejestrze.** `OCPI221` to plik 2.2.1-d2, który w środku ma wersję
   „2.2.1-d3-pre1”. Porównań pack-ev „2.2.1 vs d2” nie da się sprawdzić bez dodatkowego wpisu. Częściowo pomoże `OCPI221-CH`.
4. **Brak docelowych skilli dla trzech tematów.** W taksonomii ev-intelligence (`taxonomy/taxonomy.yaml`) identyfikatory
   (D00.04) i role rynku (D00.03) należą do `ev-domain-expert`, a platforma eMSP (D05.08) do `ev-product-designer`.
   Podgałęzie nie mają własnych skilli. Katalog `knowledge/` zawiera tylko szablon `implementation-intelligence/vendor-quirks/_szablon.yaml`.
   To jedyne miejsce na wiedzę praktyczną (klasa D, obserwacje urządzeń). **Nie ma ustalonego miejsca na praktykę
   biznesową** (uzgadnianie rozliczeń, model terminali, UX aplikacji, huby: koszty i zasięg). Luk klasy P nie wolno więc dziś
   przenieść.
5. **Niespójność w samym ev-intelligence:** `sources/niedostepne.yaml` wymienia „Dyrektywa (UE) 2015/2366 (PSD2) i PCI DSS”
   jako `niezarejestrowana`. Tymczasem `sources/eu-inne.yaml` ma już wpis `PSD2` (pobrany 2026-11-08). Wpis w niedostepne
   trzeba zawęzić do PCI DSS i rozporządzenia delegowanego 2018/389 (SCA).
6. **Dokumenty potrzebne, ale nieobecne ani w rejestrze, ani w `niedostepne.yaml`:** eMI3 V1.0 Part 2 i IDACS
   „E-mobility ID-codes” (format `evse_id` i `contract_id` w OCPI 2.3.0), 23 CFR 680 (NEVI, USA), ISO 3166-1, prawo VAT
   i faktur (UE/PL, KSeF), RODO, OICP 2.1 i OICP 2.2 (2.2 jest tylko w `not_yet_reviewed` w `hubject-oicp.yaml`).

Klasy: **F**: fakt sprawdzalny w specyfikacji lub akcie; **P**: praktyka lub zachowanie dostawcy bez źródła oficjalnego;
**R**: procedura lub heurystyka bez nowych faktów.

---

## 1. dom-ev-ocpi → `ev-ocpi-roaming-expert`

| # | Luka | Źródło pack-ev | Cel w ev-intelligence | Klasa | Źródło oficjalne / id w rejestrze |
|---|---|---|---|---|---|
| O1 | Sessions: PUT zastępuje całą listę `charging_periods` (pusta lista usuwa okresy). PATCH wymaga `last_updated` i **dopisuje** okresy. Nie wolno używać podsegmentów URL do pól wewnętrznych. Ponowiony PATCH dubluje okresy | `dom-ev-ocpi/SKILL.md:102-104`, `:150`; `references/sesje-tokeny-komendy.md:15-18` | `references/moduly.md` §3 Sessions | F | `OCPI230` §9.2 (interfejs Receiver Sessions), `OCPI221` §9.2 |
| O2 | Ogólna semantyka PUT/PATCH: PUT niesie wszystkie wymagane pola, a pominięte opcjonalne wracają do wartości domyślnych. PATCH tylko ze zmianami; po błędzie PATCH robi się GET, a gdy obiektu brak, PUT | `dom-ev-ocpi/SKILL.md:53` | `references/transport.md` (sekcja o obiektach klienta) | F | `OCPI230` §4.1.5–4.1.6 (sprawdzić numer) |
| O3 | Cykl życia Credentials: ponowny POST po rejestracji daje HTTP 405, aktualizacja idzie przez PUT, wyrejestrowanie przez DELETE, PATCH nie istnieje, GET zwraca własne poświadczenia | `dom-ev-ocpi/SKILL.md:66`; `references/moduly-i-endpointy.md:21`; `references/test-kontraktowy.md:18` | `references/moduly.md` §1 (dziś tylko odsyłacz „§7.1.2–7.1.6”) | F | `OCPI230` §7.2, §7.1.2–7.1.6 |
| O4 | Rotacja tokenu przez PUT; „zalecane co miesiąc, natychmiast przy wycieku” | `dom-ev-ocpi/SKILL.md:70` | `references/moduly.md` §1 | F* | `OCPI230` §7 (sprawdzić; jeśli specyfikacja nie podaje okresu rotacji, to P i nie przenosić) |
| O5 | Token w obiekcie Credentials jest jawny (ASCII, do 64 znaków), a do nagłówka Authorization trafia po Base64 | `dom-ev-ocpi/SKILL.md:68` | `references/transport.md` (Authorization) | F | `OCPI230` §7.3.1 (obiekt Credentials), §4.1.2 |
| O6 | Endpoint versions i szczegóły wersji: `role` SENDER/RECEIVER (przy credentials bez znaczenia); jedno zestawienie dla platformy z wieloma rolami; moduły własne z prefiksem strony; zmiana endpointów i przejście na nowszą wersję przez PUT na credentials | `references/moduly-i-endpointy.md:9-16` | `references/wersje-i-role.md` | F | `OCPI230` §6 (Versions), §7.1.2–7.1.3 |
| O7 | Tabela URL i metod dla każdego modułu i interfejsu (Sender/Receiver: locations, sessions, tokens, commands, credentials) | `references/moduly-i-endpointy.md:18-30` | `references/moduly.md` (nowa sekcja) | F | `OCPI230` §7.2, §8.2, §9.2, §10.2, §11.2, §12.2, §13.2 |
| O8 | Token: parametr `?type=` z wartością domyślną `RFID`; ten sam `uid` może istnieć w kilku typach; Tokens nie mają DELETE | `references/moduly-i-endpointy.md:27, 32` | `references/moduly.md` §6 | F | `OCPI230` §12.2.1–12.2.2 |
| O9 | Paginacja, szczegóły: `X-Total-Count` liczy obiekty widoczne dla danego klienta; kolejne zapytanie zaczyna od `date_to` poprzedniego; dane nieobecne w pełnym pull są nieważne; klient przetwarza poprawne obiekty, a błędne loguje | `references/moduly-i-endpointy.md:37-44` | `references/transport.md` (paginacja) | F | `OCPI230` §4.1.4.1, §4.1.4.2 (część pokryta) |
| O10 | Broadcast Push (`to` = hub; tylko dane wspólne, czyli Locations i Tokens, nigdy Sessions i CDR; rola „Other”); Open Routing (bez `to`; dotyczy GET, POST, PUT, PATCH, DELETE, ale nie „GET All”); GET All przez hub | `dom-ev-ocpi/SKILL.md:74-78`; `references/moduly-i-endpointy.md:46-56` | `references/transport.md` (routing; dziś tylko nazwy §4.1.9.3–9.5) | F | `OCPI230` §4.1.9.3–4.1.9.6 |
| O11 | 2.3.0: `hub_party_id` (5 znaków) w Credentials; hub zgłasza w `roles` strony za sobą, a w 2.2.1 robił to przez `hubclientinfo` | `references/moduly-i-endpointy.md:57-58`; `references/wersje-i-zmiany.md:26, 40` | `references/wersje-i-role.md` („Co zmienia 2.3.0” ma tylko jedno zdanie) | F | `OCPI230` §7.3.1, §1.1; `OCPI221` §7.3.1 |
| O12 | Platforma nie odrzuca nieznanych pól; otwarte enumy (`OpenEnum`); walidatory nie traktują nieznanej wartości jako błędu | `dom-ev-ocpi/SKILL.md:138-139, 160`; `references/wersje-i-zmiany.md:25, 37-39` | `references/transport.md` (dziś jest tylko w `ev-integration-architect/references/ocpp-ocpi-polaczenie.md:20`) | F | `OCPI230` §4.1.8 (już cytowane w ev-integration-architect), §16 (typ OpenEnum) |
| O13 | Obiekt Token: pola, `TokenType` (`RFID`, `APP_USER`, `AD_HOC_USER`, `OTHER`, w 2.3.0 także `EMAID`), unikalna para (`uid`, `type`), `group_id` do 20 znaków dla OCPP 1.x, unieważnienie przez `valid: false` bez usuwania | `references/sesje-tokeny-komendy.md:28-33` | `references/moduly.md` §6 | F | `OCPI230` §12.3.1, §12.4.4 |
| O14 | Odpowiedź real-time: `AuthorizationInfo.allowed` (`ALLOWED`, `BLOCKED`, `EXPIRED`, `NO_CREDIT`, `NOT_ALLOWED`), ciało `LocationReferences`, kod 2002 przy braku lokalizacji, 2004 przy nieznanym tokenie | `dom-ev-ocpi/SKILL.md:117-118`; `references/sesje-tokeny-komendy.md:35-36` | `references/moduly.md` §6 | F | `OCPI230` §12.2.2, §12.3.2 (AuthorizationInfo), §12.4.1 (AllowedType), §12.4.3 (LocationReferences) |
| O15 | Zalecenie `whitelist = NEVER` dla `APP_USER` i `AD_HOC_USER`; tokenów tych typów nie trzeba wcześniej wysyłać modułem Tokens, jeśli idą tylko w komendach | `dom-ev-ocpi/SKILL.md:118`; `dom-ev-emsp-platform/references/konto-i-tokeny.md:20-21` | `references/moduly.md` §6 | F | `OCPI230` §12.4.4 (TokenType, opisy), §13.3.5 |
| O16 | Token `EMAID` (2.3.0): eMSP nie powinien go wysyłać, CPO pyta wystawcę real-time, certyfikaty kontraktu są poza OCPI | `references/sesje-tokeny-komendy.md:41-42`; `references/wersje-i-zmiany.md:29` | `references/moduly.md` §6; odsyłacz do `ev-iso15118-pki-expert` | F | `OCPI230` §12.4.4, §1.1 |
| O17 | `START_SESSION`: pola `token`, `location_id`, `evse_uid` (wymagany razem z `connector_id`), `authorization_reference`. CPO może anulować rezerwację tym samym `response_url` z wynikiem `CANCELED_RESERVATION`, tylko w sytuacji awaryjnej | `references/sesje-tokeny-komendy.md:53-58` | `references/moduly.md` §7 | F | `OCPI230` §13.3.5 (StartSession), §13.3.3 (ReserveNow), §13.1 |
| O18 | Sesja z rezerwacji: `RESERVE_NOW` tworzy Session `RESERVATION`, która przechodzi w `ACTIVE` przy starcie tym samym tokenem, a w innym razie w `COMPLETED`. `evse_uid`/`connector_id` może mieć wartość `#NA`, gdy EVSE nie jest przydzielone | `dom-ev-ocpi/SKILL.md:106`; `references/sesje-tokeny-komendy.md:20-21, 26, 59` | `references/moduly.md` §3 | F | `OCPI230` §9.3.1, §9.4.3 |
| O19 | Charging Preferences: `PUT {sessions}/{session_id}/charging_preferences` (eMSP → CPO), `ChargingPreferencesResponse`, capability `CHARGING_PREFERENCES_CAPABLE` | `references/sesje-tokeny-komendy.md:24-25`; `references/moduly-i-endpointy.md:24` | `references/moduly.md` §3 | F | `OCPI230` §9.2.1.2, §9.3.2, §9.4.1; §8.4.x (Capability) |
| O20 | `Session.total_cost` to kwota, którą eMSP płaci CPO; GET listy sesji wymaga `date_from` | `references/sesje-tokeny-komendy.md:22-23`; `dom-ev-ocpi/SKILL.md:105` | `references/moduly.md` §3 | F | `OCPI230` §9.3.1, §9.2.1.1 |
| O21 | `EVSE.uid` jest stały, nie jest numerem sprzętu i nie zmienia się po wymianie urządzenia. `evse_id` jest opcjonalny, czytelny dla człowieka i może zniknąć przy `REMOVED`. Długości: Location `id` 36, `uid` 36, `evse_id` 48. `physical_reference` | `dom-ev-ocpi/SKILL.md:130-133`; `references/moduly-i-endpointy.md:60-66` | `references/moduly.md` §2 Locations | F | `OCPI230` §8.3.1–8.3.2; `OCPI221-CH` (zmiana „uid nie jako ID sprzętu”) |
| O22 | Moduł Locations u Receivera zależy od Tariffs: eMSP musi znać taryfy złączy | `references/moduly-i-endpointy.md:71` | `references/moduly.md` §2 | F | `OCPI230` §8.1 albo §2 (zależności modułów), sprawdzić |
| O23 | Nowości w Locations 2.3.0: `ConnectorCapability` `ISO_15118_2_PLUG_AND_CHARGE` i `ISO_15118_20_PLUG_AND_CHARGE`, nowe typy złączy (MCS, `TESLA_S`), `help_phone`, `accepted_service_providers`, `parking[]`; `evse_id` według IDACS „E-mobility ID-codes” zamiast eMI3 | `references/wersje-i-zmiany.md:27-31`; `references/moduly-i-endpointy.md:72-73` | `references/wersje-i-role.md` („Co zmienia 2.3.0”) | F | `OCPI230` §1.1, §8.3.x, §8.4.x. Częściowo pokryte w `ev-evse-hardware-expert/references/zlacza-i-moc.md:43` i `ev-product-designer/references/wymagania-produktu.md:21-22`. IDACS i eMI3: brak w rejestrze i w niedostepne |
| O24 | Zmiany 2.2.1 → 2.2.1-d2: przepisane Tariffs i `step_size`, wyjaśnienie Base64, nota o braku reguł zaokrąglania, `uid` nie jako ID sprzętu, usunięcie wymogu innej taryfy w każdym `charging_period` | `references/wersje-i-zmiany.md:18-20` | `references/wersje-i-role.md` | F | `OCPI221-CH` (zarejestrowany) |
| O25 | Tagi i edycje w repozytorium (`v2.3.0-ed1`, `-ed2`, `-payments`, `-bookings`); zalecenie, by w integracji zapisywać tag, a nie samą wersję | `references/wersje-i-zmiany.md:8-16` | `references/wersje-i-role.md` | F | github.com/ocpi/ocpi: **brak w rejestrze**; `EVRF-DL` pokrywa tylko część (wariant z Booking) |
| O26 | Migracja 2.2.1 → 2.3.0 w krokach (najpierw tolerancja nieznanych pól, potem PUT credentials w nowej wersji, nowe enumy, hub_party_id, rejestr partner → wersja) | `references/wersje-i-zmiany.md:36-42` | `references/wersje-i-role.md` | R | fakty z O11, O12 |
| O27 | Test kontraktowy z partnerem: 14 scenariuszy z oczekiwanym kodem, tabela objaw → hipoteza | `references/test-kontraktowy.md:8-48` | `SKILL.md` (Procedura, krok 7) albo nowa reference `onboarding.md` (D06.02) | R | oczekiwane kody to fakty z O1–O14 i z `transport.md` |

**Pokryte w ev-intelligence (pomijam):** handshake A/B/C i wygaśnięcie tokenu A (`moduly.md:14-24`); Base64 i 401
(`transport.md:202-211`); push i pull oraz interwał (`transport.md:213-215`); podstawy paginacji (`transport.md:224-229`);
nagłówki routingu i brak routingu w modułach konfiguracyjnych (`transport.md:236-242`); X-Request-ID i X-Correlation-ID
(`transport.md:244-247`); kody 1000–4003 (`transport.md:257-267`); statusy EVSE i `REMOVED` (`moduly.md:26-55`); enumy
CommandResponse i CommandResult (`moduly.md:113-118`); whitelist i `valid=false` (`moduly.md:99-105`); offline bez kolejki
(`transport.md:249-255`); wirtualne EVSE dla OCPP 1.x (`wersje-i-role.md:184-188`); mapowanie komend OCPI → OCPP
(`ev-integration-architect/references/ocpp-ocpi-polaczenie.md:80-85`); `authorization_reference` do sesji i CDR (tamże, `:85`).

---

## 2. dom-ev-oicp-hubs → `ev-ocpi-roaming-expert/references/oicp.md`

| # | Luka | Źródło pack-ev | Cel | Klasa | Źródło oficjalne / id |
|---|---|---|---|---|---|
| I1 | Kody statusu brakujące w tabeli ev-intelligence: **017** Unauthorized Access (ID niezgodne z certyfikatem), 101–122 (błędy uwierzytelnienia), 200 EvcoID locked, 320 usługa niedostępna, 501 brak komunikacji z EVSE; zasada, że logika opiera się na kodzie, a `AdditionalInfo` jest dla człowieka | `dom-ev-oicp-hubs/SKILL.md:34`; `references/operacje-oicp.md:24-43` | `oicp.md` §9 | F | `OICP23-CPO-DT #CodeType`, `OICP23-CPO-COM #Security` |
| I2 | `CPOPartnerSessionID` i `EMPPartnerSessionID` mają do 250 znaków; hub odsyła je w odpowiedziach | `SKILL.md:40-41` | `oicp.md` §3 | F | `OICP23-CPO-COM #session_handling`, `OICP23-CPO-DT` |
| I3 | ID jest przypisane do roli i unikalne na rynku; hub nie odróżnia rekordów EVSE huba od rekordów jego pod-operatorów | `SKILL.md:35-38` | `oicp.md` §2 | F | `OICP23-CPO-COM #hub_provider_and_operator`, `#provider_and_operator_ids` |
| I4 | Pull EVSE Data: `deltaType` (insert/update/delete) przy `LastCall`; paginacja `?page=0&size=20`, obowiązkowa po stronie EMP | `SKILL.md:72-74` | `oicp.md` §6 | F | `OICP23-EMP-SVC #eRoamingPullEvseData`. Typy danych EMP są w `not_yet_reviewed` |
| I5 | Obowiązki EMP: `PushAuthenticationData` obowiązkowe; odbiór CDR obowiązkowy tylko dla EMP online; `GetChargeDetailRecords` obowiązkowe dla EMP offline; EMP online i offline | `references/operacje-oicp.md:8-22` | `oicp.md` (nowa podsekcja przy §4–5) | F | `OICP23-EMP-SVC` (zarejestrowany) |
| I6 | Zmiany w 2.3 według Release Notes: nowe wersje operacji; nowe filtry `GetChargeDetailRecords` (SessionID, OperatorID, CDRForwarded); `PullEvseDataRecordType`, usunięte `OperatorEvseData`, `ChargingStationNames` jako `InfoTextType`, `ChargingModes` przeniesione do `ChargingFacilityType`, „Unspecified” odrzucane w push, `null` w pull dla starych danych; nowe pola (`HardwareManufacturer`, `SubOperatorName`, `EnergySource`, `DynamicPowerLevel`, `AccessibilityLocation`); nowe pola ChargingNotification i `ErrorClassType` | `references/operacje-oicp.md:46-62` | `oicp.md` §1 (nowa sekcja „Zmiany w 2.3”) | F | `OICP23-RN` (zarejestrowany, dziś cytowany tylko 2 razy) |
| I7 | Macierz pól obowiązkowych 2.1/2.2/2.3 (`OperatorName`, `HouseNum`, `PostalCode`, `Power`, `PaymentOptions`, `RenewableEnergy`, `ChargingStart/End`) i skutek: `null` przy partnerze na starszej wersji | `references/operacje-oicp.md:64-77` | `oicp.md` | F | kolumna 2.3: `OICP23-CPO-DT`, `OICP23-RN`; kolumny 2.1 i 2.2: OICP 2.2 jest w `not_yet_reviewed`, OICP 2.1 nie ma w rejestrze |
| I8 | ChargingNotifications: hub przekazuje EMP i odsyła jego `Acknowledgement` do CPO; powiadomienia nie zastępują CDR | `references/operacje-oicp.md:80-81` | `oicp.md` §8 | F | `OICP23-CPO-SVC #eRoamingChargingNotifications` |
| I9 | Dynamic Pricing: EMP pobiera dane tylko od CPO, z którymi ma kontrakt cenowy (`LastCall` daje zmiany); `PartnerProductID` także w `AuthorizeStart` | `references/operacje-oicp.md:82-85` | `oicp.md` §7 | F | `OICP23-EMP-SVC`, `OICP23-CPO-SVC #eRoamingAuthorizeStart`; Dynamic Pricing Functional Guide jest niezarejestrowany (`docs/DO-ZROBIENIA.md:40`) |
| I10 | DIN `OperatorID`: kod kraju według E.164 i obowiązkowa `*`; w rekordzie EVSE kraj alfa-3 (`DEU`), w ID alfa-2 | `SKILL.md:91, 95` | `oicp.md` §2 | F | `OICP23-CPO-DT #OperatorIDType`, `#CountryCodeType`/`AddressIso19773Type` (sprawdzić kotwicę) |
| I11 | Architektura adapterów: jeden model kanoniczny (ACL), osobne zewnętrzne ID sesji dla każdego protokołu, osobna kolejka push na operację i partnera, idempotentny CDR, jawna tabela `OperatorID` ↔ (`country_code`, `party_id`) | `SKILL.md:123-148`; `references/adaptery-ocpi-oicp.md:8-53` | `oicp.md` §11 (Wniosek); lepiej `ev-integration-architect` (poza grupą) | R | fakty już w `oicp.md` §3, §5, §11 |
| I12 | P2P czy hub: kryteria, koszty i zasięg hubów, Gireve i e-clearing jako huby | `SKILL.md:116-121` | D06.01 (`ev-ocpi-roaming-expert`) | P | brak źródła oficjalnego (koszty i zasięg). Gireve OCPI IG czeka w `DO-ZROBIENIA.md:38` |

**Pokryte:** model HBS i certyfikat (`oicp.md:41-50`), SessionID (`:57-60`), push sekwencyjny (`:61-62`), ścieżki autoryzacji
A/B/C i PIN (`:68-83`), RemoteStart z 603/604 i czasem poniżej 10 s (`:90-93`), jeden CDR na SessionID i dobre praktyki
(`:96-109`), ActionType (`:127-131`), statusy EVSE (`:150-151`), wersje usług (`:24-34`), wycofanie 2.1 (`:23`), tabela
OICP vs OCPI (`:217-241`), formaty EvseID i EvcoID (`:51-55`), limity AUP (`:199-215`).

---

## 3. dom-ev-tariffs-pricing → `ev-billing-tariff-expert`

| # | Luka | Źródło pack-ev | Cel | Klasa | Źródło oficjalne / id |
|---|---|---|---|---|---|
| T1 | Granice `min_current`/`max_current` i `min_power`/`max_power`: min włącznie, max wyłącznie. Przy dokładnie 32 A pasuje element z `min_current: 32` | `dom-ev-tariffs-pricing/SKILL.md:50, 58-59`; `references/przyklady.md:66-67` | `references/taryfy-ocpi.md` §3 (dziś bez włącznie/wyłącznie dla prądu i mocy) | F | `OCPI230` §11.4.7 |
| T2 | Czy `end_time` jest wyłączny: pack-ev oznacza to jako [założenie] | `SKILL.md:55`; `references/specyfikacja-taryf.md:55-56` | `taryfy-ocpi.md` §3 | F | `OCPI230` §11.4.7. Jeśli tekst nie rozstrzyga, piszemy „specyfikacja nie określa” |
| T3 | Brak pola `day_of_week` oznacza każdy dzień, a pusta lista `[]` żaden dzień | `references/specyfikacja-taryf.md:52` | `taryfy-ocpi.md` §3 | F | `OCPI230` §11.4.7 (opcjonalność) + `OCPI-TSG` cz. 2 pkt 6 |
| T4 | Okno przez północ: do którego dnia tygodnia należy część po północy (pack-ev: nierozstrzygnięte) | `references/specyfikacja-taryf.md:53-54` | `taryfy-ocpi.md` §6 (rozbieżności) | F | `OCPI230` §11.4.7; zapewne „nie określa” |
| T5 | Nadwyżka z zaokrąglenia `step_size` trafia do **ostatniego okresu** danego wymiaru i nie rozkłada się proporcjonalnie | `SKILL.md:71-72`; `references/step-size-i-zaokraglanie.md:8-9, 43` | `taryfy-ocpi.md` §4 | F | `OCPI230` §10.3.1 (przykłady step_size); sprawdzić, czy tak wynika z tekstu |
| T6 | Błędy w przykładach specyfikacji: `tariff_4` sobota 2,28 zamiast 2,375; d2 „przykład #3” 0,80 zamiast 0,73; „2.2.1 pierwotne” 0,383 zamiast 0,55; „free of charge” 0,78/0,80/0,73 | `references/przyklady.md:22-26`; `references/step-size-i-zaokraglanie.md:23-36`; `tests/test_ocpi_tariff_calc.py:5-7` | `taryfy-ocpi.md` §6 (rozbieżności z oboma cytatami i rozstrzygnięciem) | F | `OCPI230` §11 (przykłady), `OCPI221`; JSON `examples/*.json` i tag `2.2.1` **niezarejestrowane** |
| T7 | Przykłady liczbowe: VAT dla każdego składnika (15/20/10%), `max_price` i `min_price` netto i brutto, restrykcja `max_power`, `max_duration` („pierwsze 30 min gratis”), CDR z krokiem 300 s, przykłady A i B dla `tariff_14` | `references/przyklady.md:6-61`; `SKILL.md:119-133` | `taryfy-ocpi.md` (przykłady) i `evals/skill_evals/ev-billing-tariff-expert.json` | F | przykłady ze specyfikacji: `OCPI230` §11.x i §10.x; obliczenia jako **Wniosek** |
| T8 | Różnice modelu taryfy 2.2.1 i 2.3.0: w 2.2.1 `price` bez VAT, a `min/max_price` typu Price (`excl_vat`, `incl_vat`); w 2.3.0 `PriceLimit` i `tax_included`. Brak `vat` to co innego niż `0.0` | `references/specyfikacja-taryf.md:6-12, 39`; `SKILL.md:78-83` | `taryfy-ocpi.md` §1 (dziś tylko 2.3.0) | F | `OCPI221` §11.3.1, §11.4.2; `OCPI230` §11.4.2–11.4.3 |
| T9 | `tariff_alt_url` i `energy_mix` w Tariff; cena zależna od rynku nie ma własnych pól; przykład specyfikacji `PROFILE_CHEAP` z `tariff_alt_url` | `SKILL.md:30, 106`; `references/cena-dla-kierowcy.md:22-28`; `references/specyfikacja-taryf.md:24, 28` | `taryfy-ocpi.md` §1 i §5 | F | `OCPI230` §11.3.1 i przykłady §11 |
| T10 | Znaczenie `TariffType`: `REGULAR` to RFID bez preferencji albo preferencja REGULAR; `PROFILE_*` obowiązuje po wyborze profilu; CPO podaje taryfę dla każdego wspieranego profilu | `references/specyfikacja-taryf.md:58-66`; `references/przypisanie-i-zarzadzanie.md:27-28` | `taryfy-ocpi.md` §1 | F | `OCPI230` §11.4.8, §9 (Charging Preferences) |
| T11 | `Connector.tariff_ids`: kilka taryf, ale jednocześnie aktywna jedna danego `type`; taryfy tego samego typu mają rozłączne okresy ważności; przed DELETE taryfy sprawdza się, czy żaden konektor jej nie wskazuje | `references/przypisanie-i-zarzadzanie.md:22-31`; `references/specyfikacja-taryf.md:68-71` | `taryfy-ocpi.md` §5 | F | `OCPI230` §8.3.x (Connector), §11.2.2 |
| T12 | Jedna waluta na taryfę i CDR; przeliczania walut OCPI nie opisuje | `references/cena-dla-kierowcy.md:53-56`; `SKILL.md:84` | `ceny-afir-ocpp.md` §4 (czego źródła nie określają) | F | `OCPI230` §11.3.1, §10.3.1 (zapis negatywny) |
| T13 | USA, 23 CFR 680.116(a): cena przed startem w $/kWh, cena ze startu nie zmienia się w sesji, struktura opłat | `SKILL.md:102, 152`; `references/przypisanie-i-zarzadzanie.md:70-72` | `ceny-afir-ocpp.md` (nowa sekcja) albo poza zakresem | F | **brak w rejestrze i w niedostepne** (eCFR, NEVI) |
| T14 | Hierarchia przypisań (sieć → lokalizacja → EVSE → grupa klientów), podgląd zmian, audyt cztery oczy, taryfa zerowa B2B, marża na kWh, inna opłata za debet i kredyt opisana tekstem | `references/przypisanie-i-zarzadzanie.md:7-20, 48-63, 79-92`; `SKILL.md:93` | brak miejsca w ev-intelligence | P | praktyka oznaczona w pack-ev jako [założenie] |
| T15 | Zaokrąglanie w kodzie: `Decimal`, poziom (składnik, okres, suma), tryb, jedno zaokrąglenie na końcu, tolerancja 0,01 przy porównaniu z CDR | `SKILL.md:108-111`; `references/step-size-i-zaokraglanie.md:49-57` | `cdr-i-wycena.md` §6 (procedura silnika) | R | sam fakt, że OCPI nie określa zaokrąglania, jest już pokryty |
| T16 | Lista „co pokazać kierowcy przed startem” (stawki, start postoju, `step_size` > 1, limity, brutto i waluta, okna) | `references/cena-dla-kierowcy.md:33-40` | `ceny-afir-ocpp.md` (Wniosek z AFIR art. 5) | R | AFIR art. 5 (pokryty); reszta to heurystyka |

**Pokryte:** pierwszy pasujący element i element domyślny (`taryfy-ocpi.md:35-44`), AND restrykcji i czas lokalny
(`:46-58`), `step_size` raz na sesję i przykłady (`:60-81`), `reservation` (`:56-58`), `min/max_price` przed i po podatkach
(`:23-27`), `tax_included` (`:21-22`), `preauthorize_amount` (`:28`), `tariff_alt_text` (`:29-30`), brak reguł zaokrąglania
(`:31-32`), taryfa bezpłatna (`:33`), zmiana taryfy w sesji (`:83-87`), AFIR art. 5 ust. 3–5 (`ceny-afir-ocpp.md:116-146`),
interfejs Tariffs GET/PUT/DELETE (`taryfy-ocpi.md:111`), publikacja taryfy przed przypisaniem (TSG pkt 15, `:102`).

---

## 4. dom-ev-cdr-settlement → `ev-billing-tariff-expert` (wycena, pola) i `ev-ocpi-roaming-expert` (mechanika)

| # | Luka | Źródło pack-ev | Cel | Klasa | Źródło oficjalne / id |
|---|---|---|---|---|---|
| C1 | Pola CDR brakujące w ev-intelligence: wartości `auth_method` (`AUTH_REQUEST`, `COMMAND`, `WHITELIST`), `meter_id`, `remark`, `last_updated` (w praktyce data utworzenia), kiedy wolno pominąć `session_id` (bez modułu Sessions, rezerwacja bez sesji), `cdr_location` tylko z właściwym EVSE i Connectorem, `start_date_time` przy rezerwacji bez sesji | `dom-ev-cdr-settlement/SKILL.md:39`; `references/cdr-pola-i-korekty.md:11-27` | `cdr-i-wycena.md` §1–2 | F | `OCPI230` §10.3.1, §10.4.1 (AuthMethod), §10.4.2 (CdrLocation) |
| C2 | `invoice_reference_id` do 39 znaków; uzasadnienie podwójnego oznaczenia (`credit` i `credit_reference_id`) | `references/cdr-pola-i-korekty.md:24-25` | `cdr-i-wycena.md` §2 | F | `OCPI230` §10.3.1 |
| C3 | Pull CDR: filtr `date_from`/`date_to` działa po dacie utworzenia (CDR się nie zmienia) | `SKILL.md:28-29` | `ev-ocpi-roaming-expert/references/moduly.md` §4 | F | `OCPI230` §10.2.1.1 |
| C4 | Idempotentny odbiór po kluczu (`country_code`, `party_id`, `id`): ta sama treść daje sukces bez skutku, inna treść to anomalia; surowy JSON tylko do odczytu; zbieg pull i push | `SKILL.md:60-67`; `references/uzgadnianie-i-spory.md:32-33` | `cdr-i-wycena.md` §6 albo `ev-integration-architect` | R | sama unikalność `id` per `country_code`/`party_id` jest pokryta (`cdr-i-wycena.md:129`). Kod odpowiedzi na duplikat: źródło nie określa |
| C5 | Łańcuch korekt: kredytowy wysyłasz przed nowym CDR, a przy kolejnej korekcie kredytujesz **ostatni** CDR, nie pierwszy | `references/cdr-pola-i-korekty.md:59-66` | `ev-ocpi-roaming-expert/references/moduly.md` §4 (Wniosek) | R | `OCPI230` §10.1.1 (pokryty) |
| C6 | Uzgadnianie okresu: trzy źródła (CDR, Sessions, licznik), procedura w 7 krokach, tabela rozjazdów, proces sporu, model danych | `SKILL.md:69-80`; `references/uzgadnianie-i-spory.md:8-69` | D06.04 / D09.05 (bez treści w ev-intelligence) | R | brak źródła oficjalnego procesu; fakty pomocnicze pokryte |
| C7 | Kontrole spójności CDR (waluta, `total_time` względem czasów, energia względem okresów, kredytowy względem oryginału) | `references/cdr-pola-i-korekty.md:68-76` | `cdr-i-wycena.md` §6 | R | reguły własne, nie wymóg OCPI |
| C8 | Faktura kierowcy u eMSP: nota korygująca po CDR kredytowym, faktura zbiorcza, VAT, KSeF | `SKILL.md:94-101`; `references/uzgadnianie-i-spory.md:53-61` | D09.04 (nieopracowane) | P | prawo VAT i faktur UE/PL: **brak w rejestrze i w niedostepne** |

**Pokryte:** CDR jako jedyny obiekt rozliczeniowy, push przez POST i termin wysyłki (`moduly.md:67-78`), credit CDR
z ujemnym `total_cost` (`moduly.md:72-77`), taryfy z chwili startu (`cdr-i-wycena.md:127-131`), pola kosztów
(`cdr-i-wycena.md:136-155`), `charging_periods` i wymiary (`:157-167`), `signed_data` (`:169-174`), CDR bez czasu
(`:133-134`), taryfa bezpłatna w CDR (`:131`), OICP: jeden CDR na sesję (`oicp.md:97-99`).

---

## 5. dom-ev-payments → `ev-billing-tariff-expert` (`cdr-i-wycena.md` §5, `platnosc-ad-hoc.md`)

| # | Luka | Źródło pack-ev | Cel | Klasa | Źródło oficjalne / id |
|---|---|---|---|---|---|
| Y1 | Obiekt Terminal: `terminal_id`, `customer_reference` albo `party_id`/`country_code`, adres (kraj alfa-3), `invoice_base_url`, `invoice_creator`, `reference` (numer seryjny), `location_ids` i `evse_uids` (suma obu zbiorów), `last_updated` | `dom-ev-payments/references/ocpi-payments.md:15-28`; `SKILL.md:81-82` | `cdr-i-wycena.md` §5 (dziś tylko przebieg) | F | `OCPI230` §16.3 (obiekt Terminal) |
| Y2 | Financial Advice Confirmation: `id`, `authorization_reference`, `total_costs`, `currency`, `eft_data`, `capture_status_code` i `_message`; obiekt potrzebny tylko wtedy, gdy fakturę wystawia CPO | `references/ocpi-payments.md:30-44` | `cdr-i-wycena.md` §5 | F | `OCPI230` §16.3 |
| Y3 | Interfejsy i endpointy: PTP jako Sender (`terminals`: GET, `activate`, `{id}/deactivate`, PUT, PATCH; FAC: GET), CPO jako Receiver (POST Terminal, POST FAC) | `references/ocpi-payments.md:52-61`; `SKILL.md:49-57` | `cdr-i-wycena.md` §5 | F | `OCPI230` §16.2 |
| Y4 | Sekwencja aktywacji: terminal zintegrowany (referencja od producenta → `activate` → POST Terminal → PATCH przypisań) albo dostarczony osobno; po co aktywacja | `references/ocpi-payments.md:63-67`; `references/terminale-przypisanie.md:40` | `cdr-i-wycena.md` §5 | F | `OCPI230` §16.1 (Terminal Activation) |
| Y5 | Capabilities EVSE dla płatności: `CHIP_CARD_SUPPORT`, `CONTACTLESS_CARD_SUPPORT`, `CREDIT_CARD_PAYABLE`, `DEBIT_CARD_PAYABLE`, `PED_TERMINAL` | `references/terminale-przypisanie.md:42`; `dom-ev-emsp-platform/references/mapa-i-dostepnosc.md:24-25` | `cdr-i-wycena.md` §5; `ev-product-designer` | F | `OCPI230` §8.4.x (Capability) |
| Y6 | AFIR: „pula ładowania” (art. 2 pkt 51) uzasadnia jeden terminal dla kilku punktów w jednym miejscu, ale nie terminal wspólny dla różnych lokalizacji | `references/terminale-przypisanie.md:71-73` | `ceny-afir-ocpp.md` §1 | F | `AFIR` art. 2 pkt 51, art. 5 ust. 1 (zarejestrowany) |
| Y7 | SCA dla płatności inicjowanej przez kierowcę; późniejsze dobicie kwoty jako transakcja inicjowana przez sprzedawcę | `SKILL.md:115-117` | `platnosc-ad-hoc.md` §8 | F | `PSD2` art. 97 (dokument zarejestrowany, artykuł nieopracowany); RTS 2018/389 niezarejestrowane (`DO-ZROBIENIA.md:35-37`) |
| Y8 | PCI DSS na poziomie architektury: CSMS nie widzi PAN ani CVV; hosted fields, SDK PSP, tylko token i statusy | `SKILL.md:110-114` | `platnosc-ad-hoc.md` §8 | P | PCI DSS w `niedostepne.yaml` (niezarejestrowana) |
| Y9 | Pojęcia kartowe: capture ≤ blokady, void, refund, chargeback; terminy chargebacku | `references/preautoryzacja-i-sesja.md:4-13`; `SKILL.md:99-107` | `platnosc-ad-hoc.md` §7 | P | zasady schematów kartowych i PSP. `PSD2` art. 75 pokrywa tylko zwolnienie blokady (już opisane) |
| Y10 | Dobór `preauthorize_amount`, kto zatrzymuje sesję przy limicie, zapis wartości z chwili startu | `references/preautoryzacja-i-sesja.md:15-23` | `platnosc-ad-hoc.md` | R | `OCPI230` §16.4 (StopSession od PTP, pokryte) |
| Y11 | Tabela przypadków końca sesji (przerwana, bez energii, limit osiągnięty, sesja wisi, karta odrzucona, stacja offline) | `references/preautoryzacja-i-sesja.md:25-34` | `sesja-przerwana.md` §4 | R | części OCPP 2.1 są pokryte (C19–C22) |
| Y12 | Maszyna stanów płatności i klucze idempotencji capture, void i refund; timeout PSP jako stan nieznany | `references/preautoryzacja-i-sesja.md:36-40` | `platnosc-ad-hoc.md` | R | brak |
| Y13 | Cykl życia terminala, historia przypisań, warianty wyboru EVSE, wymiana „nowy najpierw”, tap-to-pay i terminal offline | `references/terminale-przypisanie.md:7-60`; `SKILL.md:77-89` | brak miejsca (D05.02/D09.03) | P | praktyka branży, [do weryfikacji] u PTP |
| Y14 | Limity kart flotowych egzekwuje eMSP przy autoryzacji; abonament poza OCPI | `references/preautoryzacja-i-sesja.md:42-46` | brak | P | [założenie] w pack-ev |
| Y15 | Dowód zakupu przy ad hoc: kwota z capture, `eft_data`, KSeF, RODO | `SKILL.md:91-97` | D09.04 | P | prawo VAT i RODO: brak w rejestrze i w niedostepne |

**Pokryte:** przebieg transakcji Payments, `InvoiceCreator`, `CaptureStatusCode` (`cdr-i-wycena.md:176-188`),
`preauthorize_amount` (`taryfy-ocpi.md:28`), AFIR art. 5 ust. 1–2 z terminem 1.01.2027 i jednym terminalem w puli
(`ceny-afir-ocpp.md:117-124`), OCPP 2.1 C18–C25 (`platnosc-ad-hoc.md`, tego nie ma w pack-ev), PSD2 art. 75–76
(`platnosc-ad-hoc.md:82-95`), OICP `PaymentOptions` (`oicp.md:155-156`), rola PTP jako Receiver CDR
(`wersje-i-role.md:168`). Moduł Direct Payment dla 2.2.1 (`OCPI-DP`) jest zarejestrowany, ale nieopracowany w obu
repozytoriach.

---

## 6. dom-ev-emsp-platform → brak skilla; najbliżej `ev-product-designer` (D05.08), fakty protokołu do `ev-ocpi-roaming-expert`

| # | Luka | Źródło pack-ev | Cel | Klasa | Źródło oficjalne / id |
|---|---|---|---|---|---|
| E1 | Cykl życia karty w operacjach OCPI: wydanie (PUT i potwierdzenie GET-em), aktywacja, zgubienie (PATCH `valid: false`), wymiana, wygaśnięcie kontraktu, odblokowanie | `dom-ev-emsp-platform/references/konto-i-tokeny.md:23-31`; `SKILL.md:42-48` | `ev-product-designer` (nowa reference) | R | fakty z O13 (`OCPI230` §12) |
| E2 | Zablokowany token nie przerywa trwającej sesji, więc przy kradzieży wysyła się `STOP_SESSION`; blokada przy `ALWAYS` działa dopiero po przetworzeniu PATCH | `SKILL.md:44-47`; `references/konto-i-tokeny.md:33-35` | `ev-product-designer` | P | [wiedza ogólna] w pack-ev. Druga część wynika z O13 (F) |
| E3 | Dobór `whitelist` do nośnika (indywidualna karta, przedpłacona, wysokie ryzyko) | `references/konto-i-tokeny.md:49-50`; `SKILL.md:35-40` | `ev-product-designer` | R | — |
| E4 | `TOKEN_GROUP_CAPABLE`, `status_schedule`, wartości `parking_restrictions` (`CUSTOMERS`, `DISABLED`, `EV_ONLY`, `PLUGGED`, `TAXIS`) | `references/konto-i-tokeny.md:18-19`; `references/mapa-i-dostepnosc.md:16, 21` | `ev-product-designer/references/wymagania-produktu.md` | F | `OCPI230` §8.3.2, §8.4.x |
| E5 | `NO_CREDIT` jako odpowiedź dla abonamentów przedpłaconych | `references/konto-i-tokeny.md:45-46` | `ev-ocpi-roaming-expert/references/moduly.md` §6 | F | `OCPI230` §12.4.1 |
| E6 | Push przekazuje zmiany „(semi) real-time” bez gwarantowanego czasu | `references/mapa-i-dostepnosc.md:32-33` | `ev-ocpi-roaming-expert/references/transport.md` | F | `OCPI230` §4.1.3 albo §8.1 (sprawdzić) |
| E7 | Świeżość statusu: wiek statusu w UI, próg nieświeżości, metryka p95 `last_updated` → odbiór | `references/mapa-i-dostepnosc.md:29-39` | `ev-product-designer` | R | — |
| E8 | Deduplikacja stacji z kilku źródeł (klucz silny i słaby, źródło prawdy dla pola, historia scaleń) | `references/mapa-i-dostepnosc.md:54-63`; `SKILL.md:56-58` | `ev-product-designer` / D06.03 | R | — |
| E9 | Kontrole jakości danych przy imporcie Locations | `references/mapa-i-dostepnosc.md:65-69` | D06.03 | R | — |
| E10 | NEVI 23 CFR 680.116(c): lista danych dla stron trzecich, status portu „w terminach OCPI 2.2.1” | `references/mapa-i-dostepnosc.md:80-85` | `ev-product-designer` | F | **brak w rejestrze i w niedostepne** |
| E11 | CarPlay, Android Auto, nawigacja w aucie | `references/mapa-i-dostepnosc.md:87-97` | — | P | dokumentacja Apple i Google to nie źródło EV, poza zasadą źródeł; nie przenosić |
| E12 | Stany aplikacji przy starcie zdalnym i mapowanie `CommandResult` na komunikat | `references/start-zdalny-i-sesja.md:21-42`; `SKILL.md:62-66, 85-94` | `ev-product-designer` (częściowo jest w `ev-ocpi-roaming-expert/SKILL.md:52-76`) | R | enumy pokryte |
| E13 | Abonamenty, sesja na granicy okresu, historia i dowody, tabele zgłoszeń wsparcia | `references/rozliczenie-i-wsparcie.md:25-69` | `ev-product-designer` / D07.06 | R | — |
| E14 | Różnica kWh między autem a stacją jako normalne straty | `references/rozliczenie-i-wsparcie.md:43` | `ev-compliance-expert` (metrologia) | P | brak źródła |
| E15 | RODO: minimalizacja danych w tokenach, retencja | `references/konto-i-tokeny.md:73-76` | — | P | RODO: brak w rejestrze i w niedostepne |

**Pokryte:** pola karty stacji (`facilities`, `opening_times`, `charging_when_closed`, `help_phone`, `energy_mix`):
`ev-product-designer/references/wymagania-produktu.md:21-22`; `publish`/`publish_allowed_to`: `moduly.md:32-41`; `max_electric_power`
i V×A: `ev-evse-hardware-expert/references/zlacza-i-moc.md:59`; AFIR art. 20 i NAP: `ceny-afir-ocpp.md:138-139` i
`ev-cpms-architect`; AFIR art. 5 ust. 2 (rezygnacja z automatycznej autoryzacji): `ceny-afir-ocpp.md:123-124`; zakaz
sprawdzania godzin i statusu w real-time: `moduly.md:98`.

---

## 7. dom-ev-identifiers → brak skilla; najbliżej `ev-domain-expert` (D00.04); formaty OICP już w `ev-ocpi-roaming-expert/references/oicp.md`

| # | Luka | Źródło pack-ev | Cel | Klasa | Źródło oficjalne / id |
|---|---|---|---|---|---|
| D1 | Mapa identyfikatorów (EVSE ID, `evse_id`, `uid`, `country_code` + `party_id`, EMAID, token, UID karty) z tym, kto je nadaje | `dom-ev-identifiers/SKILL.md:31-40`; `references/identyfikatory-ocpi-i-tokeny.md:146-173` | `ev-domain-expert` (nowa reference) | R | części F: O13, O21, D5 |
| D2 | Składnia EVSE ID: kraj 2 litery, operator 3 znaki, `E`, ID punktu 1–31 znaków, opcjonalna `*` | `references/formaty.md:100-111`; `scripts/ev_id_check.py:14-15, 63` | `ev-domain-expert`; dla OICP `oicp.md` §2 | F | eMI3 Part 2 i IDACS **brak w rejestrze i w niedostepne**. Zarejestrowane: `OICP23-CPO-DT #EvseIDType` (wyrażenie regularne ISO i DIN) i prawdopodobnie `OCHP14` (typ EVSE ID, sprawdzić) |
| D3 | Składnia EMAID: 2 + 3 + instancja 9 + cyfra kontrolna, separator `-` albo `*` | `references/formaty.md:114-123`; `scripts/ev_id_check.py:16-17, 32` | jw. | F | ISO 15118-2 Annex H (wpis „ISO 15118” w `niedostepne.yaml`, płatna); `OICP23-CPO-DT #EvcoIDType` (zarejestrowany; zob. konflikt K4); `OCHP14` (sprawdzić) |
| D4 | Algorytm cyfry kontrolnej EMAID jest niedostępny (to nie Luhn ani mod 10); praktyka Hubject i Plugsurfing; walidator OCHP | `SKILL.md:51-57`; `references/formaty.md:125-131` | `ev-domain-expert`; odpowiedź z pierwszym zdaniem o normie niedostępnej | F (niedostępne) + P | ISO 15118-2 (niedostepne); praktyka dostawców (P); ochp.eu jest zablokowany (`niedostepne.yaml`, hosty) |
| D5 | `country_code` to ISO 3166-1 alfa-2, a `party_id` to CiString(3) według ISO 15118; para identyfikuje stronę, a nie punkt | `references/identyfikatory-ocpi-i-tokeny.md:147-149` | `ev-ocpi-roaming-expert/references/moduly.md` albo `ev-domain-expert` | F | `OCPI230` §8.3.1, §12.3.2 i §16.1 (CiString); ISO 3166-1 brak w niedostepne |
| D6 | CiString nie rozróżnia wielkości liter, więc ID porównuje się po normalizacji | `SKILL.md:63-64` | `ev-domain-expert` | F + R | `OCPI230` §16.1 (definicja CiString); normalizacja to R |
| D7 | Urzędy i rejestry nadające kody operatorów w krajach | `references/identyfikatory-ocpi-i-tokeny.md:171-173`; `references/formaty.md:143` | `sources/niedostepne.yaml` | F | brak źródła; wpis do niedostepne |
| D8 | UID karty, token i kontrakt to trzy różne identyfikatory, łączy je eMSP | `SKILL.md:60-61`; `references/identyfikatory-ocpi-i-tokeny.md:160-169` | `ev-domain-expert` | R | — |

**Pokryte:** formaty EvseID, EvcoID, OperatorID i ProviderID w wersjach ISO i DIN (`oicp.md:51-55`); hasła D00.04
w taksonomii (`ev-domain-expert/references/taksonomia-drzewo.md:72-79`, bez treści).

---

## 8. dom-ev-market-roles → brak skilla; najbliżej `ev-domain-expert` (D00.03), a roaming do `ev-ocpi-roaming-expert` (D06.01)

| # | Luka | Źródło pack-ev | Cel | Klasa | Źródło oficjalne / id |
|---|---|---|---|---|---|
| M1 | Rozszerzona lista ról: host, OSD/DSO, sprzedawca energii, producent, flota, kierowca, NAP | `dom-ev-market-roles/SKILL.md:23-35` | `ev-domain-expert` | P (część F) | definicje operatora i NAP: `AFIR` art. 2 i art. 20, `AFIR-655`; OSD i sprzedawca: dyrektywa 2019/944 (niedostepne); host i producent bez źródła |
| M2 | Przepływ pieniędzy w sesji roamingowej (kierowca → eMSP → CPO → host); OCPI przenosi dane, nie pieniądze | `SKILL.md:49-56`; `references/mapa-przeplywow.md:106-123` | `ev-domain-expert` | R | role OCPI: `OCPI230` §2.3 (pokryte) |
| M3 | Modele biznesowe (CPO+eMSP, white-label, ad hoc, karta flotowa, host z udziałem w przychodach) | `SKILL.md:58-66` | `ev-domain-expert` | P | brak |
| M4 | Hub, P2P czy hybryda: kryteria i pytania przed integracją | `references/roaming-modele.md:128-150` | D06.01 | P | topologie są pokryte (`wersje-i-role.md:180-182`, `OCPI230` §3); koszty bez źródła |
| M5 | Mapa „kto z kim i jakim kanałem” | `references/mapa-przeplywow.md:106-119` | `ev-domain-expert` | R | — |
| M6 | Rynki PL, UE i USA: same oznaczenia [do weryfikacji] | `references/rynki-i-regulacje.md:151-172` | nic do przeniesienia | P | `ev-compliance-expert` ma już AFIR, PL-EMOB i EIPA z rejestru |

**Pokryte:** role OCPI i platformy (`wersje-i-role.md:158-161`), typowe moduły dla ról (`:163-178`), kierunek Tokens i
pozostałych modułów (`moduly.md`), ad hoc w AFIR (`ceny-afir-ocpp.md:117-122`).

---

## 9. Skrypty

| Skrypt | Co robi | Odpowiednik w ev-intelligence | Zależności | Testy w pack-ev | Docelowy skill | Werdykt |
|---|---|---|---|---|---|---|
| `dom-ev-tariffs-pricing/scripts/ocpi_tariff_calc.py` (321 wierszy) | Liczy koszt sesji z taryfy OCPI dla `charging_periods`: pierwszy pasujący element dla każdego wymiaru, restrykcje w czasie lokalnym (`--tz`), `step_size` raz na sesję z nadwyżką w ostatnim okresie, VAT dla każdego składnika, `min/max_price` netto i brutto. Porównuje wynik z CDR (`--cdr`, `--tolerance`), ma tryb `--json`, kody wyjścia 0/1/2 | **brak** (`tools/`: ev_kb, ev_kb_mcp, ev_kb_poufne, skill_check, skill_eval, render_taxonomy, factory_check; jedyny skrypt skilla to `ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py`) | tylko stdlib: argparse, datetime, json, math, sys, decimal, pathlib, zoneinfo. `zoneinfo` potrzebuje systemowej bazy tzdata (na Windowsie pakietu `tzdata`) | `tests/test_ocpi_tariff_calc.py` (189 wierszy), `tests/test_ocpi_tariff_cdr.py` (94 wiersze; potrzebuje `examples/ocpi-tariff-cdr/` z `cdr_flow.py` i `data/*.json`). Testy mają postać skryptów z `main()`, nie pytest ani unittest. Szukają korzenia po `.claude/hooks` (układ po instalacji fabryki), więc w tym repo się nie uruchomią. pytest nie jest zainstalowany | `ev-billing-tariff-expert/scripts/` | **Warto przenieść po adaptacji.** (1) Obsługuje tylko model 2.2.1 (`excl_vat`/`incl_vat`, ok. wierszy 202–219), a skill ev-intelligence jest oparty na 2.3.0: trzeba dodać `PriceLimit` (`before_taxes`/`after_taxes`), `tax_included` i `Price.before_taxes`/`taxes`. (2) Docstring i testy cytują tagi GitHuba: trzeba przepisać na `[OCPI230 §10.3.1]`, `[OCPI230 §11.4.x]`, a liczby testów oprzeć na przykładach z PDF. (3) Regułę T5 (nadwyżka w ostatnim okresie) trzeba sprawdzić w źródle. (4) Elementy `reservation` pomija z ostrzeżeniem. (5) Testy trzeba przepisać na unittest z `ROOT = Path(__file__).parent.parent`, jak `tests/test_ocpp_frame_check.py`, i dołączyć dane przykładu |
| `dom-ev-identifiers/scripts/ev_id_check.py` (136 wierszy) | Sprawdza składnię EVSE ID i EMAID (wykrywa typ, normalizuje separatory i wielkość liter, sprawdza limit 48 znaków, zgłasza mieszane separatory). Nie sprawdza cyfry kontrolnej ani rejestru; kody wyjścia 0/1/2 | **brak** | tylko stdlib: argparse, json, re, sys | `tests/test_ev_id_check.py` (101 wierszy), ten sam wzorzec ROOT po `.claude/hooks` | `ev-ocpi-roaming-expert/scripts/` (formaty OICP są w `oicp.md`) albo `ev-domain-expert` (D00.04) | **Nie przenosić w obecnej postaci.** Reguły pochodzą ze źródeł wtórnych (sam plik oznacza je jako [do weryfikacji]: OSM, IONITY, mobilityid). Nie obsługuje form DIN (`+49*536`). Akceptuje instancję EMAID bez prefiksu `C`, co jest sprzeczne z `OICP23-CPO-DT #EvcoIDType` (K4). Da się go przebudować na wyrażenia regularne z `OICP23-CPO-DT` (EvseIDType, EvcoIDType, OperatorIDType, ProviderIDType), które są zarejestrowanym źródłem. Wtedy jest to walidator „składni według OICP 2.3”, a nie według ISO 15118 czy eMI3 |

Pozostałe testy pack-ev z tej grupy dotyczą tylko scenariuszy modelowych: `tests/skill_evals/dom-ev-{ocpi,oicp-hubs,tariffs-pricing,
cdr-settlement,payments,emsp-platform,identifiers,market-roles}.json` (3–5 scenariuszy każdy). Kandydaci do
`evals/skill_evals/` w ev-intelligence (po weryfikacji oczekiwań):
- `patch-sesji-i-okresy` (O1);
- `ocpi-hub-routing-4001` (O10);
- `push-evse-rownolegle` i `oicp-cdr-i-sessionid` (częściowo pokryte);
- `usa-podatek-i-limity-cen` (T8);
- `kalkulator-strefa-i-cdr` (skrypt);
- `terminal-roamingowy-preautoryzacja` (Y1–Y4);
- `karta-rfid-zgubiona` (O13, E2).

Ewaluacja na modelu jest płatna i wymaga zgody (CLAUDE.md).

---

## 10. Sprzeczności pack-ev ↔ ev-intelligence

| # | Temat | pack-ev | ev-intelligence | Rozstrzygnięcie / co sprawdzić |
|---|---|---|---|---|
| K1 | Struktura `Price` w CDR i taryfie OCPI 2.3.0 | `total_cost (Price: excl_vat, incl_vat)`: `dom-ev-cdr-settlement/SKILL.md:41`, `references/cdr-pola-i-korekty.md:19, 62`; „Kwoty w polu Price mają excl_vat i incl_vat”: `dom-ev-tariffs-pricing/references/cena-dla-kierowcy.md:54`; kalkulator też (`ocpi_tariff_calc.py:202-219`). Do tego „2.3.0 w CDR zmienia wobec 2.2.1-d2 tylko odwołania do norm”: `dom-ev-cdr-settlement/SKILL.md:32-33` | `Price`: `before_taxes` wymagane, `taxes` jako lista `TaxAmount` `[OCPI230 §17.8, §17.9]`: `skills/ev-billing-tariff-expert/references/cdr-i-wycena.md:154-155` | ev-intelligence cytuje sekcję 2.3.0. Pack-ev opisuje model 2.2.1, a o zmianie typu `Price` (moduł typów, nie `mod_cdrs`) nie wspomina. Sprawdzić `OCPI221` §16 (Price) i `OCPI230` §17.8. Wniosek: pack-ev jest nieaktualny dla 2.3.0 |
| K2 | OICP 2.3: `MeteringSignature` a `SignedMeteringValues` | „`MeteringSignature` zastąpiły `SignedMeteringValues`…” (odwrócony kierunek): `dom-ev-oicp-hubs/SKILL.md:84`. Sprzeczne także z własnym `references/operacje-oicp.md:50` („usunięte MeteringSignature; nowe SignedMeteringValues”) | `SignedMeteringValues` i `CalibrationLawVerificationInfo` jako pola opcjonalne CDR: `ev-ocpi-roaming-expert/references/oicp.md:100-103, 116-122` | Błąd redakcyjny w pack-ev SKILL.md. Potwierdzić w `OICP23-RN #eRoamingChargeDetailRecord` |
| K3 | Od której wersji OICP nie ma SOAP | „SOAP nie jest dostępny dla usług od 2.2 wzwyż”: `dom-ev-oicp-hubs/SKILL.md:139-140` | „Od OICP 2.3 dostępne są tylko API REST” `[OICP23-RN #Introduction]`: `oicp.md:38` | Twierdzenia różnią się zakresem (2.2 vs 2.3). Sprawdzić `OICP-README` i `OICP23-RN #Introduction`. Do tego czasu wiąże zdanie z cytatem w ev-intelligence |
| K4 | Instancja EMAID / EvcoID | przykład `NL-TNM-000122045-U` (instancja bez `C`), reguła „instancja 9 alfanumerycznych”: `dom-ev-identifiers/references/formaty.md:119, 123`; `scripts/ev_id_check.py:32`. Sprzeczne też z własnym `dom-ev-oicp-hubs/SKILL.md:94` (`DE-8EO-CAet5e4XY-3`) | OICP ISO: „instancja 8 znaków poprzedzona C” `[OICP23-CPO-DT #EvcoIDType]`: `oicp.md:53` | ev-intelligence ma cytat ze źródła zarejestrowanego (dla OICP). Reguła ogólna ISO 15118-2 jest niedostępna (płatna), więc o EMAID poza OICP trzeba pisać „ISO 15118-2 niedostępna”. Przykład pack-ev nie spełnia reguły OICP |
| K5 | Wynik komendy po `timeout` | „Brak wyniku w `timeout` → komenda nieudana”: `dom-ev-ocpi/SKILL.md:124-125` | „gdy `CommandResult` nie przyjdzie w tym czasie, eMSP **może założyć**, że nie przyjdzie wcale” `[OCPI230 §13.3.2]`: `ev-ocpi-roaming-expert/SKILL.md:60-61`, `references/moduly.md:113-114` | Pack-ev mówi więcej, niż mówi specyfikacja. Wiąże ev-intelligence |
| K6 | Znak pozostałych sum w CDR kredytowym | „Znak pozostałych sum… spec nie rozstrzyga wprost [do weryfikacji]”: `dom-ev-cdr-settlement/SKILL.md:57-58` | „dane jak w oryginale, tylko `total_cost` z wartościami ujemnymi” `[OCPI230 §10.1.1]`: `ev-ocpi-roaming-expert/references/moduly.md:75` | ev-intelligence rozstrzyga to z cytatem; pack-ev do poprawy |
| K7 | CDR przy płatności ad hoc | „Ad hoc… **nie ma CDR do eMSP**”: `dom-ev-tariffs-pricing/SKILL.md:87`, `references/cena-dla-kierowcy.md:8`; `dom-ev-cdr-settlement/SKILL.md:101` | w module Payments CDR trafia do PTP (PTP jest Receiverem CDRs): `cdr-i-wycena.md:185-186`, `wersje-i-role.md:168` | To nie sprzeczność wprost (eMSP rzeczywiście nie dostaje CDR), ale sformułowanie w pack-ev wprowadza w błąd. Sam pack-ev to przyznaje w `dom-ev-payments/SKILL.md:129`. Przy przenoszeniu trzymać się ev-intelligence |
| K8 | „OCPI 2.2.1” jako punkt odniesienia | „2.2.1 pierwotne” daje 0,383 EUR, a d2 daje 0,55: `references/step-size-i-zaokraglanie.md:25-26`; `SKILL.md:73-74, 128` | `OCPI221` to plik d2 (wewnątrz „2.2.1-d3-pre1”): `sources/evrf-ocpi.yaml:27-30`, `wersje-i-role.md:143` | Różne dokumenty pod tą samą nazwą. Twierdzeń pack-ev o „2.2.1 pierwotnym” nie da się sprawdzić w rejestrze |
| K9 | Pokrycie hubów | „Inne huby (Gireve, e-clearing.net): w bazie ich nie ma”: `dom-ev-oicp-hubs/SKILL.md:22, 120-121` | OCHP 1.4 (e-clearing.net) opracowany w `ochp.md`; eMIP poufny, tylko werdykt: `oicp.md:257`, `sources/poufne/gireve-emip.yaml` | ev-intelligence ma więcej; nic do przenoszenia |
| K10 | (wewnątrz ev-intelligence) status PSD2 | — | `sources/niedostepne.yaml`: „Dyrektywa (UE) 2015/2366 (PSD2) i standard PCI DSS”, dostęp `niezarejestrowana`; a `sources/eu-inne.yaml` ma wpis `id: PSD2` | Do poprawy w `niedostepne.yaml`: zostawić PCI DSS i RTS 2018/389 |

## 11. Podsumowanie liczbowe

| Skill pack-ev | F | P | R | Razem |
|---|---|---|---|---|
| dom-ev-ocpi | 25 | 0 | 2 | 27 |
| dom-ev-oicp-hubs | 10 | 1 | 1 | 12 |
| dom-ev-tariffs-pricing | 13 | 1 | 2 | 16 |
| dom-ev-cdr-settlement | 3 | 1 | 4 | 8 |
| dom-ev-payments | 7 | 5 | 3 | 15 |
| dom-ev-emsp-platform | 4 | 4 | 7 | 15 |
| dom-ev-identifiers | 6 | 0 | 2 | 8 |
| dom-ev-market-roles | 0 | 4 | 2 | 6 |
| **Razem** | **68** | **16** | **23** | **107** |

Uwagi do liczenia:
- D4 liczę jako F (fakt niedostępny), a M1 jako P.
- E2 liczę jako P, choć druga połowa wynika z O13.
- Sprzeczności K1–K10 (10 pozycji) liczę osobno, poza tabelą.
- Z 68 luk F tylko kilka wymaga źródła spoza rejestru: O25, T6 (część), T13, E10, D2, D3, D7, I7 (kolumny 2.1/2.2) i Y7 (RTS).
  Pozostałe da się sprawdzić w już zarejestrowanych `OCPI230`, `OCPI221`, `OCPI221-CH`, `OCPI-TSG`, `OICP23-*`, `AFIR` i `PSD2`.

Najcenniejsze luki:
1. O1–O2: semantyka PUT/PATCH w Sessions. PATCH dopisuje `charging_periods`, a ponowienie dubluje okresy. To częsty błąd
   integracji, a źródło `OCPI230` §9.2 jest zarejestrowane.
2. O13–O16, E5: szczegóły modułu Tokens. `TokenType`, `AuthorizationInfo.allowed` z `NO_CREDIT`, `LocationReferences`
   z 2002/2004, zalecenie NEVER dla APP_USER i AD_HOC_USER, token EMAID w 2.3.0 (`OCPI230` §12).
3. Y1–Y5: moduł Payments OCPI 2.3.0. Obiekty Terminal i FAC, endpointy, aktywacja, capabilities płatnicze; ev-intelligence
   ma tylko przebieg (`OCPI230` §16).
4. O10–O12: Broadcast Push, Open Routing, GET All, `hub_party_id` i tolerancja nieznanych pól w 2.3.0 (`OCPI230` §4.1.8,
   §4.1.9, §7.3.1).
5. I1, I5, I6 i T1–T6: pełna tabela kodów OICP z 017, obowiązki EMP i zmiany z Release Notes (`OICP23-*`), a także
   granice restrykcji taryf i błędy w przykładach specyfikacji (`OCPI230` §11.4.7, §10.3.1).
