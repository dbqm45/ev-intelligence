---
name: ev-energy-smart-charging-expert
description: Użyj przy smart charging i zarządzaniu mocą ładowania EV — profile OCPP, stack level, load balancing, limit przyłącza, EMS/DSO, OCPI ChargingProfiles, V2G, AFIR.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy projektowaniu i sprawdzaniu sterowania mocą ładowania — profile ładowania OCPP 1.6 i 2.0.1 (ChargePointMaxProfile / ChargingStationMaxProfile, TxDefaultProfile, TxProfile, ChargingStationExternalConstraints), rodzaje Absolute, Recurring, Relative, stack level i różnica wyboru profilu między wersjami, harmonogram złożony i GetCompositeSchedule, jednostki A i W, fazy i przeliczenie mocy na prąd, zachowanie offline i po restarcie, równoważenie w stacji, sterowanie centralne i Local Controller, limity zewnętrzne z EMS, HEMS i DSO (NotifyChargingLimit, LimitChangeSignificance), priorytet ładowania, moduł ChargingProfiles w OCPI 2.3.0 dla eMSP i SCSP, wymogi AFIR (smart recharging, punkt digitally-connected, ocena ładowania dwukierunkowego) i przegląd zmian OCPP 2.1 (V2X, DER). Każdy fakt z cytatem ze źródła oficjalnego. Nie do składni komunikatów OCPP i błędów RPC (ev-ocpp-expert), architektury modułów CPMS (ev-cpms-architect), wymagań sprzętowych AFIR i ISO 15118 w aneksie II (ev-evse-hardware-expert) ani taryf i wyceny (ev-billing-tariff-expert)."
  slowa: "smart charging, inteligentne ładowanie, zarządzanie mocą, load balancing, równoważenie obciążenia, DLM, dynamic load management, limit przyłącza, moc przyłączeniowa, ChargingProfile, SetChargingProfile, ClearChargingProfile, GetCompositeSchedule, composite schedule, harmonogram złożony, stackLevel, stack level, ChargePointMaxProfile, ChargingStationMaxProfile, TxDefaultProfile, TxProfile, ChargingStationExternalConstraints, Absolute, Recurring, Relative, chargingRateUnit, A czy W, numberPhases, phaseToUse, minChargingRate, przełączanie faz, Phases3to1, SmartChargingCtrlr, ProfileStackLevel, ChargeProfileMaxStackLevel, offline smart charging, Local Controller, kontroler lokalny, EMS, HEMS, DSO, OSD, limit zewnętrzny, NotifyChargingLimit, LimitChangeSignificance, chargingPriority, priorytet ładowania, OCPI ChargingProfiles, ActiveChargingProfile, SCSP, agregator, smart recharging AFIR, digitally-connected, V2G, V2X, ładowanie dwukierunkowe, bidirectional, DER, OCPP 2.1 blok Q, PV, magazyn energii, peak shaving"
---

# Energy & Smart Charging Expert — sterowanie mocą ładowania

Skill odpowiada, **ile mocy dostanie pojazd i kto o tym decyduje**: profile OCPP, ich łączenie, limity przyłącza,
sygnały zewnętrzne, profile z roamingu i wymogi AFIR. Taksonomia: D08.01–D08.03, D08.06 (przegląd). Sieć: brak.

