# Identyfikatory i role rynkowe

**Źródła niedostępne.** Pełnej składni EVSE ID i eMA ID (Contract ID) nie da się tu sprawdzić. OCPI odsyła do dokumentu
„E-mobility ID-codes: the purpose of IDs, ID usage and ID format” na stronie EV Roaming Foundation, którego nie ma w
rejestrze `[OCPI230 §2.5]` `[OCPI230 §8.3.2]`. OICP opiera wyrażenia regularne na DIN SPEC 91286 (niezarejestrowana) i
ISO 15118-1 (norma płatna, `sources/niedostepne.yaml`) `[OICP23-CPO-DT #EvseIDType]`. Algorytmu cyfry kontrolnej eMA ID
żaden dokument w bazie nie podaje. Poniżej jest tylko to, co mówią OCPI 2.3.0 i 2.2.1, OICP 2.3, AFIR z aktem
wykonawczym 2025/655, ustawa o elektromobilności i dokumentacja EIPA. Zdania **Wniosek** to interpretacja.

## Spis treści
1. Mapa identyfikatorów
2. Strona w OCPI: `country_code` i `party_id`
3. EVSE ID i identyfikator punktu
4. Token, kontrakt i UID karty
5. Kto nadaje kody operatorów i dostawców
6. Role rynkowe: AFIR, PL, OCPI, OICP
7. Rozbieżności
8. Czego źródła nie określają

## 1. Mapa identyfikatorów
| Identyfikator | Co identyfikuje | Kto nadaje | Typ i reguła | Znacznik |
|---|---|---|---|---|
| `country_code` + `party_id` | stronę w danej roli (CPO, eMSP…) | strona; w rejestrach krajowych (sekcja 5) | alfa-2 i `CiString(3)` „following the ISO-15118 standard” | `[OCPI230 §7.4.1]` |
| `Location.id` | lokalizację w platformie CPO | CPO | `CiString(36)`, nigdy nie zmieniany | `[OCPI230 §8.3.1]` |
| `EVSE.uid` | EVSE technicznie, w platformie CPO | CPO | `CiString(36)`, nigdy nie zmieniany; nie do wyświetlania | `[OCPI230 §8.3.2]` |
| `EVSE.evse_id` | EVSE „human readable” | CPO, z kodem operatora | `CiString(48)`, opcjonalny | `[OCPI230 §8.3.2]` |
| `Connector.id` | złącze w obrębie EVSE | CPO | `CiString(36)`; dwa złącza różnych EVSE mogą mieć ten sam `id` | `[OCPI230 §8.3.3]` |
| `Token.uid` + `type` | token (karta, aplikacja) | RFID: zwykle ukryty ID nośnika; aplikacja: eMSP | `CiString(36)` | `[OCPI230 §12.3.2]` |
| `Token.contract_id` | kontrakt kierowcy w platformie eMSP | eMSP | `CiString(36)`; zalecany format eMA ID | `[OCPI230 §12.3.2]` |
| `visual_number` | numer nadrukowany na karcie | wydawca | `string(64)`; może być równy `contract_id` | `[OCPI230 §12.3.2]` |
| `group_id` | grupa tokenów działających jak jeden | eMSP | `CiString(36)`; OCPP 1.5/1.6 (`parentId`) do 20 znaków | `[OCPI230 §12.3.2]` |
| OperatorID / ProviderID | CPO / EMP w Hubject | rola partnera, unikalne na całym rynku | wyrażenie regularne ISO albo DIN | `[OICP23-CPO-COM #provider_and_operator_ids]` |
| EvseID / EvcoID | punkt / kontrakt w OICP | CPO / EMP | wyrażenie regularne ISO albo DIN | `[OICP23-CPO-DT #EvseIDType]` `[OICP23-CPO-DT #EvcoIDType]` |
| UID (RFID) | kartę RFID w OICP | nośnik | 8, 14 albo 20 znaków szesnastkowych | `[OICP23-CPO-DT #UIDType]` |
| Recharging Point ID code | punkt dla NAP | operator, z kodem operatora od IDRO | „combination of string/text and numeric” | `[AFIR-655 Annex, tabela B]` |
| Identyfikator EIPA | bazę, punkt i operatora w PL | Rejestr (kod operatora) i operator (reszta) | przykłady `PL-S77`, `PL-S77-P12345ABC`, `PL-S77-E12345ABC` | `[EIPA-OPIS §3]` |

