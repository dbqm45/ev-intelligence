# OICP 2.3 (Hubject): architektura, usługi, typy danych, porównanie z OCPI

Źródła: repozytorium Hubject `github.com/hubject/oicp` przypięte do commita 119c5d5 (2026-06-17), licencja CC BY-SA 4.0
(`sources/hubject-oicp.yaml`). Specyfikacja ma części dla CPO i EMP. Cytaty dotyczą części CPO, chyba że znacznik mówi
`EMP`. Lokalizator `#…` to kotwica AsciiDoc w pliku. Zdania **Wniosek** to interpretacja, nie tekst specyfikacji.

## Spis treści
1. Wersje i status
2. Architektura: HBS, role, identyfikatory
3. Zasady komunikacji
4. Autoryzacja
5. CDR i dane do Eichrecht
6. Dane i statusy EVSE
7. Ceny (Dynamic Pricing)
8. Rezerwacja i powiadomienia o ładowaniu
9. Kody statusu
10. Limity wywołań (Hubject AUP)
11. OICP a OCPI: różnice i mapowanie
12. Rozbieżności w dokumentach
13. Czego nie opracowano

## 1. Wersje i status
- Wydania: OICP 2.3 i 2.2. Nowe wdrożenia muszą opierać się na 2.3. Wersję 2.1 wycofano 13.04.2023 `[OICP-README]`.
- Od 2.1 każda usługa ma własną wersję, niezależną od wersji OICP `[OICP23-CPO-INTRO]`. W OICP 2.3:

  | Usługa | Wersja |
  |---|---|
  | eRoamingAuthorization | 2.1 |
  | eRoamingChargeDetailRecord | 2.2 |
  | eRoamingReservation | 1.1 |
  | eRoamingEVSEData | 2.3 |
  | eRoamingEVSEStatus | 2.1 |
  | eRoamingDynamicPricing | 1.0 |
  | eRoamingChargingNotifications | 1.1 |

- Każdą wersję OICP HBS musi wspierać przez dwa lata. Partner musi wskazać wersję OICP, której używa
  `[OICP23-CPO-INTRO]`.
- Od OICP 2.3 dostępne są tylko API REST `[OICP23-RN #Introduction]`. Wszystkie usługi są synchroniczne, a komunikaty
  muszą używać UTF-8 `[OICP23-CPO-COM #rest]`.

## 2. Architektura: HBS, role, identyfikatory
- **Model hubowy:** CPO i EMP łączą się z Hubject Brokering System (HBS), a nie bezpośrednio ze sobą. Hubject
  przetwarza żądania zwykle tylko wtedy, gdy między EMP a CPO jest ważna umowa na daną usługę. Zarządzanie umowami
  odbywa się w portalu, poza zakresem OICP `[OICP23-CPO-INTRO]`.
- **Role:** EMP (ProviderID) i CPO (OperatorID). Partner może mieć obie role i wtedy dostaje dwa ID
  `[OICP23-CPO-COM #provider_and_operator_ids]`.
- **Bezpieczeństwo:** przy każdym żądaniu Hubject porównuje ProviderID albo OperatorID z danymi certyfikatu klienta
  SSL partnera `[OICP23-CPO-COM #Security]`.
- **Hub i sub-partnerzy:** pola ProviderID i OperatorID zawsze zawierają ID partnera, który komunikuje się bezpośrednio
  z Hubject. ID sub-partnerów występują tylko pośrednio, w EvcoID i EvseID `[OICP23-CPO-COM #hub_provider_and_operator]`.
- **Formaty ID** (ISO albo DIN):
  - EvseID: przykłady ISO „DE*AB7*E840*6487”, DIN „+49*810*000*438” `[OICP23-CPO-DT #EvseIDType]`;
  - EvcoID: ISO z instancją 8 znaków poprzedzoną „C”, DIN z instancją 6 znaków `[OICP23-CPO-DT #EvcoIDType]`;
  - OperatorID: ISO „DE*A36”, DIN „+49*536” `[OICP23-CPO-DT #OperatorIDType]`;
  - ProviderID: ISO „DE8EO” lub „DE-8EO” `[OICP23-CPO-DT #ProviderIDType]`.

## 3. Zasady komunikacji
- **SessionID:** Hubject nadaje SessionID (GUID) po pierwszym żądaniu, np. `eRoamingAuthorizeStart`. Każde kolejne
  żądanie tej sesji musi go zawierać. Partnerzy mogą dodać własne `CPOPartnerSessionID` i `EMPPartnerSessionID`
  `[OICP23-CPO-COM #session_handling]`.
