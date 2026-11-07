# Dane rynkowe: infrastruktura, flota, struktura cen

Źródła: EIPA `[EIPA-STAT]` `[EIPA-OPIS]` `[EIPA-API]`, Eurostat `[ESTAT-EQR]` `[ESTAT-EQS]` `[ESTAT-ESMS]`, EAFO
`[EAFO-PL-PKT]` `[EAFO-EU-KAT]` `[EAFO-CENY]`, Bundesnetzagentur `[BNETZA-LIS]` `[BNETZA-LSR]`. Wszystkie to migawki z 7.11.2026.
Liczby podajesz zawsze z datą i źródłem, bo zbiory są aktualizowane. Zdania **Wniosek** to obliczenia i interpretacja.

## Spis treści
1. Polska: infrastruktura (EIPA, EAFO)
2. Polska i UE: flota i rejestracje (Eurostat)
3. UE: punkty według kategorii AFIR (EAFO)
4. Niemcy: rejestr BNetzA
5. Struktura cen ładowania (EAFO, dane z 2024 r.)
6. Rozbieżności między źródłami
7. Czego nie ma

## 1. Polska: infrastruktura (EIPA, EAFO)
Liczba punktów ładowania w EIPA na koniec roku `[EIPA-STAT]`:

| Data | Lokalizacje | Stacje | Punkty ładowania |
|---|---|---|---|
| 31.12.2021 | 1537 | 1883 | 3582 |
| 31.12.2022 | 2020 | 2514 | 4819 |
| 31.12.2023 | 3026 | 3721 | 7089 |
| 31.12.2024 | 4630 | 5573 | 10596 |
| 31.12.2025 | 6186 | 7427 | 14930 |
| 07.11.2026 | 6693 | 8297 | 16563 |

- EAFO, publicznie dostępne punkty według AFIR, Polska `[EAFO-PL-PKT]`:
  - 2025 Q4: 8398 AC i 6123 DC;
  - 2026 Q3: 8761 AC i 7131 DC.
- Model danych EIPA: baza (Charging Pool) → stacja → punkt → złącza. Dozorem UDT objęte są stacje. Ceny i metody
  płatności w EIPA są takie, jak dla użytkownika bez umowy `[EIPA-OPIS]`.
- API EIPA dla operatorów (REST 2.1): bazy, stacje, punkty, złącza, ceny, status punktu, słowniki metod płatności i
  uwierzytelnienia `[EIPA-API]`.

**Wniosek:** w latach 2021–2025 liczba punktów w EIPA wzrosła około 4,2 razy (z 3582 do 14930). Udział DC w punktach
EAFO wzrósł z 32% (2024 Q4: 3006 z 9555) do 45% (2026 Q3: 7131 z 15892).

## 2. Polska i UE: flota i rejestracje (Eurostat)
Samochody osobowe, kategoria napędu „Electricity” (`mot_nrg=ELC`) `[ESTAT-EQR]` `[ESTAT-EQS]`:

| Rok | Nowe ELC, PL | Nowe ogółem, PL | Flota ELC, PL | Nowe ELC, UE27 | Flota ELC, UE27 |
|---|---|---|---|---|---|
| 2021 | 7092 (i) | 450831 (i) | 18132 | 885038 | 1941460 |
| 2022 | 11293 (i) | 421565 | 30841 | 1129786 | 3015656 |
| 2023 | 17078 (i) | 477258 (i) | 51364 | 1547676 | 4434882 |
| 2024 | 16564 (i) | 554248 | 62182 | 1455122 | 5774179 |
| 2025 | 43311 (i) | 600504 | 102710 (i) | 1888016 | 7592725 |

- (i) oznacza wartość uzupełnioną przez Eurostat lub inną agencję. Według metadanych luki uzupełnia się danymi EAFO i
  ACEA `[ESTAT-ESMS]`.
- Hybrydy plug-in w PL w 2025 r., benzynowe i diesla razem: 33941 nowych (27619 i 6322) i 100245 we flocie (95233 i
  5012) `[ESTAT-EQR]` `[ESTAT-EQS]`.
- Definicji kategorii „Electricity” z glosariusza Eurostatu nie pobrano. Nie zakładasz z pamięci, że to dokładnie BEV.

**Wniosek:**
- udział kategorii ELC w nowych samochodach osobowych w 2025 r. wynosi w PL około 7,2% (43311 z 600504), a w UE27
  około 17,3% (1888016 z 10937447);
- cel AFIR z art. 3 ust. 1 (1,3 kW na BEV i 0,80 kW na PHEV) daje dla floty PL z 2025 r. około 133,5 MW plus około
  80,2 MW, razem około 214 MW mocy publicznej `[AFIR art. 3 ust. 1]`. To przybliżenie: Eurostat podaje tylko samochody
  osobowe, a AFIR mówi o pojazdach lekkich. Mocy zainstalowanej w PL baza nie zawiera, więc spełnienia celu nie da się
  tu sprawdzić.

## 3. UE: punkty według kategorii AFIR (EAFO)
Polska, wrzesień 2026 `[EAFO-EU-KAT]`:

