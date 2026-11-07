# Karta urządzenia — co z protokołu, co ręcznie

Znaczniki jak w `SKILL.md`. Układ karty jest **wnioskiem**. Każde pole wskazuje źródło danych.

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
- Moc i fazy: `EVSE.Power` (maxLimit, wymagany), `SupplyPhases` (stacja, EVSE, złącze), `EVSE.DischargePower` (V2X).
- Złącza: `Connector.ConnectorType` (wymagany), `Connector.ChargeProtocol`.
- Czytnik: `TokenReader.TokenType`.
- Terminal płatniczy (`PaymentCtrlr`, jeśli jest): `VendorName`, `Model`, `SerialNumber`, `FirmwareVersion`,
  `TerminalID`, `PaymentServiceProvider`, `Connected`, `Problem`, `IMSI`, `ICCID`.
- Reset per EVSE: `EVSE.AllowReset`.
W 1.6 tych danych nie ma w protokole. Konfigurację odczytuje `GetConfiguration` (np. `NumberOfConnectors`,
`SupportedFeatureProfiles`, `ConnectorPhaseRotation`) `[16 §9.1]`.

## 2. Uzupełniane ręcznie (lub z dokumentacji producenta)
- 1.6: typ złącza, gniazdo czy kabel, moc maksymalna, napięcie i prąd, liczba faz (protokół ich nie przesyła).
- Dane statyczne AFIR na poziomie punktu i stacji `[AFIR art. 20 ust. 2 lit. a–b]`:
  - liczba złączy, typ złącza, typ prądu;
  - moc maksymalna stacji i punktu;
  - kompatybilność typów pojazdów;
  - plug-and-charge, usługi smart recharging;
  - urządzenia płatnicze (czytnik kart, zbliżeniowe, inne ad hoc);
  - energia 100% odnawialna.
  Format według załącznika 2025/655 i od 14.04.2026 DATEX II `[AFIR-655 art. 1]`.
- Zgodność z aneksem II AFIR: data instalacji lub modernizacji, normy złączy, ISO 15118 (`references/wymagania-afir.md`).
- Certyfikaty (np. OCA dla OCPP, legalizacja licznika): domeny D13 i D10, nieopracowane.

## 3. Weryfikacja deklaracji (Wniosek)
- Porównaj `NotifyReport` z kartą producenta. Rozbieżności (np. inna moc maksymalna, brak `PaymentCtrlr`) zapisuj
  jako obserwacje D21 z modelem i wersją firmware.
- `ConnectorCapability` w OCPI ustawiaj dopiero po potwierdzeniu, że funkcja działa dla kierowcy `[OCPI230 §8.4.4]`.
