# Karta urządzenia — co z protokołu, co ręcznie

Znaczniki jak w `SKILL.md`. Układ karty jest **wnioskiem**. Każde pole wskazuje źródło danych.

## Spis treści
1. Pobierane automatycznie (`BootNotification`, Device Model, komponenty fizyczne)
2. Gniazdo czy kabel — co mówi protokół
3. Uzupełniane ręcznie
4. Weryfikacja deklaracji

## 1. Pobierane automatycznie
### Z `BootNotification`
| Pole | OCPP 1.6 `[S16]` `[16 §6.3]` | OCPP 2.0.1 `[201-P3]` |
|---|---|---|
| Producent | `chargePointVendor` (wymagane, maks. 20) | `chargingStation.vendorName` (wymagane) |
| Model | `chargePointModel` (wymagane, maks. 20) | `chargingStation.model` (wymagane) |
| Numer seryjny | `chargePointSerialNumber` (maks. 25); `chargeBoxSerialNumber` „Deprecated, will be removed in future version” | `chargingStation.serialNumber` |
| Firmware | `firmwareVersion` (maks. 50) | `chargingStation.firmwareVersion` |
| Modem | `iccid`, `imsi` (maks. 20) | `chargingStation.modem.iccid`, `.imsi` |
| Licznik | `meterType`, `meterSerialNumber` (maks. 25) | — (w Device Model) |
| Przyczyna startu | — | `reason` (np. `PowerUp`, `FirmwareUpdate`, `Watchdog`) |

### Z Device Model 2.0.1 (`GetBaseReport` → `NotifyReport`) `[201-CSV]`
- Struktura: `EVSE` i `Connector` (zmienna `Available` = komponent istnieje); `EVSE.EvseId` / `ISO15118EvseId`.
- Moc i fazy: `EVSE.Power` (maxLimit, wymagany), `SupplyPhases` (stacja, EVSE, złącze), `EVSE.DischargePower` (V2X;
  status w 2.0.1 niejasny, patrz `references/zlacza-i-moc.md` §3).
- Złącza: `Connector.ConnectorType` (wymagany), `Connector.ChargeProtocol`.
- Czytnik: `TokenReader.TokenType`.
- Terminal płatniczy (`PaymentCtrlr`, jeśli jest): `VendorName`, `Model`, `SerialNumber`, `FirmwareVersion`,
  `TerminalID`, `PaymentServiceProvider`, `Connected`, `Problem`, `IMSI`, `ICCID`.
- Reset per EVSE: `EVSE.AllowReset`.
W 1.6 tych danych nie ma w protokole. Konfigurację odczytuje `GetConfiguration` (np. `NumberOfConnectors`,
`SupportedFeatureProfiles`, `ConnectorPhaseRotation`) `[16 §9.1]`.