**Wniosek:** UID karty, `contract_id` i `party_id` to trzy różne poziomy: nośnik, umowa kierowcy i strona rynku.
CPO uczy się z tokenu, który eMSP wydał kontrakt, i do niego kieruje CDR `[OCPI230 §12]`.

## 2. Strona w OCPI: `country_code` i `party_id`
- Każda rola platformy ma unikalną kombinację `role`, `party_id` i `country_code`. Platforma może mieć tę samą rolę
  kilka razy, np. CPO z usługą white-label dla „wirtualnych” CPO `[OCPI230 §7.3.1]`.
- `country_code` jest po to, by URL obiektu był unikalny, bo `party_id` może się powtarzać w różnych krajach. Strona
  działająca w kilku krajach może używać kraju siedziby dla wszystkich połączeń `[OCPI230 §7.3.1]`.
- `party_id` i `country_code` nie mają bezpośredniego związku z kodami w EVSE ID i Contract ID (eMI3/IDACS). Strona
  MAY wysyłać EVSE ID z innym kodem operatora niż jej `party_id` `[OCPI230 §7.3.1]`.
- `country_code` w Location to kraj CPO (alfa-2), a kraj lokalizacji to pole `country` (ISO 3166-1 alfa-3)
  `[OCPI230 §8.3.1]`.
- `hub_party_id` (`CiString(5)`): kod kraju i `party_id` huba sklejone w jeden ciąg `[OCPI230 §7.3.1]`.
- `CiString` nie rozróżnia wielkości liter i dopuszcza tylko drukowalne ASCII. `string` rozróżnia wielkość liter
  `[OCPI230 §17.4]` `[OCPI230 §17.11]`.

**Wniosek:** porównujesz identyfikatory OCPI po normalizacji wielkości liter, a klucz strony w bazie danych to para
(`country_code`, `party_id`) z rolą, nigdy sam `party_id`.

## 3. EVSE ID i identyfikator punktu
- **OCPI:** `evse_id` jest zgodny z dokumentem „E-mobility ID-codes” (niedostępny). Jest opcjonalny, bo przy statusie
  `REMOVED` można go usunąć i użyć ponownie w terenie `[OCPI230 §8.3.2]`. W CDR (`CdrLocation`) `evse_id` jest
  obowiązkowy `[OCPI230 §10.4.4]`. OCPI 2.2.1 odsyłał do „eMI3 standard version V1.0, Part 2” `[OCPI221 §8.3.2]`.
- `uid` nie powinien opierać się na identyfikatorze sprzętu: po przeniesieniu tego samego urządzenia do innej
  lokalizacji złamałby wymóg unikalności `[OCPI230 §8.3.2]`.
- Ładowarka OCPP 1.x z kilkoma złączami na EVSE: CPO SHOULD pokazać złącza jako osobne EVSE (mapowanie EVSE ID na
  connector ID) `[OCPI230 §8.3.2]` `[OCPI230 §13.3.5]`.
- **OICP, EvseID** `[OICP23-CPO-DT #EvseIDType]`:
  - ISO: kraj alfa-2, kod operatora 3 znaki, litera `E`, potem 1–30 znaków `[A-Z0-9*]`; separator `*` opcjonalny;
  - DIN: kod kraju według ITU-T E.164 (np. `+49`), separator `*` obowiązkowy;
  - przykłady: `DE*AB7*E840*6487`, `DEAB7E8406487`, `+49*810*000*438`.
- **OICP, OperatorID:** ISO `DE*A36` lub `DEA36`, DIN `+49*536`; to część EvseID `[OICP23-CPO-DT #OperatorIDType]`.
- **AFIR:** ID punktu dla NAP zawiera kod operatora wydany przez IDRO i służy m.in. do rozliczeń i rezerwacji
  `[AFIR-655 Annex, tabela B]`. Mapowanie EVRF: pole `evse_id` w EVSE `[OCPI-NAP-MAP]`.
- **EIPA:** identyfikator punktu `PL-S77-E12345ABC`. Część z kodem operatora nadaje Rejestr, resztę operator, unikalną
  w obrębie swojej infrastruktury. Baza ma analogiczny identyfikator z `P` `[EIPA-OPIS §3]`.

