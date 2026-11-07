# Wymagania sprzętowe AFIR (wersja skonsolidowana 2026-01-08)

Źródło: `[AFIR]` z `sources/eu-afir.yaml`. Aneks II w zakresie złączy i ISO 15118 zmieniony rozporządzeniem delegowanym
(UE) 2025/656 (M1). Normy wymienione poniżej są płatne, a ich treści nie opracowano.

## 1. Złącza — aneks II pkt 1 (instalacja lub modernizacja od 8.01.2026)
„Installed” to pierwsze umieszczenie sprzętu, oprogramowania i infrastruktury elektrycznej. „Renovated” to poważna lub
całkowita wymiana sprzętu punktu `[AFIR Annex II pkt 0]`.

| Zastosowanie | Wymóg minimalny | Punkty sprzed 8.01.2026 |
|---|---|---|
| AC normal-power, lekkie pojazdy (pkt 1.1) | gniazda lub złącza Type 2 (Mode 3) wg EN IEC 62196-2:2022; ≤ 3,7 kW do Mode 2: gniazda wg IEC 60884-1:2022 | — |
| DC normal-power, lekkie (pkt 1.1) | Combo 2 (Mode 4) wg EN IEC 62196-3:2022 | EN IEC 62196-3:2014 do modernizacji |
| AC high-power, lekkie (pkt 1.2) | złącza Type 2 (Mode 3) wg EN IEC 62196-2:2022 | EN IEC 62196-2:2017 do modernizacji |
| DC high-power, lekkie (pkt 1.2) | Combo 2 (Mode 4) wg EN IEC 62196-3:2022 | EN IEC 62196-3:2014 do modernizacji |
| Kategoria L, AC ≤ 3,7 kW (pkt 1.3.1) | Type 3A wg EN IEC 62196-2:2022 (Mode 3) lub gniazda IEC 60884-1:2022 (Mode 1/2) | — |
| Kategoria L, AC > 3,7 kW (pkt 1.3.2) | Type 2 wg EN IEC 62196-2:2022 | EN IEC 62196-2:2017 |
| Kategoria L, DC (pkt 1.3.3) | Combo 2 wg EN IEC 62196-3:2022 | EN IEC 62196-3:2014 |
| Autobusy AC / DC (pkt 1.4) | Type 2 (EN IEC 62196-2:2022) / Combo 2 (EN IEC 62196-3:2022) | odpowiednio 2017 / 2014 |
| Autobusy, ACD w Mode 4 (pkt 1.5) | EN 61851-23-1:2020 z interfejsami wg EN 50696:2021 (pantograf na infrastrukturze, na dachu, pod pojazdem, z boku) | — |
| Ciężkie, DC high-power dla lekkich i ciężkich (pkt 1.6) | co najmniej Combo 2 wg EN IEC 62196-3:2022 | — |
| Ładowanie bezprzewodowe statyczne, lekkie (pkt 1.7) | EN IEC 61980-1:2021, -2:2023, -3:2022 | — |
Punkty 1.8–1.18 (m.in. ładowanie bezprzewodowe dynamiczne, wymiana baterii, dostępność dla osób z niepełnosprawnościami)
zawierają w tekście skonsolidowanym tylko tytuły, bez wymagań.

## 2. Komunikacja pojazd–punkt — aneks II pkt 2.1
- Publiczne punkty AC i DC (lekkie i ciężkie) instalowane lub modernizowane **od 8.01.2026**: co najmniej EN ISO
  15118-1:2019, -2:2016, -3:2016, -4:2019, -5:2019 (pkt 2.1.1).
- Publiczne **od 1.01.2027**: co najmniej EN ISO 15118-20:2022. Przy automatycznym uwierzytelnianiu (np.
  plug-and-charge) zarówno EN ISO 15118-2:2016, jak i 15118-20:2022 (pkt 2.1.2).
- Prywatne od 1.01.2027: EN IEC 61851-1:2019 (Mode 2) albo EN ISO 15118-20:2022 (Mode 3 lub 4) (pkt 2.1.3).
- Pkt 2.2–2.4 (komunikacja punkt–backend, operator–eMSP/roaming, operator–OSD) zawierają w tekście skonsolidowanym
  tylko tytuły. **AFIR nie wskazuje dziś normy dla OCPP ani OCPI.**

## 3. Wymagania z art. 5 dotyczące sprzętu
- Ad hoc i płatność: od 13.04.2024 instrument powszechnie używany, przez co najmniej jedno z: (a) czytnik kart,
  (b) urządzenie zbliżeniowe czytające karty, (c) dla < 50 kW np. kod QR. Od 1.01.2027 punkty ≥ 50 kW na TEN-T i w
  bezpiecznych parkingach, także starsze, muszą spełniać (a) albo (b). Jeden terminal może obsługiwać kilka punktów
  w puli. Wymogi nie dotyczą punktów bezpłatnych (ust. 1).
- Opcja odmowy automatycznego uwierzytelniania (ad hoc albo inna umowa) wyraźnie pokazana w punkcie (ust. 2).
- Ceny pokazywane na stacji przed sesją (ust. 4); szczegóły w `ev-cpms-architect`.
- „Digitally-connected” do 14.10.2024 (ust. 7). Definicja: wysyła i odbiera informacje w czasie rzeczywistym,
  komunikuje się dwukierunkowo z siecią i pojazdem, jest zdalnie monitorowany i sterowany, w tym start/stop i pomiar
  przepływu energii `[AFIR art. 2]`.
- Smart recharging dla zbudowanych po 13.04.2024 lub modernizowanych po 14.10.2024 (ust. 8). Definicja: natężenie
  dostarczanej energii dostosowywane w czasie rzeczywistym na podstawie informacji przekazywanych elektronicznie
  `[AFIR art. 2]`.
- **Kabel stały we wszystkich publicznych punktach DC do 14.04.2025** (ust. 10).
- Gdy operator nie jest właścicielem, właściciel udostępnia punkt o cechach technicznych pozwalających spełnić ust. 2, 7,
  8 i 10 (ust. 11).

## 4. Definicje (art. 2)
- „recharging point”: interfejs (stały lub mobilny, z siecią lub bez) mogący mieć kilka złączy, ale ładujący jeden
  pojazd naraz; z wyłączeniem urządzeń ≤ 3,7 kW o określonym głównym przeznaczeniu (pełna treść w art. 2).
- „recharging station”: instalacja w danym miejscu z jednym lub więcej punktów. „Recharging pool”: jedna lub więcej
  stacji w danym miejscu.
- „connector”: fizyczny interfejs między punktem a pojazdem.
- „normal power” ≤ 22 kW, „high-power” > 22 kW.
