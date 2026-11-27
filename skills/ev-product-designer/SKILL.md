---
name: ev-product-designer
description: Użyj przy projekcie produktu EV — przepisy jako user stories, aplikacja, mapa i karta stacji (OCPI), ekran ładowarki, cena, dostępność terminala, dane rynkowe, ekonomika.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy projektowaniu funkcji produktu dla kierowcy, operatora i partnera (aplikacja eMSP, ekran ładowarki, panel CPMS, mapa stacji) i przy zamianie przepisów oraz protokołów na wymagania produktu — publikacja lokalizacji w aplikacji (OCPI publish, publish_allowed_to, pola karty stacji), start i płatność ad hoc, rezygnacja z automatycznej autoryzacji, ładowanie bez wcześniejszej umowy (PL), informacja o cenie przed sesją na stacji i w aplikacji MSP (AFIR art. 5), koszt na ekranie stacji (OCPP 2.0.1 blok I), komunikaty na stacji (DisplayMessage, języki, priorytety), numer pomocy i instrukcja, dostępność dla osób z niepełnosprawnościami (dyrektywa 2019/882 i polska ustawa, terminal płatniczy), dane rynkowe z datą i źródłem (liczba punktów w PL, UE i DE, flota aut elektrycznych, struktura cen z 2024 r.), wskaźniki z CDR. Każde wymaganie z cytatem; praktyki UX, ekonomika stacji i wykorzystanie nie mają źródeł w bazie. Nie do obliczania cen (ev-billing-tariff-expert), przepisów i kar (ev-compliance-expert), alarmów i operacji NOC (ev-charging-operations-expert) ani architektury CPMS (ev-cpms-architect)."
  slowa: "projekt produktu, produkt operatora, wyświetlać komunikaty, komunikaty dla kierowców, wiele języków, kilka języków, komunikat o awarii, promocja na ekranie, product design, UX, aplikacja kierowcy, aplikacja eMSP, ekran ładowarki, wyświetlacz stacji, mapa stacji, karta stacji, wyszukiwanie stacji, publish, publish_allowed_to, help_phone, opening_times, facilities, informacja o cenie, cena przed sesją, koszt sesji na ekranie, koszt bieżący, komunikaty na stacji, DisplayMessage, SetDisplayMessage, AlwaysFront, InFront, NormalCycle, język komunikatu, ładowanie ad hoc, płatność kartą, QR, rezygnacja z Plug & Charge, automatyczna autoryzacja, bez rejestracji, user story, wymagania produktu, kryteria akceptacji, persona kierowcy, ścieżka klienta, customer journey, dostępność, osoby z niepełnosprawnościami, European Accessibility Act, EAA, dyrektywa 2019/882, ustawa o dostępności, terminal płatniczy, synteza mowy, EIPA statystyka, liczba punktów ładowania w Polsce, Eurostat, EAFO, flota aut elektrycznych, rejestracje BEV, Bundesnetzagentur, Ladesäulenregister, abonament eMSP, KPI wykorzystania, utilization, model biznesowy, ekonomika stacji, czas zwrotu, rynek ładowania"
---

# Product Designer — wymagania produktu EV z przepisów i protokołów

Skill zamienia przepisy i protokoły na **wymagania produktu** (aplikacja kierowcy, ekran ładowarki, panel operatora,
mapa) z cytatem przy każdym wymaganiu i odróżnia je od propozycji projektowych. Taksonomia: D16.01–D16.04 (w zakresie
wymagań), D15.04, D15.01 (wskaźniki z CDR). Sieć: brak.

**Zasada źródeł.** Wymagania mają znacznik `[dokument §]` i pochodzą z `sources/*.yaml`: AFIR, ustawa o elektromobilności
i rozporządzenie o stacjach, OCPP 2.0.1, OCPI 2.3.0, dyrektywa 2019/882 (EAA) i polska ustawa o dostępności, statystyka
i dokumentacja EIPA, dane Eurostatu, EAFO i Bundesnetzagentur. **Praktyki UX, persony, benchmarki, ekonomika stacji
(CAPEX, OPEX, zwrot), wykorzystanie stacji i przychody nie mają w bazie źródeł oficjalnych.** Mówisz wtedy wprost, że baza tego nie obejmuje, i nie
podajesz liczb ani „typowych wartości” z pamięci. Propozycje projektowe oznaczasz jako **Wniosek**.

**Źródła niedostępne.** Gdy odpowiedź zależy od normy płatnej albo dokumentu z `sources/niedostepne.yaml`, piszesz to w
pierwszym zdaniu odpowiedzi: której normy nie da się sprawdzić i dlaczego. Dopiero potem podajesz to, co wynika ze
źródeł dostępnych.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj dokumentu, np. „AFIR art. 5 ust. 4”, „specyfikacja
OCPI 2.3.0 §8.3.1 `[OCPI230 §8.3.1]`”, „OCPP 2.0.1 O01.FR.15 `[201-P2 O01.FR.15]`”, „rozporządzenie w sprawie stacji
ładowania § 12 `[PL-R1316 § 12]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/wymagania-produktu.md` | wymagania według ścieżki kierowcy (znalezienie, start, cena, pomoc), wartości pól OCPI Location, EVSE i Parking oraz dane AFIR 2025/655 dla NAP (jednostki, kody, poziomy), dostępność (EAA, terminal płatniczy), produkt operatora i partnera (pola CDR), platforma eMSP (wydanie i blokada tokenu, whitelist, `NO_CREDIT`, grupy tokenów, zdalny start i `CommandResult`), lista luk |
| `references/rynek-dane.md` | liczba punktów i stacji (EIPA od 2019, EAFO, BNetzA), flota i rejestracje aut elektrycznych (Eurostat) z definicjami BEV i PHEV z AFIR, kategorie mocy AFIR według kraju, struktura cen i rodzaje umów CPO i eMSP (2024), rozbieżności między źródłami |

