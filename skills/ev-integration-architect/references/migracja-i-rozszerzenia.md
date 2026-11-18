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
7. Tożsamość, adres i poświadczenia: co nie przenosi się samo
8. Stan zapisany w stacji: autoryzacja, profile ładowania, rezerwacje, dostępność
9. Transakcje w chwili przełączenia
10. OCPI przy zmianie platformy CPO
11. Lista kontrolna migracji
12. Migracja: czego źródła nie określają
13. Rozszerzenia OCPP: cztery mechanizmy
14. Rozszerzenia OCPI
15. Testy zgodności i macierz kompatybilności
16. Rozbieżności

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

## 7. Tożsamość, adres i poświadczenia: co nie przenosi się samo
**OCPP 1.6.** Rdzeń 1.6 nie ma klucza z adresem CSMS ani slotów profili `[OCA-WP-MIG §4]`. Biała księga
bezpieczeństwa 1.6-J standaryzuje tylko klucze `AuthorizationKey` (hasło Basic Auth, tylko zapis), `CpoName` (pole O w
CSR) i `SecurityProfile` (po zmianie stacja rozłącza się i łączy z nowym profilem) `[SWP4 §7.2]` `[SWP4 §7.5]`
`[SWP4 §7.6]`. Klucza z adresem CSMS w niej nie ma: adres zawsze jest kluczem producenta. Nie ma też mechanizmu powrotu
do starego CSMS.

**OCPP 2.0.1.** Sloty i kolejność:
- Dostępne numery slotów stacja podaje w `valuesList` zmiennej `NetworkConfigurationPriority`, a slot bieżącego
  połączenia w `OCPPCommCtrlr.ActiveNetworkProfile` (tylko odczyt) `[201-P2 B09]` `[201-P2 §2.1.1 ActiveNetworkProfile]`.
- `SetNetworkProfile`: `Accepted` po zapisaniu `[201-P2 B09.FR.01]`. `Rejected` przy błędnej treści
  (`InvalidNetworkConf`) `[201-P2 B09.FR.02]`, przy slocie spoza `valuesList` (`InvalidConfSlot`) `[201-P2 B09.FR.05]`
  albo przy niższym `securityProfile` bez `AllowSecurityProfileDowngrade` (`NoSecurityDowngrade`)
  `[201-P2 B09.FR.04]`. `Failed`, gdy zapis poprawnego profilu się nie uda `[201-P2 B09.FR.03]`.
- Zmiana aktywnego profilu działa dopiero po restarcie. Błąd w B09 nie psuje bieżącego połączenia `[201-P2 B09]`.
- `NetworkConnectionProfileType` zawiera też `ocppVersion` (ignorowane: wersję ustala uzgodnienie WebSocket),
  `ocppTransport`, `messageTimeout`, `ocppInterface` oraz opcjonalnie `vpn` i `apn`. `ocppCsmsUrl` (≤ 512 znaków) podaje
  się bez identyfikatora stacji: stacja dokleja `SecurityCtrlr.Identity` `[201-P2 §2.35 NetworkConnectionProfileType]`.
- `SetVariables(NetworkConfigurationPriority)` zwraca `Accepted` albo `RebootRequired`, a `Rejected`, gdy któryś
  wskazany slot nie ma poprawnej konfiguracji `[201-P2 B10.FR.01]` `[201-P2 B10.FR.02]`.

**Identyfikator i hasło są wspólne dla wszystkich slotów (2.0.1).**
- `SecurityCtrlr.Identity` ma dostęp „ReadOnly or ReadWrite”, więc nie każda stacja pozwoli go zmienić
  `[201-P2 §2.2.2 Identity]`. `BasicAuthPassword` jest tylko do zapisu: nowy CSMS nie odczyta starego hasła
  `[201-P2 §2.2.1 BasicAuthPassword]`.
