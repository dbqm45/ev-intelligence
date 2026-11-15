# OICP 2.3 (Hubject): architektura, usługi, typy danych, porównanie z OCPI

Źródła: repozytorium Hubject `github.com/hubject/oicp` przypięte do commita 119c5d5 (2026-06-17), licencja CC BY-SA 4.0
(`sources/hubject-oicp.yaml`). Specyfikacja ma części dla CPO i EMP. Cytaty dotyczą części CPO, chyba że znacznik mówi
`EMP`. Lokalizator `#…` to kotwica AsciiDoc w pliku. Zdania **Wniosek** to interpretacja, nie tekst specyfikacji.

## Spis treści
1. Wersje i status (zmiany w 2.3, pola obowiązkowe 2.1/2.2/2.3)
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
- **REST i SOAP:** usługi wprowadzone od OICP 2.2 są dostępne tylko przez REST, SOAP nie działa dla nich
  `[OICP23-CPO-COM #rest]`. Od OICP 2.3 dostępne są tylko API REST `[OICP23-RN #Introduction]` (zakres obu zdań: §12).
  Wszystkie usługi są synchroniczne, a komunikaty muszą używać UTF-8 `[OICP23-CPO-COM #rest]`.

### Zmiany w 2.3 względem 2.2
Release Notes są skrótem. Przy rozbieżności wiąże pełna specyfikacja 2.3 `[OICP23-RN #Introduction]`.

- **Wersje operacji** `[OICP23-RN #OICP2.3ChangesOnEndpoint]`:

  | Operacja | 2.2 | 2.3 |
  |---|---|---|
  | `eRoamingChargeDetailRecord`, `eRoamingGetChargeDetailRecord` | 2.1 | 2.2 |
  | `eRoamingPushEvseData`, `eRoamingPullEvseData` | 2.2 | 2.3 |
  | `eRoamingChargingNotification` | 1.0 | 1.1 |

  Nie wszystkie usługi zmieniły wersję `[OICP23-RN #OICP2.3ChangesOnEndpoint]`. **Wniosek:** „V2.1” w nazwie
  `eRoamingAuthorizeStart_V2.1` to wersja operacji, nie protokołu `[OICP23-CPO-SVC #eRoamingAuthorizeStart]`.
- **CDR:** usunięte `MeteringSignature`. Zastępują je nowe `SignedMeteringValues` i `CalibrationLawVerificationInfo`.
  `ChargingStart`, `ChargingEnd` i `ConsumedEnergy` są obowiązkowe `[OICP23-RN #eRoamingChargeDetailRecord]`.
- **GetChargeDetailRecords:** nowe filtry `SessionID`, `OperatorID`, `CDRForwarded`
  `[OICP23-RN #eRoamingGetChargeDetailRecord]`.
- **EVSE Data** `[OICP23-RN #eRoamingEVSEData]`:
  - pull ma paginację, a odpowiedź używa nowego typu `PullEvseDataRecordType`; pola `OperatorEvseData` w odpowiedzi
    pull już nie ma;
  - `ChargingStationName` → `ChargingStationNames` (obowiązkowe, typ `InfoTextType`); `EnChargingStationName` usunięte;
  - `ChargingModes` przeniesione z rekordu EVSE do `ChargingFacilityType`;
  - wartości „Unspecified” (`Plugs`, `Accessibility`, `PowerType`) push 2.3 nie przyjmuje; pull 2.3 zwraca w ich
    miejscu `null` dla danych wgranych przez OICP 2.1 i 2.2;
  - obowiązkowe: `OperatorName`, `PostalCode` i `HouseNum` w adresie, `Power` i `PowerType`, `PaymentOptions`;
  - nowe pola m.in. `HardwareManufacturer`, `ChargingStationImage`, `SubOperatorName`, `DynamicPowerLevel`,
    `RenewableEnergy`, `EnergySource`, `EnvironmentalImpact`, `CalibrationLawDataAvailability`,
    `AccessibilityLocation`, `ChargingStationLocationReference`, w adresie `ParkingFacility` i `ParkingSpot`;
    w `ValueAddedServiceType` wartość `RoofProvided`;
  - nowe filtry pull: `AuthenticationModes`, `Accessibility`, `CalibrationLawDataAvailability`, `RenewableEnergy`,
    `IsHubjectCompatible`, `IsOpen24Hours`.