### Komponenty fizyczne Device Model `[201-APP §3.2]`
Lista komponentów jest niewyczerpująca, a ich zmienne są opcjonalne. Gdy element stacji pasuje do opisu komponentu
standardowego, stacja SHALL użyć tego komponentu zamiast własnego `[201-APP §3.2]`. Ten sam zestaw jest w 2.1
`[21-APP §3.2]`. Pola przydatne w karcie:
| Komponent | Zmienne „sprzętowe” (wybór) | Znacznik |
|---|---|---|
| `ChargingStation` | `VendorName`, `Model`, `ECVariant`, `SerialNumber`, `SupplyPhases(MaxLimit)`, `ACVoltage(MaxLimit)`, `Power(MaxLimit)` (z obciążeniami pomocniczymi) | `[201-APP §3.2.11]` |
| `EVSE` | `SupplyPhases`, `PhaseRotation`, `ChargeProtocol`, `ISO15118EvseId`, `AllowReset` | `[201-APP §3.2.29]` |
| `Connector` | `ConnectorType`, `SupplyPhases(MaxLimit)`, `PhaseRotation`, `ChargeProtocol` | `[201-APP §3.2.14]` |
| `Controller` | `Manufacturer`, `Model`, `SerialNumber`, `VersionNumber` (wersja sprzętu), `FirmwareVersion` | `[201-APP §3.2.19]` |
| `DataLink` | `IMSI`, `ICCID`, `NetworkAddress`, `SignalStrength`, `Fallback` (zapasowy SIM/sieć) | `[201-APP §3.2.22]` |
| `ElectricalFeed` | `PowerType`, `Power`, `SupplyPhases`, `PhaseRotation`, `ACVoltage`; prosta stacja z jednym zasilaniem może je pominąć | `[201-APP §3.2.24]` |
| `FiscalMetering` | `Manufacturer[Meter]`, `Model[Meter]`, `SerialNumber[Meter]`, `Manufacturer[CT]`, `Model[CT]`, `SerialNumber[CT]`, `Certificate`, `EnergyImportRegister` | `[201-APP §3.2.31]` |
| `TokenReader` | `Enabled`, `Problem`, `TokenType` | `[201-APP §3.2.52]` |
| `AcDcConverter` | `DCVoltage`, `DCCurrent`, `Power`, `Temperature`, `FanSpeed` | `[201-APP §3.2.2]` |
| `LiquidCoolingSystem` | chłodzenie cieczą „typically used to cool the connector cables of very high power Charging Stations” | `[201-APP §3.2.37]` |
| `ConnectorPlugRetentionLock` | blokada wtyczki (`Active` = Locked, `Problem` = Locking Failed, `Tries`) | `[201-APP §3.2.17]` |
| `CableBreakawaySensor` | wykrycie wyrwania kabla (stałego lub odłączanego); `Tripped` = wymagana ręczna kontrola | `[201-APP §3.2.9]` |
| `RCD`, `RCDRecloser` | `RCD.Tripped` = otwarty, wymaga ręcznego resetu; `RCD.Operated` = otwarty i samoczynnie załączony; recloser: `Enabled`, `Tries(SetLimit)`, `Active(Set)` (inicjuje ponowne załączenie) | `[201-APP §3.2.44]` `[201-APP §3.2.45]` |
| `OverCurrentProtection` | `Active` = zadziałanie, `Operated` = otwarty i samoczynnie załączony | `[201-APP §3.2.41]` |
| `GroundIsolationProtection` | test izolacji: `Active` = upływ, `Impedance` = rezystancja izolacji | `[201-APP §3.2.33]` |
| `CPPWMController` | `State` („IEC 61851-1 states ("A" to "E")”), `DCVoltage` (napięcie CP 0–12 V), `Percentage` (wypełnienie 1 kHz) | `[201-APP §3.2.21]` |
- `CPPWMController` OCA opisuje jako sygnalizację „IEC 61851-1 / SAE J1772” `[201-APP §3.2.21]`. CSMS może więc
  odczytać stan CP, napięcie i wypełnienie PWM, ale **znaczenie stanów, napięć i przeliczenie wypełnienia na prąd
  określa norma IEC 61851-1 (płatna, niedostępna: `sources/niedostepne.yaml`)**. SAE J1772 nie jest zarejestrowana.
  Tych wartości nie interpretujesz z pamięci.
- Typ i parametry RCD (np. wymagany rodzaj wyłącznika różnicowoprądowego) wynikają z norm IEC 61851-1 i IEC 60364-7-722
  (niedostępne). Device Model podaje tylko stan zadziałania `[201-APP §3.2.44]`.
- **Klasa dokładności licznika:** w komponentach i zmiennych standardowych 2.0.1 i 2.1 nie ma zmiennej klasy
  dokładności ani klasy MID (`FiscalMetering` ma producenta, model, numer i certyfikat) `[201-APP §3.2.31]`. Pole
  uzupełniasz ręcznie. Wymagania dla „systemu pomiarowego EVSE” z dyrektywy (UE) 2026/706, przywoływanej w materiałach
  wtórnych, nie są sprawdzone: akt nie jest w rejestrze źródeł.

## 2. Gniazdo czy kabel — co mówi protokół
- OCPP 2.0.1: prefiks wartości `c…` („captive cabled”) albo `s…` („socket”) w `ConnectorEnumType` `[201-P2 §3.22]`; w
  2.1 prefiksy `c`, `s`, `w`, `b` są zdefiniowane wprost `[21-APP §7.3]`.
