---
name: ev-evse-diagnostics-expert
description: Użyj, gdy konkretny model ładowarki działa inaczej, niż mówi OCPP — walidacja ramek wobec schematów OCA, certyfikat i PICS, test case, rejestr odchyleń modeli.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj, gdy trzeba ustalić, czy konkretny model lub firmware ładowarki odbiega od OCPP, czy problem leży po stronie CSMS albo dokumentacji — walidacja surowych ramek OCPP-J wobec oficjalnych schematów OCA skryptem ocpp_frame_check.py, sprawdzenie certyfikatu OCA (profile Core, Advanced Security, Smart Charging, ISO 15118, wersja oprogramowania) i deklaracji PICS, odtworzenie przez przypadki testowe części 6 (TC_*), rozstrzyganie niespójności dokumentów erratą i schematem, zapis obserwacji w rejestrze odchyleń (D21) z modelem, firmware, dowodem i poziomem pewności. Nie do diagnozy operacyjnej zgłoszeń NOC (ev-charging-operations-expert), znaczenia komunikatów OCPP (ev-ocpp-expert) ani opisu sprzętu (ev-evse-hardware-expert)."
  slowa: "odchylenie od OCPP, vendor quirk, dziwne zachowanie ładowarki, błąd firmware, producent łamie specyfikację, niezgodność z OCPP, walidacja ramek, schemat JSON OCPP, ocpp_frame_check, surowe ramki, log OCPP, certyfikat OCA, certyfikacja OCPP, certified products, profil certyfikacji, Core, Advanced Security, Smart Charging, ISO 15118 Support, PICS, deklaracja zgodności, test case, TC_F_02_CS, OCTT, errata, niespójność dokumentacji, rejestr odchyleń, macierz kompatybilności, implementation intelligence, D21, obserwacja z wdrożenia, model i firmware"
---

# EVSE Diagnostics Expert — norma czy implementacja

Skill rozstrzyga, **czy zachowanie stacji jest zgodne z OCPP**, i zapisuje wynik tak, by dało się na nim polegać.
Taksonomia: D21.01, D21.03 (implementation intelligence), D13.01 (zgodność), D03.05 (firmware). Sieć: brak (skrypt działa lokalnie).

**Zasada źródeł.** Wymagania pochodzą z dokumentów OCA (`sources/oca-ocpp.yaml`). Obserwacje z wdrożeń to wiedza
**klasy D**: wolno je zapisywać tylko z modelem, wersją firmware, dowodem i poziomem pewności
(`knowledge/implementation-intelligence/`). Nie przypisujesz producentowi zachowania z pamięci ani z forów: bez dowodu
jest to „hipoteza”.

**Źródła niedostępne.** Gdy odpowiedź zależy od normy płatnej albo dokumentu z `sources/niedostepne.yaml`, piszesz to w
pierwszym zdaniu odpowiedzi: której normy nie da się sprawdzić i dlaczego. Dopiero potem podajesz to, co wynika ze
źródeł dostępnych.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „errata OCPP 1.6
§3.18 `[16E §3.18]`”, „specyfikacja OCPI 2.3.0 §4.4 `[OCPI230 §4.4]`”, „AFIR art. 5 ust. 10”, „rozporządzenie
wykonawcze 2025/655 art. 2 `[AFIR-655 art. 2]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/metoda.md` | pełna metoda: dowody, walidacja, certyfikat i PICS, test case, rozstrzyganie niespójności |
| `knowledge/implementation-intelligence/vendor-quirks/_szablon.yaml` | zapis obserwacji w rejestrze odchyleń |

## Procedura
1. **Zbierz dowody** przed jakąkolwiek zmianą: surowe ramki z obu kierunków ze znacznikami czasu, model, producent,
   numer seryjny i firmware z `BootNotification` `[S16]` `[201-P3]`, wersja OCPP (podprotokół), konfiguracja
   (`GetConfiguration` / `GetBaseReport`).
