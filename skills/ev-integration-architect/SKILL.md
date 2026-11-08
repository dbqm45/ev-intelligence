---
name: ev-integration-architect
description: Użyj przy łączeniu systemów EV — brama OCPP–OCPI, resynchronizacja po awarii, mapowanie na Locations, migracja CSMS, rozszerzenia OCPP, testy wdrożeń i kompatybilności.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy projektowaniu i przeglądzie integracji między systemami elektromobilności — przeciwne zasady OCPP i OCPI (kolejkowanie offline kontra synchronizacja przez GET, odrzucanie i tolerowanie nieznanych pól, messageId kontra X-Request-ID i X-Correlation-ID, jedno oczekujące CALL na połączenie, ponowne łączenie z back-off), mapowanie stacji OCPP na OCPI Locations i EVSE, wiele złączy na EVSE w OCPP 1.x (nota aplikacyjna OCA), START_SESSION i autoryzacja przy przejściu OCPI→OCPP, migracja ładowarek do nowego CSMS (OCPP 1.6 i 2.0.1, SetNetworkProfile, NetworkConfigurationPriority, B09/B10, profile bezpieczeństwa 2 i 3, SIM, QR, dane), rozszerzenia OCPP (Device Model, customData, DataTransfer, CustomizationCtrlr, vendorId) i OCPI, testy zgodności i macierz kompatybilności. Każdy fakt z cytatem ze źródła oficjalnego (OCA, EVRF). Nie do architektury modułów CPMS (ev-cpms-architect), szczegółów komunikatów OCPP (ev-ocpp-expert), mechaniki OCPI (ev-ocpi-roaming-expert) ani oceny zgodności konkretnego modelu (ev-evse-diagnostics-expert)."
  slowa: "integracja, architektura integracji, brama OCPP OCPI, gateway, synchronizacja danych, po awarii, resynchronizacja, kolejkowanie, ponawianie, retry, idempotencja, deduplikacja, korelacja, messageId, X-Request-ID, X-Correlation-ID, back-off, RetryBackOffWaitMinimum, lawina połączeń, Local Controller, mapowanie stacji na Locations, model trójpoziomowy, wiele złączy na EVSE, wirtualne EVSE, Multiple Connectors per EVSE, START_SESSION_CONNECTOR_REQUIRED, connector_id, migracja ładowarek, zmiana operatora, przeniesienie stacji do nowego CSMS, SetNetworkProfile, NetworkConfigurationPriority, NetworkProfileConnectionAttempts, B10, stranded asset, CSMSRootCertificate, AdditionalRootCertificateCheck, profil bezpieczeństwa 3, przeniesienie SIM, eSIM, APN, naklejki QR, EVSEID przy zmianie CSO, rozszerzenia OCPP, DataTransfer, customData, Device Model własny komponent, CustomizationCtrlr, vendorId, rozszerzenia OCPI, nieznane pola, testy zgodności, interoperacyjność, macierz kompatybilności, adapter"
---

# Integration Architect — łączenie systemów EV

Skill odpowiada, **jak połączyć systemy EV, żeby dane się zgadzały**: brama OCPP–OCPI, synchronizacja po awarii,
mapowanie obiektów, migracja stacji między CSMS, rozszerzenia protokołów i testy zgodności. Taksonomia: D05.07,
D13.02, D13.03, D14.01, D14.02, D21.02. Sieć: brak.

**Zasada źródeł.** Fakty mają znacznik `[dokument §]` i pochodzą z `sources/*.yaml`: specyfikacje OCA i EVRF oraz białe
księgi i nota aplikacyjna OCA. **Białe księgi to zalecenia z doświadczeń członków OCA, nie wymagania.** Ogólne wzorce
IT spoza dokumentów EV (brokery komunikatów, bazy danych, API gateway, ERP, CRM, płatności) nie są opracowane. Mówisz
wtedy, że baza tego nie obejmuje, i nie odpowiadasz z pamięci.