## 4. Token, kontrakt i UID karty
- `Token.uid`: dla `RFID` zwykle ukryty identyfikator odczytany przez czytnik (to nie wymóg); dla `APP_USER` i
  `AD_HOC_USER` unikalny identyfikator wygenerowany przez eMSP. Nazwa `uid` ma odróżniać pole od `contract_id`
  `[OCPI230 §12.3.2]`.
- `TokenType`: `AD_HOC_USER` (jednorazowy), `APP_USER` (ten sam dla każdej sesji użytkownika), `EMAID` (gdy stacja i
  pojazd komunikują się według ISO 15118), `OTHER`, `RFID`. eMSP-owi zaleca się nie wysyłać tokenów `EMAID`, bo CPO
  i tak dowiaduje się ze stacji, kto wydał token, i pyta go w autoryzacji real-time. Zarządzanie certyfikatami
  kontraktowymi jest poza OCPI 2.3.0 `[OCPI230 §12.4.4]`.
- **OICP, EvcoID** `[OICP23-CPO-DT #EvcoIDType]`:
  - ISO: instancja 8 znaków poprzedzona `C`; opcjonalny separator tylko `-`; przykład `DE-8EO-CAet5e4XY-3`;
  - DIN: instancja 6 znaków; separator `*` albo `-`; przykład `DE*8EO*Aet5e4*3`;
  - na końcu znak kontrolny (w wyrażeniu: cyfra lub litera dla ISO, cyfra lub `X` dla DIN).
- **OICP, ProviderID:** kraj alfa-2 i 3 znaki, część EvcoID; przykłady `DE8EO`, `DE-8EO`
  `[OICP23-CPO-DT #ProviderIDType]`.
- **OICP, identyfikacja:** w komunikatach eRoamingAuthorization `RFIDIdentification` MUST NOT być użyte, a dla RFID
  SHOULD tylko `RFIDMifareFamilyIdentification`; zdalna autoryzacja MUST tylko `RemoteIdentification`; Plug & Charge przez
  `PlugAndChargeIdentification` z EvcoID `[OICP23-CPO-DT #IdentificationType]`. Hubject zamienia małe litery na wielkie
  w EvcoID (QR, zdalna) i w UID `[OICP23-CPO-DT #QRCodeIdentificationType]` `[OICP23-CPO-DT #RFIDIdentificationType]`.

## 5. Kto nadaje kody operatorów i dostawców
- **AFIR:** państwo członkowskie wyznacza IDRO, które do 14.04.2025 wydaje i prowadzi unikalne kody co najmniej dla
  operatorów punktów ładowania i dostawców usług mobilności `[AFIR art. 20 ust. 1]`.
- **OCPI 2.3.0:** dostawców i operatorów trzeba znać z góry, a wymagania formatu i listę urzędów nadających kody
  podaje strona EV Roaming Foundation (poza bazą) `[OCPI230 §2.5]`.
- **OCPI 2.2.1** wymieniał rejestry krajowe: Benelux IDRO, BDEW (DE), Austrian Mobile Power (AT, lista niepubliczna),
  AFIREV (FR), urząd węgierski i EIPA dla Polski `[OCPI221 §2.5.1]` `[OCPI221 §2.5.2]` `[OCPI221 §2.5.3]`
  `[OCPI221 §2.5.4]` `[OCPI221 §2.5.5]` `[OCPI221 §2.5.6]`. W 2.3.0 tej listy już nie ma.
- **EIPA:** przy rejestracji Rejestr nadaje operatorowi lub dostawcy unikalny identyfikator albo uznaje identyfikator
  podany w formularzu `[EIPA-OPIS §5]`; kod operatora jest „unikalny w UE” `[EIPA-OPIS §3]`.
- Ustawa o elektromobilności nie wspomina IDRO ani nadawania kodów (w tekście nie ma tych pojęć). Czy EIPA jest IDRO
  w rozumieniu AFIR art. 20 ust. 1, źródła w bazie nie mówią.

