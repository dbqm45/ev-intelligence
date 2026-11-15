# Wersje OCPP, status i licencja

Stan na 2026-11-07. Źródła: dokumenty OCA z `sources/oca-ocpp.yaml` (znaczniki jak w `SKILL.md`).

## Aktualne wydania na stronie pobrań OCA `[OCA-DL]`
| Wersja | Aktualne wydanie | Starsze wydania dostępne na stronie |
|---|---|---|
| 2.1 | **Edition 2** (części z 2025-12-03), errata 2026-09 (2026-10-07), załączniki v2.1 | Edition 1 (all files & errata) |
| 2.0.1 | **Edition 4** (części z 2025-12-03), errata 2026-09 (2026-10-07), załączniki v1.5 | Edition 3, Edition 2, „part 2 edition 1 & errata” |
| 2.0 | tylko „Errata and changelog” | — |
| 1.6 | „all files & errata”: 1.6 edition 2 (2017-09-28), errata 1.6 i OCPP-J 1.6 (2025-04) | — |
| 1.6 security | **Security Whitepaper Edition 4** (2026-02-05) | Edition 3 |
| 1.5, 1.2 | pakiety archiwalne | — |

- Schematy JSON w pakiecie 2.0.1 Edition 4 mają datę 2020-03-31 (oznaczenie „OCPP 2.0.1 FINAL”), czyli kolejne edycje
  nie zmieniły schematów `[201-P3]` (ReadMe pakietu).
- Schematy w pakiecie 2.1 Edition 2 mają datę 2025-01-23 i nagłówek „OCPP 2.1 Edition 1” `[21-P3]` (ReadMe pakietu).
- Załączniki części 2 (komponenty i zmienne Device Model) mogą być aktualizowane bez nowego wydania OCPP, o ile nowe
  elementy są opcjonalne (ReadMe pakietów 2.0.1 Ed4 i 2.1 Ed2).

## Normalizacja w IEC
| Fakt | Źródło |
|---|---|
| OCPP 2.0.1 przyjęte przez IEC jako norma w październiku 2024 | `[OCA-N1]` |
| OCPP 2.1 wydane w styczniu 2025 | `[OCA-N1]`, `[OCA-N2]` |
| OCPP 2.1 Edition 1 przyjęte przez IEC jako IEC 63584-210 (2025-09-02) | `[OCA-N1]` |
| OCPP 2.1 Edition 1 opublikowane jako IEC 63584-210:2025 (komunikat 2025-12-09) | `[OCA-N2]` |
Numeru części IEC 63584 dla 2.0.1 sprawdzone źródła OCA nie podają. Specyfikacje OCA nie wspominają o IEC 63584.

## Rozbieżności wewnątrz specyfikacji
Przy (pozornej) sprzeczności między tekstem opisowym, diagramami sekwencji, przykładami i wymaganiami pierwszeństwo mają
**wymagania** (np. `B01.FR.05`), w 2.0.1 i 2.1 `[201-P2 §2.1.2]` `[21-P2 §2.1.2]`. **Wniosek:** w rozstrzygnięciu najpierw
cytujesz wymaganie FR, potem erratę i schemat; przykład JSON albo diagram nie przesądzają.

## 1.6: OCPP-J i OCPP-S
OCPP 1.6 ma dwa warianty transportu: SOAP (OCPP-S) i JSON (OCPP-J); dokument bazowy opisuje protokół, a transport
opisują osobne specyfikacje `[16 §3.2]`. Edycja 2 nie zmienia komunikatów względem 1.6 z 2015 r., a scala znane errata
`[16 §3.1]`. Ten skill opisuje wariant JSON (`[J16]`); specyfikacji OCPP-S nie ma w rejestrze źródeł.

## Zgodność między wersjami
- 2.0.1 „is not backward compatible with OCPP 1.6 or OCPP 1.5” `[201-P0 rozdz. 2]`.
- 2.1 „is an extension of OCPP 2.0.1”. Schematy 2.1 to schematy 2.0.1 rozszerzone o pola opcjonalne. Logika aplikacji
  2.0.1 działa w 2.1 bez zmian z drobnymi wyjątkami wymienionymi w części 0 (np. przypadki użycia A02 i A03:
  `SignCertificateRequest` zyskał pole `requestId`) `[21-P0 §1.1]`.
- Nowe akcje 2.1 względem 2.0.1: 27 (porównanie list schematów `[201-P3]`, `[21-P3]`; lista w `komunikaty-201.md`).

## Podprotokół WebSocket (`Sec-WebSocket-Protocol`)
| Wersja | Ciąg | Źródło |
|---|---|---|
| 1.2 / 1.5 / 1.6 / 2.0 | `ocpp1.2`, `ocpp1.5`, `ocpp1.6`, `ocpp2.0` | `[J16 §3.1.2]` |
| 2.0.1 | `ocpp2.0.1` | `[201-P4 §3.1.2]` |
| 2.1 | `ocpp2.1` | `[21-P4 §3.1.2]` |
Gdy CSMS nie zgadza się na żaden z zaproponowanych podprotokołów, „MUST complete the WebSocket handshake with a response
without a Sec-WebSocket-Protocol header and then immediately close the WebSocket connection” `[J16 §3.2]`.
Nieznany identyfikator stacji w ścieżce URL → CSMS SHOULD odpowiedzieć HTTP 404 i przerwać połączenie `[J16 §3.2]`.

## Identyfikator stacji w URL połączenia
- URL połączenia = endpoint OCPP-J + `/` + identyfikator stacji, kodowany procentowo zgodnie z RFC 3986 (np. „RDAM 123”
  → `…/ocppj/RDAM%20123`) (OCPP-J 1.6 §3.1.1 `[J16 §3.1.1]`).
- 1.6 z dodatkiem bezpieczeństwa: przy Basic Auth nazwa użytkownika SHALL być równa identyfikatorowi stacji z URL
  (A00.FR.204), hasło jest w kluczu `AuthorizationKey` (A00.FR.205), a Central System SHALL sprawdzić zgodność identyfikatora i klucza
  z nagłówkiem autoryzacji (A00.FR.207) (Security Whitepaper ed. 4 §2.3.1 `[SWP4 §2.3.1]`).
- 2.0.1: identyfikator ma typ `identifierString`, **bez znaku `:`** (bo jest nazwą użytkownika Basic Auth, a `:` oddziela
  ją od hasła), **maks. 48 znaków**. Zalecane jest, by CSMS nie polegał wyłącznie na URL, tylko sprawdzał tożsamość
  względem danych uwierzytelniających (OCPP 2.0.1 część 4 §3.1.1 `[201-P4 §3.1.1]`).
- OCPP-J 1.6 §3.1.1 nie podaje limitu długości ani zakazu `:` `[J16 §3.1.1]`.

## Licencja
Dokumenty i schematy OCA są udostępniane na licencji **Creative Commons Attribution-NoDerivatives 4.0** (nota
w `[16]`, `[16E]`, `[J16E]`, `[SWP4]`, `[201-P0]` oraz w nagłówkach schematów `[21-P3]`). Wniosek dla repozytorium:
cytujemy fakty z atrybucją i numerem sekcji, nie publikujemy zmienionych wersji dokumentów ani schematów.
