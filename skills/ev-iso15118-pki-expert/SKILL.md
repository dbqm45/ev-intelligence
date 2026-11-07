---
name: ev-iso15118-pki-expert
description: Użyj przy bezpieczeństwie OCPP i Plug & Charge — profile bezpieczeństwa, TLS, certyfikaty stacji i V2G, OCSP, podpis firmware, ISO 15118 w OCPP i OCPI.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy bezpieczeństwie komunikacji ładowarka–CSMS i integracji ISO 15118 po stronie backendu — profile bezpieczeństwa OCPP 1–3 i ich obniżanie, TLS 1.2+, zestawy szyfrów, hasło Basic Auth, certyfikat stacji (O i CN), hierarchie CSO i producenta, unieważnianie (szybkie wygasanie, weryfikacja online), certyfikat główny CSMS i AdditionalRootCertificateCheck, bezpieczna aktualizacja firmware (podpis RSA-PSS lub ECDSA), cztery PKI Plug & Charge według OCPP (CSO, CPS, MO, OEM), typy certyfikatów w OCPP 2.0.1, instalacja certyfikatu w pojeździe (Get15118EVCertificate), OCSP, autoryzacja certyfikatem umowy (C07, eMAID, ContractValidationOffline), Plug & Charge w OCPP 1.6 przez DataTransfer (nota OCA), zmiany OCPP 2.1 dla ISO 15118-20, możliwości Plug & Charge w OCPI i wymogi AFIR. Treść normy ISO 15118 jest płatna i nieopracowana. Nie do V2X i DER (ev-energy-smart-charging-expert), sprzętu i aneksu II AFIR (ev-evse-hardware-expert) ani komunikatów OCPP spoza bezpieczeństwa (ev-ocpp-expert)."
  slowa: "bezpieczeństwo OCPP, security profile, profil bezpieczeństwa, profil 1, profil 2, profil 3, AllowSecurityProfileDowngrade, TLS 1.2, cipher suite, zestaw szyfrów, ECDHE, forward secrecy, Basic Auth, BasicAuthPassword, mTLS, certyfikat klienta, certyfikat stacji, ChargingStationCertificate, SignCertificate, CertificateSigned, CSR, CertSigningWaitMinimum, CSMSRootCertificate, AdditionalRootCertificateCheck, InstallCertificate, DeleteCertificate, GetInstalledCertificateIds, unieważnienie certyfikatu, revocation, OCSP, szybkie wygasanie, CA, PKI, V2G PKI, V2G Root, MO Root, OEM provisioning, CPS, contract certificate, certyfikat umowy, eMAID, Plug & Charge, PnC, ISO 15118, ISO 15118-2, ISO 15118-20, Get15118EVCertificate, GetCertificateStatus, ContractValidationOffline, CentralContractValidationAllowed, iso15118CertificateHashData, ISO15118PnCEnabled, org.openchargealliance.iso15118pnc, podpis firmware, secure firmware update, InvalidFirmwareSignature, security event, SecurityEventNotification, Improved security for OCPP 1.6-J"
---

# ISO 15118 & PKI Expert — bezpieczeństwo OCPP i Plug & Charge od strony backendu

Skill odpowiada, **jak zabezpieczyć połączenie stacja–CSMS i obsłużyć certyfikaty Plug & Charge**: profile
bezpieczeństwa, TLS, certyfikaty, unieważnianie, podpis firmware, ISO 15118 w OCPP 1.6 i 2.0.1, OCPI i AFIR. Taksonomia:
D11.01, D11.02, D01.06 (od strony OCPP). Sieć: brak.

**Zasada źródeł.** Fakty mają znacznik `[dokument §]` i pochodzą z `sources/*.yaml`: OCPP 2.0.1 i 2.1, biała księga
bezpieczeństwa 1.6-J i nota OCA o Plug & Charge w 1.6, OCPI 2.3.0, AFIR. **ISO 15118 (wszystkie części) jest normą
płatną bez dostępu** (`sources/niedostepne.yaml`): sekwencji komunikacji pojazd–stacja (SLAC, SDP, TLS V2G), komunikatów
V2G i profili certyfikatów V2G PKI nie opisujesz. Mówisz, że wymagają normy, i nie uzupełniasz z pamięci. Tak samo przy
VDE-AR-E 2802-100-1 i IEC 62443.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „OCPP 2.0.1 A00.FR.005
`[201-P2 A00.FR.005]`”, „OCPP 2.0.1 C07.FR.07 `[201-P2 C07.FR.07]`”, „nota aplikacyjna OCA o Plug & Charge w 1.6 §2.2
`[OCA-AN-PNC §2.2]`”, „errata OCPP 2.0.1 2026-09 `[201-E]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/bezpieczenstwo-ocpp.md` | profile bezpieczeństwa, TLS i szyfry, Basic Auth, profil 3, certyfikaty i hierarchie, unieważnianie, podpis firmware, 1.6-J i 2.1 |
| `references/iso15118-w-ocpp.md` | PKI Plug & Charge według OCPP, typy certyfikatów, M01–M06, autoryzacja C07 i offline, Plug & Charge w 1.6, 2.1, OCPI, AFIR |