## 6. Role rynkowe: AFIR, PL, OCPI, OICP
| Rola | AFIR | PL (ustawa o elektromobilności) | OCPI 2.3.0 `[OCPI230 §2.3]` | OICP 2.3 |
|---|---|---|---|---|
| Operator punktu (CPO) | odpowiada za zarządzanie i eksploatację punktu i świadczy usługę ładowania, także w imieniu i na rzecz MSP `[AFIR art. 2 pkt 39]` | operator ogólnodostępnej stacji: budowa, zarządzanie, bezpieczeństwo, eksploatacja, konserwacja, remonty `[PL-EMOB art. 2]` (pkt 7) | CPO: prowadzi sieć punktów | CPO z OperatorID `[OICP23-CPO-COM #provider_and_operator_ids]` |
| Dostawca usług (eMSP) | MSP: osoba prawna świadcząca odpłatnie usługi użytkownikowi końcowemu, w tym sprzedaż usługi ładowania `[AFIR art. 2 pkt 36]` | dostawca usługi ładowania: brak definicji w art. 2; zakres usługi w `[PL-EMOB art. 3 ust. 2 pkt 2]` | eMSP: daje kierowcom dostęp do usług ładowania | EMP z ProviderID |
| Platforma e-roamingu / hub | e-roaming platform łączy uczestników rynku, w szczególności MSP i operatorów `[AFIR art. 2 pkt 26]` | — | Roaming Hub: jedno połączenie techniczne do wielu partnerów; Hub jako funkcja platformy `[OCPI230 §2.4]` | HBS Hubject; zwykle tylko przy ważnej umowie EMP–CPO `[OICP23-CPO-INTRO]` |
| NAP | cyfrowy interfejs państwa, jeden punkt dostępu do danych `[AFIR art. 2 pkt 38]` | operator przekazuje dane o dostępności i cenie do rejestru (EIPA) `[PL-EMOB art. 3 ust. 1 pkt 4]` | NAP: krajowa baza; dane są wysyłane i pobierane | — |
| NSP | wśród „data users” jest digital map provider `[AFIR art. 2 pkt 16]` | — | NSP: informacja o lokalizacjach | — |
| SCSP | — | — | usługa smart charging dla innych stron | — |
| PTP, PSP | usługa płatnicza według PSD2 `[AFIR art. 2 pkt 42]` | — | PTP: system zarządzania terminalami; PSP: acquiring | — |
| OSD | według dyrektywy 2019/944 `[AFIR art. 2 pkt 18]` (niedostępna) | nie może być operatorem, właścicielem stacji ani dostawcą usługi; wyjątki w ust. 2, 5, 5a `[PL-EMOB art. 3a ust. 1]` | — | — |
| Użytkownik końcowy | osoba kupująca paliwo alternatywne do bezpośredniego użycia w pojeździe `[AFIR art. 2 pkt 24]` | użytkownik pojazdu elektrycznego `[PL-EMOB art. 7]` | EV driver | — |

- **Łączenie ról:** operator może wykonywać zadania dostawcy `[PL-EMOB art. 6]`; role OCPI można łączyć w jednej
  firmie, a platforma nie jest rolą, tylko obsługuje jedną lub wiele ról `[OCPI230 §2.3]`; partner OICP z obiema rolami
  dostaje dwa ID `[OICP23-CPO-COM #provider_and_operator_ids]`.
- **Relacja operator–dostawca w PL:** operator zapewnia, że na stacji działa co najmniej jeden dostawca, daje
  dostawcom dostęp na podstawie umowy na zasadach rynkowych i przekazuje im dane do rozliczenia
  `[PL-EMOB art. 3 ust. 1 pkt 1]` `[PL-EMOB art. 3 ust. 1 pkt 6]` `[PL-EMOB art. 3 ust. 1 pkt 10]`; dostawca korzysta
  ze stacji na podstawie umowy z operatorem `[PL-EMOB art. 4]`.
- **E-roaming (AFIR):** wymiana danych i płatności między operatorem punktu a MSP, od którego użytkownik kupuje usługę
  `[AFIR art. 2 pkt 25]`. Płatność umowna to płatność użytkownika na rzecz MSP na podstawie umowy z MSP
  `[AFIR art. 2 pkt 15]`. Ładowanie ad hoc nie wymaga rejestracji, umowy pisemnej ani relacji z operatorem
  wykraczającej poza zakup usługi `[AFIR art. 2 pkt 47]`.
- Typowe moduły OCPI dla ról i zmiany ról między 2.2.1 a 2.3.0: skill `ev-ocpi-roaming-expert`
  (`references/wersje-i-role.md`).

