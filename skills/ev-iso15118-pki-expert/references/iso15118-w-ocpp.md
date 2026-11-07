# ISO 15118 i Plug & Charge w OCPP 1.6, 2.0.1, 2.1, OCPI i AFIR

Źródła: OCPP 2.0.1 część 2: blok M, C07/C08 `[201-P2]`, nota aplikacyjna OCA „Using ISO 15118 Plug & Charge with OCPP
1.6” `[OCA-AN-PNC]`, OCPP 2.1 część 0 `[21-P0]`, OCPI 2.3.0 `[OCPI230]`, AFIR `[AFIR]`. **Treść ISO 15118 jest płatna i
niedostępna** (`sources/niedostepne.yaml`). Ten plik opisuje tylko to, co o ISO 15118 mówią dokumenty bezpłatne. Zdania
**Wniosek** to rekomendacje.

## Spis treści
1. Czego tu nie ma
2. Cztery PKI według OCPP
3. Certyfikaty, którymi zarządza OCPP 2.0.1
4. Instalacja i aktualizacja certyfikatu w pojeździe (M01–M02)
5. Certyfikaty w stacji (M03–M06)
6. Autoryzacja Plug & Charge (C07) i EIM (C08)
7. Plug & Charge w OCPP 1.6 (nota aplikacyjna OCA)
8. OCPP 2.1 i ISO 15118-20
9. OCPI i AFIR
10. Rozbieżności

## 1. Czego tu nie ma
Sekwencje SLAC, SDP i TLS między pojazdem a stacją, struktura komunikatów V2G, profile certyfikatów V2G PKI, wymagania
ISO 15118-20 (BPT, tryby sterowania). OCPP odsyła do nich numerami stron i rozdziałów ISO 15118 `[201-P2 M01]`. Bez
dostępu do normy na takie pytania odpowiadasz, że wymagają normy, i nie uzupełniasz z pamięci.

## 2. Cztery PKI według OCPP `[201-P2 M §2.1]`
- Plug & Charge opiera się na podpisach cyfrowych i certyfikatach X.509. Według OCPP potrzebne są cztery PKI: CSO,
  dostawcy provisioningu certyfikatów (CPS), operatora mobilności (MO) i producenta pojazdu (OEM).
- Kotwicą zaufania CSO i CPS jest V2G Root CA. OEM i MO mogą mieć własne Root CA albo certyfikaty pochodne od V2G Root.
- OCPP przenosi łańcuchy:
  - CPS: Prov Sub-CA 1, Sub-CA 2, certyfikat provisioningu (w `CertificateInstallationRes` i `CertificateUpdateRes`);
  - MO: MO Sub-CA 1, Sub-CA 2, certyfikat umowy (contract certificate);
  - certyfikat provisioningu OEM (w `CertificateInstallationReq`).
- OCPP zaleca profil bezpieczeństwa z TLS, bo bez niego można „zepsuć” bezpieczeństwo ISO 15118 `[201-P2 M §1]`.

## 3. Certyfikaty, którymi zarządza OCPP 2.0.1 `[201-P2 M §2]`
| Typ | Do czego | Przypadki użycia |
|---|---|---|
| `ChargingStationCertificate` | połączenie stacja–CSMS | A02, A03 |
| `V2GChargingStationCertificate` | TLS pojazd–stacja | A02, A03 |
| `V2GRootCertificate` | TLS pojazd–stacja; wystarczy zainstalować root | M03–M05 |
| `V2GIntermediateCertificate` | pośrednie między certyfikatem stacji V2G a V2G Root | A02, A03, M03, M04 |
| `MORootCertificate` | autoryzacja Plug & Charge; pośrednie MO dostarcza pojazd | M03–M05 |
| CPS Certificate Chain | autoryzacja Plug & Charge | M03–M05 |
| `EVContractCertificate` | autoryzacja Plug & Charge, krótsza ważność | M01, M02 |
| `OEMProvisioningCertificate` | instalacja certyfikatów w pojeździe, długa ważność, instaluje OEM | M01, M02 |

## 4. Instalacja i aktualizacja certyfikatu w pojeździe
- M01: na `CertificateInstallationReq` z ISO 15118 stacja SHALL przekazać żądanie do CSMS w
  `Get15118EVCertificateRequest` z `action = Install`. CSMS przekazuje je dalej, np. do puli certyfikatów umów według
  wytycznych VDE-AR-E 2802-100-1 (niedostępne) `[201-P2 M01.FR.01]`.
