# Topologie sterowania, limity zewnętrzne, OCPI ChargingProfiles, AFIR, OCPP 2.1

Źródła: `[16]`, `[201-P2 K]`, `[201-APP]`, OCPI 2.3.0 `[OCPI230 §14]`, AFIR skonsolidowany `[AFIR]`, OCPP 2.1 część 0
`[21-P0]` i część 2 `[21-P2]`. Zdania **Wniosek** to rekomendacje.

## Spis treści
1. Cztery typy sterowania w OCPP
2. Local Controller
3. Limity zewnętrzne (EMS, DSO, licznik) w 2.0.1
4. Wielu aktorów naraz: reguły SC.01–SC.04
5. Priorytet ładowania (2.0.1)
6. OCPI 2.3.0: moduł ChargingProfiles
7. AFIR: smart recharging i ładowanie dwukierunkowe
8. OCPP 2.1: co dochodzi w energii
9. Czego baza nie obejmuje

## 1. Cztery typy sterowania
Według OCPP smart charging to możliwość wpływania przez CSMS na moc lub prąd ładowania (w 2.0.1 także rozładowania)
pojedynczego pojazdu albo na łączny pobór stacji lub grupy stacji `[16 §3.13]` `[201-P2 K §1]`.

| Typ | Kto liczy limity | Mechanizm |
|---|---|---|
| Internal Load Balancing (K04) | stacja, między swoimi EVSE | stały limit od CSMS, np. prąd przyłącza; profil stacji tylko na EVSE 0 `[201-P2 K04.FR.02, K04.FR.03]` |
| Central Smart Charging (K02) | CSMS, także dla kilku stacji na jednym przyłączu | profile od CSMS, np. na podstawie prognozy od DSO; CSMS SHALL trzymać się limitów systemów zewnętrznych `[201-P2 K02.FR.01]` |
| Local Smart Charging (K03) | Local Controller dla grupy stacji | limity grupy wstępnie skonfigurowane albo ustawione przez CSMS `[201-P2 K §2.3]` |
| External Smart Charging Control Signals (K11–K14) | system zewnętrzny (DSO, HEMS, licznik) | dowolny protokół do stacji (Modbus, EEBUS, nawet OCPP); stacja zapisuje limit jako `ChargingStationExternalConstraints` `[201-P2 K §2.4]` |

- 1.6 opisuje trzy pierwsze typy `[16 §3.13.4]`. Algorytm liczenia harmonogramów w CSMS jest poza zakresem specyfikacji
  `[16 §3.13.4]`.
- Sterowanie sygnałem Control Pilot (AC, IEC 61851) ma ograniczenia, bo pojazd nie przekazuje nim swoich potrzeb
  `[16 §3.13.4]` `[201-P2 K §2.2]`. W 2.0.1 po autoryzacji EVSE AC ustawia maksymalny prąd przez Control Pilot
  (K02.FR.02) `[201-P2 K02.FR.02]`.
- Profil to **limit, nie cel**: pojazd może pobierać mniej (temperatura, stan baterii, kabel jednofazowy, limity
  lokalne) `[OCPI230 §14]`.

## 2. Local Controller
- Komponent logiczny: osobne urządzenie albo „master” jednej ze stacji. Działa jak proxy komunikatów OCPP członków
  grupy, może nie mieć własnych złączy `[16 §3.13.4]`.
- Przekazuje komunikaty między stacjami a CSMS, więc CSMS może adresować każdą stację osobno, a Local Controller wie o
  transakcjach `[16 §3.13.4]`.
- Może dynamicznie zmieniać limity stacji w trakcie ładowania (K03.FR.01–02); stacja SHALL uwzględnić nowy profil w
  harmonogramie złożonym (K03.FR.03) `[201-P2 K03.FR.03]`.

## 3. Limity zewnętrzne w 2.0.1 (K11–K13)
- Stacja SHALL NOT ładować szybciej niż limit zewnętrzny (K11.FR.01) `[201-P2 K11.FR.01]`.
- Zmiana limitu większa niż `LimitChangeSignificance` → stacja SHALL wysłać `NotifyChargingLimitRequest`, z
  harmonogramem, jeśli włączono `NotifyChargingLimitWithSchedules` (K11.FR.02–03); zmiana mocy ładowania większa niż
  próg → `TransactionEvent` z `triggerReason = ChargingRateChanged` (K11.FR.04) `[201-P2 K11.FR.02]`.
- `chargingLimitSource` w takim zgłoszeniu SHALL NOT być `CSO` (K11.FR.05) `[201-P2 K11.FR.05]`.
- Raportując taki limit, stacja używa celu `ChargingStationExternalConstraints`; zaleca się ujemne `id`, żeby nie
  kolidowało z `id` od CSMS (K11.FR.06). Każda zmiana limitu w profilu `Absolute`/`Relative` oznacza nowy profil (może
  mieć to samo `id`) `[201-P2 K11.FR.06]`.