- **ChargingNotification:** nowe pola `ChargingDuration` (ms), `ConsumedEnergyProgress`, `PenaltyTimeStart`,
  `ErrorType`, `ErrorAdditionalInfo` `[OICP23-RN #eRoamingChargingNotification]`.
- **Nowe typy danych:** `EnergySourceType`, `EnvironmentalImpactType`, `SignedMeteringValuesType`,
  `CalibrationLawVerificationType`, `AccessibilityLocationType`, `EnergyType`, `CalibrationLawDataAvailabilityType`,
  `MeteringStatusType`, `ErrorClassType` `[OICP23-RN #OICP2.3DataTypeChanges]`.

### Pola obowiązkowe 2.1 / 2.2 / 2.3
Tabela z Release Notes 2.3 (M obowiązkowe, O opcjonalne, „—” pola nie ma) `[OICP23-RN #OICPVersionsCrossFunctional]`.
Specyfikacji 2.1 i 2.2 nie opracowano (§13), więc kolumny 2.1 i 2.2 pochodzą tylko z tego dokumentu.

| Pole | Usługa | 2.1 | 2.2 | 2.3 |
|---|---|---|---|---|
| `OperatorName`, `ChargingStationName` | EVSEData | O | O | M |
| `HouseNum`, `PostalCode` (adres) | EVSEData | O | O | M |
| `Power`, `PowerType` (`ChargingFacilities`) | EVSEData | O | O | M |
| `PaymentOptions` | EVSEData | O | O | M |
| `RenewableEnergy`, `CalibrationLawDataAvailability` | EVSEData | — | — | M |
| `ChargingStart`, `ChargingEnd` | ChargeDetailRecord | O | O | M |

EMP na 2.3 może w `eRoamingPullEvseData` nie dostać pól EVSEData z tej tabeli (HBS podaje `null`), jeśli CPO wgrał
dane w 2.1 lub 2.2 `[OICP23-RN #OICPVersionsCrossFunctional]`.

**Wniosek:** EMP na 2.3 nie odrzuca rekordu EVSE tylko z powodu braku pola obowiązkowego w 2.3. Model wewnętrzny musi
dopuszczać brak tych pól po stronie odbioru.

## 2. Architektura: HBS, role, identyfikatory
- **Model hubowy:** CPO i EMP łączą się z Hubject Brokering System (HBS), a nie bezpośrednio ze sobą. Hubject
  przetwarza żądania zwykle tylko wtedy, gdy między EMP a CPO jest ważna umowa na daną usługę. Zarządzanie umowami
  odbywa się w portalu, poza zakresem OICP `[OICP23-CPO-INTRO]`.
- **Role:** EMP (ProviderID) i CPO (OperatorID). ID jest przypisane do roli i unikalne na całym rynku. Partner może mieć
  obie role i wtedy dostaje dwa ID. Po tym, które ID przyszło w żądaniu, Hubject rozpoznaje rolę partnera w danej
  sesji `[OICP23-CPO-COM #provider_and_operator_ids]`.
- **Bezpieczeństwo:** przy każdym żądaniu Hubject porównuje ProviderID albo OperatorID z danymi certyfikatu klienta
  SSL partnera. Przy niezgodności nie wykonuje operacji i odpowiada kodem 017 „Unauthorized Access”
  `[OICP23-CPO-COM #Security]`.
- **Hub i sub-partnerzy:** pola ProviderID i OperatorID zawsze zawierają ID partnera, który komunikuje się bezpośrednio
  z Hubject. ID sub-partnerów występują tylko pośrednio, w EvcoID i EvseID. ID sub-partnera trzeba skonfigurować w
  Hubject przed użyciem. Gdy Hubject nie zna ID z EvcoID lub EvseID, sprawdza, czy wiąże je zarejestrowany hub, i
  prowadzi proces w imieniu huba (np. autoryzacja online i CDR trafiają do hub EMP). CPO z punktami w kilku krajach
  daje każdemu EVSE właściwy kod kraju i OperatorID: sub-operatora albo własne główne
  `[OICP23-CPO-COM #hub_provider_and_operator]`.