- M02: to samo dla `CertificateUpdateReq` z `action = Update` `[201-P2 M02.FR.01]`.
- Przebieg sesji Plug & Charge z ISO 15118-2 w OCPP (instalacja certyfikatu, `Authorize` z
  `iso15118CertificateHashData`, `TransactionEvent`, `NotifyEVChargingNeeds`, profil ładowania) pokazuje rysunek 120
  `[201-P2 M §1]`. Według uwagi pod rysunkiem timeout `ChargeParameterDiscoveryReq` wynosi 2 s i może być wydłużony do
  60 s na profil z CSMS, z odwołaniem do ISO 15118-2.

## 5. Certyfikaty w stacji
- M03: CSMS pobiera listę zainstalowanych certyfikatów (`GetInstalledCertificateIds`) `[201-P2 M03]`.
- M04, usuwanie: `Accepted` po usunięciu, `NotFound`, `Failed` (stacja może odmówić usunięcia ostatniego certyfikatu
  danego typu). Certyfikatu stacji nie usuwa się przez `DeleteCertificate` (M04.FR.06) `[201-P2 M04.FR.03]`.
- M05, instalacja CA: przekroczenie `CertificateEntries.maxLimit` albo nieważny certyfikat → `Rejected`
  (M05.FR.06–07); zasady wymiany certyfikatu głównego CSMS opisuje `bezpieczenstwo-ocpp.md`, sekcja 6
  `[201-P2 M05.FR.06]`.
- M06, OCSP: stacja SHALL pobierać i buforować status OCSP swoich certyfikatów V2G (M06.FR.06), odświeżać po wymianie
  certyfikatu i co najmniej raz w tygodniu (M06.FR.07, M06.FR.10). CSMS zwraca odpowiedź OCSP według RFC 6960, w
  kodowaniu DER (M06.FR.08–09) `[201-P2 M06.FR.10]`.

## 6. Autoryzacja Plug & Charge (C07) i EIM (C08)
- Online: stacja SHALL wysłać `AuthorizeRequest` z eMAID i danymi do zapytania OCSP o certyfikat umowy i łańcuch
  (C07.FR.01–02). CSMS SHALL sprawdzić ważność przez OCSP, bieżący albo buforowany (C07.FR.05) `[201-P2 C07.FR.05]`.
- Stacja bez odpowiedniego root, przy `CentralContractValidationAllowed = true`, przekazuje łańcuch certyfikatu umowy w
  PEM do sprawdzenia w CSMS (C07.FR.06) `[201-P2 C07.FR.06]`.
- Odpowiedzi CSMS (C07.FR.13–17) `[201-P2 C07.FR.14]`:

| Stan | `certificateStatus` | `idTokenInfo.status` |
|---|---|---|
| łańcuch ważny, token zablokowany, wygasły, nieważny albo nieznany | `ContractCancelled` | stan tokenu |
| łańcuch ważny, token w porządku | `Accepted` | stan tokenu (np. `ConcurrentTx` dalej blokuje ładowanie) |
| certyfikat wygasł | `CertificateExpired` | `Expired` |
| certyfikat unieważniony | `CertificateRevoked` | `Invalid` |
| łańcucha nie da się zweryfikować | `CertChainError` | `Invalid` |

- **Offline** `[201-P2 C07.FR.07]`:
  - `ContractValidationOffline = false` → stacja SHALL NOT pozwolić ładować (C07.FR.07);
  - `true` → stacja sprawdza certyfikat lokalnie (C07.FR.08);
  - ważny certyfikat przy `LocalAuthorizeOffline = true` → wyszukanie eMAID na liście lokalnej albo w cache (C07.FR.09)
    i zachowanie jak w C13 lub C12 (C07.FR.10–11);
  - eMAID nieznany przy `OfflineTxForUnknownIdEnabled = true` → ładowanie według C15 (C07.FR.12).
- C08: autoryzacja zewnętrznym środkiem identyfikacji (EIM, np. RFID) w sesji ISO 15118 `[201-P2 C08]`.

## 7. Plug & Charge w OCPP 1.6 `[OCA-AN-PNC]`
- OCPP 1.6 nie obsługuje komunikatów ISO 15118. Nota OCA opisuje rozwiązanie pośrednie: komunikaty z OCPP 2.0.1 (nieco
  uproszczone) opakowane w `DataTransfer` `[OCA-AN-PNC §1.1]` `[OCA-AN-PNC §1.3]`.
- Obejmuje zarządzanie certyfikatami i autoryzację Plug & Charge, **bez smart charging ISO 15118**: ten wymaga OCPP
  2.0.1. Przy jednoczesnym wdrożeniu bezpieczeństwa OCPP i Plug & Charge OCA zdecydowanie zaleca 2.0.1 `[OCA-AN-PNC §1.3]`.
