# Złącza, moc i fazy — zapis w OCPP, OCPI i AFIR

Znaczniki jak w `SKILL.md`. Zdania **Wniosek** to rekomendacje wyprowadzone z cytowanych faktów.

## Spis treści
1. Typy złączy (OCPP 1.6, 2.0.1, 2.1; OCPI 2.2.1 i 2.3.0; odpowiedniki)
2. Moc, napięcie, prąd, fazy
3. Rozbieżności w dokumentach OCA

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
| `sType3` | w specyfikacji: „IEC62196-2 Type 2 socket a.k.a. Scame” (opis niespójny z nazwą, patrz §3) |
| `s309-1P-16A`, `s309-1P-32A`, `s309-3P-16A`, `s309-3P-32A` | gniazda IEC60309 1- i 3-fazowe 16 A / 32 A |
| `sBS1361` | UK domestic socket (13 A) |
| `sCEE-7-7` | CEE 7/7 16A socket (może reprezentować 7/4 i 7/5, Schuko) |
| `Other1PhMax16A`, `Other1PhOver16A`, `Other3Ph` | inne gniazda 1-fazowe ≤ 16 A / > 16 A, inne 3-fazowe |
| `Pan` | Pantograph connector |
| `wInductive`, `wResonant` | bezprzewodowe: indukcyjne / rezonansowe |
| `Undetermined`, `Unknown` | jeszcze nieustalone (np. przed podłączeniem) / nieustalalne |
Prefiks: `c…` opisane jako „captive cabled”, `s…` jako „socket” (z opisów wartości).
- Enum służy w `ReserveNowRequest` `[201-P2 §3.22]`. Zmienna Device Model `Connector.ConnectorType` (wymagana,
  `ReadOnly`, typ `string`) przyjmuje wartości `ConnectorEnumType` oraz dodatkowo `cGBT`, `cChaoJi`, `OppCharge`
  `[201-P2 §2.13.4]` `[201-CSV]`.
- `ConnectorType` jest „distinct and orthogonal to Charging Protocol, Power Type, Phases” `[201-APP §3.2.14]`. Protokół
  sterowania opisuje osobna zmienna `ChargeProtocol`: `CHAdeMO`, `ISO15118` („as used with CCS”), `CPPWM` (sygnalizacja
  po przewodzie Control Pilot), `Uncontrolled` (np. gniazdo Schuko), `Undetermined`, `Unknown` `[201-APP rozdz. 4]`.
- OCA: enum nie obejmuje wszystkich gniazd na świecie. Lekkie i domowe gniazda raportuje się jako `Other1PhMax16A` itd.
  `[201-P2 §3.22]`.
- Przykład OCA (stacja z dwoma EVSE): EVSE 1 ze złączem `sType2`, `SupplyPhases` = 3, `Power` maxLimit 22000; EVSE 2 ze
  złączami `cCCS2` i `cG105`, `SupplyPhases` = 0, `Power` maxLimit 50000 `[201-P2 §2.13.8]`.
- Nieznany typ w `ReserveNow`: kod przyczyny `UnknownConnectorType` („Connector type is not known on EVSE”)
  `[201-APP §5]` `[21-APP §5]`.

### OCPP 2.1 `ConnectorEnumStringType` `[21-APP §7.3]`
- W 2.1 to już nie enumeracja, tylko „predefined set of strings for more flexibility” `[21-APP §7.3]`. Pole
  `ReserveNowRequest.connectorType` ma typ `string[0..20]` z wartościami z tego aneksu `[21-P2 §1.69.1]`.
- Prefiksy zdefiniowane wprost: `c` = captive cabled, `s` = socket, `w` = wireless, `b` = battery (wymiana baterii)
  `[21-APP §7.3]`.
- Wartości nowe względem `ConnectorEnumType` 2.0.1 (opisy OCA):
| Wartość | Opis (OCA) |
|---|---|
| `bBatterySlot` | slot stacji wymiany baterii (typ nieokreślony) |
| `cChaoJi` | ChaoJi (captive cabled) a.k.a. CHAdeMO 3.0 |
| `cGBT-DC` | GB/T 20234.3 DC connector (captive cabled) |
| `cLECCS` | Light Equipment Combined Charging System IS17017 (captive cabled) |
| `cMCS` | Megawatt Charging System (captive cabled) |
| `cNACS` | North American Charging Standard J3400 (captive cabled) |
| `cNACS-CCS1` / `cCCS1-NACS` | wbudowany adapter NACS→CCS1 / CCS1→NACS (captive cabled) |
| `cUltraChaoJi` | Ultra-ChaoJi for megawatt charging (captive cabled) |
| `sType1` | IEC62196-2 Type 1 socket a.k.a. J1772 |
| `OppCharge` | Pantograph down connector |
- Zmienione opisy: `sType3` = „IEC62196-2 Type 3 socket a.k.a. Scame”, `Pan` = „Pantograph up connector”, `cG105` =
  „… a.k.a. CHAdeMO (captive cabled)” `[21-APP §7.3]`.