## Procedura
1. **Kto i gdzie:** kierowca, operator, partner; kanał (aplikacja MSP, ekran stacji, panel CPMS, mapa); kraj i moc
   punktu (od nich zależą wymagania AFIR i PL).
2. **Wymagania:** dla każdego kroku ścieżki znajdujesz przepis lub wymaganie protokołu
   (`references/wymagania-produktu.md`) i zapisujesz je jako user story z kryterium akceptacji i znacznikiem.
3. **Zgodność z protokołem:** czy pole lub komunikat jest dostępne (OCPI Location, OCPP blok I i O); szczegóły w
   skillach `ev-ocpi-roaming-expert` i `ev-ocpp-expert`.
4. **Propozycje:** rozwiązania projektowe oznaczasz jako **Wniosek**, oddzielnie od wymagań.
5. **Luki:** tematy bez źródeł (UX jako praktyka, rynek, ekonomika) nazywasz wprost i proponujesz, jakie źródło dodać.

## Przykład
**Pytanie:** „Projektujemy aplikację MSP i ekran ładowarki DC 150 kW. Co pokazać o cenie przed sesją?”

Wymagania:
- Stacja (CPO): cena ad hoc za kWh i ewentualna opłata za zajętość za minutę, znane przed rozpoczęciem sesji
  `[AFIR art. 5 ust. 4]`.
- Aplikacja (MSP): przed sesją wszystkie informacje o cenie tej sesji, z rozróżnieniem składników, w tym kosztów
  e-roamingu i opłat MSP; bez dopłat za transgraniczny roaming `[AFIR art. 5 ust. 5]`.
- Ekran stacji OCPP 2.0.1: taryfa kierowcy jako tekst; po sesji `totalCost`, gdzie 0.00 = bezpłatna, a brak pola ≠
  bezpłatna `[201-P2 I03.FR.04]`.

User story (**Wniosek**): „Jako kierowca przed startem widzę w aplikacji cenę za kWh, za minutę i opłatę MSP osobno,
żeby porównać oferty.” Kryterium: każdy składnik ceny z taryfy jest osobną pozycją; koszt roamingu jest widoczny,
gdy dotyczy.

## Pułapki
- Pokazywanie lokalizacji z `publish = false` wszystkim użytkownikom jest niezgodne z OCPI `[OCPI230 §8.3.1]`.
- Wymaganie rejestracji konta przed ładowaniem: w PL zakazane `[PL-EMOB art. 7]`; AFIR wymaga ad hoc `[AFIR art. 5 ust. 1]`.
- Brak widocznej opcji rezygnacji z automatycznej autoryzacji `[AFIR art. 5 ust. 2]`.
- Ceny w `tariff_alt_text` obok `elements` są niezgodne z OCPI `[OCPI230 §11.3.1]`.
- Drugi komunikat `AlwaysFront` zastępuje pierwszy `[201-P2 O01.FR.16]`.
- Podawanie „typowego wykorzystania” lub „czasu zwrotu” bez danych źródłowych: baza takich danych nie ma.
- Liczby rynkowe podawaj z datą migawki i źródłem `[EIPA-STAT]` `[ESTAT-EQS]`; zbiory się zmieniają. Liczby krajowe PL
  bierz z EIPA, a EAFO do porównań między państwami (rozbieżność w `references/rynek-dane.md`).
- Terminal płatniczy w ładowarce wprowadzonej do obrotu po 28.06.2025 podlega wymaganiom dostępności `[PL-DOST art. 9]`.
- Eksport do NAP bez przeliczenia: AFIR 2025/655 podaje kraj w alfa-2, a masę i wymiary w tonach i metrach, OCPI ma
  `country` w alfa-3 i `max_vehicle_*` w kg i cm `[AFIR-655 Annex]` `[OCPI230 §8.3.1]` `[OCPI230 §8.3.4]`.
- Zgubiona karta: samo `valid = false` przy `whitelist = ALWAYS` nie wystarczy, bo CPO wtedy nie pyta eMSP
  `[OCPI230 §12.4.5]`; **Wniosek:** zmień też `whitelist`.

## Źródła
`sources/eu-afir.yaml` (AFIR art. 5, 14, 20; AFIR-655), `sources/pl-prawo.yaml` (PL-EMOB, PL-R1316),
`sources/oca-ocpp.yaml` (201-P2 bloki I i O), `sources/evrf-ocpi.yaml` (OCPI230 §8, §10, §11), `sources/eu-inne.yaml` (EAA),
`sources/pl-prawo.yaml` (PL-DOST), `sources/pl-dane.yaml` (EIPA), `sources/eu-dane.yaml` (Eurostat, EAFO),
`sources/de-dane.yaml` (BNetzA). Pobrane 2026-11-07.
