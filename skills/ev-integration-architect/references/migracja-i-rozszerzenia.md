# Migracja stacji do innego CSMS, rozszerzenia protokołów, testy zgodności

Źródła: OCA „Migrating Charging Stations” v1.0 `[OCA-WP-MIG]`, OCA „Customizing OCPP Implementations” v1.1
`[OCA-WP-CUST]`, OCPP 2.0.1 części 2 i 4 `[201-P2]` `[201-P4]`, OCPI 2.3.0 `[OCPI230]`, certyfikacja OCA `[OCA-CERT]`
`[OCA-LIST]`. Białe księgi OCA to zalecenia na podstawie doświadczeń członków. Wymaganiami są tylko cytowane
wymagania specyfikacji. Studia przypadków z załączników `[OCA-WP-MIG]` nie są tu wykorzystywane. Zdania **Wniosek**
to rekomendacje.

## Spis treści
1. Co trzeba przenieść
2. Kolejność migracji
3. Migracja OCPP 1.6
4. Migracja OCPP 2.0.1: profile sieci (B09, B10)
5. Profil bezpieczeństwa 3
6. Typowe przeszkody
7. Rozszerzenia OCPP: cztery mechanizmy
8. Rozszerzenia OCPI
9. Testy zgodności i macierz kompatybilności
10. Rozbieżności

## 1. Co trzeba przenieść `[OCA-WP-MIG §2]`
- Stacje: konfiguracja połączenia z backendem (URL), karty SIM, naklejki QR/NFC, umowy i konfiguracja terminali
  płatniczych, oznakowanie.
- Konta użytkowników: dane, płatności, historia, preferencje.
- Dane w CSMS: identyfikatory, lokalizacje, konfiguracje. Dla roamingu zmienia się zewnętrzny identyfikator EVSE
  (EVSEID) przy nowym CSO. Do tego umowy roamingowe (np. OCPI) i listy autoryzacji; sposób ich kopiowania między CSMS
  jest własny dla każdego systemu `[OCA-WP-MIG §3.2]`.

## 2. Kolejność migracji `[OCA-WP-MIG §3]`
1. **Test każdego modelu stacji** z nowym CSMS, z uwzględnieniem wersji oprogramowania. Bez oficjalnej certyfikacji OCPP
   obu stron test zgodności jest konieczny. Rozbieżności usuwa producent (firmware) albo adapter `[OCA-WP-MIG §3.1]`.
2. **Sposób zmiany konfiguracji sieci** dla modelu: polecenia OCPP (`ChangeConfiguration` / `SetNetworkProfile`, wymaga
   pomocy starego CSO), firmware od producenta, własny skrypt albo wizyta technika `[OCA-WP-MIG §3.1]`.
3. **SIM i APN**: czy da się przenieść kartę do operatora nowego CSO; jeśli nie, wymiana na miejscu `[OCA-WP-MIG §3.1]`.
4. **Przeniesienie danych** z CSMS, umów roamingowych, kont kierowców (tylko gdy CSO jest też MSP) `[OCA-WP-MIG §3.2]`.
5. **Migracja w partiach**, nie wszystkich stacji naraz. Dla każdej partii: SIM, konfiguracja sieci, pozostałe
   parametry, lista autoryzacji, QR/NFC, oznakowanie `[OCA-WP-MIG §3.3]`. Stałe kody QR/NFC są podatne na oszustwa; o
   ile się da, zaleca się dynamiczne kody na wyświetlaczu.

## 3. Migracja OCPP 1.6 `[OCA-WP-MIG §4]`
- OCPP 1.6 nie określa konfiguracji połączenia z siecią, a nazwy kluczy nie są ustandaryzowane. Trzeba je znaleźć w
  dokumentacji producenta. OCA podaje przykładowe nazwy spotykane w praktyce: `OcppCsmsUrl` albo `CSMSURL`,
  `BasicAuthPassword` albo `AuthorizationKey`, `SecurityProfile`, `CpoName`.
- Bez kluczy konfiguracji potrzebny jest producent (port serwisowy, pakiet przez `UpdateFirmware`) albo wizyta.
- **Konfiguracja wymaga kilku komunikatów. Zerwanie połączenia w połowie może sprawić, że stacja nie połączy się z
  żadnym CSMS.**

## 4. Migracja OCPP 2.0.1: profile sieci
Według białej księgi `[OCA-WP-MIG §5.1]`, z wymaganiami części 2:
1. Certyfikat główny nowego CSMS: `InstallCertificateRequest` z `certificateType = CSMSRootCertificate` (przypadek M05).
   Przy `SecurityCtrlr.AdditionalRootCertificateCheck = true` stacja przyjmie go tylko wtedy, gdy jest podpisany
   bieżącym certyfikatem głównym.