**Zasada źródeł.** Fakty mają znacznik `[dokument §]` i pochodzą z `sources/*.yaml`: OCPP 1.6 i 2.0.1 (OCA), OCPI 2.3.0
(EVRF), AFIR (wersja skonsolidowana), OCPP 2.1 część 0. **ISO 15118 i IEC 61851 (płatne), protokoły sieci i budynku
(EEBUS, OpenADR, IEC 61850, Modbus), przyłączenie do sieci i rynek energii nie są opracowane.** Wtedy mówisz, czego
brakuje, i nie odpowiadasz z pamięci.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „OCPP 2.0.1 K01.FR.50
`[201-P2 K01.FR.50]`”, „OCPP 1.6 §3.13.6 `[16 §3.13.6]`”, „errata OCPP 1.6 §3.37 `[16E §3.37]`”, „specyfikacja OCPI
2.3.0 §14.3 `[OCPI230 §14.3]`”, „AFIR art. 5 ust. 8”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/profile-ocpp.md` | cele i rodzaje profili, stack level (1.6 vs 2.0.1), harmonogram złożony, A/W i fazy, zmiana i usuwanie, offline, zmienne, rozbieżności dokumentów |
| `references/sterowanie-i-topologie.md` | równoważenie w stacji, sterowanie centralne, Local Controller, limity zewnętrzne (EMS, DSO), wielu aktorów, priorytet, OCPI ChargingProfiles, AFIR, OCPP 2.1 |

## Procedura
1. **Kontekst:** wersja OCPP, AC czy DC, liczba EVSE i stacji na wspólnym przyłączu, kto ustala limity (CSMS, Local
   Controller, EMS/DSO, eMSP lub SCSP przez OCPI). Typ sterowania według OCPP `[201-P2 K §2]`.
2. **Profile:** cel i miejsce (`evseId` 0 czy EVSE), rodzaj (`Absolute`, `Recurring`, `Relative`), ważność, stack level.
   Wybór profilu zależy od wersji (`references/profile-ocpp.md`, sekcja 3).
3. **Wynik:** harmonogram złożony to minimum wiodących profili różnych celów; `TxProfile` zastępuje
   `TxDefaultProfile`; limit stacji dotyczy wszystkich EVSE łącznie `[201-P2 K §3.5]` `[16 §3.13.3]`. Sprawdzasz go
   przez `GetCompositeSchedule`.
4. **Jednostki i fazy:** `W` łącznie, `A` na fazę, domyślnie 3 fazy `[201-P2 K01.FR.49]` `[201-P2 K01.FR.50]`.
5. **Awaria łączności:** co stacja zrobi offline i po restarcie `[201-P2 K06.FR.02]` `[201-P2 K01.FR.27]`. Profil
   ograniczenia przyłącza ma być zapisany na stacji, a nie tylko wysyłany per transakcja.
6. **Inni aktorzy:** limity zewnętrzne, profile z OCPI, priorytety (`references/sterowanie-i-topologie.md`).
7. **Luki:** ISO 15118, protokoły sieci, prawo przyłączeniowe wymieniasz jako nieopracowane.

## Przykład
**Pytanie:** „10 ładowarek AC OCPP 2.0.1 na przyłączu 100 kW, CSMS steruje centralnie przez `TxProfile`. Co się stanie
przy utracie łączności?”

Fakty:
- Offline po otrzymaniu `TxProfile` stacja używa go do końca transakcji albo do jego wygaśnięcia `[201-P2 K06.FR.01]`.
- Offline przed transakcją: stacja używa dostępnych profili, np. `TxDefaultProfile` `[201-P2 K07.FR.01]`.
- **Bez żadnych profili stacja ładuje bez ograniczeń** `[201-P2 K06.FR.02]`.
- Profile są trwałe po restarcie `[201-P2 K01.FR.27]`. Po wygaśnięciu `TxProfile` stacja wraca do najniższego z
  `TxDefaultProfile` i `ChargingStationMaxProfile` `[201-P2 K02.FR.08]`.

**Wniosek:**
- każdej stacji zapisujesz trwały `ChargingStationMaxProfile` (`Absolute` albo `Recurring`, nie `Relative`
  `[201-P2 K01.FR.38]`) z bezpiecznym limitem, np. 100 kW / 10 stacji → 10 kW, w `A` dla AC: 10000 / (230 × 3) ≈ 14,5 A
  na fazę. To limit wszystkich EVSE stacji łącznie `[201-P2 K04.FR.05]`. `TxDefaultProfile` na EVSE 0 obowiązuje każde
  EVSE osobno `[201-P2 K01.FR.14]`, więc przy dwóch EVSE nie chroni przyłącza;
- `TxProfile` od CSMS rozdziela wtedy moc dynamicznie w granicach tego limitu;
- nie da się tym ustawić limitu wspólnego dla kilku stacji: `ChargingStationMaxProfile` dotyczy jednej stacji. Wspólny
  limit grupy offline wymaga Local Controllera albo zewnętrznego systemu przy przyłączu `[201-P2 K §2.3]`.

## Pułapki
- Wybór profilu w stosie różni się wersjami: w 2.0.1 liczy się profil z okresem zdefiniowanym w danej chwili, w 1.6
  najwyższy ważny `stackLevel` `[201-P2 K §3.5]` `[16 §3.13.2]`. Najwyższy profil 1.6 bez `duration` blokuje niższe na
  zawsze `[16E §3.7]`.
- `W` przy AC bez `numberPhases` oznacza 3 fazy. Auto jednofazowe dostanie wtedy około 1/3 mocy `[201-P2 K01.FR.49]`.
- CSMS nie może ustawić ani usunąć `ChargingStationExternalConstraints` `[201-P2 K01.FR.22]` `[201-P2 K10.FR.08]`
  `[201-E]`.
- Kilka stron wysyłających profile naraz daje minimum, czyli wolniejsze ładowanie niż potrzeba `[OCPI230 §14.1]`.
- Profil z OCPI dotyczy tylko sesji w toku i jest asynchroniczny: odpowiedź `ACCEPTED` od CPO nie znaczy, że EVSE go
  przyjęło `[OCPI230 §14.3]`.
- Nazwy zmiennych w wymaganiach 2.0.1 różnią się od Device Model (`RateUnit`, `NotifyChargingLimitWithSchedules`).
  W implementacji obowiązują nazwy z załącznika (`references/profile-ocpp.md`, sekcja 9).

## Źródła
`sources/oca-ocpp.yaml` (16 §3.13, §5.7, §5.16, §7.8–7.14, §9.4; 16E; S16; 201-P2 blok K; 201-APP §3.1.16; 201-CSV;
201-E; 21-P0), `sources/evrf-ocpi.yaml` (OCPI230 §14), `sources/eu-afir.yaml` (AFIR art. 2, 5, 14, 15). Pobrane
2026-11-07.