- Hub CPO może wgrywać dane i statusy EVSE sub-operatorów, a Hubject nie odróżnia rekordów huba od rekordów
  sub-operatorów `[OICP23-CPO-SVC #eRoamingEvseData]` `[OICP23-CPO-SVC #eRoamingEvseStatus]`. Tak samo przy danych
  uwierzytelniających hub EMP i sub-EMP `[OICP23-EMP-SVC #eRoamingAuthenticationData]`.
- **Formaty ID** (ISO albo DIN):
  - EvseID: przykłady ISO „DE*AB7*E840*6487”, DIN „+49*810*000*438” `[OICP23-CPO-DT #EvseIDType]`;
  - EvcoID: ISO z instancją 8 znaków poprzedzoną „C”, DIN z instancją 6 znaków `[OICP23-CPO-DT #EvcoIDType]`;
  - OperatorID: ISO „DE*A36”, DIN „+49*536”. ISO: kod kraju alfa-2, separator „*” opcjonalny. DIN: kod kraju według
    planu numeracji ITU-T E.164, separator „*” obowiązkowy `[OICP23-CPO-DT #OperatorIDType]`;
  - ProviderID: ISO „DE8EO” lub „DE-8EO” `[OICP23-CPO-DT #ProviderIDType]`;
  - kraj w adresie rekordu EVSE (`Country` w `AddressIso19773Type`) to `CountryCodeType`: od OICP 2.2 tylko kod
    alfa-3, np. `DEU` `[OICP23-CPO-DT #AddressIso19773Type]` `[OICP23-CPO-DT #CountryCodeType]`. W EvseID i OperatorID
    w formie ISO kraj jest alfa-2 `[OICP23-CPO-DT #EvseIDType]` `[OICP23-CPO-DT #OperatorIDType]`.

## 3. Zasady komunikacji
- **SessionID:** Hubject nadaje SessionID (GUID) po pierwszym żądaniu, np. `eRoamingAuthorizeStart`. Każde kolejne
  żądanie tej sesji musi go zawierać. Żądanie z SessionID nienadanym przez Hubject albo nieważnym dostaje odpowiedź
  negatywną. Partnerzy mogą dodać własne `CPOPartnerSessionID` i `EMPPartnerSessionID`. Hubject wiąże
  `CPOPartnerSessionID` z SessionID i dodaje je do każdej odpowiedzi `[OICP23-CPO-COM #session_handling]`.
- Oba pola są opcjonalne, typu String, do 250 znaków `[OICP23-CPO-SVC #eRoamingAuthorizeStartmessage]`. Występują też
  w `eRoamingAcknowledgement` `[OICP23-CPO-SVC #eRoamingAcknowledgementmessage]`. Tekst sekcji o sesjach mówi o
  odsyłaniu tylko `CPOPartnerSessionID`; o `EMPPartnerSessionID` takiego zdania nie ma.
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
- `eRoamingAuthorizeStart` ma opcjonalne pole `PartnerProductID` (nazwa produktu cenowego, unikalna)
  `[OICP23-CPO-SVC #eRoamingAuthorizeStartmessage]`.

**Obowiązki EMP: online i offline.** Specyfikacja EMP rozróżnia EMP „online” i „offline”. Komunikat
`eRoamingPushAuthenticationData` jest tylko dla EMP przyjętych do Hubject jako offline
`[OICP23-EMP-SVC #eRoamingPushAuthenticationDatamessage]`.