- **Push sekwencyjny:** żądania push tej samej operacji muszą iść kolejno, nigdy równolegle. Partner czeka na odpowiedź
  przed kolejnym żądaniem, bo równoległe żądania mogą się wyprzedzić i nadpisać dane `[OICP23-CPO-COM #data_push_operations]`.
- **Czas:** format ISO 8601 z przesunięciem strefy, np. „2014-02-01T15:45:00+02:00”. CPO musi podawać przesunięcie
  właściwe dla lokalizacji punktu, bo zależą od niego opłaty zależne od czasu `[OICP23-CPO-COM #time_zones]`.
- **Każdy komunikat wymaga odpowiedzi**, co najmniej `eRoamingAcknowledgement` z polami `Result` i `StatusCode`
  `[OICP23-CPO-COM #status_codes]` `[OICP23-CPO-SVC #eRoamingAcknowledgementmessage]`.

## 4. Autoryzacja
**eRoamingAuthorizeStart** (CPO wysyła, obowiązkowe) `[OICP23-CPO-SVC #eRoamingAuthorizeStart]`: CPO nie rozpoznaje
danych klienta i pyta Hubject. Hubject nadaje SessionID i ma trzy drogi:
- **A, offline:** sprawdza dane uwierzytelniające wgrane przez EMP (`eRoamingPushAuthenticationData`);
- **B, znany EMP:** QR i Plug & Charge niosą EvcoID, z którego Hubject wyprowadza ProviderID i przekazuje żądanie
  wprost do EMP. Niedostępny EMP jest traktowany jak odpowiedź „NotAuthorized”;
- **C, broadcast:** gdy EMP nie da się ustalić (np. RFID), Hubject wysyła żądanie do wszystkich EMP, którzy mają umowę z
  CPO. Autoryzacja jest pozytywna, jeśli autoryzuje choć jeden EMP.

Przy odmowie Hubject usuwa SessionID. Odpowiedź (`eRoamingAuthorizationStart`) zawiera `AuthorizationStatus`
(`Authorized` / `NotAuthorized`), `StatusCode` i opcjonalnie listę identyfikatorów uprawnionych do zatrzymania
`[OICP23-CPO-SVC #eRoamingAuthorizationStartmessage]` `[OICP23-CPO-DT #AuthorizationStatusType]`.

- **PIN przy QR:** w `eRoamingAuthorizeStart` PIN musi być podany jawnie. Hubject haszuje go sam, więc PIN wysłany już
  jako hash daje „hash z hasha” i odmowę `[OICP23-CPO-SVC #eRoamingAuthorizeStart]`. EMP może wgrać PIN-y jawnie albo
  jako hash; domyślną funkcją jest Bcrypt `[OICP23-EMP-SVC #eRoamingPushAuthenticationData]`.
- **Typy identyfikacji:** jedna z pięciu opcji: `RFIDMifareFamilyIdentification`, `RFIDIdentification`,
  `QRCodeIdentification`, `PlugAndChargeIdentification`, `RemoteIdentification`. `RFIDIdentification` nie może być
  użyta w autoryzacji; dla RFID należy używać `RFIDMifareFamilyIdentification`. W autoryzacji zdalnej tylko
  `RemoteIdentification` `[OICP23-CPO-DT #IdentificationType]`.
- **eRoamingAuthorizeStop** (opcjonalne) musi zawierać SessionID. Sesję autoryzowaną offline przez HBS można zatrzymać
  tylko tym samym medium, którym ją rozpoczęto `[OICP23-CPO-SVC #eRoamingAuthorizeStop]`.
- **eRoamingAuthorizeRemoteStart** (CPO odbiera, obowiązkowe): EMP startuje sesję z aplikacji, z ProviderID i EvseID.
  Hubject sprawdza umowę, a jeśli CPO wgrał dane EVSE, także EvseID (kod 603 „Unknown EvseID”) i
  `IsHubjectCompatible` (kod 604). CPO odpowiada `eRoamingAcknowledgement`. Dobra praktyka to czas żądania poniżej 10 s
  z podróżą w sieci `[OICP23-CPO-SVC #eRoamingAuthorizeRemoteStart]`.
- **eRoamingAuthorizeRemoteStop** wymaga SessionID z RemoteStart `[OICP23-CPO-SVC #eRoamingAuthorizeRemoteStop]`.

## 5. CDR i dane do Eichrecht
- **eRoamingChargeDetailRecord** (CPO wysyła, obowiązkowe): CDR po zakończeniu ładowania, z tym samym SessionID. Hubject
  przyjmuje **tylko jeden CDR na SessionID**, zapisuje go i przekazuje EMP. Gdy EMP jest nieosiągalny, CPO i tak dostaje
  wynik pozytywny, o ile zapis się udał `[OICP23-CPO-SVC #eRoamingChargeDetailRecord]`.