## Procedura
1. **Zakres:** bezpieczeństwo połączenia stacja–CSMS czy Plug & Charge; wersja OCPP; czy pytanie dotyczy treści ISO 15118
   (wtedy: niedostępne).
2. **Profil bezpieczeństwa:** w terenie co najmniej profil z TLS; obniżanie tylko z 3 na 2 i tylko przy
   `AllowSecurityProfileDowngrade` `[201-P2 A00.FR.005]`.
3. **TLS i certyfikaty:** TLS ≥ 1.2, wymagane zestawy szyfrów, O i CN w certyfikatach, hierarchia CSO
   (`references/bezpieczenstwo-ocpp.md`).
4. **Cykl życia:** wymiana certyfikatu stacji (A02/A03), certyfikat główny CSMS (M05), unieważnianie i OCSP.
5. **Plug & Charge:** typy certyfikatów, instalacja w pojeździe przez CSMS, autoryzacja C07 i tryb offline; w 1.6
   nota OCA (`references/iso15118-w-ocpp.md`).
6. **Roaming i regulacje:** możliwości złącza w OCPI tylko przy faktycznej dostępności; daty ISO 15118 z AFIR.
7. **Luki:** treść ISO 15118, wytyczne VDE, normy cyberbezpieczeństwa: odsyłasz do `sources/niedostepne.yaml`.

## Przykład
**Pytanie:** „Stacja OCPP 2.0.1 z Plug & Charge straciła łączność. Czy pojazd z certyfikatem umowy może ładować?”

Fakty:
- Online stacja wysyła `AuthorizeRequest` z eMAID i danymi OCSP, a CSMS sprawdza certyfikat `[201-P2 C07.FR.01]`
  `[201-P2 C07.FR.05]`.
- Offline przy `ContractValidationOffline = false` stacja SHALL NOT pozwolić ładować `[201-P2 C07.FR.07]`.
- Przy `true` stacja sprawdza certyfikat lokalnie. Przy ważnym certyfikacie i `LocalAuthorizeOffline = true` szuka eMAID
  na liście lokalnej albo w cache `[201-P2 C07.FR.08]` `[201-P2 C07.FR.09]`. eMAID nieznany przy
  `OfflineTxForUnknownIdEnabled = true` → ładowanie `[201-P2 C07.FR.12]`.

**Wniosek:** o zachowaniu offline decydują trzy zmienne, które CSMS ustawia świadomie. Do lokalnej weryfikacji stacja
potrzebuje zainstalowanego `MORootCertificate` (M05) i aktualnych danych OCSP (M06, odświeżanie co najmniej raz w
tygodniu) `[201-P2 M06.FR.10]`. Szczegóły kryptograficznej weryfikacji łańcucha określa ISO 15118, która jest
niedostępna.

## Pułapki
- Hasło Basic Auth w 2.0.1 to ciąg UTF-8, nie base64 ani oktety; inaczej niż w 1.6 `[201-P2 A00.FR.205]`.
- Identyfikator stacji z `:` psuje Basic Auth, bo jest nazwą użytkownika `[201-P2 A00.FR.204]`.
- Obniżenie profilu na 1 przez OCPP jest zabronione `[201-P2 A00.FR.005]`.
- Preinstalowany zestaw dobrze znanych CA na stacji to ryzyko; do OCPP tylko hierarchia CSO `[201-P2 A §1.4.2]`.
- Podpis firmware po erracie 2026-04: RSA-PSS albo ECDSA (ECSchnorr usunięty) `[201-E]`.
- W 1.6 Plug & Charge według noty OCA: opakowany `Authorize` jest obowiązkowy, a w `StartTransaction.req` jest eMAID
  `[OCA-AN-PNC §5]`. Smart charging ISO 15118 wymaga 2.0.1 `[OCA-AN-PNC §1.3]`.
- `ISO_15118_2_PLUG_AND_CHARGE` w OCPI tylko wtedy, gdy kierowca faktycznie może z tego skorzystać `[OCPI230 §8.4.4]`.

## Źródła
`sources/oca-ocpp.yaml` (201-P2 bloki A, C07–C08, L01, M; 201-E; SWP4; OCA-AN-PNC; 21-P0), `sources/evrf-ocpi.yaml`
(OCPI230 §8.4.4), `sources/eu-afir.yaml` (AFIR Annex II). Niedostępne: `sources/niedostepne.yaml`. Pobrane 2026-11-07.
