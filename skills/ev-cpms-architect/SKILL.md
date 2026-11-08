---
name: ev-cpms-architect
description: Użyj przy projekcie lub ocenie CPMS/CSMS — brama OCPP, onboarding stacji, topologie, model statusów, sesje, ładowarki własne i roamingowe, AFIR, publikacja do NAP.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy projektowaniu albo ocenie architektury i modułów CPMS/CSMS — warstwa połączeń OCPP-J (identyfikacja stacji, uwierzytelnianie, ponowne łączenie i restart CSMS), onboarding i provisioning (BootNotification Pending/Accepted/Rejected), topologie z lokalnym proxy, kontrolerem, EMS i DSO, model statusów i dostępności (offline vs niedostępna vs awaria), sesje i transakcje z kolejkami offline, ładowarki własne (OCPP) vs zewnętrzne (OCPI), projekt publikacji danych AFIR do NAP (API, format, częstotliwość, jakość) i wymagania cenowe, separacja tenantów. Każde ograniczenie z cytatem ze specyfikacji OCA, EVRF albo AFIR, decyzje projektowe oznaczone jako wniosek. Nie do integracji i migracji między systemami, bramy OCPP–OCPI (ev-integration-architect), algorytmów i profili sterowania mocą (ev-energy-smart-charging-expert), szczegółów komunikatów OCPP (ev-ocpp-expert), mechaniki OCPI (ev-ocpi-roaming-expert), KPI dostępności i raportów operacyjnych NOC (ev-charging-operations-expert) ani doboru domen dla zadania (ev-domain-expert)."
  slowa: "CPMS, CSMS, architektura CPMS, projekt CPMS, moduł CPMS, backend ładowarek, brama OCPP, WebSocket gateway, restart CSMS, reconnect storm, tysiące połączeń, ponowne łączenie ładowarek, identyfikator stacji w URL, onboarding ładowarki, provisioning, dopuszczenie stacji, BootNotification Pending, model statusów, status ładowarki w CPMS, offline niedostępna awaria, dostępność stacji, ładowarki roamingowe, stacje partnerów, ładowarki zewnętrzne, własne vs roamingowe, local controller, local proxy, EMS, DSO, topologia sieci ładowarek, AFIR, dane dla NAP, dane statyczne i dynamiczne, cena ad hoc, multi-tenancy, tenant, white-label, uprawnienia operatora, model danych Location EVSE Connector, API do NAP, publikacja danych dynamicznych, DATEX II, częstotliwość aktualizacji danych AFIR, moduł danych dla krajowego punktu dostępowego"
---

# CPMS Architect — projekt systemu zarządzania ładowaniem

Skill prowadzi **decyzje projektowe** CPMS. Szczegóły protokołów są w `ev-ocpp-expert` i `ev-ocpi-roaming-expert`;
tu łączysz je z wymaganiami prawnymi w projekt modułu. Taksonomia: D05.01–D05.05. Sieć: brak.

**Zasada źródeł.** Architektury CPMS nie opisuje żadna norma. Skill składa się więc z dwóch rodzajów zdań:
- **ograniczenia** z dokumentów OCA, EVRF i AFIR (`sources/*.yaml`), ze znacznikiem `[dokument §]`;
- **wnioski**, czyli decyzje projektowe wyprowadzone z tych ograniczeń, oznaczone słowem **Wniosek**.
Nie dodajesz „dobrych praktyk branżowych” bez źródła.

**Źródła niedostępne.** Gdy odpowiedź zależy od normy płatnej albo dokumentu z `sources/niedostepne.yaml`, piszesz to w
pierwszym zdaniu odpowiedzi: której normy nie da się sprawdzić i dlaczego. Dopiero potem podajesz to, co wynika ze
źródeł dostępnych.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „errata OCPP 1.6
§3.18 `[16E §3.18]`”, „specyfikacja OCPI 2.3.0 §4.4 `[OCPI230 §4.4]`”, „AFIR art. 5 ust. 10”, „rozporządzenie
wykonawcze 2025/655 art. 2 `[AFIR-655 art. 2]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/ograniczenia.md` | katalog ograniczeń per moduł: połączenia, onboarding, topologie, sesje, roaming, AFIR, bezpieczeństwo |
| `references/model-statusow.md` | model statusów i dostępności dla stacji własnych i roamingowych, mapowanie na AFIR i OCPI |

## Procedura
1. **Zakres zasobów.** Stacje własne (OCPP: pełne sterowanie) czy zewnętrzne (OCPI: dane i komendy partnera).
   Dla zewnętrznych dostępne są tylko komendy `START_SESSION`, `STOP_SESSION`, `RESERVE_NOW`, `CANCEL_RESERVATION`,
   `UNLOCK_CONNECTOR` `[OCPI230 §13.4.3]` i dane modułów Locations, Sessions, CDRs, Tariffs.
2. **Wersje i topologia.** Wersje OCPP w flocie (1.6 i 2.x są niezgodne `[201-P0 rozdz. 2]`). Czy są proxy lub kontrolery
   lokalne, EMS albo sygnały DSO `[201-P1 rozdz. 8]`.