- Pola `DataTransfer`: `vendorId = org.openchargealliance.iso15118pnc`, `messageId` = nazwa komunikatu 2.0.1
  (`Authorize`, `CertificateSigned`, `DeleteCertificate`, `Get15118EVCertificate`, `GetCertificateStatus`,
  `GetInstalledCertificateIds`, `InstallCertificate`, `SignCertificate`, `TriggerMessage`), `data` = komunikat w JSON
  `[OCA-AN-PNC §2.2]`.
- Włączenie i wykrycie: klucz `ISO15118PnCEnabled`. CSMS bez obsługi noty odpowiada `Rejected`, `UnknownVendorId` albo
  `UnknownMessageId`. Wtedy stacja SHALL NOT ponawiać `SignCertificate` bez `TriggerMessage` `[OCA-AN-PNC §2.1]`.
- Z białą księgą bezpieczeństwa 1.6: komunikaty opakowane tylko dla przypadków ISO 15118. Na przykład `MORootCertificate`
  usuwa się opakowanym `DeleteCertificate`, a certyfikat główny CS zwykłym komunikatem z białej księgi
  `[OCA-AN-PNC §2.3]`.
- Autoryzacja: opakowany `Authorize` jest obowiązkowy dla Plug & Charge, zwykłego `Authorize.req` SHALL NOT się wtedy
  używać, a `StartTransaction.req` MUST zawierać eMAID w `idTag`. Przy EIM używa się zwykłego `Authorize.req`
  `[OCA-AN-PNC §5]`.
- Offline: klucz `ContractValidationOffline` i reguły jak w 2.0.1, z kluczami 1.6 (`LocalAuthorizeOffline`,
  `AllowOfflineTxForUnknownId`). Usuwanie z listy lokalnej eMAID po wygaśnięciu umowy należy do CS `[OCA-AN-PNC §5]`.

## 8. OCPP 2.1 i ISO 15118-20 (lista zmian) `[21-P0 rozdz. 2]`
- A02/A03: `requestId` w `SignCertificateRequest` i obsługa certyfikatów ISO 15118-20.
- C07/C08: zaktualizowane o przebiegi ISO 15118-20. M01: zaktualizowany dla ISO 15118-20.
- K18–K20: przypadki ISO 15118-20; V2X i DER: skill `ev-energy-smart-charging-expert`.
- Szczegółów wymagań bloków A, C i M w 2.1 nie opracowano.

## 9. OCPI i AFIR
- OCPI 2.3.0: możliwości złącza `ISO_15118_2_PLUG_AND_CHARGE` i `ISO_15118_20_PLUG_AND_CHARGE` oznaczają, że kierowca
  **faktycznie** może z nich skorzystać; samo wsparcie sprzętu nie wystarcza `[OCPI230 §8.4.4]`.
- AFIR, aneks II: publiczne punkty instalowane od 8.01.2026 zgodne z EN ISO 15118-1…-5, a od 1.01.2027 co najmniej
  EN ISO 15118-20:2022; przy Plug & Charge zarówno 15118-2, jak i 15118-20 `[AFIR Annex II pkt 2.1.1]`
  `[AFIR Annex II pkt 2.1.2]`. Szczegóły w skillu `ev-evse-hardware-expert`.

**Wniosek:** ogłaszanie w OCPI Plug & Charge dla stacji, która ma tylko sprzętowe wsparcie ISO 15118, a nie ma
skonfigurowanych certyfikatów V2G i umowy z MO lub pulą certyfikatów, jest niezgodne z §8.4.4.

## 10. Rozbieżności
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| nazwa wytycznych VDE | M01.FR.01: „VDE-AR-2802-100-1” `[201-P2 M01.FR.01]` | M02.FR.01: „VDE-AR-E 2802-100-1” `[201-P2 M02.FR.01]` | literówka w M01; ten sam dokument (VDE-AR-E 2802-100-1) |
| klucz ładowania nieznanego tokenu offline | 1.6 (nota OCA): `AllowOfflineTxForUnknownId` `[OCA-AN-PNC §5]` | 2.0.1: `OfflineTxForUnknownIdEnabled` `[201-P2 C07.FR.12]` | różne wersje protokołu; ta sama funkcja |
| errata wspomniane w nocie 1.6 | nota (2020) przywołuje erratę 2.0.1 dodającą `CertSigningWaitMinimum`, `CertSigningRepeatTimes` `[OCA-AN-PNC §3.1]` | Edition 4 ma je w treści: podwajanie odstępu od `CertSigningWaitMinimum` przy braku `CertificateSigned` (A02.FR.18) i zatrzymanie ponowień po limicie do czasu `TriggerMessage` (A02.FR.19); definicja w §2.2.8 `[201-P2 A02.FR.18]` | erratę włączono do Edition 4 |
