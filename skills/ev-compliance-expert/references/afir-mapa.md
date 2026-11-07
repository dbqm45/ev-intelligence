# AFIR: mapa obowiązków według adresata

Źródło: AFIR, wersja skonsolidowana `[AFIR]`, rozporządzenie wykonawcze 2025/655 `[AFIR-655]`. Ten plik kieruje do
szczegółów w innych skillach; nie powtarza ich treści. Zdania **Wniosek** to interpretacja.

## Państwa członkowskie
- Cele mocy dla pojazdów lekkich, liczone na koniec każdego roku od 2024: co najmniej 1,3 kW na zarejestrowany pojazd
  BEV i 0,80 kW na PHEV z publicznie dostępnych stacji `[AFIR art. 3 ust. 1]`.
- Sieć TEN-T, pule w każdym kierunku co najwyżej co 60 km `[AFIR art. 3 ust. 4]`:
  - sieć bazowa: do 31.12.2025 pula ≥ 400 kW z punktem ≥ 150 kW; do 31.12.2027 ≥ 600 kW z dwoma punktami ≥ 150 kW;
  - sieć kompleksowa: do 31.12.2027 na co najmniej 50% długości ≥ 300 kW z punktem ≥ 150 kW; do 31.12.2030 ≥ 300 kW;
    do 31.12.2035 ≥ 600 kW z dwoma punktami ≥ 150 kW.
- Ramy krajowe (art. 14), sprawozdania i ocena elastyczności oraz ładowania dwukierunkowego (art. 15): skill
  `ev-energy-smart-charging-expert`.

## Operatorzy punktów ładowania `[AFIR art. 5]`
| Obowiązek | Przepis | Szczegóły w skillu |
|---|---|---|
| ładowanie ad hoc, terminal płatniczy, rezygnacja z automatycznego uwierzytelnienia | ust. 1–2 | `ev-billing-tariff-expert`, `ev-evse-hardware-expert` |
| ceny rozsądne, porównywalne, niedyskryminujące; ≥ 50 kW za kWh i ewentualnie za minutę; kolejność składników < 50 kW | ust. 3–4 | `ev-billing-tariff-expert` |
| punkty „digitally-connected” od 14.10.2024; smart recharging dla nowych i odnowionych | ust. 7–8 | `ev-energy-smart-charging-expert` |
| kabel stały na publicznych punktach DC od 14.04.2025 | ust. 10 | `ev-evse-hardware-expert` |

## Dostawcy usług mobilności (MSP)
Ceny rozsądne, przejrzyste i niedyskryminujące; przed sesją wszystkie składniki ceny z kosztami e-roamingu; bez
dodatkowych opłat za transgraniczny e-roaming `[AFIR art. 5 ust. 5]`.

## Dane dla NAP
Dane statyczne i dynamiczne bezpłatnie przez API `[AFIR art. 20]`; częstotliwość aktualizacji: statyczne do 24 h,
dynamiczne do 1 minuty `[AFIR-655 art. 2]`. Projekt publikacji: skill `ev-cpms-architect`.

## Wymagania techniczne
Złącza, ISO 15118 z datami, kategorie pojazdów `[AFIR Annex II]`: skill `ev-evse-hardware-expert`. Normy, do których
odsyła aneks II, są płatne (`sources/niedostepne.yaml`).

## Relacja z prawem krajowym
- AFIR uchylił dyrektywę 2014/94/UE od 13.04.2024; odesłania do dyrektywy czyta się jako odesłania do AFIR
  `[AFIR art. 25]`.
- **Wniosek:** krajowe przepisy wdrażające dawną dyrektywę (np. polska ustawa o elektromobilności) zostają w mocy, ale
  tam, gdzie AFIR reguluje to samo (np. częstotliwość danych), stosujesz AFIR jako rozporządzenie stosowane
  bezpośrednio. Przykład rozbieżności: `prawo-pl.md`, sekcja 9.
