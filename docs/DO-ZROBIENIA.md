# Do zrobienia później

Sprawy odłożone przez właściciela projektu. Stan na 2026-11-08. Po załatwieniu sprawy usuń wpis albo przenieś go do
historii w commicie.

## Decyzje właściciela
- **Konto czytelnika EIPA:** pełne dane EIPA (status i ceny punktów przez API odczytu) wymagają rejestracji konta
  e-mailem na eipa.udt.gov.pl. Bez zgody właściciela nie zakładamy konta. Po założeniu: pobrać dane, dodać je do
  `sources/pl-dane.yaml` i uzupełnić `skills/ev-product-designer/references/rynek-dane.md`.
- **Płatna ewaluacja na modelu:** tylko za zgodą (CLAUDE.md). Przebiegi Opus 5.5 z 2026-11-07/08 objęły wszystkie
  13 skilli (`docs/evals/`).
- **Do sprawdzenia: ryzyko licencyjne eMIP przy `ev_confidential_check`.** Nawet werdykt „WYSTEPUJE” to minimalna
  informacja o protokole przekazana pytającemu, a seria pytań tak/nie może częściowo odtworzyć treść (limity: 10
  terminów na wywołanie, 30 na minutę). To interpretacja licencji Gireve (rozdz. 1.4 Confidentiality), nie opinia
  prawna. Przed użyciem przez osoby spoza organizacji albo komercyjnym: pisemne potwierdzenie Gireve albo opinia
  prawna; do tego czasu rozważyć wyłączenie narzędzia dla tokenów zewnętrznych.
- **eMIP (Gireve), poziom 2:** dziś `ev_confidential_check` sprawdza tylko występowanie nazw. Ocena zgodności całego
  opisu (werdykt i kategoria problemu bez treści) wymaga modelu po stronie serwera: klucz API, koszt, Twoja zgoda.
  Do rozważenia też pisemne potwierdzenie Gireve przy użyciu komercyjnym.
- **Tematy bez skilla w bazie** (z ewaluacji dev2 i taksonomii 1.1.0, gdzie poddomena ma `skills: []`): wybór
  lokalizacji stacji (D17/D18), serwis terenowy (D07.04), obsługa kierowcy (D07.06), RODO historii ładowań, NIS2 i
  EN 18031 (RED), protokoły D01.08–D01.11 (CHAdeMO, OpenADR/OSCP, Modbus, standardy w przygotowaniu). Każdy wymaga
  najpierw źródeł oficjalnych w `sources/*.yaml`.

## Scalanie wiedzy z pack-ev (fabryka tf)
- **Stan i plan:** `todo/tf-pack-ev/README.md` i `STATUS.md`. Treść pack-ev (36 skilli `dom-ev-*`, skrypty, testy)
  leży w `todo/tf-pack-ev/zrodlo/` **bez cytatów i bez weryfikacji**: z niej bierzemy tylko temat, a fakt opracowujemy
  od nowa ze źródła z rejestru. Pilot `ev-ocpp-expert` i analizator logu: zrobione 2026-11-15.
- **Decyzje właściciela (2026-11-15):** bez nakładki fabryki i person w tym repozytorium; praktyka (P) trafia tu, gdy
  pasuje, a reszta zostaje w `todo/tf-pack-ev/` z adnotacją; zakres obejmuje **USA** (NEVI 23 CFR 680, NIST HB44 —
  źródła do rejestracji, taksonomia D12.06 do rozszerzenia); tematy bez skilla trafiają do istniejących `ev-*`.
- **Źródła do rejestracji przed dalszymi falami:** RED III, EPBD, NIS2, CRA, Data Act, RED DA 2022/30 i 2026/339,
  dyrektywa 2000/84/WE, zmiana MID 2026/706 (najpierw potwierdzić w EUR-Lex), OCMF (S.A.F.E. e.V.), RFC 6455, RODO,
  strony certyfikacji OCA 1.6/2.1 i OCTT, 23 CFR 680, NIST HB44; do `niedostepne.yaml`: SAE J1772, SAE J3400,
  IEC 62955. Szczegóły: `todo/tf-pack-ev/analiza/luki-podsumowanie.md`.
- **Do poprawy w bazie** (wykryte przy analizie): `sources/niedostepne.yaml` oznacza PSD2 jako niezarejestrowaną, choć
  `sources/eu-inne.yaml` ma wpis PSD2.

## Hosty, które nie działają
| Host | Objaw | Co daje | Co zrobić |
|---|---|---|---|
| `www.iea.org` | HTTP 403 mimo dodania do listy domen | IEA Global EV Outlook 2026 (raport CC BY 4.0, dane na licencji IEA innej niż CC) | sprawdzić, czy blokuje automatyczne pobieranie; ewentualnie pobrać ręcznie i podać plik |
| `www.ochp.eu` | połączenie resetowane mimo dodania do listy | strona OCHP; specyfikacja jest już z GitHuba | prawdopodobnie strona nieczynna; nic nie robić |
| `commission.europa.eu` | połączenie odrzucone przez proxy | nota prawna Komisji: warunki ponownego wykorzystania danych Eurostatu i EAFO | dodać host; potem zastąpić „[niesprawdzone]” w `sources/eu-dane.yaml` |

Pełna lista zablokowanych hostów: `sources/niedostepne.yaml`, sekcja `hosty_zablokowane`.

## Źródła do przejrzenia (hosty działają)
- **Płatności kartą (D09.03):** polska ustawa o usługach płatniczych (transpozycja PSD2 art. 75–76, isap.sejm.gov.pl),
  rozporządzenie delegowane (UE) 2018/389 (SCA, wyjątki dla terminali bezobsługowych), EUR-Lex. Dziś skill
  `ev-billing-tariff-expert` opiera blokadę środków tylko na PSD2; PCI DSS to norma branżowa (sprawdzić dostępność).
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