- CSMS nie zakłada, nie zastępuje i nie usuwa tych profili (K01.FR.05, K01.FR.22, K10.FR.08–09, errata K01.FR.62)
  `[201-P2 K10.FR.08]` `[201-E]`.
- Stacja reaguje na sygnały zewnętrzne, gdy `SmartChargingCtrlr.ExternalControlSignalsEnabled` na to pozwala
  `[201-APP §3.1.16]`.

**Wniosek:** w CSMS limit zewnętrzny pokazujesz jako osobną warstwę (źródło, czas, wartość) i uwzględniasz w
planowaniu, ale go nie zdejmujesz. Do zmiany potrzebny jest kontakt z właścicielem systemu zewnętrznego (EMS, DSO).

## 4. Wielu aktorów naraz (2.0.1, rozdz. 4 bloku K)
Mechanizmy limitów: profil od CSMS, pojazd przez ISO 15118, sygnał lokalny (HEMS, DSO), równoważenie w stacji
`[201-P2 K §4]`.
- SC.01: wynik połączenia ≤ najniższego limitu ze wszystkich harmonogramów (bezpieczeństwo).
- SC.02: przy zmianie stacja SHALL zawsze informować CSMS: `NotifyEVChargingSchedule` (ISO 15118),
  `NotifyChargingLimit` (sygnał zewnętrzny), `TransactionEvent` (równoważenie).
- SC.03: dla sygnału zewnętrznego i równoważenia zgłoszenie MAY zostać pominięte, gdy zmiana jest mniejsza niż
  `LimitChangeSignificance`.
- SC.04: `GetCompositeSchedule` raportuje oczekiwany, najniższy limit.

OCPI ostrzega, że kilka stron wysyłających profile naraz daje nieprzewidywalny wynik: w OCPP liczy się minimum, więc
ładowanie jest wolniejsze niż potrzeba `[OCPI230 §14.1]`.

## 5. Priorytet ładowania w 2.0.1
- Transakcja z wyższym `chargingPriority` SHALL być obsługiwana jak najdłużej, nawet kosztem wstrzymania innych
  (K03.FR.04) `[201-P2 K03.FR.04]`.
- `chargingPriority` z `TransactionEventResponse` dotyczy tylko tej transakcji i nie trafia np. do cache autoryzacji
  (K03.FR.05). Brak wartości oznacza priorytet 0 (K03.FR.06) `[201-P2 K03.FR.05]`.

## 6. OCPI 2.3.0: moduł ChargingProfiles `[OCPI230 §14]`
- Służy eMSP albo dostawcy usług smart charging (SCSP, agregator) do wysyłania profili do sesji w toku i do odczytu
  `ActiveChargingProfile`, czyli profilu wyliczonego przez EVSE z wszystkich wejść, także limitów lokalnych.
  Zależność: moduł Sessions. Struktury bazują na OCPP 1.6 i 2.0.
- Profil może utworzyć właściciel tokenu dla sesji tego tokenu. Bez umowy z inną stroną CPO może odrzucić jej profile.
  Obowiązują lokalne przepisy o prywatności, umowy i ewentualnie zgoda kierowcy.
- Topologie `[OCPI230 §14.1]`: eMSP generuje profile; eMSP deleguje do SCSP (CPO nie widzi różnicy); CPO deleguje do
  SCSP (eMSP o tym nie wie, a CPO informuje kierowcę, np. naklejką albo w tekście taryfy).
- Przebieg asynchroniczny `[OCPI230 §14.3]`: odbiorca (CPO) od razu odpowiada `ChargingProfileResponse` (`ACCEPTED`,
  `NOT_SUPPORTED`, `REJECTED`, `TOO_OFTEN`, `UNKNOWN_SESSION` oraz `timeout` w sekundach). Wynik z EVSE (`ACCEPTED`,
  `REJECTED`, `UNKNOWN`) wysyła później metodą POST na `response_url` `[OCPI230 §14.5.1, §14.6.5–14.6.6]`.
- Interfejs odbiorcy: GET (`ActiveChargingProfile`), PUT (ustawienie lub zmiana profilu dla sesji), DELETE
  (anulowanie); POST i PATCH n/a `[OCPI230 §14.4.1]`.
- Po pierwszym udanym profilu dla sesji CPO SHALL informować nadawcę o zmianach `ActiveChargingProfile` `[OCPI230 §14.3]`.
- `ChargingProfile`: `start_date_time` (brak = względny od startu ładowania), `duration`, `charging_rate_unit` (`W`
  łącznie, `A` na fazę), `min_charging_rate`, lista `charging_profile_period` (`start_period`, `limit` z jednym miejscem
  po przecinku) `[OCPI230 §14.6.2–14.6.4]`.