- Po `SetVariables(BasicAuthPassword)` stacja od razu się rozłącza i łączy z nowym hasłem z tym samym CSMS
  `[201-P2 A01]`. Po `Accepted` CSMS SHALL przestać przyjmować stare hasło `[201-P2 A01.FR.03]`.
- OCA ostrzega: po zmianie identyfikatora albo hasła pod nowy CSMS powrót do slotu starego CSMS się nie uda
  `[OCA-WP-MIG §5.1]`.
- **Wniosek:** w 2.0.1 przenieś stację ze starym identyfikatorem i hasłem, a hasło zmień dopiero z nowego CSMS. Inny
  wariant to uzgodnienie hasła z nowym CSMS z wyprzedzeniem, ale wtedy stary CSMS musi przyjąć nowe hasło do chwili
  resetu. W 2.1 identyfikator i hasło są częścią profilu, więc problem znika `[OCA-WP-MIG §5.1]`.

**Wyższy profil bezpieczeństwa zamyka drogę powrotu.**
- Podniesienie profilu wymaga ważnego `CSMSRootCertificate` (A05.FR.02), a dla profilu 3 także certyfikatu stacji
  `[201-P2 A05.FR.03]`.
- Po udanym połączeniu z wyższym profilem stacja SHALL usunąć wszystkie profile sieci z niższym `securityProfile`
  `[201-P2 A05.FR.06]`. Przy migracji z 1 do 2 slot starego CSMS znika więc sam.
- Certyfikaty: przy `AdditionalRootCertificateCheck = true` certyfikat główny nowego CSMS musi być podpisany bieżącym
  `[201-P2 M05.FR.10]`, czyli potrzebna jest współpraca starego CSO. Gdy stacja wraca do starego profilu, sprawdza
  serwer zapasowym, starym certyfikatem głównym `[201-P2 M05.FR.16]`. Szczegóły PKI, hasła i profilu 3:
  `skills/ev-iso15118-pki-expert/references/bezpieczenstwo-ocpp.md` §4–6.

## 8. Stan zapisany w stacji: autoryzacja, profile ładowania, rezerwacje, dostępność
Stacja przechowuje stan ustawiony przez stary CSMS. Nowy CSMS go nie zna, a OCPP nie przenosi go między systemami.

| Stan | OCPP 1.6 | OCPP 2.0.1 | Co robi nowy CSMS (**Wniosek**) |
|---|---|---|---|
| lista lokalna | SHOULD przetrwać restart `[16 §3.5.2]`; wersja 0 = pusta, −1 = brak obsługi `[16 §5.10]` | SHOULD przetrwać restart `[201-P2 D01.FR.10]`; zmienia ją tylko `SendLocalList` `[201-P2 D01.FR.09]`; wersja 0 = brak listy `[201-P2 D02.FR.02]` | odczytaj wersję. Wyślij pełną listę (`Full`) z nową numeracją albo pustą `Full`, która usuwa wszystkie wpisy `[201-P2 D01.FR.04]`. Kopiowanie list między CSMS jest specyficzne dla systemu `[OCA-WP-MIG §3.2]` |
| pamięć autoryzacji (cache) | SHOULD przetrwać restart `[16 §3.5.1]`, wg erraty także reset `[16E §3.4]` | SHOULD przetrwać restart `[201-P2 C10.FR.02]`; `ClearCache` `[201-P2 C11.FR.01]` | wyczyść `ClearCache` po pierwszym połączeniu, bo wpisy zostały wydane przez stary CSMS |
| profile ładowania | wg erraty SHALL przetrwać restart `[16E §3.37]`; brak odczytu listy profili, tylko `GetCompositeSchedule` `[16 §5.7]`; `ClearChargingProfile` z filtrami `[16 §6.13]` | SHALL przetrwać restart `[201-P2 K01.FR.27]`; odczyt `GetChargingProfiles` `[201-P2 K09]`; usuwanie `[201-P2 K10]` | odczytaj (2.0.1) albo wyczyść (1.6) i ustaw od nowa własne profile |
| rezerwacje | — | stan `Reserved` przetrwa restart `[201-P2 B01.FR.13]` `[201-P2 B11.FR.05]`; przejście EVSE w `Unavailable` anuluje rezerwację i wysyła `ReservationStatusUpdate(Removed)` `[201-P2 H01.FR.17]` | zakończ rezerwacje przed przełączeniem. Nowy CSMS nie zna `reservationId`, a pierwszy sygnał dostanie w `TransactionEvent` `[201-P2 H01.FR.15]` |
| niedostępność | `Unavailable` z `ChangeAvailability` przetrwa restart `[16 §4.9]` | `Inoperative` ustawione przez CSMS wraca po restarcie `[201-P2 B11.FR.02]` `[201-P2 B12.FR.06]` | po migracji z `Inoperative` (B10.FR.05) nowy CSMS musi przywrócić `Operative`, inaczej stacja zostanie niedostępna |