2. Profil połączenia w drugim slocie: `SetNetworkProfileRequest` (`configurationSlot`, `connectionData` z `ocppCsmsUrl`
   i `securityProfile`). Stacja SHALL obsługiwać co najmniej dwa sloty (B09.FR.06) `[201-P2 B09.FR.06]`. W 2.0.1 profil
   nie zawiera `identity` ani `basicAuthPassword`; zmienia się je przez `SetVariables`. OCPP 2.1 dodał te pola do
   profilu `[OCA-WP-MIG §5.1]`.
3. Kolejność prób: `OCPPCommCtrlr.NetworkConfigurationPriority`, np. „2,1” (najpierw nowy, potem stary CSMS). Stacja
   próbuje `NetworkProfileConnectionAttempts` razy dla każdego wpisu (B10.FR.03) `[201-P2 B10.FR.03]`.
4. Przed resetem zaleca się ustawić stację jako `Inoperative` i poczekać na opróżnienie kolejki komunikatów
   transakcyjnych (sprawdzenie przez `GetTransactionStatus`). Inaczej nowy CSMS dostanie komunikaty transakcji, której
   startu nie zna, a stary nie dostanie zakończeń (B10.FR.05) `[201-P2 B10.FR.05]`.
5. Reset. Stacja SHALL rozłączyć się ze starym CSMS przed połączeniem z nowym (B10.FR.06) i po zmianie profilu SHALL
   wysłać `BootNotification` (B10.FR.10) `[201-P2 B10.FR.10]`. Nowy CSMS pobiera pełny Device Model przez
   `GetBaseReport(FullInventory)`, a po udanej migracji profil starego CSMS usuwa się ze slotu `[OCA-WP-MIG §5.1]`.
6. Gdy żaden wpis się nie połączy, stacja SHOULD wrócić do profilu ostatniego udanego połączenia (B10.FR.07) albo zacząć
   od nowa od wszystkich wpisów (B10.FR.08) i SHOULD NOT przestawać próbować, żeby nie stać się „stranded asset”
   (B10.FR.09) `[201-P2 B10.FR.09]`.

**Wniosek:** w planie migracji partia zaczyna się od kilku stacji każdego modelu i wersji firmware. Dalsze partie
idą dopiero po potwierdzeniu `BootNotification` w nowym CSMS i po usunięciu starego profilu.

## 5. Profil bezpieczeństwa 3 `[OCA-WP-MIG §5.2]`
- Stacja uwierzytelnia się certyfikatem klienta podpisanym przez CA CSMS (A03). Najpierw wykonuje się kroki z sekcji 4,
  bez hasła.
- Nowy CSMS musi zaufać certyfikatom podpisanym przez stary:
  - ma certyfikat główny starego CSO i akceptuje jego nazwę w polu O (`organizationName`);
  - sprawdza, czy CN (`commonName`) zawiera numer seryjny stacji.
- Po połączeniu nowy CSMS ustawia `SecurityCtrlr.OrganizationName` i zleca nowy certyfikat (A02).

## 6. Typowe przeszkody `[OCA-WP-MIG §6]`
- Różne interpretacje OCPP po stronie stacji i CSMS. Certyfikacja OCPP obu stron zmniejsza ryzyko; certyfikat można
  sprawdzić na stronie OCA `[OCA-LIST]`. Rozwiązania: firmware od producenta albo dostosowanie CSMS.
- Brak wsparcia producenta: szczególnie ryzykowne przy OCPP 1.6 z własnymi nazwami kluczy. OCA zaleca długie umowy
  wsparcia i depozyt (ESCROW) firmware.
- Brak współpracy starego CSO:
  - zostaje dostęp serwisowy producenta, i to z profilem 1 bez TLS, bo stacja nie ma certyfikatu nowego CSMS (potem
    przejście na profil 2);
  - albo wizyta z laptopem;
  - dane stacji wpisuje się ręcznie.
  
  OCA zaleca zapisać w umowie z CPO obowiązek współpracy przy migracji.
- SIM przypisane do konta starego CSO: transfer albo wymiana na miejscu. eSIM ze zdalnym provisioningiem tego unika.

## 7. Rozszerzenia OCPP: cztery mechanizmy `[OCA-WP-CUST]`
- OCA ostrzega: rozszerzenia wpływają na zgodność; użycie trzeba udokumentować, a warto najpierw skonsultować z OCA
  `[OCA-WP-CUST §1.1]`.
- OCPP 1.6 ma tylko klucze konfiguracji, `DataTransfer` i mechanizm aktualizacji firmware. 2.0.1 dodaje Device Model i
  `customData` `[OCA-WP-CUST §1.2]`.

