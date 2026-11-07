# Bezpieczeństwo OCPP: profile, TLS, certyfikaty, unieważnianie, firmware

Źródła: OCPP 2.0.1 Edition 4, część 2, blok A i L `[201-P2]`, errata 2026-09 `[201-E]`, biała księga OCA „Improved
security for OCPP 1.6-J” edition 4 `[SWP4]`, OCPP 2.1 część 0 `[21-P0]`. Zdania **Wniosek** to rekomendacje.

## Spis treści
1. Cele i zakres
2. Profile bezpieczeństwa
3. TLS i zestawy szyfrów
4. Hasło Basic Auth
5. Profil 3: certyfikat stacji
6. Certyfikaty i hierarchie
7. Unieważnianie
8. Bezpieczna aktualizacja firmware
9. OCPP 1.6-J i 2.1
10. Rozbieżności

## 1. Cele i zakres `[201-P2 A §1.1]`
Kanał chroniony silną kryptografią, wzajemne uwierzytelnienie stacji i CSMS, bezpieczna aktualizacja firmware (źródło,
integralność, niezaprzeczalność) i rejestrowanie zdarzeń bezpieczeństwa. Tych samych czterech celów używa biała księga
dla 1.6-J `[SWP4 §1.2]`.

## 2. Profile bezpieczeństwa `[201-P2 A §1.3]`
| Profil | Uwierzytelnienie stacji | Uwierzytelnienie CSMS | Kanał |
|---|---|---|---|
| 1 | HTTP Basic | brak | bez szyfrowania |
| 2 | HTTP Basic | certyfikat serwera TLS | TLS |
| 3 | certyfikat klienta TLS | certyfikat serwera TLS | TLS |

- Profil 1 tylko w zaufanych sieciach (np. VPN); w terenie zdecydowanie zaleca się profil z TLS. Implementacja 2.0.1 bez
  bezpieczeństwa nie jest poprawną implementacją 2.0.1 `[201-P2 A §1.3]`.
- Bez poprawnej daty i czasu stacja nie zweryfikuje certyfikatu serwera. OCA podaje rozwiązania: NTP, czas z sieci
  komórkowej, narzędzie instalatora `[201-P2 A §1.3]`.
- Jeden profil naraz (A00.FR.001). Profil musi być skonfigurowany przed komunikacją OCPP (A00.FR.004). CSMS może mieć
  różne profile na różnych portach (A00.FR.006) `[201-P2 A00.FR.001]`.
- **Obniżanie profilu** (A00.FR.005): tylko gdy jest `AllowSecurityProfileDowngrade = true`, i tylko z 3 na 2. Obniżenie
  z 2 lub 3 na 1 przez OCPP jest zabronione `[201-P2 A00.FR.005]`.

## 3. TLS i zestawy szyfrów `[201-P2 A §1.3.5]`
- CSMS jest serwerem TLS i uwierzytelnia się certyfikatem CSMS. Stacja weryfikuje ścieżkę certyfikacji i zgodność CN z
  FQDN CSMS (A00.FR.306–309). Przy złym certyfikacie stacja zgłasza zdarzenie `InvalidCsmsCertificate` i rozłącza się
  (A00.FR.310–311) `[201-P2 A00.FR.310]`.
- Tylko TLS 1.2 lub nowszy; obie strony sprawdzają wersję. Stara wersja albo SSL → rozłączenie, a po stronie stacji
  zdarzenie `InvalidTLSVersion` (A00.FR.313–316) `[201-P2 A00.FR.313]`.
- CSMS SHALL obsługiwać co najmniej `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`, `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`,
  `TLS_RSA_WITH_AES_128_GCM_SHA256` i `TLS_RSA_WITH_AES_256_GCM_SHA384`. To wymaga dwóch certyfikatów, a przy profilu 3
  zdolności wystawiania certyfikatów klienta dla obu rodzajów (A00.FR.318) `[201-P2 A00.FR.318]`.
