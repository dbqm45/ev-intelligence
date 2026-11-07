# OCHP 1.4 i OCHPdirect 0.2 (e-clearing.net): clearing house, CDR, statusy

Źródła: repozytorium `github.com/e-clearing-net/OCHP`, commit 034363a (2023-12-14), licencja typu MIT
(`sources/eclearing-ochp.yaml`). Lokalizator `#…` to tytuł nagłówka w pliku Markdown. Zdania **Wniosek** to
interpretacja.

## Spis treści
1. Status wersji
2. Model: clearing house
3. Usługi interfejsu
4. CDR: walidacja i statusy
5. Autoryzacja i tokeny
6. Statusy EVSE i punktu
7. Transport i bezpieczeństwo
8. OCHPdirect
9. OCHP a OCPI i OICP
10. Rozbieżności w dokumentach

## 1. Status wersji
- Według README aktualne wersje to OCHP 1.4 i OCHPdirect 0.2 `[OCHP-README]`.
- Daty wydań `[OCHP14 #Protocol Release Log]` `[OCHPD02 #Protocol Release Log]`:
  - OCHP 1.4: 15.08.2016 (taryfy, zmiany w obsłudze CDR, nowa rola PSO);
  - OCHP 1.3: 27.03.2015;
  - OCHPdirect 0.2: 15.08.2016.
- **Wniosek:** w repozytorium nie ma wydania nowszego niż z 2016 r. Czy protokół jest nadal rozwijany ani ilu partnerów
  go używa, źródła nie mówią. Strona `www.ochp.eu` nie odpowiada z sieci sesji.

## 2. Model: clearing house
- Clearing house zamienia wiele połączeń dwustronnych na jedno połączenie każdego partnera z clearing house
  `[OCHP14 #Clearing House]`.
- „Clearing” w OCHP to przypisanie CDR do właściwego EVSP. Rozliczenie finansowe jest poza zakresem protokołu
  `[OCHP14 #Clearing House functionality]`.
- Zasady clearing house `[OCHP14 #Functional principles of an EV Clearing House]`:
  - przezroczystość dla kierowcy;
  - niezależność od modeli biznesowych i taryf partnerów;
  - anonimowość, czyli jak najmniej danych osobowych.
- Role: EV User, EVSP (dostawca usług), EVSE Operator, NSP (nawigacja), PSO (operator parkingu) `[OCHP14 #Introduction]`.

## 3. Usługi interfejsu `[OCHP14 #CH-Partner Interface description]`
Interfejs obejmuje wymianę:
- danych autoryzacyjnych (roaming list, whitelist);
- CDR;
- informacji o punktach (statycznych i live);
- taryf;
- pojedynczych zapytań o autoryzację;
- danych o miejscach parkingowych.

- **Autoryzacje:** EVSP wysyła swoją listę (`SetRoamingAuthorisationList`), a później tylko zmiany
  (`UpdateRoamingAuthorisationList`). CMS operatora pobiera listę globalną i aktualizacje `[OCHP14 #Exchange Authorisation Data]`.
- **Punkty:** CMS wysyła `SetChargePointList`, a NSP pobiera `GetChargePointList` `[OCHP14 #Exchange Charge Point Information]`.
- **Taryfy:** CPO wysyła taryfy (także dla konkretnych EMP) przez `UpdateTariffs`, a MDM pobiera je przez
  `GetTariffUpdates` `[OCHP14 #Exchange Tariff Information]`. Składniki rozliczeniowe (`BillingItemType`):
  - `parkingtime`, `usagetime`, `reservationtime` (godziny);
  - `energy` (kWh);
  - `power` (kW);
  - `serviceFee` i `reservation` (mnożnik 1.0).

  `[OCHP14 #BillingItemType]`
- **Kody wyniku:** `ok`, `partly`, `not-authorized`, `invalid-id`, `server`, `format`, `roaming` `[OCHP14 #ResultCodeType]`.

## 4. CDR: walidacja i statusy `[OCHP14 #CDR Validation Process]`
1. Operator wysyła CDR (`AddCDRs`) w odstępach uzgodnionych dwustronnie. Clearing house sprawdza wiarygodność.
2. Niewiarygodne CDR wracają do operatora do poprawy. Wiarygodne dostają status `accepted` i trafiają do EVSP.
3. EVSP pobiera CDR (`GetCDRs`) i potwierdza albo odrzuca je (`ConfirmCDRs`):
   - `approved`: CDR jest archiwizowany;
   - `declined`: operator może wysłać poprawiony CDR jako `revised` z tym samym CDR-ID albo zamknąć sprawę jako
     `rejected`, czyli zrezygnować z roszczenia.

- CDR zostają w kolejce do pobrania, dopóki `ConfirmCDRs` nie potwierdzi pobrania. W OCHP 1.4 pierwsze 5 znaków
  CDR-ID to ID CPO, więc identyfikator jest unikalny w całym clearing house `[OCHP14 #Process Charge Data Records]`.
- Statusy (`CdrStatusType`): `new`, `accepted`, `rejected`, `declined`, `approved`, `revised`. Status zmienia tylko
  clearing house `[OCHP14 #CdrStatusType]`.
- Pola CDR m.in. `cdrId`, `evseId`, `emtId`, `contractId`, `startDateTime` i `endDateTime` (czas lokalny punktu),
  `chargePointType` (AC/DC), `chargingPeriods` (jeden okres na pozycję rachunku), `totalCost` (netto, bez VAT),
  `currency` (ISO 4217) `[OCHP14 #CDRInfo]`.