- `OCPPCommCtrlr.UnlockOnEVSideDisconnect`: dla EVSE tylko z kablami stałymi zmienna SHALL być `ReadOnly` z wartością
  `false`; przy kablach stałych i gniazdach dotyczy tylko gniazd `[201-APP §3.1.12]`.
- Kod przyczyny `FixedCable` dla `UnlockConnector`: „The connector has its own fixed cable that cannot be unlocked”;
  `NoCable`: brak podłączonego kabla `[201-APP §5]`.
- OCPP 1.6: `UnlockConnectorOnEVSideDisconnect` (wymagany, RW) `[16 §9.1.33]`; `UnlockConnector` zwraca `NotSupported`,
  gdy punkt „has no connector lock, or ConnectorId is unknown” `[16 §7.46]`. Typu złącza 1.6 nie przesyła.
- OCPI: `Connector.format` = `SOCKET` / `CABLE` `[OCPI230 §8.4.5]`; capability EVSE `UNLOCK_CAPABLE` = złącza mają
  blokadę mechaniczną, którą eMSP może zdalnie zwolnić `[OCPI230 §8.4.3]`.
- **Wniosek:** prefiks `c…` w `NotifyReport`, `UnlockOnEVSideDisconnect` = `ReadOnly`/`false` i odpowiedź `FixedCable`
  to trzy niezależne sygnały kabla stałego. Zgodne ustaw jako OCPI `format = CABLE`, sprzeczne zapisz jako obserwację D21.
- Limit prądu kabla i jego kodowanie (rezystor PP) określają EN IEC 62196 i IEC 61851-1 (płatne, niedostępne). OCPP i
  OCPI nie mają pola prądu kabla. Pośrednio jest OCPI `max_amperage` złącza `[OCPI230 §8.3.3]`.

## 3. Uzupełniane ręcznie (lub z dokumentacji producenta)
- 1.6: typ złącza, gniazdo czy kabel, moc maksymalna, napięcie i prąd, liczba faz (protokół ich nie przesyła).
  Wyjątek: kolejność faz per złącze w `ConnectorPhaseRotation` (`NotApplicable` dla jednofazowych i DC) `[16 §9.1.7]`.
- Dane statyczne AFIR na poziomie punktu i stacji `[AFIR art. 20 ust. 2 lit. a–b]`:
  - liczba złączy, typ złącza, typ prądu;
  - moc maksymalna stacji i punktu;
  - kompatybilność typów pojazdów;
  - plug-and-charge, usługi smart recharging;
  - urządzenia płatnicze (czytnik kart, zbliżeniowe, inne ad hoc);
  - energia 100% odnawialna.
  Format według załącznika 2025/655 i od 14.04.2026 DATEX II `[AFIR-655 art. 1]`.
- Typy pojazdów w OCPI 2.3.0: `Parking.vehicle_types` (`VehicleType`: m.in.
  `MOTORCYCLE` ≈ L, `PERSONAL_VEHICLE` ≈ M1, `VAN` ≈ N1, `RIGID`, `SEMI_TRACTOR`, `BUS`). Obiekt `Parking` dodano w 2.3.0
  na potrzeby sprawozdawczości AFIR do NAP `[OCPI230 §8.3.4]` `[OCPI230 §8.4.28]`.
- Zgodność z aneksem II AFIR: data instalacji lub modernizacji, normy złączy, ISO 15118 (`references/wymagania-afir.md`).
- Klasa dokładności licznika (patrz §1, `FiscalMetering`).
- Certyfikaty (np. OCA dla OCPP, legalizacja licznika): domeny D13 i D10, nieopracowane.

## 4. Weryfikacja deklaracji (Wniosek)
- Porównaj `NotifyReport` z kartą producenta. Rozbieżności (np. inna moc maksymalna, brak `PaymentCtrlr`) zapisuj
  jako obserwacje D21 z modelem i wersją firmware.
- `ConnectorCapability` w OCPI ustawiaj dopiero po potwierdzeniu, że funkcja działa dla kierowcy `[OCPI230 §8.4.4]`.
- `ChargingStation.Power(MaxLimit)` obejmuje obciążenia pomocnicze `[201-APP §3.2.11]`, więc nie przepisuj go do mocy
  punktu w karcie AFIR. Moc punktu bierz z `EVSE.Power` maxLimit `[201-P2 §2.13.7]`.