- `TOO_OFTEN`: CPO może ograniczać częstotliwość żądań, żeby nie przeciążać łączy stacji `[OCPI230 §14.3]`.

**Wniosek:** profil z OCPI jest dla CPO wejściem do własnego planowania, a nie bezpośrednim poleceniem dla stacji.
Mapowanie na OCPP `TxProfile` i minimum z limitami lokalnymi zostaje po stronie CPO.

## 7. AFIR: smart recharging i ładowanie dwukierunkowe
- Definicje `[AFIR art. 2]`:
  - „smart recharging” (pkt 65): moc dostarczana do baterii dostosowywana w czasie rzeczywistym na podstawie informacji
    z komunikacji elektronicznej;
  - „bi-directional recharging” (pkt 11): smart recharging z możliwym odwróceniem kierunku przepływu, z baterii do
    punktu ładowania;
  - „digitally-connected recharging point” (pkt 17): wysyła i odbiera informacje w czasie rzeczywistym, komunikuje się
    dwukierunkowo z siecią i pojazdem, jest zdalnie monitorowany i sterowany, w tym start, stop i pomiar przepływów.
- Obowiązki operatora `[AFIR art. 5 ust. 7–8]`:
  - od 14.10.2024 wszystkie publiczne punkty „digitally-connected”;
  - publiczne punkty zbudowane po 13.04.2024 lub odnowione po 14.10.2024 zdolne do smart recharging.
- Państwa członkowskie `[AFIR art. 14 ust. 2 lit. h]` `[AFIR art. 15 ust. 3–4]`:
  - ramy krajowe obejmują środki, żeby rozmieszczenie punktów, w tym dwukierunkowych, wspierało elastyczność systemu i
    udział OZE;
  - do 30.06.2024 i co 3 lata ocena, jak punkty mogą wspierać elastyczność (także rynek bilansujący);
  - regulator na podstawie danych od OSP i OSD ocenia potencjał ładowania dwukierunkowego.

**Wniosek:** AFIR wymaga zdolności do smart recharging, ale nie wskazuje protokołu. Wymogi komunikacji z pojazdem
(ISO 15118) są w aneksie II (skill `ev-evse-hardware-expert`).

## 8. OCPP 2.1: co dochodzi w energii (przegląd z części 0)
Według listy zmian OCPP 2.1 `[21-P0 rozdz. 2]`:
- blok K: nowe cele `PriorityCharging` i `LocalGeneration`; `operationMode` w okresie harmonogramu dla scenariuszy
  dwukierunkowych; profile dynamiczne do częstych, nieplanowanych zmian limitów (K01); K18–K20 dla ISO 15118-20;
  K21–K22 priorytet ładowania nadpisujący profil na żądanie użytkownika; K23–K27 topologie z EMS;
- blok Q (przepływ dwukierunkowy, V2X): Q01–Q04 sterowanie centralne, Q05–Q06 zewnętrzne, Q07–Q08 regulacja
  częstotliwości centralna i lokalna, Q09 lokalne równoważenie z V2X, Q10–Q12 stan bezczynności, offline i wznowienie;
- sterowanie DER: stacja i pojazd jako rozproszone źródła energii (w części 0 U01–U05, w części 2 R01–R05); według opisu bloku po stronie sieci IEC
  61850 i IEEE 2030.5, po stronie pojazdu ISO 15118-20 Amendment 1 `[21-P0 rozdz. 3]`;
- blok J: nowe wielkości pomiarowe dla ładowania dwukierunkowego i lokalizacja pomiaru `Upstream`.

Bloki Q (V2X) i R (DER) z części 2 OCPP 2.1 opisuje `references/v2x-der-ocpp21.md`. Niespójność oznaczeń z części 0
(nagłówek „R DER Control” z U01–U05) rozstrzyga część 2: przypadki mają numery R01–R05 `[21-P2 R01]`.

## 9. Czego baza nie obejmuje
- ISO 15118-2/-20 i IEC 61851 (normy płatne): treść komunikacji pojazd–ładowarka i sygnału Control Pilot. Bloki K15–K17
  OCPP 2.0.1 (ISO 15118) wymieniam tylko z nazwy.
- Protokoły po stronie sieci i budynku (EEBUS, Modbus, OpenADR, IEC 61850, IEC 60870-5-104, DNP3): OCPP tylko je
  wymienia `[201-P2 K §2.4]`.
- Przyłączenie do sieci (D08.04), taryfy dystrybucyjne i rynek energii (D08.05), regulacje krajowe dotyczące
  elastyczności i DSO: wymagają źródeł prawa krajowego i UE (np. dyrektywa 2019/944, której nie ma w rejestrze).