3. **Model danych.** Hierarchia OCPI to Location → EVSE → Connector, a OCPP to Charging Station → EVSE → Connector
   `[OCPI230 §8.1.2]`. „EVSE” w OCPP, „EVSE” w OCPI i „recharging point” w AFIR mają to samo kryterium: jeden pojazd
   naraz `[201-P1 §1.2.1]` `[OCPI230 §2.6]` `[AFIR art. 2]`. **Wniosek:** EVSE jest jednostką dostępności i raportowania
   AFIR, a Location to osobny byt grupujący stacje (OCPI preferuje jedną Location na grupę stacji `[OCPI230 §8.1.2]`).
4. **Ograniczenia modułu.** Wypisz je z `references/ograniczenia.md` z cytatami: co MUSI, co POWINNO, czego NIE WOLNO.
5. **Decyzje.** Każdą decyzję zapisz jako **Wniosek** ze wskazaniem ograniczeń, z których wynika, i z alternatywą,
   jeśli źródła dopuszczają kilka rozwiązań.
6. **Wymagania prawne.** Dla stacji publicznych sprawdź AFIR: ad hoc i ceny (art. 5), dane statyczne i dynamiczne oraz
   API dla NAP (art. 20). Szczegóły aktów delegowanych to domena D12 (`ev-compliance-expert`, jeszcze nieopracowany).
   Akty nieprzeczytane wymień jako lukę (`sources/eu-afir.yaml` → `not_yet_reviewed`).
7. **Kryteria akceptacji** z przypadkami brzegowymi: restart CSMS, ponowne połączenie bez Boot, stacja w `Pending`,
   transakcja offline z `transactionId = -1` (1.6), luka w `seqNo` (2.0.1), EVSE `UNKNOWN` u partnera.

## Przykład
**Zadanie:** „Po restarcie CSMS tysiące stacji łączą się naraz, a po ponownym połączeniu większość nie wysyła
`BootNotification`, więc nie znamy statusów złączy.”

Ograniczenia:
- stacja łączy się ponownie z wykładniczo rosnącym opóźnieniem i losowym rozrzutem, właśnie po to, by nie przeciążyć
  CSMS po jego restarcie `[201-P4 §5.4]`;
- po ponownym połączeniu stacja SHOULD NOT wysyłać `BootNotification`, jeśli nic w nim się nie zmieniło; serwer
  dopasowuje tożsamość już przy zestawieniu WebSocketu `[201-P4 §5.4]`;
- tożsamość stacji jest w URL połączenia. Zalecane jest, by CSMS nie polegał tylko na URL, lecz sprawdzał ją względem
  danych uwierzytelniających `[201-P4 §3.1.1]`;
- po przekroczeniu `OfflineThreshold` zaleca się, by stacja wysłała `StatusNotification` dla wszystkich złączy `[201-CSV]`.

**Wniosek, projekt:**
- stan połączenia jest w CSMS niezależny od Boot: zmienia się przy zestawieniu i zamknięciu WebSocketu po
  uwierzytelnieniu;
- po ponownym połączeniu, gdy brak świeżego statusu, CSMS sam wysyła `TriggerMessage` (`StatusNotification`), z limitem
  równoległości, żeby nie zablokować bramy;
- jedno niezakończone CALL na połączenie `[201-P4 §4.1.1]`, więc kolejka poleceń jest per stacja.

Kryterium akceptacji: po restarcie CSMS każda stacja ma znany status złączy w czasie T bez ręcznej interwencji, nawet gdy
nie wysłała `BootNotification`.

## Pułapki
- Traktowanie „offline” jako statusu OCPP: to stan wyznaczany przez CSMS. W OCPI brak informacji (także offline) to
  `UNKNOWN` `[OCPI230 §8.4.26]`.
- Szukanie oficjalnego mapowania statusów OCPP → OCPI → AFIR: żadne ze źródeł go nie definiuje
  (`references/model-statusow.md`).
- Inicjowanie komunikatów do stacji po `Rejected`: CSMS SHALL NOT `[201-P2 B03.FR.03]`.
- Zdalny start w `Pending`: stacja SHALL odpowiedzieć `Rejected` `[201-P2 B02.FR.05]`.
- Kontroler lokalny traktowany jak „zwykła” stacja bez logiki: CSMS „will possess the logic to deal with the Local
  Controller” `[201-P1 §8.3]`.
- Uprawnienia operatorów wyłącznie po stronie stacji: OCPP nie ma kontroli dostępu na stacji, zalecana jest kontrola
  dostępu w CSMS `[201-P2 A §1.2]`.

## Źródła
`sources/oca-ocpp.yaml` (201-P0, 201-P1, 201-P2, 201-P4, 201-CSV, 16, 16E), `sources/evrf-ocpi.yaml` (OCPI230),
`sources/eu-afir.yaml` (AFIR, wersja skonsolidowana 2026-01-08). Pobrane 2026-11-07.