Pozostałe parametry istotne w nowej sieci ustawia się w każdej partii `[OCA-WP-MIG §3.3]`. Przykłady (`OrganizationName`
w 2.0.1, `CpoName` w 1.6-J) to **Wniosek**.

## 9. Transakcje w chwili przełączenia
- **2.0.1:** reset w B10 to `OnIdle`. Przy trwających transakcjach stacja czeka na ich koniec. Natychmiastowe
  przełączenie wymaga wcześniejszego zatrzymania transakcji `[201-P2 B10]`. Zalecane `Inoperative` i pusta kolejka
  przed resetem są w §4 pkt 4 `[201-P2 B10.FR.05]`.
- **2.0.1:** do zaakceptowania `BootNotification` stacja nie wysyła nic poza nim, także zbuforowanych komunikatów
  `[201-P2 B01.FR.08]`. Po akceptacji niewysłane komunikaty transakcji trafią do nowego CSMS. `transactionId` nadaje
  stacja `[201-P2 E §1.2]`, więc nowy CSMS może zapisać zakończenie pod tym identyfikatorem, ale nie zna startu.
- **1.6:** `transactionId` nadaje Central System `[16 §6.46]`. Stacja kolejkuje komunikaty transakcji offline i wysyła
  je chronologicznie `[16 §3.7]`. Przy `Reset` stacja SHALL wysłać `StopTransaction` przed resetem, a bez odpowiedzi
  kolejkuje go `[16 §5.14]`. Taki zakolejkowany `StopTransaction` trafi do nowego systemu z identyfikatorem nadanym
  przez stary.
- **OCPI:** CDR nie można zmienić ani zastąpić po wysłaniu; korekta to Credit CDR `[OCPI230 §10.1]`.
- **Wniosek:** każda transakcja ma mieć start i koniec w jednym systemie. Nowy CSMS powinien przyjmować i oznaczać
  komunikaty o nieznanych transakcjach (do uzgodnienia ze starym CSO), a nie wystawiać z nich drugiego CDR.

## 10. OCPI przy zmianie platformy CPO
- **Rejestracja od nowa.** Każdy partner (eMSP, hub) wymienia credentials z nową platformą: token A przekazany poza
  OCPI, `GET versions`, POST z tokenem B, odpowiedź z tokenem C `[OCPI230 §7.1.1]`. POST zwraca 405, jeśli klient
  był już zarejestrowany `[OCPI230 §7.2.2]`.
- **Zmiana adresu istniejącej rejestracji.** PUT na credentials z nowym `url` sprawia, że druga strona pobiera
  endpointy od nowa `[OCPI230 §7.1.3]` `[OCPI230 §7.2.3]`. PUT wymaga obecnego tokenu, czyli udziału starej platformy.
- **Wyrejestrowanie.** DELETE: obie strony kończą automatyczną komunikację `[OCPI230 §7.2.4]`.
- **Role.** Każda rola w credentials ma unikalną kombinację `role`, `party_id`, `country_code` `[OCPI230 §7.3.1]`.
  Location wskazuje CPO, który ją „posiada” (`country_code`, `party_id`) `[OCPI230 §8.3.1]`.