- Komponent `Connector` w 2.1 ma te same zmienne co w 2.0.1 (`ConnectorType`, `SupplyPhases`, `ChargeProtocol`…)
  `[21-APP §3.2.14]`.

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
- `TESLA_S`: „Mechanically compatible with SAE J3400 but uses CAN bus for communication instead of power line
  communication” `[OCPI230 §8.4.6]`.
- `Connector.format`: `SOCKET` (kierowca przynosi wtyczkę) / `CABLE` (kabel przytwierdzony).
- `Connector.power_type`: `AC_1_PHASE`, `AC_2_PHASE`, `AC_2_PHASE_SPLIT`, `AC_3_PHASE`, `DC`.
- `capabilities`: m.in. `ISO_15118_2_PLUG_AND_CHARGE`, `ISO_15118_20_PLUG_AND_CHARGE`, ale tylko gdy kierowca naprawdę
  może z nich skorzystać.
- Jedno EVSE może mieć wiele złączy, ale w użyciu jest jedno naraz.
- OpenEnum: zbiór wartości nie jest zamknięty. Wśród przykładów OCPI wprost podaje typy złączy: wspólne wartości dla
  popularnych typów i miejsce na nowe lub własne. Nazwy nowych wartości SHOULD stosować RFC 6648 i wytyczne EVRF
  „extending OCPI” `[OCPI230 §17.3]`. Rozszerzalność enumów to zmiana wprowadzona w 2.3.0 `[OCPI230 §18.1]`.
- W OCPI 2.3.0 nie ma wartości `ConnectorType` dla ładowania bezprzewodowego ani dla wymiany baterii (w tekście nie
  występuje „wireless” ani „inductive” w tym znaczeniu) `[OCPI230 §8.4.6]`.

### OCPI 2.2.1 — różnice `[OCPI221 §8.3.3, §8.4.5]`
- `ConnectorType` jest zwykłym „enum”, nie OpenEnum, i nie zawiera `MCS` ani `SAE_J3400` `[OCPI221 §8.4.5]`.
- Obiekt `Connector` nie ma pola `capabilities` (ani `ConnectorCapability`). Pola `standard`, `format`, `power_type`,
  `max_voltage`, `max_amperage`, `max_electric_power` są jak w 2.3.0 `[OCPI221 §8.3.3]`.
- NEMA, GB/T, ChaoJi i `DOMESTIC_M`–`O` oraz `AC_2_PHASE`, `AC_2_PHASE_SPLIT` doszły w 2.2.1 `[OCPI230 §18.3]`;
  `PANTOGRAPH_TOP_DOWN` i `PANTOGRAPH_BOTTOM_UP` już w 2.2 `[OCPI230 §18.4]`.
- **Wniosek:** jak przekazać złącze MCS lub NACS partnerowi na OCPI 2.2.1, specyfikacja 2.2.1 nie określa. Przed
  wysłaniem takiej lokalizacji ustal to z partnerem albo użyj 2.3.0.