- Pola obowiązkowe: `SessionID`, `EvseID`, `Identification`, `ChargingStart`, `ChargingEnd`, `SessionStart`,
  `SessionEnd`, `ConsumedEnergy` (kWh). Opcjonalne m.in. `MeterValueStart`, `MeterValueEnd`, `PartnerProductID`,
  `SignedMeteringValues` (najwyżej 10 wartości) i `CalibrationLawVerificationInfo`
  `[OICP23-CPO-SVC #eRoamingChargeDetailRecordmessage]`.
- **Dobre praktyki dla CDR:**
  - CDR wysłany około 1 s po zamknięciu w systemie CPO, nie dłużej niż 10 s;
  - `PartnerProductID` jest wymagane przy niektórych cenach (zalecane AC1, AC3, DC, Free);
  - prawdziwa strefa czasowa w czasach sesji, bo od niej zależą taryfy dzienne i nocne.

  `[OICP23-CPO-SVC #eRoamingChargeDetailRecord]`
- **EMP:** `eRoamingGetChargeDetailRecords` jest obowiązkowe dla EMP offline, a opcjonalne dla EMP online:
  - zakres dat jest wymagany;
  - od 2.3 działa paginacja: domyślnie 20 rekordów, najwyżej 2000 na stronę;
  - Hubject nie sprawdza, czy CDR był już wcześniej pobrany.

  `[OICP23-EMP-SVC #eRoamingGetChargeDetailRecords]`
- **Eichrecht:**
  - punkt deklaruje `CalibrationLawDataAvailability`: `Local` (dane na stacji), `External` (dostarczane zewnętrznie),
    `Not Available` `[OICP23-CPO-DT #CalibrationLawDataAvailabilityType]`;
  - przy `External` CDR musi zawierać `SignedMeteringValues`, w kolejności Start, Progress1…Progress8, End, w formacie
    obsługiwanym przez Transparency Software CPO `[OICP23-CPO-DT #SignedMeteringValuesType]`;
  - `CalibrationLawVerificationInfo` niesie m.in. ID certyfikatu, klucz publiczny, URL z danymi do faktury i format
    kodowania (np. „EDL40 Mennekes: V1”) `[OICP23-CPO-DT #CalibrationLawVerificationType]`.

  Szczegóły prawa niemieckiego: skill `ev-compliance-expert`, plik `metrologia.md`.

## 6. Dane i statusy EVSE
- **eRoamingPushEvseData** (CPO, obowiązkowe):
  - pole `ActionType`: `fullLoad`, `update`, `insert`, `delete`;
  - Hubject wersjonuje każdy push i potrafi odtworzyć stan danych z dowolnej chwili;
  - EvseID niezgodny z OperatorID daje kod 018.

  `[OICP23-CPO-SVC #eRoamingPushEvseData]`
- Pola obowiązkowe rekordu EVSE m.in.:
  - `EvseID`, `ChargingStationNames`, `Address`, `GeoCoordinates`, `Plugs`, `ChargingFacilities`;
  - `RenewableEnergy`, `CalibrationLawDataAvailability`, `AuthenticationModes`, `PaymentOptions`,
    `ValueAddedServices`, `Accessibility`, `HotlinePhoneNumber`;
  - `IsOpen24Hours`, `IsHubjectCompatible`, `DynamicInfoAvailable`.

  `[OICP23-CPO-DT #EvseDataRecordType]`
- **eRoamingPullEvseData** (EMP, obowiązkowe):
  - delta pull przez `LastCall`, nie da się go łączyć z wyszukiwaniem `SearchCenter`;
  - paginacja, domyślnie 20 rekordów;
  - zalecane wywołanie raz dziennie.

  `[OICP23-EMP-SVC #eRoamingPullEvseData]`
- **eRoamingPushEvseStatus** (CPO, obowiązkowe): ten sam mechanizm `ActionType`. Statusy wysyła się pojedynczo, żeby
  uniknąć wyścigów `[OICP23-CPO-SVC #eRoamingPushEvseStatus]`.
- **eRoamingPullEvseStatus** (EMP, obowiązkowe): wariant pełny, `ByID` (do 100 EvseID) i `ByOperatorID`; zalecana
  częstotliwość od 1 do 5 minut `[OICP23-EMP-SVC #eRoamingPullEvseStatus]`.
- **Statusy EVSE:** `Available`, `Reserved`, `Occupied`, `OutOfService`, `EvseNotFound` (brak takiego EvseID w bazie
  Hubject), `Unknown` `[OICP23-CPO-DT #EvseStatusType]`.