- **Locations.**
  - `Location.id` i `EVSE.uid` nigdy się nie zmieniają w ramach platformy CPO `[OCPI230 §8.3.1]` `[OCPI230 §8.3.2]`.
  - Lokalizacji i EVSE nie usuwa się: EVSE wycofuje się statusem `REMOVED` przez PUT albo PATCH `[OCPI230 §8.1]`.
  - `evse_id` można zdjąć z EVSE w stanie `REMOVED`, żeby użyć go ponownie `[OCPI230 §8.3.2]`.
  - Przy nowym CSO zmienia się EVSEID `[OCA-WP-MIG §3.2]`.
- **Tokens.** Nowa platforma pobiera pełną listę tokenów od eMSP metodą GET (pull przy starcie systemu)
  `[OCPI230 §12.1.2]`.
- **Wniosek:** gdy zmienia się CSO (nowy `party_id`), stara platforma oznacza EVSE jako `REMOVED`, a nowa publikuje
  nowe obiekty z nowymi EVSEID. Gdy CSO zostaje, a zmienia się tylko platforma, zachowaj `id` i `uid` z eksportu, żeby
  u eMSP nie powstały duplikaty. W każdej chwili tylko jedna platforma publikuje daną lokalizację.

## 11. Lista kontrolna migracji
**Wniosek** (na podstawie §1–10):
1. Inwentarz: model, firmware, wersja OCPP, profil bezpieczeństwa, sposób zmiany sieci, SIM/APN, terminal płatniczy
   `[OCA-WP-MIG §3.1]`.
2. Test każdego modelu z nowym CSMS, w tym zachowanie przy nieudanym połączeniu (B10.FR.07/08 to SHOULD).
3. Poświadczenia: decyzja o identyfikatorze i haśle (§7). Certyfikat główny nowego CSMS: podpis starym przy
   `AdditionalRootCertificateCheck`. Dla profilu 3 nowy CSMS ufa CA starego CSO `[OCA-WP-MIG §5.2]`.
4. Przed przełączeniem: koniec rezerwacji i zdalnych startów, `Inoperative`, pusta kolejka transakcji
   (`GetTransactionStatus`).
5. 1.6: zapisz bieżące wartości kluczy (`GetConfiguration`), żeby móc wrócić. Zmieniaj je w kolejności, w której
   zerwanie połączenia w połowie nie odetnie stacji `[OCA-WP-MIG §4]`.
6. 2.0.1: `SetNetworkProfile` do wolnego slotu, `NetworkConfigurationPriority` z nowym slotem na początku, `Reset OnIdle`.
7. Po `BootNotification` w nowym CSMS: `GetBaseReport(FullInventory)`, `Operative`, `ClearCache`, lista lokalna
   (`Full`), profile ładowania, `OrganizationName`/`CpoName`, nowy certyfikat stacji (A02), nowe hasło.
8. Usuń slot starego CSMS dopiero po potwierdzeniu partii.
9. OCPI: credentials z każdym partnerem, pull tokenów, publikacja Locations, `REMOVED` po stronie starej platformy,
   QR/NFC i oznakowanie `[OCA-WP-MIG §3.3]`.
10. Uzgodnienie transakcji i CDR z okresu przełączenia ze starym CSO.

## 12. Migracja: czego źródła nie określają
- Klucza konfiguracji z adresem CSMS w 1.6: nie ma go ani w rdzeniu, ani w białej księdze bezpieczeństwa.
- Komunikatu usuwającego profil sieci w 2.0.1. W B09/B10 nie ma takiego komunikatu, a biała księga mówi tylko, że slot
  starego CSMS „should be removed” `[OCA-WP-MIG §5.1]`. **Wniosek:** w praktyce usuwasz slot z
  `NetworkConfigurationPriority`.