| Operacja (strona EMP) | Nagłówek „Implementation” | Zawężenie w opisie komunikatu |
|---|---|---|
| `eRoamingAuthorizeStart` (odbiór), odpowiedź `eRoamingAuthorizationStart` | `MANDATORY` | odpowiedź obowiązkowa tylko dla EMP online `[OICP23-EMP-SVC #eRoamingAuthorizationStart]` |
| `eRoamingAuthorizeStop` (odbiór) | `OPTIONAL` | odpowiedź obowiązkowa tylko dla EMP online `[OICP23-EMP-SVC #eRoamingAuthorizationStop]` |
| `eRoamingAuthorizeRemoteStart` (wysyłka) | `MANDATORY` | — `[OICP23-EMP-SVC #eRoamingAuthorizeRemoteStart]` |
| `eRoamingChargeDetailRecord` (odbiór) | `MANDATORY` | komunikat obowiązkowy tylko dla EMP online `[OICP23-EMP-SVC #eRoamingChargeDetailRecordmessage]` |
| `eRoamingGetChargeDetailRecords` (wysyłka) | EMP online `OPTIONAL`, EMP offline `MANDATORY` | — `[OICP23-EMP-SVC #eRoamingGetChargeDetailRecords]` |
| `eRoamingPushAuthenticationData` (wysyłka) | `MANDATORY` | komunikat tylko dla EMP offline `[OICP23-EMP-SVC #eRoamingPushAuthenticationDatamessage]` |
| `eRoamingPullEvseData`, `eRoamingPullEvseStatus` (wysyłka) | `MANDATORY` | — `[OICP23-EMP-SVC #eRoamingPullEvseData]` `[OICP23-EMP-SVC #eRoamingPullEvseStatus]` |
| `eRoamingPullPricingProductData`, `eRoamingPullEVSEPricing`, `eRoamingChargingNotifications` | `OPTIONAL` | — `[OICP23-EMP-SVC #eRoamingPullPricingProductData]` `[OICP23-EMP-SVC #eRoamingPullEVSEPricing]` `[OICP23-EMP-SVC #eRoamingChargingNotifications]` |

Usługę `eRoamingAuthenticationData` oferuje tylko Hubject. Dzięki wgranym danym Hubject autoryzuje żądania CPO bez
przekazywania ich do EMP `[OICP23-EMP-SVC #eRoamingAuthenticationData]`. `eRoamingPushAuthenticationData` musi iść
sekwencyjnie, a EvcoID niezgodny z ProviderID (lub sub-ProviderID) daje kod 019
`[OICP23-EMP-SVC #eRoamingPushAuthenticationData]`.

**Wniosek:** nagłówek `MANDATORY` czytasz razem z notą komunikatu (rozbieżność: §12). EMP online odpowiada na
`AuthorizeStart` i przyjmuje CDR. EMP offline wgrywa dane uwierzytelniające i sam pobiera CDR przez
`eRoamingGetChargeDetailRecords`. Specyfikacja nie opisuje, jak wybiera się tryb przy przyjęciu do Hubject; to ustala
się z Hubject.

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
- Żądanie ma obowiązkowe `ProviderID`, `From`, `To` i opcjonalne filtry: lista `SessionID`, `OperatorID`,
  `CDRForwarded` (czy CDR został przekazany EMP) `[OICP23-EMP-SVC #eRoamingGetChargeDetailRecordsmessage]`.
  Parametry paginacji idą na końcu adresu: `...?page=0&size=20` `[OICP23-EMP-SVC #eRoamingGetChargeDetailRecords]`.

  **Wniosek:** `CDRForwarded` = `false` pozwala EMP online dobrać CDR-y, których Hubject nie zdołał mu przekazać.
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
  - bez `LastCall` zwraca wszystkie ważne rekordy, każdy z atrybutem `lastUpdate`;
  - delta pull przez `LastCall`: każdy rekord w odpowiedzi ma `deltaType` (`insert`, `update`, `delete`), rekordów bez
    zmian nie ma w odpowiedzi;
  - delty nie da się łączyć z wyszukiwaniem `SearchCenter`;
  - od 2.3 paginacja, której EMP musi używać: parametry na końcu adresu `...?page=0&size=20`, domyślnie 20 rekordów.

  `[OICP23-EMP-SVC #eRoamingPullEvseData]` `[OICP23-CPO-DT #EvseDataRecordType]`