- Stacja: para ECDHE_ECDSA albo para RSA (A00.FR.319). TLS_RSA nie daje forward secrecy, więc zalecane jest ECDHE, a w
  niektórych jurysdykcjach forward secrecy jest obowiązkowe `[201-P2 A00.FR.319]`.
- Bez szyfrów oznaczonych jako nieodpowiednie (A00.FR.320) i bez kompresji TLS (A00.FR.321) `[201-P2 A00.FR.320]`.

## 4. Hasło Basic Auth (profile 1 i 2) `[201-P2 A §1.3.3]`
- Nazwa użytkownika = identyfikator stacji z URL połączenia. Identyfikator nie może zawierać `:` (A00.FR.204).
- Hasło w zmiennej `BasicAuthPassword`: losowe, co najmniej 16 znaków; `maxLimit` od 40 do 64; wysyłane jako ciąg UTF-8,
  nie w kodowaniu oktetowym ani base64 (A00.FR.205). Kodowanie hasła różni się od OCPP 1.6 `[201-P2 A00.FR.205]`.
- CSMS SHALL sprawdzić parę identyfikator i hasło (A00.FR.207).

## 5. Profil 3: certyfikat stacji `[201-P2 A §1.3.7]`
- Stacja uwierzytelnia się certyfikatem klienta TLS (A00.FR.401–402). CSMS weryfikuje ścieżkę certyfikacji, nazwę CSO w
  polu O i numer seryjny stacji w polu CN (A00.FR.403–405) `[201-P2 A00.FR.404]`.
- Certyfikat nie należy do CSO (np. zaraz po instalacji) → zaleca się go wymienić przed dalszą komunikacją
  (A00.FR.406). Brak ważnego certyfikatu → CSMS SHALL rozłączyć (A00.FR.407) `[201-P2 A00.FR.406]`.
- Wymiana certyfikatu stacji: A02 (na żądanie CSMS) i A03 (z inicjatywy stacji), przez `SignCertificate` (CSR) i
  `CertificateSigned` `[201-P2 A02]` `[201-P2 A03]`.

## 6. Certyfikaty i hierarchie `[201-P2 A §1.4]`
- Klucze w OCPP: certyfikat CSMS, certyfikat stacji, certyfikat podpisu firmware (klucz u producenta), certyfikat SECC
  (stacja; TLS ISO 15118-2 między stacją a pojazdem) `[201-P2 A §1.4]`.
- Właściwości `[201-P2 A §1.4.1]`:
  - klucz o sile co najmniej 112 bitów symetrycznych: RSA/DSA ≥ 2048 bitów, krzywe eliptyczne ≥ 224 bity
    (A00.FR.501–503);
  - podpis CA zalecany RSA-PSS albo ECDSA, skrót SHA256 (A00.FR.505–506);
  - format X.509 w PEM, numer seryjny, nazwa organizacji w O (A00.FR.507–509);
  - certyfikat CSMS: CN = FQDN; certyfikat stacji: CN = numer seryjny stacji, nie URL ani IP (A00.FR.510–511);
  - `subjectAltName` typu `dnsName` nie powinien być używany (wyjątek: CSMS osiągalny różnymi ścieżkami sieciowymi);
    zdecydowanie odradza się Extended Key Usage ze względu na zgodność z ISO 15118 (A00.FR.511, A00.FR.514);
  - certyfikat stacji używany też jako SECC musi spełniać ISO 15118-2 (A00.FR.513), której treść jest niedostępna
    (`sources/niedostepne.yaml`).
- Dwie hierarchie: CSO (certyfikaty CSMS i stacji) oraz producenta (podpis firmware). CSO może być CA dla swojej
  hierarchii; dla podpisu firmware zaleca się zaufaną stronę trzecią (niezaprzeczalność) (A00.FR.601–604) `[201-P2 A §1.4.2]`.
- Nie zaleca się preinstalowanych zestawów dobrze znanych CA na stacji: do połączenia OCPP tylko certyfikaty hierarchii
  CSO `[201-P2 A §1.4.2]`.