- Słowniki:
  - `AuthenticationModeType`: `NFC RFID Classic`, `NFC RFID DESFire`, `PnC` (ISO/IEC 15118), `REMOTE` (aplikacja, QR,
    telefon), `Direct Payment`, `No Authentication Required` `[OICP23-CPO-DT #AuthenticationModeType]`;
  - `PaymentOptionType`: `No Payment`, `Direct`, `Contract`. `No Payment` nie łączy się z innymi
    `[OICP23-CPO-DT #PaymentOptionType]`.

## 7. Ceny (Dynamic Pricing)
- Usługa od OICP 2.2, opcjonalna. Ma cztery operacje: CPO wysyła produkty cenowe (`eRoamingPushPricingProductData`) i
  ich przypisanie do EVSE (`eRoamingPushEVSEPricing`), a EMP je pobiera (`Pull…`) `[OICP23-CPO-SVC #eRoamingDynamicPricing]`.
  Ceny wysyła się bez VAT `[OICP23-CPO-SVC #eRoamingPushPricingProductData]`.
- Produkt cenowy `[OICP23-CPO-DT #PricingProductDataType]` `[OICP23-CPO-DT #PricingProductDataRecordType]`:
  - ma cenę za jednostkę `HOUR`, `KILOWATT_HOUR` albo `MINUTE`, walutę, maksymalną moc i okna dostępności;
  - `ProviderID` = `*` oznacza ofertę dla wszystkich EMP.
- Składniki dodatkowe (`AdditionalReferenceType`): `START FEE`, `FIXED FEE`, `PARKING FEE`, `MINIMUM FEE`,
  `MAXIMUM FEE` `[OICP23-CPO-DT #AdditionalReferenceType]`.
- Standardowe `ProductID`: `Standard Price`, `AC1`, `AC3`, `DC`. Dozwolone są też własne, do 50 znaków
  `[OICP23-CPO-DT #ProductIDType]`.

Pełny opis jest w dokumencie Hubject „Dynamic Pricing — Functional Guide”, który nie jest opracowany.

## 8. Rezerwacja i powiadomienia o ładowaniu
- **Rezerwacja** (opcjonalna dla CPO, Hubject musi ją włączyć) `[OICP23-CPO-SVC #eRoamingReservation]`
  `[OICP23-CPO-SVC #eRoamingAuthorizeRemoteReservationStop]`:
  - start ma pole `Duration` w minutach;
  - po `eRoamingAuthorizeRemoteReservationStop` CPO musi wysłać CDR.
- **eRoamingChargingNotifications** (opcjonalne) `[OICP23-CPO-SVC #eRoamingChargingNotifications]`
  `[OICP23-CPO-SVC #eRoamingChargingNotificationsendmessage]`:
  - typy `Start`, `Progress`, `End`, `Error`;
  - `Progress` nie częściej niż co 5 minut na sesję;
  - `End` oznacza koniec przepływu energii przy wciąż aktywnej sesji i może nieść `PenaltyTimeStart`.

## 9. Kody statusu (wybór) `[OICP23-CPO-DT #CodeType]`
| Kod | Znaczenie |
|---|---|
| 000 | Success |
| 018 / 019 | Inconsistent EvseID / EvcoID |
| 102 | RFID Authentication failed – invalid UID |
| 106 | No positive authentication response |
| 120–122 | PLC (ISO/IEC 15118) — invalid EvcoID, invalid certificate, time out |
| 210 | No valid contract |
| 300 / 310 | Partner not found / did not respond |
| 400 | Session is invalid |
| 510 | No EV connected to EVSE |
| 601 / 602 | EVSE already reserved / already in use, wrong token |
| 603 / 604 | Unknown EVSE ID / EVSE ID is not Hubject compatible |
| 700 | EVSE out of service |

## 10. Limity wywołań (Hubject AUP) `[HBJ-AUP]`
- Limity na minutę, m.in.:
  - `PullEVSEStatus`: 6;
  - `PullEVSEStatusByID`: 300;
  - `PullEVSEData`: 100;
  - `PushEVSEStatus`: 2000;
  - `PushEVSEData`: 375;
  - `AuthorizationStart`: 200;
  - `ChargeDetailRecord`: 350;
  - `PushEVSEPricing` i `PushPricingProductData`: po 6.
- Przy HTTP 429 zalecane są ponowienia z wykładniczym odstępem i losowością. O podniesienie limitu prosi się 6 tygodni
  wcześniej, możliwe są dodatkowe koszty.
