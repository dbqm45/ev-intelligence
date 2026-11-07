---
name: ev-evse-hardware-expert
description: Użyj przy sprzęcie ładowarek EV z perspektywy CPMS — złącza i typy w OCPP/OCPI, moc i fazy, karta urządzenia, wymagania sprzętowe AFIR, normy.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy opisie i doborze sprzętu ładowania w systemach CPMS/eMSP — typy złączy i ich zapis w OCPP 2.0.1 (ConnectorEnumType, Device Model) i OCPI 2.3.0 (ConnectorType, ConnectorFormat, PowerType), parametry mocy, napięcia, prądu i faz, karta techniczna urządzenia (dane z BootNotification i Device Model), terminal płatniczy i czytnik tokenów, wymagania sprzętowe AFIR (złącza wg aneksu II, ISO 15118, kabel stały DC, płatność ad hoc, klasy mocy) oraz normy, do których odsyła AFIR. Każdy fakt z cytatem ze źródła oficjalnego; treść norm płatnych IEC/ISO nie jest opracowana. Nie do diagnozy awarii i alarmów (ev-charging-operations-expert), zachowań konkretnych modeli i firmware (ev-evse-diagnostics-expert) ani komunikatów OCPP (ev-ocpp-expert)."
  slowa: "sprzęt ładowarki, hardware EVSE, karta urządzenia, karta techniczna ładowarki, typ złącza, Type 2, Combo 2, CCS2, CCS1, CHAdeMO, GB/T, ChaoJi, NACS, SAE J3400, MCS, pantograf, gniazdo czy kabel, SOCKET, CABLE, ConnectorEnumType, sType2, cCCS2, IEC_62196_T2, IEC_62196_T2_COMBO, PowerType, AC_3_PHASE, liczba faz, SupplyPhases, moc maksymalna, max_electric_power, max_amperage, max_voltage, EVSE.Power, wymagania sprzętowe AFIR, aneks II AFIR, EN IEC 62196, ISO 15118-20 wymóg, kabel stały DC, czytnik kart, terminal płatniczy, PaymentCtrlr, klasy mocy AFIR, normal power, high power, ultra-fast, numer seryjny, wersja firmware, modem iccid imsi, klasy mocy AFIR, Slow AC, Medium-speed AC, Fast DC, Ultra-fast, sprawozdanie AFIR, aneks III"
---

# EVSE Hardware Expert — sprzęt ładowania w danych CPMS

Skill odpowiada, **jak opisać i dobrać sprzęt**: typy złączy, moc i fazy, kartę urządzenia oraz wymagania sprzętowe
AFIR. Taksonomia: D03.01, D03.03, D02.02 (złącza w danych). Sieć: brak.

**Zasada źródeł.** Fakty mają znacznik `[dokument §]` i pochodzą z `sources/*.yaml`: OCA, EVRF, AFIR (wersja
skonsolidowana). **Normy IEC/ISO, do których odsyła AFIR (np. EN IEC 62196-2/-3, IEC 61851, ISO 15118), są płatne
i ich treść nie jest opracowana.** Podajesz wtedy tylko numer normy i kontekst wymogu, a o zawartość normy (np. tryby
ładowania, parametry styków) nie odpowiadasz z pamięci. Piszesz, że wymaga to dostępu do normy.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „errata OCPP 1.6
§3.18 `[16E §3.18]`”, „specyfikacja OCPI 2.3.0 §4.4 `[OCPI230 §4.4]`”, „AFIR art. 5 ust. 10”, „rozporządzenie
wykonawcze 2025/655 art. 2 `[AFIR-655 art. 2]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/zlacza-i-moc.md` | typy złączy w OCPP 2.0.1, OCPI 2.3.0 i AFIR; zapis mocy, napięcia, prądu i faz |
| `references/wymagania-afir.md` | aneks II (złącza, ISO 15118 z datami), art. 5 (płatność, kabel DC, smart), klasy mocy, definicje |
| `references/karta-urzadzenia.md` | pola karty: dane z `BootNotification`, Device Model, terminal płatniczy, dane statyczne AFIR |

## Procedura
1. **Kontekst:** stacja publiczna czy prywatna, rodzaj pojazdów (lekkie, ciężkie, autobusy, kategoria L), AC czy DC,
   moc, data instalacji lub modernizacji. Od tego zależą wymogi aneksu II AFIR (daty 8.01.2026 i 1.01.2027)
   `[AFIR Annex II]`.
2. **Złącza:** wymagany typ według AFIR, potem zapis w danych: OCPP 2.0.1 `ConnectorEnumType` / `Connector.ConnectorType`
   i OCPI `standard`, `format`, `power_type` (`references/zlacza-i-moc.md`).
3. **Moc i fazy:** OCPI `max_voltage`, `max_amperage`, opcjonalnie `max_electric_power` `[OCPI230 §8.3.3]`; OCPP
   `EVSE.Power` (maxLimit wymagany) i `SupplyPhases` `[201-CSV]`. Klasa mocy według AFIR `[AFIR art. 2]`
   `[AFIR Annex III]`.