| Kategoria | Liczba |
|---|---|
| AC < 7,4 kW | 246 |
| AC 7,4–22 kW | 8241 |
| AC > 22 kW | 274 |
| DC < 50 kW | 460 |
| DC 50–150 kW | 4196 |
| DC 150–350 kW | 1746 |
| DC ≥ 350 kW | 729 |

Plik zawiera te same kategorie dla wszystkich państw UE27, więc służy do porównań między krajami.

## 4. Niemcy: rejestr BNetzA
Stan na 1.09.2026 `[BNETZA-LIS]`:
- 119416 urządzeń ładowania, 214334 punkty (157762 zwykłe i 56572 szybkie);
- 13003 operatorów;
- skumulowana moc nominalna urządzeń około 9,38 GW;
- punkty > 299 kW: 20095; 149–299 kW: 21526.

Obowiązek zgłoszenia dotyczy publicznych punktów powyżej 3,7 kW uruchomionych od 17.03.2016. Punkty szybkie (> 22 kW)
są ujęte w całości `[BNETZA-LIS]`. Dane mają licencję CC BY 4.0 z uznaniem autorstwa „Bundesnetzagentur.de”
`[BNETZA-KARTE]`.

**Metody płatności i klucze publiczne (lista BNetzA z 1.09.2026)** `[BNETZA-LSR]`:
- lista ma 116443 urządzenia, w tym 85288 zwykłych i 31155 szybkich. Obejmuje tylko operatorów z zakończoną procedurą
  zgłoszenia, więc jest mniejsza niż zestawienie (119416);
- metody płatności (kolumna `Bezahlsysteme`) według mocy nominalnej urządzenia i daty uruchomienia (liczby policzone
  z pliku):

| Grupa | Urządzenia | Z kartą (NFC albo czytnik, kredytowa albo debetowa) | Z Plug & Charge |
|---|---|---|---|
| ≥ 50 kW, uruchomione od 13.04.2024 | 15735 | 15069 (95,8%) | 2569 (16,3%) |
| ≥ 50 kW, uruchomione przed 13.04.2024 | 15771 | 4428 (28,1%) | 1161 (7,4%) |
| < 50 kW, uruchomione od 13.04.2024 | 27593 | 7512 (27,2%) | 926 (3,4%) |

- 34924 urządzenia (30,0%) mają klucz publiczny licznika co najmniej dla jednego punktu (kolumny `Public Key1…6`).

**Wniosek:** po 13.04.2024 (data stosowania AFIR) płatność kartą w nowych urządzeniach ≥ 50 kW stała się w Niemczech
prawie powszechna, a w urządzeniach < 50 kW dominują metody online i RFID. AFIR art. 5 ust. 1 dopuszcza poniżej 50 kW
także np. QR. Dane to deklaracje operatorów; rzeczywistej dostępności terminala lista nie potwierdza.

## 5. Struktura cen ładowania (EAFO, dane z 2024 r.)
- Składniki ceny ad hoc i eMSP według EAFO: energia (kWh), czas (minuty lub godziny podłączenia albo zajęcia miejsca),
  opłata stała za sesję, inne opłaty (roaming, kary za postój). W większości umów eMSP dochodzi abonament
  `[EAFO-CENY]`.
- Polska, stopień stosowania składników `[EAFO-CENY-CPO]` `[EAFO-CENY-MSP]`:
  - taryfy CPO ad hoc: ENERGY 82, FLAT 41, TIME 12;
  - taryfy eMSP: ENERGY 100, FLAT 56, TIME 41.

  Strona nie podaje jednostki; wartości mieszczą się w przedziale 0–100.
- Średni miesięczny abonament eMSP w Polsce: 9,4 `[EAFO-ABON]`. Jednostki w pliku nie podano.
- Dane pochodzą od Eco-Movement, ostatnia aktualizacja 16.01.2024. Tekst strony odwołuje się do „proponowanego”
  rozporządzenia AFIR `[EAFO-CENY]`.

**Wniosek:** to obraz rynku sprzed stosowania AFIR (13.04.2024). Do projektu cennika używasz go tylko jako tła. O
wymaganiach decyduje AFIR art. 5 (skill `ev-billing-tariff-expert`).

## 6. Rozbieżności między źródłami
- **Liczba punktów w PL na koniec 2025 r.:** EIPA podaje 14930 (31.12.2025) `[EIPA-STAT]`, a EAFO 14521 (2025 Q4:
  8398 AC i 6123 DC) `[EAFO-PL-PKT]`.
  **Rozstrzygnięcie:** w PL rejestrem ustawowym jest EIPA `[PL-EMOB art. 42]`, więc liczby krajowe bierzesz z EIPA.
  EAFO służy do porównań między państwami. Przyczyny różnicy (definicja punktu publicznie dostępnego, data
  odniesienia) źródła nie wyjaśniają.

## 7. Czego nie ma
- wykorzystanie stacji, przychody, CAPEX i OPEX;
- moc zainstalowana w PL;
- aktualne ceny (2026) według kraju;
- dane IEA (www.iea.org odpowiada 403);
- pełne dane EIPA dla czytelników (wymagają rejestracji konta);
- CEPiK (dane.gov.pl): nieprzejrzany.