**Wniosek:** OCHP ma jawny obieg akceptacji CDR (zatwierdzenie albo odrzucenie przez EVSP i korekta `revised`). W OCPI
korektą jest credit CDR, a w OICP Hubject przyjmuje jeden CDR na sesję (`oicp.md`).

## 5. Autoryzacja i tokeny
- Podstawą jest whitelist: EVSP wysyła tokeny do clearing house, a operator je pobiera i autoryzuje lokalnie w imieniu
  EVSP `[OCHPD02 #The usual situation without OCHPdirect]`.
- **Pojedyncze zapytanie** (gdy lista lokalna nie jest zsynchronizowana) sprawdza tylko repozytorium tokenów w
  clearing house. Nie jest to zapytanie na żywo do backendu EVSP `[OCHP14 #Request for a single authorization]`.
- `tokenType`: `rfid` (UID karty szesnastkowo, big endian), `remote` (tylko w CDR sesji uruchomionej zdalnie, nie na
  whitelist), `15118` `[OCHP14 #tokenType]`. Reprezentacja tokenu może być jawna albo jako hash SHA-1 lub SHA-256
  `[OCHP14 #tokenRepresentation]`.
- Metody dostępu do punktu (`AuthMethodType`): m.in. `Public`, `DirectCreditcard`, `RfidMifareCls`, `Iec15118`,
  `OchpDirectAuth`, `OperatorAuth` `[OCHP14 #AuthMethodType]`.

## 6. Statusy EVSE i punktu
- **Status ogólny punktu** (`ChargePointStatusType`, stany wielodniowe): `Unknown`, `Operative`, `Inoperative`,
  `Planned`, `Closed` `[OCHP14 #ChargePointStatusType]`.
- **Status live** (dwupoziomowy) `[OCHP14 #MajorType]` `[OCHP14 #MinorType]`:
  - główny (`MajorType`): `available`, `not-available`, `unknown`;
  - szczegółowy (`MinorType`): `available`, `reserved`, `charging`, `blocked`, `outoforder`.
- **TTL** `[OCHP14 #Live Status Interface]`:
  - każdy status live ma czas ważności. Po jego upływie clearing house albo odbiorca może status odrzucić, a status EVSE
    przechodzi wtedy na `unknown`;
  - operator wysyła aktualizację tylko przy zmianie statusu albo przed upływem TTL;
  - dozwolone pary statusów podaje tabela w specyfikacji, inne kombinacje są zakazane.

## 7. Transport i bezpieczeństwo
- SOAP 1.1 jest obowiązkowy `[OCHP14 #Binding to Transport Protocol]`. Uwierzytelnienie to WS-Security Username Token
  w nagłówku SOAP (hasło jako `PasswordText`) `[OCHP14 #User Identification]`. Operacje są zdefiniowane w WSDL
  `[OCHP14-WSDL]`.

## 8. OCHPdirect
- Rozszerzenie od OCHP 1.3 do komunikacji bezpośredniej operator–dostawca: Remote Start/Stop, Live Info, Charge Event,
  Remote Control, Remote Action `[OCHP14 #OCHPdirect Extension]`.
- Operator działa tu jako serwer SOAP; komunikacja odwrotna (dostawca jako serwer) jest możliwa. Adresy endpointów i
  tokeny bezpieczeństwa partnerzy publikują przez clearing house `[OCHPD02 #Basic Principles of OCHPdirect]`.
- Odpowiedzialność za autoryzację przechodzi na dostawcę: operator nie powinien odrzucać zdalnej autoryzacji z innych
  powodów niż umowne lub technicznie uzasadnione `[OCHPD02 #The situation with OCHPdirect]`.
- Interfejs zabezpiecza się TLS 1.2 i Basic Authentication, bez certyfikatów klienta
  `[OCHPD02 #Security of the OCHPdirect interface]`.

## 9. OCHP a OCPI i OICP (Wniosek)
| Temat | OCHP 1.4 | OICP 2.3 (`oicp.md`) | OCPI 2.3.0 (`moduly.md`) |
|---|---|---|---|
| Topologia | clearing house + opcjonalnie OCHPdirect | hub Hubject | peer-to-peer albo hub |
| Transport | SOAP 1.1, WS-Security | REST | REST/JSON |
| Autoryzacja | whitelist w clearing house; pojedyncze zapytanie bez backendu EVSP | offline, do EMP albo broadcast | whitelist albo real-time |
| Korekta CDR | `declined` → `revised` / `rejected` | jeden CDR na SessionID | credit CDR |
| Status live | major/minor z TTL | 6 wartości | 9 wartości |

**Wniosek:** mapowanie statusu live OCHP na OCPI jest bliższe niż z OICP, bo OCHP ma `blocked` i `charging` w
statusie szczegółowym. TTL nie ma odpowiednika w OCPI, więc po jego upływie ustawiasz `UNKNOWN`.

## 10. Rozbieżności w dokumentach
- **Nazwa operacji pojedynczej autoryzacji:**
  - opis procesu: `RequestLiveRoamingAuthorisation.req` `[OCHP14 #Request the CHS to authorize one single token for roaming]`;
  - rozdział komunikatów: `RequestSingleRoamingAuthorisation.req` `[OCHP14 #RequestSingleRoamingAuthorisation.req]`;
  - WSDL: operacja `GetSingleRoamingAuthorisation` `[OCHP14-WSDL]`.

  **Rozstrzygnięcie:** do implementacji wiąże WSDL, bo z niego generuje się klienta SOAP. Pozostałe nazwy traktujesz
  jako opisowe.