### Odpowiedniki (Wniosek z porównania opisów)
| Fizycznie | OCPP 2.0.1 | OCPP 2.1 | OCPI 2.3.0 `standard` + `format` |
|---|---|---|---|
| Type 2, gniazdo | `sType2` | `sType2` | `IEC_62196_T2` + `SOCKET` |
| Type 2, kabel | `cType2` | `cType2` | `IEC_62196_T2` + `CABLE` |
| Type 1, gniazdo | brak wartości | `sType1` | `IEC_62196_T1` + `SOCKET` |
| CCS2 / Combo 2, kabel | `cCCS2` | `cCCS2` | `IEC_62196_T2_COMBO` + `CABLE` |
| CCS1 / Combo 1, kabel | `cCCS1` | `cCCS1` | `IEC_62196_T1_COMBO` + `CABLE` |
| CHAdeMO, kabel | `cG105` | `cG105` | `CHADEMO` + `CABLE` |
| ChaoJi, kabel | `cChaoJi` (tylko Device Model) | `cChaoJi` | `CHAOJI` + `CABLE` |
| GB/T DC, kabel | `cGBT` (tylko Device Model) | `cGBT-DC` | `GBT_DC` + `CABLE` |
| NACS / SAE J3400, kabel | brak | `cNACS` | `SAE_J3400` + `CABLE` |
| MCS, kabel | brak | `cMCS` | `MCS` + `CABLE` |
| Type 3A (kategoria L) | brak osobnej wartości | brak osobnej wartości | `IEC_62196_T3A` |
| Type 3C „Scame”, gniazdo | `sType3` (opis błędny) | `sType3` | `IEC_62196_T3C` + `SOCKET` |
| Pantograf | `Pan` | `Pan` („up”), `OppCharge` („down”) | `PANTOGRAPH_BOTTOM_UP` / `PANTOGRAPH_TOP_DOWN` |
| Bezprzewodowe | `wInductive`, `wResonant` | `wInductive`, `wResonant` | brak wartości |
| Adapter NACS↔CCS1 | brak | `cNACS-CCS1`, `cCCS1-NACS` | brak wartości |
Oficjalnej tabeli mapowania OCPP ↔ OCPI dla typów złączy w sprawdzonych dokumentach nie ma. Przypisanie `Pan` ↔
`PANTOGRAPH_BOTTOM_UP` i `OppCharge` ↔ `PANTOGRAPH_TOP_DOWN` wynika tylko ze słów „up”/„down” w opisach i nie jest
potwierdzone. Czy Type 3 OCPP odpowiada 3A czy 3C, rozstrzyga norma EN IEC 62196-2 (płatna, niedostępna).

## 2. Moc, napięcie, prąd, fazy
- OCPI: `max_voltage` (V; dla `AC_3_PHASE` linia–neutralny), `max_amperage` (A) wymagane; `max_electric_power` (W)
  opcjonalne, gdy niższe niż wynika z U × I. Dla AC na moc maksymalną wpływa też liczba użytych faz `[OCPI230 §8.3.3]`.
- OCPP 2.0.1 Device Model:
  - `EVSE.Power`: wymagany `maxLimit` = maksymalna moc, jaką EVSE może dostarczyć; wartość `Actual` (moc chwilowa)
    „desired, but not required” `[201-P2 §2.13.7]`;
  - `ChargingStation.SupplyPhases`, `EVSE.SupplyPhases`, `Connector.SupplyPhases` (wymagane): „1 or 3 for AC, 0 means
    DC”; wartość pusta (null) = liczba faz nieznana `[201-P2 §2.13.6]`;
  - `ChargingStation`: `SupplyPhases(MaxLimit)` (obsługiwane fazy), `ACVoltage(MaxLimit)` (projektowe maksymalne
    napięcie AC), `Power(MaxLimit)` — „designed total operating load power, including standby/ancilliary loads”
    `[201-APP §3.2.11]`;
  - `PhaseRotation`: trzy litery z R, S, T i `x` (faza niepodłączona), np. `RST`, `RSx`, `Rxx`; pusty ciąg = nie dotyczy
    lub nieznane. Aby raportować pomiary per faza względem sieci, wartość muszą mieć wszystkie komponenty od `Connector`
    do `ElectricalFeed` `[201-P2 §2.13.5]`;
  - `EVSE.DischargePower`: dla V2X `[201-CSV]` (patrz §3);
  - `EVSE.AllowReset`: czy EVSE da się resetować osobno `[201-P2 §2.13.3]`.
- OCPP 2.1, nowe zmienne EVSE:
  - `DischargePower` („New in OCPP 2.1”): wymagana, gdy obsługiwane jest V2X; `maxLimit` = znamionowa maksymalna moc
    rozładowania, `maxSet` = skonfigurowana; moc rozładowania jest dodatnia `[21-P2 §2.14.9]`;
  - `DCInputPhaseControl` („New in OCPP 2.1”): gdy `true`, `numberPhases` i `PhaseToUse` w
    `ChargingSchedulePeriodType` wybierają fazy wejściowe z sieci dla EVSE DC `[21-P2 §2.14.7]`.
- OCPP 1.6: brak mocy EVSE w protokole. `ConnectorPhaseRotation` (klucz wymagany, RW) podaje kolejność faz per złącze
  względem licznika (lub sieci); `NotApplicable` dla punktów jednofazowych i DC, `Unknown` gdy nieznana `[16 §9.1.7]`.
- **Wniosek:** `ChargingStation.Power(MaxLimit)` obejmuje obciążenia pomocnicze, a `EVSE.Power` maxLimit to moc dla
  pojazdu. Do OCPI `max_electric_power` i do klasy mocy AFIR bierz moc EVSE lub złącza, nie moc całej stacji.