- Certyfikat główny CSMS (M05): przy `AdditionalRootCertificateCheck = true` nowy certyfikat główny musi być podpisany
  starym; stary zostaje tymczasowo jako zapasowy i jest usuwany po udanym połączeniu z nowym (M05.FR.09–13)
  `[201-P2 M05.FR.10]`.

## 7. Unieważnianie `[201-P2 A §1.5]`
| Certyfikat | Zalecana metoda |
|---|---|
| CSMS | szybkie wygasanie: ważność krótsza niż 24 h (A00.FR.701) |
| stacji | weryfikacja online przez CSMS (A00.FR.702); CSMS SHALL sprawdzić ważność w serwerze CA (A00.FR.705) |
| podpisu firmware | weryfikacja online; CSMS powinien sprawdzić certyfikat i podpis przed przekazaniem stacji (A00.FR.707) |

- Zaleca się osobny serwer CA, który śledzi unieważnienia (A00.FR.703–704). Stacja komunikuje się z CA tylko przez
  CSMS, więc przejęta stacja nie zaatakuje CA bezpośrednio `[201-P2 A §1.5]`.
- Unieważnienie certyfikatu nie wymaga zamknięcia połączenia, które może trwać ponad 24 h `[201-P2 A §1.5]`.

## 8. Bezpieczna aktualizacja firmware (L01) `[201-P2 L01]`
- Każdy stan procesu → `FirmwareStatusNotification` z tym samym `requestId` (L01.FR.01, L01.FR.10). Zły certyfikat
  podpisu albo podpis → zdarzenia `InvalidFirmwareSigningCertificate`, `InvalidFirmwareSignature` (L01.FR.02–03)
  `[201-P2 L01.FR.02]`.
- Weryfikacja podpisu po pobraniu: według erraty 2026-04 stacja SHALL zweryfikować podpis z `UpdateFirmwareRequest`
  skrótem całego pliku; algorytm podpisu RSA-PSS albo ECDSA. Wcześniejszy tekst dopuszczał ECSchnorr `[201-E]`
  (L01.FR.04, errata §2.16).
- Instalacja po zakończeniu transakcji, jeśli nie da się instalować w trakcie. Wolne EVSE → `Unavailable`, chyba że
  `AllowNewSessionsPendingFirmwareUpdate = true` (L01.FR.06–07) `[201-P2 L01.FR.07]`.
- Zaleca się szyfrowany transfer (HTTPS, SFTP, FTPS albo zaszyfrowany plik) (L01.FR.08). Podpis cyfrowy nad skrótem
  obrazu, najlepiej wykonany przez producenta (L01.FR.09) `[201-P2 L01.FR.09]`.

## 9. OCPP 1.6-J i 2.1
- 1.6-J: biała księga OCA dodaje do 1.6-J mechanizmy bezpieczeństwa z 2.x: bezpieczne połączenie, zdarzenia
  bezpieczeństwa, bezpieczną aktualizację firmware. Edition 4 zastępuje poprzednie, a OCA odradza implementowanie
  starszych. Dotyczy tylko OCPP-J, nie SOAP `[SWP4 §1]` `[SWP4 §1.1]` `[SWP4 §1.4]`.
- 2.1: obniżenie profilu z 3 na 2 przestało być zabronione (A05); certyfikaty ISO 15118-20 w A02/A03; `requestId` w
  `SignCertificateRequest` `[21-P0 rozdz. 2]`.

## 10. Rozbieżności
| Temat | Dokument A | Dokument B | Rozstrzygnięcie |
|---|---|---|---|
| algorytm podpisu firmware | L01.FR.04 w części 2: RSA-PSS albo ECSchnorr `[201-P2 L01.FR.04]` | errata 2026-04: RSA-PSS albo ECDSA, odwołanie do właściwości certyfikatów `[201-E]` | errata |
| obniżanie profilu | 2.0.1: tylko z 3 na 2 przy `AllowSecurityProfileDowngrade` `[201-P2 A00.FR.005]` | 2.1, lista zmian A05: obniżenie z 3 na 2 nie jest już zabronione `[21-P0 rozdz. 2]` | zależnie od wersji; szczegółów A05 w 2.1 nie opracowano |