## 7. Rozbieżności
- **Hub w OCPI 2.3.0.** §2.3 wymienia rolę „Roaming Hub”, a enum `Role` w 2.3.0 ma tylko `CPO`, `EMSP`, `NAP`, `NSP`,
  `OTHER`, `SCSP` `[OCPI230 §17.10]`. W 2.2.1 enum miał `HUB` `[OCPI221 §16.6]`. Changelog mówi tylko, że klienci huba
  są raportowani jako zwykłe role `[OCPI230 §18.1]`. **Rozstrzygnięcie:** wartości pola `role` bierzesz z enuma
  §17.10; hub identyfikuje `hub_party_id` `[OCPI230 §7.3.1]`. Jaką wartość `role` hub 2.3.0 podaje dla siebie,
  specyfikacja nie mówi. PTP i PSP z §2.3 też nie mają wartości w enumie.
- **Separator w EVSE ID.** EIPA podaje przykład z łącznikiem `PL-S77-E12345ABC` `[EIPA-OPIS §3]`, a wyrażenie ISO w OICP
  dopuszcza tylko opcjonalną `*` `[OICP23-CPO-DT #EvseIDType]`, więc ten zapis nie przejdzie walidacji Hubject (sprawdzone
  wyrażeniem z dokumentu). OCPI zostawia format dokumentowi zewnętrznemu. **Wniosek:** do OICP wysyłasz postać z `*`;
  którą postać wymaga rejestr polski, dokumentacja EIPA nie mówi poza przykładem.
- **Wielkość liter.** OCPI: `CiString` bez rozróżniania wielkości liter `[OCPI230 §17.4]`; OICP: EvseID ISO tylko wielkie
  litery `[OICP23-CPO-DT #EvseIDType]`, a Hubject sam podnosi litery w EvcoID i UID
  `[OICP23-CPO-DT #QRCodeIdentificationType]`. **Wniosek:** normalizujesz do wielkich liter przed porównaniem i
  wysyłką.
- **Kod kraju.** Ten sam kraj ma trzy zapisy: AFIR-655 „Country” stacji w alfa-2 `[AFIR-655 Annex, tabela A]`, OCPI
  `Location.country` w alfa-3 i `country_code` (kraj CPO) w alfa-2 `[OCPI230 §8.3.1]`, OICP `CountryCodeType` w alfa-3
  `[OICP23-CPO-DT #CountryCodeType]`. Dokument przeglądowy EVRF mapuje „Country” na `country_code` z uwagą o alfa-3
  `[OCPI-NAP-MAP]`, co nie zgadza się z tabelą pól OCPI. **Rozstrzygnięcie:** wiąże specyfikacja; kraj stacji to
  `Location.country`, zamieniony na alfa-2 dla NAP.
- **Przykłady `contract_id` w OCPI** (np. `DE8ACC12E46L89`) nie spełniają wyrażenia EvcoID z OICP (sprawdzone).
  **Rozstrzygnięcie:** OCPI tylko zaleca format eMA ID `[OCPI230 §12.3.2]`; w Hubject obowiązuje wyrażenie
  `[OICP23-CPO-DT #EvcoIDType]`.
- **Przykład UID w OICP.** Przykład `AFFH1768` nie spełnia wyrażenia z tej samej sekcji, które dopuszcza tylko cyfry
  i litery A–F (tu jest `H`) `[OICP23-CPO-DT #UIDType]`. **Rozstrzygnięcie:** wiąże wyrażenie regularne, nie przykład.
- **Umowa eMSP.** EAFO opisuje ładowanie eMSP jako umowę kierowcy z CPO `[EAFO-CENY]`, a AFIR definiuje płatność umowną
  jako płatność na rzecz MSP na podstawie umowy z MSP `[AFIR art. 2 pkt 15]`. **Rozstrzygnięcie:** wiąże definicja
  AFIR.

## 8. Czego źródła nie określają
- składnia EVSE ID i eMA ID według eMI3/IDACS, algorytm cyfry kontrolnej, ISO 15118 Annex z formatem EMAID (normy i
  dokumenty niedostępne, patrz początek pliku);
- format kodów operatora wymagany przez polski rejestr poza przykładem EIPA;
- role spoza AFIR, ustawy i protokołów (host lokalizacji, producent, flota) i modele biznesowe ról;
- przepływ pieniędzy między stronami: AFIR mówi tylko, że e-roaming obejmuje wymianę płatności `[AFIR art. 2 pkt 25]`.