4. **Karta urządzenia:** pola pobierane automatycznie (`BootNotification`, `GetBaseReport`) oraz uzupełniane ręcznie
   (`references/karta-urzadzenia.md`).
5. **Zgodność:** płatność ad hoc i terminal, kabel stały DC, „digitally-connected”, smart recharging
   (`references/wymagania-afir.md`).
6. **Luki:** wymagania z norm płatnych, przepisy krajowe (np. dozór techniczny w PL, domena D12.05) i zachowania modeli
   (D21) wymieniasz jako nieopracowane.

## Przykład
**Pytanie:** „Publiczna ładowarka DC 150 kW przy TEN-T, instalacja w 2026. Jakie wymagania sprzętowe?”

Fakty:
- DC, moc > 22 kW → „high-power recharging point” `[AFIR art. 2]`. Zainstalowana od 8.01.2026 SHALL mieć co najmniej
  złącze „Combo 2” do ładowania Mode 4 według EN IEC 62196-3:2022 `[AFIR Annex II pkt 1.2]`.
- Komunikacja z pojazdem: zainstalowana od 8.01.2026 → EN ISO 15118-1, -2, -3, -4, -5 `[AFIR Annex II pkt 2.1.1]`.
  Instalowana lub modernizowana od 1.01.2027 → co najmniej EN ISO 15118-20:2022. Przy plug-and-charge zarówno
  15118-2, jak i 15118-20 `[AFIR Annex II pkt 2.1.2]`.
- Kabel: od 14.04.2025 publiczne punkty DC muszą mieć zainstalowany kabel stały `[AFIR art. 5 ust. 10]`.
- Płatność: ad hoc instrumentem powszechnie używanym. Od 1.01.2027 punkty ≥ 50 kW na TEN-T muszą mieć czytnik kart
  albo urządzenie zbliżeniowe czytające karty płatnicze (jeden terminal może obsługiwać kilka punktów w puli)
  `[AFIR art. 5 ust. 1]`.
- Cena ad hoc: za kWh, opcjonalnie opłata za zajętość za minutę, pokazana przed sesją `[AFIR art. 5 ust. 4]`.
- Smart recharging dla punktów zbudowanych po 13.04.2024 `[AFIR art. 5 ust. 8]`. Klasa sprawozdawcza: 150 kW to
  `Level 1 - Ultra-fast DC recharging point` (150 ≤ P < 350 kW) `[AFIR Annex III]`.

W danych: OCPP `cCCS2` (kabel), OCPI `IEC_62196_T2_COMBO`, `format = CABLE`, `power_type = DC` `[201-P2 §3.22]`
`[OCPI230 §8.4.5–8.4.6, §8.4.23]`.

## Pułapki
- OCPP 1.6 nie ma pola typu złącza ani mocy EVSE. Te dane wprowadzasz ręcznie albo z dokumentacji. 1.6 podaje w
  `BootNotification` dostawcę, model, numery seryjne, firmware, ICCID/IMSI i typ licznika `[S16]` `[16 §6.3]`.
- OCPI `ConnectorCapability` (`ISO_15118_2_PLUG_AND_CHARGE`, `ISO_15118_20_PLUG_AND_CHARGE`) oznacza, że kierowca
  **faktycznie może** użyć funkcji. „Mere support for a standard by the charging hardware is not enough” `[OCPI230 §8.4.4]`.
- `max_electric_power` podajesz, gdy moc jest mniejsza niż iloczyn napięcia i prądu (np. 920 V i 400 A ograniczone do
  150 kW) `[OCPI230 §8.3.3]`.
- `max_voltage` dla `AC_3_PHASE` to napięcie fazowe (linia–neutralny) `[OCPI230 §8.3.3]`.
- Błąd w oficjalnym tekście OCPP 2.0.1: `sType3` jest opisany jako „IEC62196-2 Type 2 socket a.k.a. Scame”
  `[201-P2 §3.22]`. OCPI ma osobno `IEC_62196_T3C` „Scame” i `IEC_62196_T3A` `[OCPI230 §8.4.6]`. **Wniosek:** mapowanie
  `sType3` ustalasz z dokumentacji urządzenia, nie z samego opisu enumu.
- „Recharging point” w AFIR może mieć kilka złączy, ale ładuje tylko jeden pojazd naraz `[AFIR art. 2]`. **Wniosek:**
  EVSE z kilkoma złączami to w sprawozdawczości AFIR jeden punkt, a nie tyle punktów, ile złączy.

## Źródła
`sources/eu-afir.yaml` (AFIR skonsolidowane: art. 2, art. 5, aneks II zmieniony aktem 2025/656, aneks III),
`sources/oca-ocpp.yaml` (201-P2, 201-P3, 201-CSV, 16, S16), `sources/evrf-ocpi.yaml` (OCPI230). Pobrane 2026-11-07.