**Źródła niedostępne.** Gdy odpowiedź zależy od normy płatnej albo dokumentu z `sources/niedostepne.yaml`, piszesz to w
pierwszym zdaniu odpowiedzi: której normy nie da się sprawdzić i dlaczego. Dopiero potem podajesz to, co wynika ze
źródeł dostępnych.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „specyfikacja OCPI 2.3.0
§4.4 `[OCPI230 §4.4]`”, „OCPP 2.0.1 część 4 §4.1.1 `[201-P4 §4.1.1]`”, „OCPP 2.0.1 B10.FR.05 `[201-P2 B10.FR.05]`”,
„biała księga OCA o migracji §5.1 `[OCA-WP-MIG §5.1]`”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/ocpp-ocpi-polaczenie.md` | różnice OCPP i OCPI (offline, nieznane pola, korelacja), zasady OCPP-J, mapowanie na Locations, wiele złączy na EVSE, START_SESSION, szkielet bramy |
| `references/migracja-i-rozszerzenia.md` | migracja stacji (1.6, 2.0.1, profil 3, przeszkody), rozszerzenia OCPP i OCPI, testy i macierz kompatybilności, rozbieżności |

## Procedura
1. **Granice systemów:** kto jest właścicielem danych (stacja, CSMS, CPO, eMSP), jaki protokół na każdej granicy i w
   jakiej wersji.
2. **Awaria łączności na każdej granicy:** OCPP kolejkuje komunikaty transakcyjne `[16 §3.7]`, a OCPI nie kolejkuje i
   synchronizuje przez GET `[OCPI230 §4.4]`. Projektujesz oba zachowania osobno.
3. **Identyfikatory:** `messageId` po stronie OCPP `[201-P4 §4.1.4]`, `X-Request-ID` i `X-Correlation-ID` po stronie
   OCPI `[OCPI230 §4.2]`. Deduplikacja i logi całego łańcucha.
4. **Mapowanie obiektów:** stacja → Location (grupa w jednym miejscu) `[OCPI230 §8.1.2]`; stacje 1.x z wieloma
   złączami na EVSE według noty OCA `[OCA-AN-MC §4]`.
5. **Zmiana:** migracja stacji (`references/migracja-i-rozszerzenia.md`), rozszerzenia (Device Model przed
   `DataTransfer`) `[OCA-WP-CUST §1.4]`.
6. **Weryfikacja:** certyfikaty OCA, test na modelu i firmware, wpis w rejestrze odchyleń.
7. **Luki:** wzorce IT spoza dokumentów EV i testy OCPI wymieniasz jako nieopracowane.

## Przykład
**Pytanie:** „Po kilkugodzinnej awarii łącza do eMSP mamy niewysłane aktualizacje sesji i CDR. Kolejkować je tak jak
ładowarka w OCPP?”

Fakty:
- OCPP: offline stacja MUST kolejkować komunikaty transakcyjne i wysłać je chronologicznie `[16 §3.7]`.
- OCPI: komunikatów SHOULD NOT kolejkować; po nieudanym lub przeterminowanym POST, PUT czy PATCH klient nie wysyła ich
  później ponownie `[OCPI230 §4.4]`.
- Po przywróceniu połączenia to odbiorca pobiera bieżący stan przez GET, np. CDR z okresu przerwy z filtrem daty i
  statusy EVSE z Locations `[OCPI230 §4.4]`.

**Wniosek:**
- nie budujesz kolejki ponowień do eMSP;
- zapewniasz, że Twoje endpointy Sender (CDRs, Sessions, Locations) zwracają dane z okresu przerwy przez `date_from`;
- dla danych, które Ty odbierasz od partnera, robisz po awarii GET z datą ostatniej udanej synchronizacji;
- dla nowych CDR po awarii zostaje zwykły push.

## Pułapki
- Przeniesienie modelu OCPP („kolejkuj i ponawiaj”) na OCPI daje dublowanie aktualizacji i niezgodny stan `[OCPI230 §4.4]`.
- Walidator OCPI odrzucający nieznane pola łamie specyfikację (SHALL NOT) `[OCPI230 §4.1.8]`. W OCPP nieznane pola
  poza `customData` odrzuca schemat `[OCA-WP-CUST §1.2.2]`.
- `messageId` w 2.0.1 musi być unikalny także między połączeniami tej samej stacji, a ponowienie może mieć ten sam
  `messageId` `[201-P4 §4.1.4]`.
- Migracja 1.6: klucze sieci nie są ustandaryzowane, a konfiguracja wymaga kilku komunikatów. Zerwanie połączenia w
  połowie może odciąć stację od każdego CSMS `[OCA-WP-MIG §4]`.
- Migracja 2.0.1 z transakcjami w toku: bez `Inoperative` i opróżnionej kolejki nowy CSMS dostanie zakończenia
  transakcji, których startu nie zna (B10.FR.05) `[201-P2 B10.FR.05]`.
- Powrót stacji do starego profilu po nieudanych próbach jest w 2.0.1 tylko zaleceniem (SHOULD), nie gwarancją
  `[201-P2 B10.FR.07]`.
- Zmiana CSO zmienia zewnętrzne identyfikatory EVSE (EVSEID) w roamingu `[OCA-WP-MIG §3.2]`.

## Źródła
`sources/oca-ocpp.yaml` (16, J16, 201-P2 B09, B10, E13; 201-P4 §4, §5, §6; OCA-AN-MC; OCA-WP-MIG; OCA-WP-CUST; OCA-CERT;
OCA-LIST), `sources/evrf-ocpi.yaml` (OCPI230 §4, §8, §13, §14, §18). Pobrane 2026-11-07.