- `LastCall` nie łączy się też z `CountryCodes` i `OperatorIds`. Pozostałe filtry: `AuthenticationModes`,
  `Accessibility`, `CalibrationLawDataAvailability`, `RenewableEnergy`, `IsHubjectCompatible`, `IsOpen24Hours`.
  Zalecane wywołanie raz dziennie `[OICP23-EMP-SVC #eRoamingPullEVSEDatamessage]`.
- Odpowiedź niesie listę `content` i pola strony: `number`, `size`, `totalElements`, `totalPages`, `numberOfElements`,
  `first`, `last` `[OICP23-EMP-SVC #eRoamingEVSEDatamessage]`.

  **Wniosek:** pętlę stron kończysz po `last` = `true`, nie po liczbie rekordów. Specyfikacja nie opisuje, jak delta
  `LastCall` współdziała z paginacją. Bezpieczniej zapisać nowy `LastCall` dopiero po pobraniu wszystkich stron.
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

- **Pobieranie przez EMP:** Hubject sprawdza, czy EMP ma ważny kontrakt flexible/dynamic pricing (dla typu usługi
  Authorization) z CPO, których `OperatorIDs` podano w żądaniu. EMP dostaje tylko dane wgrane przez tych CPO dla
  niego. `OperatorIDs` jest obowiązkowe, a `LastCall` daje tylko zmiany od podanej chwili
  `[OICP23-EMP-SVC #eRoamingPullPricingProductData]` `[OICP23-EMP-SVC #eRoamingPullPricingProductDatamessage]`
  `[OICP23-EMP-SVC #eRoamingPullEVSEPricing]`.
- Taryfę wskazuje `PartnerProductID` w `eRoamingAuthorizeStart` `[OICP23-CPO-SVC #eRoamingAuthorizeStartmessage]` i w CDR
  `[OICP23-CPO-SVC #eRoamingChargeDetailRecordmessage]`.

Pełny opis jest w dokumencie Hubject „Dynamic Pricing — Functional Guide”. Nie ma go w rejestrze źródeł, więc nie jest
opracowany.

## 8. Rezerwacja i powiadomienia o ładowaniu
- **Rezerwacja** (opcjonalna dla CPO, Hubject musi ją włączyć) `[OICP23-CPO-SVC #eRoamingReservation]`
  `[OICP23-CPO-SVC #eRoamingAuthorizeRemoteReservationStop]`:
  - start ma pole `Duration` w minutach;
  - po `eRoamingAuthorizeRemoteReservationStop` CPO musi wysłać CDR.
- **eRoamingChargingNotifications** (opcjonalne) `[OICP23-CPO-SVC #eRoamingChargingNotifications]`
  `[OICP23-CPO-SVC #eRoamingChargingNotificationsendmessage]`:
  - typy `Start`, `Progress`, `End`, `Error`;
  - `Progress` nie częściej niż co 5 minut na sesję;
  - `End` oznacza koniec przepływu energii przy wciąż aktywnej sesji i może nieść `PenaltyTimeStart`;
  - Hubject przekazuje wszystkie cztery typy do EMP. EMP odpowiada `eRoamingAcknowledgement`, a Hubject przekazuje to
    potwierdzenie do CPO `[OICP23-CPO-SVC #eRoamingChargingNotifications]`;
  - `Error` wymaga `ErrorType` z `ErrorClassType` (`Connector Error`, `Critical Error`); `ErrorAdditionalInfo` do 250
    znaków `[OICP23-CPO-SVC #eRoamingChargingNotificationserrormessage]` `[OICP23-CPO-DT #ErrorClassType]`.

  **Wniosek:** powiadomienia nie zastępują CDR. Są opcjonalne, a CDR po zakończeniu ładowania CPO musi wysłać
  `[OICP23-CPO-SVC #eRoamingChargeDetailRecord]`. Wiążące dane rozliczenia bierzesz z CDR.