| Cel | Mechanizm (2.0.1) | Uwagi |
|---|---|---|
| stan, wartość lub zdarzenie komponentu; konfiguracja | **Device Model**: własne komponenty i zmienne, `GetVariables`, monitory (`SetVariableMonitoring` → `NotifyEvent`) | najmniej zmian w oprogramowaniu, zgodny z innymi systemami `[OCA-WP-CUST §1.2.1]` |
| dodatkowe pola w istniejącym komunikacie | **`customData`** z wymaganym `vendorId`; system bez rozszerzenia ignoruje te pola | schematów OCPP się nie zmienia `[OCA-WP-CUST §1.2.2]` |
| zupełnie nowy komunikat | **`DataTransfer`** (`vendorId`, opcjonalnie `messageId`, `data`); nieznane → `UnknownVendorId` / `UnknownMessageId` | największy wpływ na oprogramowanie `[OCA-WP-CUST §1.2.3]` |
| rzadkie przesłanie dużego pliku | **`UpdateFirmware`** | status mówi tylko o pobraniu i instalacji `[OCA-WP-CUST §1.2.4]` |

- `vendorId`: odwrócona nazwa domeny DNS organizacji, opcjonalnie z nazwą funkcji (P01.FR.02) `[OCA-WP-CUST §1.2.3]`.
  To jednocześnie granulacja włączania i wyłączania rozszerzenia `[OCA-WP-CUST §1.5.1]`.
- Każde rozszerzenie stacja zgłasza instancją komponentu `CustomizationCtrlr` (instancja = `vendorId`, zmienna
  `Enabled`); CSMS może je wyłączyć `[OCA-WP-CUST §1.3]`.
- Zasady zgodności `[OCA-WP-CUST §1.5.1]`:
  - system z rozszerzeniem MUST działać poprawnie z systemem standardowym;
  - wyłączone przez CSMS rozszerzenie = zachowanie standardowe;
  - nie zgłoszone rozszerzenie: stacja wnioskuje z odpowiedzi CSMS i przy braku wsparcia go nie używa.
- Certyfikacja: stację bada się z symulowanym CSMS, który wyłącza wszystkie zgłoszone rozszerzenia, a CSMS z
  symulowaną stacją bez rozszerzeń `[OCA-WP-CUST §1.5.2]`.

## 8. Rozszerzenia OCPI `[OCPI230 §4.1.8]`
- Platforma SHALL NOT odrzucać nieopisanych pól.
- Rozszerzając OCPI, implementator SHOULD zakładać, że rozszerzenie wejdzie do OCPI albo stanie się powszechne; SHOULD
  wybierać znaczące, nieużywane nazwy i SHOULD NOT dodawać przedrostków `x-` ani `custom`. Dalsze zasady: strona EVRF
  „extending OCPI” (nieopracowana).

**Wniosek:** odwrotnie niż w OCPP, w OCPI rozszerzenie to nowe pole o zwykłej nazwie, a odbiorca musi tolerować pola,
których nie zna. Walidator OCPI w bramie nie może odrzucać nieznanych pól.

## 9. Testy zgodności i macierz kompatybilności
- Certyfikacja OCA: certyfikat Core nie obejmuje opcjonalnych profili (np. Smart Charging); certyfikaty są na liście
  OCA z wersją oprogramowania `[OCA-CERT]` `[OCA-LIST]`. Metodę porównania certyfikatu, PICS i przypadków testowych
  części 6 opisuje skill `ev-evse-diagnostics-expert`.
- Obserwacje z wdrożeń (model × firmware × funkcja) zapisuje się w rejestrze odchyleń
  `knowledge/implementation-intelligence/vendor-quirks/` z dowodem i poziomem pewności.
- Testy OCPI (środowiska hubów, narzędzia EVRF) i testy interoperacyjności (plugfesty) nie są opracowane.

**Wniosek:** macierz kompatybilności CSMS × model × firmware × funkcja budujesz z trzech źródeł: certyfikat i PICS
(deklaracja), wynik własnego testu przypadku z części 6 (obserwacja), wpis w rejestrze odchyleń. Status „zweryfikowane”
dajesz tylko przy teście na tej wersji firmware.

## 10. Rozbieżności
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| powrót do ostatniego profilu | biała księga: „there is a requirement that states that … the charging station needs to fall back” `[OCA-WP-MIG §5.1]` | B10.FR.07 to SHOULD, alternatywą jest B10.FR.08 `[201-P2 B10.FR.07]` | specyfikacja: zalecenie, nie obowiązek; nie zakładaj go bez testu modelu |
| odwołanie w B10.FR.07 | uwaga: „section 5.3. Reconnecting” części 4 `[201-P2 B10.FR.07]` | w części 4 Edition 4 ponowne łączenie to §5.4, a §5.3 to WebSocket Ping `[201-P4 §5.4]` | §5.4 |
| synchroniczność CALL | 1.6: SHOULD NOT `[J16 §4.1.1]` | 2.0.1: SHALL NOT `[201-P4 §4.1.1]` | zależnie od wersji; CSMS powinien tolerować skrzyżowane CALL w obu |
