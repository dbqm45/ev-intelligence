# Do zrobienia później

Sprawy odłożone przez właściciela projektu. Stan na 2026-11-07. Po załatwieniu sprawy usuń wpis albo przenieś go do
historii w commicie.

## Decyzje właściciela
- **Konto czytelnika EIPA:** pełne dane EIPA (status i ceny punktów przez API odczytu) wymagają rejestracji konta
  e-mailem na eipa.udt.gov.pl. Bez zgody właściciela nie zakładamy konta. Po założeniu: pobrać dane, dodać je do
  `sources/pl-dane.yaml` i uzupełnić `skills/ev-product-designer/references/rynek-dane.md`.
- **Płatna ewaluacja na modelu:** tylko za zgodą (CLAUDE.md). Nowe scenariusze w ev-product-designer
  (`terminal-dostepnosc`, `liczba-punktow-pl`) nie mają jeszcze przebiegu.

- **Do sprawdzenia: ryzyko licencyjne eMIP przy `ev_confidential_check`.** Nawet werdykt „WYSTEPUJE” to minimalna
  informacja o protokole przekazana pytającemu, a seria pytań tak/nie może częściowo odtworzyć treść (limity: 10
  terminów na wywołanie, 30 na minutę). To interpretacja licencji Gireve (rozdz. 1.4 Confidentiality), nie opinia
  prawna. Przed użyciem przez osoby spoza organizacji albo komercyjnym: pisemne potwierdzenie Gireve albo opinia
  prawna; do tego czasu rozważyć wyłączenie narzędzia dla tokenów zewnętrznych.
- **eMIP (Gireve), poziom 2:** dziś `ev_confidential_check` sprawdza tylko występowanie nazw. Ocena zgodności całego
  opisu (werdykt i kategoria problemu bez treści) wymaga modelu po stronie serwera: klucz API, koszt, Twoja zgoda.
  Do rozważenia też pisemne potwierdzenie Gireve przy użyciu komercyjnym.

## Hosty, które nie działają
| Host | Objaw | Co daje | Co zrobić |
|---|---|---|---|
| `www.iea.org` | HTTP 403 mimo dodania do listy domen | IEA Global EV Outlook 2026 (raport CC BY 4.0, dane na licencji IEA innej niż CC) | sprawdzić, czy blokuje automatyczne pobieranie; ewentualnie pobrać ręcznie i podać plik |
| `www.ochp.eu` | połączenie resetowane mimo dodania do listy | strona OCHP; specyfikacja jest już z GitHuba | prawdopodobnie strona nieczynna; nic nie robić |
| `commission.europa.eu` | połączenie odrzucone przez proxy | nota prawna Komisji: warunki ponownego wykorzystania danych Eurostatu i EAFO | dodać host; potem zastąpić „[niesprawdzone]” w `sources/eu-dane.yaml` |

Pełna lista zablokowanych hostów: `sources/niedostepne.yaml`, sekcja `hosty_zablokowane`.

## Źródła do przejrzenia (hosty działają)
- **Gireve OCPI 2.2.1 Implementation Guide V1.6** (www.gireve.com/download/): zasady Gireve jako huba OCPI. Licencji w
  dokumencie nie znaleziono; pobrany, nieopracowany.
- **Hubject Dynamic Pricing — Functional Guide** (support.hubject.com) i dokumentacja OpenAPI OICP 2.3.
- **CEPiK w dane.gov.pl:** rejestracje pojazdów w PL, dokładniejsze niż Eurostat (część wartości Eurostatu dla PL ma
  flagę „i”, czyli jest uzupełniona z innych źródeł).
- **Specyfikacja usługi sieciowej EIPA w BIP UDT** (art. 42 ust. 9 ustawy o elektromobilności): na bip.udt.gov.pl nie
  znaleziono. Na razie zostaje `EIPA-API` z eipa.udt.gov.pl.
- **Glosariusz Eurostatu:** definicja kategorii „Electricity” (czy to dokładnie BEV).
- **Instrukcja obsługi EIPA** (EIPA-instrukcja-obslugi-1205.pdf): pobrana, ale jeszcze nieprzejrzana.
- **EAFO:** pozostałe pliki CSV dla PL (wzrost, punkty DC, HDV). Przy pierwszym pobraniu serwer zwrócił 429, więc
  trzeba je pobierać z odstępami.