## 9. Kody statusu `[OICP23-CPO-DT #CodeType]`
| Kod | Znaczenie | Obszar |
|---|---|---|
| 000 | Success | ogólne |
| 001 / 002 / 009 | Hubject system error / database error / Data transaction error | wewnętrzne |
| 017 | Unauthorized Access (ID niezgodne z certyfikatem klienta `[OICP23-CPO-COM #Security]`) | wewnętrzne |
| 018 / 019 | Inconsistent EvseID / EvcoID | wewnętrzne |
| 021 / 022 | System error / Data error | ogólne |
| 101 | QR Code Authentication failed – Invalid Credentials | uwierzytelnienie |
| 102 / 103 | RFID Authentication failed – invalid UID / card not readable | uwierzytelnienie |
| 105 | PLC Authentication failed – invalid EvcoID | uwierzytelnienie |
| 106 | No positive authentication response | uwierzytelnienie, wewnętrzne |
| 110 | QR Code App Authentication failed – time out error | uwierzytelnienie |
| 120–122 | PLC (ISO/IEC 15118) — invalid underlying EvcoID, invalid certificate, time out | uwierzytelnienie |
| 200 | EvcoID locked | uwierzytelnienie |
| 210 | No valid contract | sesja |
| 300 / 310 / 320 | Partner not found / did not respond / Service not available | sesja |
| 400 | Session is invalid | sesja |
| 501 | Communication to EVSE failed | EVSE |
| 510 | No EV connected to EVSE | EVSE |
| 601 / 602 | EVSE already reserved / already in use, wrong token | EVSE |
| 603 / 604 | Unknown EVSE ID / EVSE ID is not Hubject compatible | EVSE |
| 700 | EVSE out of service | EVSE |

- Kody są ustandaryzowane, żeby dało się je przetwarzać automatycznie. Backend analizuje tylko kod, niezależnie od
  opisu. Opcjonalne `AdditionalInfo` niesie informacje indywidualne, a `Description` powinno zawierać tylko
  zdefiniowane wartości `[OICP23-CPO-COM #status_codes]`.
- `StatusCodeType`: `Code` (M), `Description` (O, do 200 znaków), `AdditionalInfo` (O, do 1000 znaków)
  `[OICP23-CPO-DT #StatusCodeType]`.
- Ogólne błędy systemu HBS Hubject przechwytuje i odpowiada domyślnym `eRoamingAcknowledgement`
  `[OICP23-CPO-COM #error_handling]`.

**Wniosek:** reguły ponowień i komunikaty dla kierowcy wiążesz z `Code`. Tekstu `AdditionalInfo` nie parsujesz, tylko
logujesz.

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

**Wniosek: adapter OICP obok OCPI.** Każdy punkt wynika z faktów wyżej, ale specyfikacje go nie opisują:
- jeden model wewnętrzny, a OCPI i OICP jako osobne adaptery, bo tożsamość sesji i strony jest w obu inna (tabela wyżej);
- SessionID Hubject (GUID, wiodący identyfikator procesu `[OICP23-CPO-COM #session_handling]`) trzymasz obok własnego ID
  sesji i ID sesji OCPI; własne ID wysyłasz jako `CPOPartnerSessionID` (do 250 znaków, §3);
- push do HBS idzie sekwencyjnie w obrębie operacji (§3), więc każda operacja push ma własną kolejkę z jednym żądaniem
  naraz; statusy EVSE nie czekają wtedy za dużym `fullLoad` danych EVSE;
- wysyłka CDR jest idempotentna po SessionID, bo Hubject przyjmuje jeden CDR na SessionID (§5);
- stronę w OCPI wyznacza para `country_code` i `party_id`, unikalna razem z rolą `[OCPI230 §7.3.1]`, a w OICP
  `OperatorID` albo `ProviderID` (§2). Forma DIN OperatorID ma numeryczny kod kraju E.164 (`+49*536`), więc mapowanie
  `OperatorID` ↔ (`country_code`, `party_id`) trzymasz jako jawną tabelę konfiguracji, a nie wyprowadzasz z ciągu.

## 12. Rozbieżności w dokumentach
- **Nazwa wartości:** Release Notes podają nową wartość `AuthenticationModeType` jako „No Authentication Requires”
  `[OICP23-RN #eRoamingEVSEData]`, a typy danych jako „No Authentication Required” `[OICP23-CPO-DT #AuthenticationModeType]`.
  **Rozstrzygnięcie:** wiodąca jest pełna specyfikacja, nie Release Notes, bo tak mówi wstęp Release Notes
  `[OICP23-RN #Introduction]`. Używasz „No Authentication Required”.