- AFIR: „power output” to teoretyczna moc maksymalna punktu, stacji lub puli w kW `[AFIR art. 2]`. Normal power ≤ 22 kW,
  high-power > 22 kW `[AFIR art. 2]`.
- Klasy sprawozdawcze dla publicznych punktów (AFIR aneks III pkt 2 `[AFIR Annex III]`, nazwy podkategorii dosłownie):
| Kategoria | Podkategoria | Moc maksymalna |
|---|---|---|
| Category 1 (AC) | `Slow AC recharging point, single-phase` | P < 7,4 kW |
| Category 1 (AC) | `Medium-speed AC recharging point, triple-phase` | 7,4 kW ≤ P ≤ 22 kW |
| Category 1 (AC) | `Fast AC recharging point, triple-phase` | P > 22 kW |
| Category 2 (DC) | `Slow DC recharging point` | P < 50 kW |
| Category 2 (DC) | `Fast DC recharging point` | 50 kW ≤ P < 150 kW |
| Category 2 (DC) | `Level 1 - Ultra-fast DC recharging point` | 150 kW ≤ P < 350 kW |
| Category 2 (DC) | `Level 2 - Ultra-fast DC recharging point` | P ≥ 350 kW |
  Tabela przypisuje AC < 7,4 kW i 7,4–22 kW do definicji „normal-power”, a AC > 22 kW do „high-power”. Dane raportuje się
  osobno dla pojazdów lekkich i ciężkich: liczba punktów i stacji per podkategoria oraz łączna moc stacji (pkt 3).

## 3. Rozbieżności w dokumentach OCA
- **`sType3` w 2.0.1.** Specyfikacja: „IEC62196-2 Type 2 socket a.k.a. Scame” `[201-P2 §3.22]`. W 2.1: „IEC62196-2 Type
  3 socket a.k.a. Scame” `[21-APP §7.3]`. Rozstrzygnięcie: opis 2.0.1 to błąd redakcyjny (Type 2 ma osobną wartość
  `sType2`); znaczenie wartości to gniazdo Type 3 „Scame”.
- **Źródło wartości `Connector.ConnectorType` w 2.0.1.** Część 2: `ConnectorEnumType` z części 2 plus `cGBT`, `cChaoJi`,
  `OppCharge`, typ `string` `[201-P2 §2.13.4]`; tak samo CSV `[201-CSV]`. Aneks PDF v1.5: „A value of
  ConnectorStringEnumType (See Appendix 7)”, typ `OptionList` `[201-APP §3.2.14]` `[201-APP rozdz. 4]`, ale aneks 2.0.1
  ma tylko rozdziały 1–5. Rozstrzygnięcie (Wniosek): dla 2.0.1 obowiązuje lista z `[201-P2 §2.13.4]`; odwołanie do
  „Appendix 7” pasuje do aneksu 2.1, gdzie §7.3 istnieje.
- **Źródło wartości w 2.1.** Część 2 nadal pisze „ConnectorEnumType … plus additionally: cGBT, cChaoJi, OppCharge”
  `[21-P2 §2.14.4]`, choć w 2.1 pole `connectorType` odwołuje się do `ConnectorEnumStringType` z aneksu `[21-P2 §1.69.1]`.
  Aneks ma `cGBT-DC`, a nie `cGBT`; `cChaoJi` i `OppCharge` są już na liście `[21-APP §7.3]`. Nazwa w opisie komponentu
  to „ConnectorStringEnumType” `[21-APP §3.2.14]`, a nagłówek listy „ConnectorEnumStringType” `[21-APP §7.3]`.
  Rozstrzygnięcie (Wniosek): wartości bierz z `[21-APP §7.3]`. Pole jest typu string, więc CSMS powinien przyjąć także
  `cGBT` ze stacji zgodnych z tekstem części 2.
- **`EVSE.DischargePower` w 2.0.1.** CSV v1.5 wymienia zmienną (wymagalność „V2X”) `[201-CSV]`, ale lista zmiennych
  infrastruktury w części 2 Edition 4 jej nie zawiera `[201-P2 §2.13.1–2.13.8]`, a 2.1 oznacza ją „New in OCPP
  2.1” `[21-P2 §2.14.9]`. Rozstrzygnięcie (Wniosek): dla stacji 2.0.1 zmienna jest opcjonalnym rozszerzeniem z CSV;
  nie zakładaj, że stacja ją raportuje.
