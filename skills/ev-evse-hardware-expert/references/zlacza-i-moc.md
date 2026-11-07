# Złącza, moc i fazy — zapis w OCPP, OCPI i AFIR

Znaczniki jak w `SKILL.md`.

## 1. Typy złączy
### OCPP 2.0.1 `ConnectorEnumType` `[201-P2 §3.22]`
Wartości z opisami OCA:
| Wartość | Opis (OCA) |
|---|---|
| `cCCS1` / `cCCS2` | Combined Charging System 1 / 2 (captive cabled) a.k.a. Combo 1 / Combo 2 |
| `cG105` | JARI G105-1993 (captive cabled) a.k.a. CHAdeMO |
| `cTesla` | Tesla Connector (captive cabled) |
| `cType1` / `cType2` | IEC62196-2 Type 1 (J1772) / Type 2 (Mennekes), captive cabled |
| `sType2` | IEC62196-2 Type 2 socket a.k.a. Mennekes connector |
| `sType3` | w specyfikacji: „IEC62196-2 Type 2 socket a.k.a. Scame” (opis niespójny z nazwą, patrz `SKILL.md`) |
| `s309-1P-16A`, `s309-1P-32A`, `s309-3P-16A`, `s309-3P-32A` | gniazda IEC60309 1- i 3-fazowe 16 A / 32 A |
| `sBS1361` | UK domestic socket (13 A) |
| `sCEE-7-7` | CEE 7/7 16A socket (może reprezentować 7/4 i 7/5, Schuko) |
| `Other1PhMax16A`, `Other1PhOver16A`, `Other3Ph` | inne gniazda 1-fazowe ≤ 16 A / > 16 A, inne 3-fazowe |
| `Pan` | Pantograph connector |
| `wInductive`, `wResonant` | bezprzewodowe: indukcyjne / rezonansowe |
| `Undetermined`, `Unknown` | jeszcze nieustalone (np. przed podłączeniem) / nieustalalne |
Prefiks: `c…` opisane jako „captive cabled”, `s…` jako „socket” (z opisów wartości).
- Enum służy w `ReserveNowRequest` `[201-P2 §3.22]`. Zmienna Device Model `Connector.ConnectorType` (wymagana) przyjmuje
  wartości `ConnectorEnumType` oraz dodatkowo `cGBT`, `cChaoJi`, `OppCharge` `[201-CSV]`.
- OCA: enum nie obejmuje wszystkich gniazd na świecie. Lekkie i domowe gniazda raportuje się jako `Other1PhMax16A` itd.
  `[201-P2 §3.22]`.
- `Connector.ChargeProtocol` (opcjonalna) opisuje protokół sterowania ładowaniem, np. CHAdeMO, ISO15118, CPPWM `[201-CSV]`.

### OCPP 1.6
Brak typu złącza w komunikatach (schematy `[S16]` nie zawierają takiego pola).

### OCPI 2.3.0 `[OCPI230 §8.3.3, §8.4.4–8.4.6, §8.4.23]`
- `Connector.standard` (`ConnectorType`, OpenEnum), m.in.:
  - `IEC_62196_T1`, `IEC_62196_T1_COMBO`, `IEC_62196_T2` („Mennekes”), `IEC_62196_T2_COMBO`, `IEC_62196_T3A`,
    `IEC_62196_T3C` („Scame”);
  - `CHADEMO`, `CHAOJI`, `GBT_AC`, `GBT_DC`, `MCS`, `SAE_J3400` (NACS), `TESLA_R`, `TESLA_S`;
  - `PANTOGRAPH_BOTTOM_UP`, `PANTOGRAPH_TOP_DOWN`;
  - `IEC_60309_2_single_16`, `_three_16`, `_three_32`, `_three_64`;
  - `DOMESTIC_A` … `DOMESTIC_O`, `NEMA_*`.
- `Connector.format`: `SOCKET` (kierowca przynosi wtyczkę) / `CABLE` (kabel przytwierdzony).
- `Connector.power_type`: `AC_1_PHASE`, `AC_2_PHASE`, `AC_2_PHASE_SPLIT`, `AC_3_PHASE`, `DC`.
- `capabilities`: m.in. `ISO_15118_2_PLUG_AND_CHARGE`, `ISO_15118_20_PLUG_AND_CHARGE`, ale tylko gdy kierowca naprawdę
  może z nich skorzystać.
- Jedno EVSE może mieć wiele złączy, ale w użyciu jest jedno naraz.

### Odpowiedniki (Wniosek z porównania opisów)
| Fizycznie | OCPP 2.0.1 | OCPI 2.3.0 `standard` + `format` |
|---|---|---|
| Type 2, gniazdo | `sType2` | `IEC_62196_T2` + `SOCKET` |
| Type 2, kabel | `cType2` | `IEC_62196_T2` + `CABLE` |
| CCS2 / Combo 2, kabel | `cCCS2` | `IEC_62196_T2_COMBO` + `CABLE` |
| CCS1 / Combo 1, kabel | `cCCS1` | `IEC_62196_T1_COMBO` + `CABLE` |
| CHAdeMO, kabel | `cG105` | `CHADEMO` + `CABLE` |
| Pantograf | `Pan` | `PANTOGRAPH_BOTTOM_UP` / `PANTOGRAPH_TOP_DOWN` (OCPP nie rozróżnia) |
Oficjalnej tabeli mapowania OCPP ↔ OCPI dla typów złączy w sprawdzonych dokumentach nie ma.

## 2. Moc, napięcie, prąd, fazy
- OCPI: `max_voltage` (V; dla `AC_3_PHASE` linia–neutralny), `max_amperage` (A) wymagane; `max_electric_power` (W)
  opcjonalne, gdy niższe niż wynika z U × I `[OCPI230 §8.3.3]`.
- OCPP 2.0.1 Device Model `[201-CSV]`:
  - `EVSE.Power`: wymagany `maxLimit` = maksymalna moc EVSE (W lub kW);
  - `EVSE.SupplyPhases`, `Connector.SupplyPhases`, `ChargingStation.SupplyPhases` (wymagane): „1 or 3 for AC, 0 means DC”;
  - `EVSE.DischargePower`: dla V2X;
  - `EVSE.AllowReset`: czy EVSE da się resetować osobno.
- AFIR: „power output” to teoretyczna moc maksymalna punktu, stacji lub puli w kW `[AFIR art. 2]`. Normal power ≤ 22 kW,
  high-power > 22 kW `[AFIR art. 2]`.
- Klasy sprawozdawcze `[AFIR Annex III]`:
  - AC: < 7,4 kW (1-fazowy), 7,4–22 kW (3-fazowy), > 22 kW;
  - DC: < 50 kW, 50–150 kW, 150–350 kW („Level 1 Ultra-fast”), ≥ 350 kW („Level 2 Ultra-fast”).