- Przeniesienia listy lokalnej, cache, profili ładowania i rezerwacji między CSMS (poza zdaniem, że kopiowanie list jest
  specyficzne dla systemu `[OCA-WP-MIG §3.2]`).
- Jak nowy CSMS ma obsłużyć komunikaty transakcji, której startu nie zna.
- Migracji CPO między platformami w OCPI: brak procedury przeniesienia rejestracji, Locations ani sesji w toku.
- Rezerwacji w 1.6 przy przełączeniu: nie opracowano.

## 13. Rozszerzenia OCPP: cztery mechanizmy `[OCA-WP-CUST]`
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

## 14. Rozszerzenia OCPI `[OCPI230 §4.1.8]`
- Platforma SHALL NOT odrzucać nieopisanych pól.
- Rozszerzając OCPI, implementator SHOULD zakładać, że rozszerzenie wejdzie do OCPI albo stanie się powszechne; SHOULD
  wybierać znaczące, nieużywane nazwy i SHOULD NOT dodawać przedrostków `x-` ani `custom`. Dalsze zasady: strona EVRF
  „extending OCPI” (nieopracowana).

**Wniosek:** odwrotnie niż w OCPP, w OCPI rozszerzenie to nowe pole o zwykłej nazwie, a odbiorca musi tolerować pola,
których nie zna. Walidator OCPI w bramie nie może odrzucać nieznanych pól.

## 15. Testy zgodności i macierz kompatybilności
- Certyfikacja OCA: certyfikat Core nie obejmuje opcjonalnych profili (np. Smart Charging); certyfikaty są na liście
  OCA z wersją oprogramowania `[OCA-CERT]` `[OCA-LIST]`. Metodę porównania certyfikatu, PICS i przypadków testowych
  części 6 opisuje skill `ev-evse-diagnostics-expert`.
- Obserwacje z wdrożeń (model × firmware × funkcja) zapisuje się w rejestrze odchyleń
  `knowledge/implementation-intelligence/vendor-quirks/` z dowodem i poziomem pewności.
- Testy OCPI (środowiska hubów, narzędzia EVRF) i testy interoperacyjności (plugfesty) nie są opracowane.

**Wniosek:** macierz kompatybilności CSMS × model × firmware × funkcja budujesz z trzech źródeł: certyfikat i PICS
(deklaracja), wynik własnego testu przypadku z części 6 (obserwacja), wpis w rejestrze odchyleń. Status „zweryfikowane”
dajesz tylko przy teście na tej wersji firmware.

## 16. Rozbieżności
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| powrót do ostatniego profilu | biała księga: „there is a requirement that states that … the charging station needs to fall back” `[OCA-WP-MIG §5.1]` | B10.FR.07 to SHOULD, alternatywą jest B10.FR.08 `[201-P2 B10.FR.07]` | specyfikacja: zalecenie, nie obowiązek; nie zakładaj go bez testu modelu |
| odwołanie w B10.FR.07 | uwaga: „section 5.3. Reconnecting” części 4 `[201-P2 B10.FR.07]` | w części 4 Edition 4 ponowne łączenie to §5.4, a §5.3 to WebSocket Ping `[201-P4 §5.4]` | §5.4 |
| klucze sieci w 1.6 | „The configuration key names are not standardized”; przykłady `BasicAuthPassword` albo `AuthorizationKey`, `SecurityProfile`, `CpoName` `[OCA-WP-MIG §4]` | biała księga bezpieczeństwa 1.6-J definiuje `AuthorizationKey`, `CpoName`, `SecurityProfile`, ale nie adres CSMS `[SWP4 §7.2]` `[SWP4 §7.6]` | przy stacji z SWP4 te trzy klucze są standardowe; adres CSMS zawsze sprawdzasz w dokumentacji producenta |
| synchroniczność CALL | 1.6: SHOULD NOT `[J16 §4.1.1]` | 2.0.1: SHALL NOT `[201-P4 §4.1.1]` | zależnie od wersji; CSMS powinien tolerować skrzyżowane CALL w obu |