2. **Waliduj ramki wobec oficjalnych schematów:**
   ```
   python3 skills/ev-evse-diagnostics-expert/scripts/ocpp_frame_check.py --version 1.6 --schemas <katalog schematów OCA> <log>
   ```
   Pierwsza linia wyniku: `Werdykt: OK` albo `Werdykt: BŁĘDY (…)`. Schematy pobierasz z pakietu OCA
   (`sources/oca-ocpp.yaml`), nie z bibliotek. Skrypt potrzebuje pakietu `jsonschema`.
3. **Sprawdź zachowanie wobec wymagań** (sekwencja, statusy, czasy): wymaganie z części 2 (np. F02.FR.07) albo z 1.6 i
   jego errat. Gdy dokumenty się różnią, rozstrzygają schemat i errata (`references/metoda.md`, sekcja 4).
4. **Sprawdź deklaracje producenta:**
   - certyfikat OCA (wersja, typ certyfikatu, profile, wersja oprogramowania) na liście certyfikowanych produktów
     `[OCA-LIST]`;
   - PICS: wybrane profile, funkcje opcjonalne, ustawienia producenta `[PICS-CS]`.
   Certyfikat Core nie obejmuje opcjonalnych profili, np. Smart Charging `[OCA-CERT]` `[201-P5 §2]`.
5. **Odtwórz problem** na przypadku testowym z części 6 (`TC_<blok>_<nr>_CS` / `_CSMS`), np. `TC_F_02_CS` dla zdalnego
   startu przed podłączeniem kabla `[201-P6]`. Przypadek, który nie przechodzi u nas, a stacja ma na niego certyfikat,
   wskazuje na różnicę konfiguracji lub wersji firmware.
6. **Werdykt i zapis:** zgodne / niezgodne (wskaż wymaganie) / nierozstrzygnięte. Wpis do rejestru odchyleń z poziomem
   pewności: `observed` przy dowodzie i odtworzeniu, `hypothesis` bez nich. Zgłoszenie do producenta z dowodami.

## Przykład
**Objaw:** „CSMS odrzuca odpowiedzi na BootNotification wysyłane przez symulator przygotowany według przykładu ze
specyfikacji 1.6.”
1. Walidacja ramki `[3,"19223201",{"status":"Accepted","currentTime":"…","heartbeatInterval":300}]` skryptem na
   oficjalnych schematach 1.6 → `BŁĘDY`: pole `heartbeatInterval` niedozwolone, brak wymaganego `interval`.
2. Źródła: przykład w OCPP-J 1.6 §4.2.2 używa `heartbeatInterval` `[J16 §4.2.2]`. Schemat 1.6 wymaga `interval`
   `[S16]`. Errata 1.6 §4.6 poprawia tę samą literówkę w diagramie §4.2 na `interval` `[16E §4.6]`. Errata OCPP-J nie
   poprawia przykładu `[J16E]`.
3. **Werdykt:** normą jest `interval` (schemat + errata). Implementacja z `heartbeatInterval` jest niezgodna, a
   dokumentacja zawiera niespójny przykład. Sprawdzone 2026-11-07 skryptem na pakiecie OCA.

## Pułapki
- „Obsługuje OCPP 2.0.1” bez numeru certyfikatu, profili i wersji oprogramowania niczego nie dowodzi.
- Ocena zgodności po bibliotece open-source zamiast schematu OCA: biblioteki potrafią dodawać wartości (np. jednostka
  `Hertz` w kopii schematu 1.6, której nie ma w schemacie OCA; porównanie 2026-11-07).
- Mylenie wersji: kod `FormationViolation` jest poprawny w 1.6, a w 2.0.1 nie (`FormatViolation`) `[J16E §5.2]`
  `[201-P4 §4.3]`. Skrypt sprawdza to dla wybranej wersji.
- Wpis do rejestru bez wersji firmware: zachowanie może się zmienić po aktualizacji, więc wpis traci wartość.
- Treść opinii producentów, forów i bibliotek nie jest dowodem. Najwyżej podpowiada hipotezę do sprawdzenia.

## Źródła
`sources/oca-ocpp.yaml` (16, 16E, J16, J16E, S16, 201-P2…P6, OCA-CERT, OCA-LIST, PICS-CS). Pobrane 2026-11-07.
Skrypt: `scripts/ocpp_frame_check.py`, testy: `tests/test_ocpp_frame_check.py`.