- Testów obciążeniowych i skanów bezpieczeństwa nie wolno robić na produkcji. Na środowisku QA wymagają zgody Hubject.

**Wniosek:** EMP, który odświeża statusy pełnym `PullEVSEStatus`, ma 6 wywołań na minutę. Przy zalecanym odświeżaniu co
1–5 minut `[OICP23-EMP-SVC #eRoamingPullEvseStatus]` to wystarcza dla jednego klienta. Dla wielu kopii aplikacji
potrzebny jest centralny cache po stronie EMP.

## 11. OICP a OCPI: różnice i mapowanie
| Temat | OICP 2.3 | OCPI 2.3.0 |
|---|---|---|
| Topologia | zawsze przez HBS; umowy CPO–EMP w portalu Hubject `[OICP23-CPO-INTRO]` | peer-to-peer albo przez hub `[OCPI230 §2.3]` |
| Uwierzytelnienie | certyfikat klienta SSL zgodny z OperatorID / ProviderID `[OICP23-CPO-COM #Security]` | tokeny credentials A/B/C `[OCPI230 §7.1.1]` |
| Dane lokalizacji | CPO robi push do HBS, EMP robi pull z HBS `[OICP23-CPO-SVC #eRoamingEvseData]` | pull wymagany, push opcjonalny `[OCPI230 §4.1.3]` |
| Autoryzacja nieznanego RFID | broadcast do EMP z umową `[OICP23-CPO-SVC #eRoamingAuthorizeStart]` | whitelist tokenów albo autoryzacja real-time u eMSP `[OCPI230 §12.1.3]` `[OCPI230 §12.4.5]` |
| Identyfikator sesji | SessionID nadaje Hubject `[OICP23-CPO-COM #session_handling]` | obiekt Session należy do systemu CPO `[OCPI230 §9]` |
| Korekta CDR | jeden CDR na SessionID `[OICP23-CPO-SVC #eRoamingChargeDetailRecord]` | credit CDR `[OCPI230 §10.1.1]` |

**Mapowanie statusów EVSE (Wniosek):**

| OICP `[OICP23-CPO-DT #EvseStatusType]` | OCPI `[OCPI230 §8.4.26]` | Uwaga |
|---|---|---|
| `Available` | `AVAILABLE` | |
| `Reserved` | `RESERVED` | |
| `Occupied` | `CHARGING` | OICP nie odróżnia zajęcia przez ładowanie od przeszkody (`BLOCKED`) |
| `OutOfService` | `OUTOFORDER` albo `INOPERATIVE` | OICP nie odróżnia awarii od czasowej niedostępności |
| `Unknown` | `UNKNOWN` | |
| `EvseNotFound` | brak | odpowiedź HBS na nieznany EvseID, nie stan punktu |
| brak | `PLANNED`, `REMOVED`, `BLOCKED` | `REMOVED` → w OICP usuwasz rekord (`ActionType` `delete`) |

**Wniosek:** przy mapowaniu z OCPI do OICP tracisz rozróżnienia (BLOCKED/CHARGING, OUTOFORDER/INOPERATIVE). W CPMS
trzymasz status w modelu bogatszym (np. OCPI lub OCPP) i dopiero na wyjściu rzutujesz go na OICP. Korekty CDR,
których OICP nie przewiduje (jeden CDR na SessionID), uzgadniasz poza protokołem.

## 12. Rozbieżności w dokumentach
- **Nazwa wartości:** Release Notes podają nową wartość `AuthenticationModeType` jako „No Authentication Requires”
  `[OICP23-RN #eRoamingEVSEData]`, a typy danych jako „No Authentication Required” `[OICP23-CPO-DT #AuthenticationModeType]`.
  **Rozstrzygnięcie:** wiodąca jest pełna specyfikacja, nie Release Notes, bo tak mówi wstęp Release Notes
  `[OICP23-RN #Introduction]`. Używasz „No Authentication Required”.
- **Kotwice z literówkami w części EMP:** `#eRoamingAuthoizeStart`, `#eRoamingAuthroizeRemoteStop` (oryginał). Przy
  linkowaniu do dokumentu kopiujesz je dokładnie.

## 13. Czego nie opracowano
- dokumentacja OpenAPI (repozytoria `oicp-cpo-2.3-api-doc`, `oicp-emp-2.3-api-doc`);
- OICP 2.2;
- Dynamic Pricing Functional Guide;
- typy danych części EMP poza wybranymi;
- załączniki z diagramami;
- eMIP (Gireve) i OCHP: hosty `www.gireve.com` i `www.ochp.eu` są niedostępne (`sources/niedostepne.yaml`).