- **SOAP: od 2.2 czy od 2.3?** Część „Communication” mówi: „All new services to be introduced in the future,
  beginning with OICP 2.2, will be only available over the REST API” `[OICP23-CPO-COM #rest]`. Release Notes: „From
  OICP 2.3 version only REST API’s are offered” `[OICP23-RN #Introduction]`. **Rozstrzygnięcie:** zdania nie są
  sprzeczne, mają inny zakres. Pierwsze dotyczy usług nowych od 2.2 (np. Dynamic Pricing, która jest „Since OICP 2.2”
  `[OICP23-EMP-SVC #eRoamingDynamicPricing]`), drugie całego OICP 2.3. Zdanie „SOAP nie działa dla wszystkich usług od
  2.2” jest więc zbyt szerokie. Czy usługi starsze niż 2.2 działają w OICP 2.2 przez SOAP, wynika ze specyfikacji 2.2,
  której nie opracowano.
- **„Implementation: MANDATORY” a nota komunikatu (EMP):** nagłówek `eRoamingPushAuthenticationData` mówi `MANDATORY`
  `[OICP23-EMP-SVC #eRoamingPushAuthenticationData]`, a nota komunikatu: „only for EMPs onboarded to the Hubject
  platform as offline EMPs” `[OICP23-EMP-SVC #eRoamingPushAuthenticationDatamessage]`. Odbiór
  `eRoamingChargeDetailRecord` ma nagłówek `MANDATORY` `[OICP23-EMP-SVC #eRoamingChargeDetailRecord]` i notę „only
  mandatory for online EMPs” `[OICP23-EMP-SVC #eRoamingChargeDetailRecordmessage]`. **Rozstrzygnięcie:** dokument nie
  podaje reguły pierwszeństwa. **Wniosek:** nota jest węższa i bardziej szczegółowa, więc obowiązek zależy od trybu
  EMP (tabela w §4).
- **`lang` w `InfoTextType`:** typ danych ma `lang` jako obowiązkowe `[OICP23-CPO-DT #InfoTextType]`, a Release Notes
  mówią, że przy mapowaniu `ChargingStationName` z 2.2 „NO value will be provided in the “lang” field”
  `[OICP23-RN #eRoamingEVSEData]`. **Rozstrzygnięcie:** wiąże pełna specyfikacja `[OICP23-RN #Introduction]`, więc CPO
  na 2.3 zawsze podaje `lang`. **Wniosek:** EMP musi przyjąć `ChargingStationNames` bez `lang` dla danych z 2.2.
- **Opis `eRoamingPullEVSEPricing`:** zaczyna się od „When an EMP sends an eRoamingPullPricingProductData request”
  `[OICP23-EMP-SVC #eRoamingPullEVSEPricing]`. Z nagłówka i komunikatu wynika, że chodzi o `eRoamingPullEVSEPricing`.
- **Kotwice z literówkami w części EMP:** `#eRoamingAuthoizeStart`, `#eRoamingAuthroizeRemoteStop` (oryginał). Przy
  linkowaniu do dokumentu kopiujesz je dokładnie.

## 13. Czego nie opracowano
- dokumentacja OpenAPI (repozytoria `oicp-cpo-2.3-api-doc`, `oicp-emp-2.3-api-doc`);
- OICP 2.2;
- Dynamic Pricing Functional Guide (poza rejestrem źródeł);
- kolumny 2.1 i 2.2 w tabeli pól obowiązkowych (§1) pochodzą z Release Notes 2.3, nie ze specyfikacji 2.1 i 2.2;
- wybór między połączeniem P2P a hubem (koszty, zasięg hubów): brak źródła oficjalnego;
- typy danych części EMP poza wybranymi (m.in. `PullEvseDataRecordType`);
- załączniki z diagramami;
- eMIP (Gireve): licencja z klauzulą poufności, tylko werdykt `ev_confidential_check`; OCHP: `ochp.md`.
