# OCPI — wersje, role, moduły

Źródła: `sources/evrf-ocpi.yaml` (znaczniki jak w `SKILL.md`). Stan na 2026-11-07.

## Status wersji
| Wersja | Status według źródeł | Źródło |
|---|---|---|
| 2.1.1 | wydana w lipcu 2017, „Contained all basic modules for CPO-MSP communication” | `[EVRF-V25]` |
| 2.2 | „will not be supported anymore” (zastąpiona przez 2.2.1) | `[EVRF-DL]` |
| 2.2.1 | wydana w październiku 2021, aktualizacja dokumentu we wrześniu 2023; strona pobrań nadal nazywa ją „the current official release of OCPI”, z deliverable 2 („d2”) | `[EVRF-V25]` `[EVRF-DL]` |
| 2.3.0 | dostępna od 21.02.2025 (dokument z tą datą); dostępny wariant z modułem Booking v1.1 | `[EVRF-DL]` `[OCPI230]` |
| 3.0 | „Update October 2026: … waiting official review by CENELEC and because of that not yet released. Current expected release date of OCPI v3.0 is H2 2027” | `[EVRF-DL]` |

Rozbieżności w źródłach EVRF:
- strona pobrań jednocześnie opisuje 2.2.1 jako „current official release” i udostępnia 2.3.0 od 02.2025 `[EVRF-DL]`;
- prezentacja z 08.2025 podaje dla 3.0 „To be released – H2 2025”, a strona pobrań (aktualizacja z 10.2026) H2 2027.
  Nowsze jest źródło `[EVRF-DL]`;
- plik „OCPI-2.2.1-d2.pdf” ma na stronie tytułowej „document version 2.2.1-d3-pre1, 2023-09-07” `[OCPI221]`.

## Co zmienia 2.3.0 względem 2.2.1 `[OCPI230 §1.1]`
„Only the minimal changes to 2.2.1” potrzebne, by spełnić przepisy obowiązujące od 2025 i umożliwić rozszerzenia:
- dodatkowe moduły, pola i wartości dla części enumów (rozszerzenia);
- obiekt `Parking` (m.in. przydatność dla pojazdów ciężarowych i osób z niepełnosprawnościami);
- informacje o EVSE dla osób z niepełnosprawnościami;
- struktury podatkowe Ameryki Północnej;
- wartości enumów z projektu OCPI 3.0, w tym oznaczające obsługę ISO 15118;
- pole w obiekcie Credentials z `party_id` huba (połączenie platform z obsługą huba z platformami bez niej);
- nowy moduł Payments.

2.2 względem 2.1.1 wprowadziło m.in. huby, nagłówki routingu, Hub Client Info, platformy z wieloma rolami,
Charging Profiles, credit CDR i `CancelReservation` `[OCPI230 §1.3.1]`.

## Role `[OCPI230 §2.3]`
CPO, eMSP, NAP (krajowa baza punktów, dane są do niej wysyłane i z niej pobierane), NSP (informacja o lokalizacjach),
Roaming Hub, SCSP (smart charging), PTP (operator systemu terminali płatniczych), PSP (usługi acquiringu).
Od 2.2 OCPI opisuje **platformy**: platforma nie jest rolą, tylko obsługuje jedną lub wiele ról. Hub też jest platformą.

## Typowe moduły per rola `[OCPI230 §2.3.1]`
Tabela „typical”, a nie wymagania (Sender / Receiver / Both). Odczytana z PDF, strona 9.

| Moduł | CPO | eMSP | Hub | NSP | NAP | SCSP | PTP |
|---|---|---|---|---|---|---|---|
| CDRs | Sender | Receiver | Both | | | | Receiver |
| Charging Profiles | Receiver | | Both | | | Sender | |
| Commands | Receiver | Sender | Both | | | | Sender |
| Credentials | Both | Both | Both | Both | Both | Both | Both |
| Hub Client Info | Receiver | Receiver | Sender | Receiver | Receiver | Receiver | |
| Locations | Sender | Receiver | Both | Receiver | Both | | Receiver |
| Sessions | Sender | Receiver | Both | | | Receiver | Receiver |
| Tariffs | Sender | Receiver | Both | Receiver | Both | | Receiver |
| Tokens | Receiver | Sender | Both | | | | |
| Payments | Receiver | | | | | | Sender |
| Versions | Both | Both | Both | Both | Both | Both | Both |

## Topologie `[OCPI230 §3]`
Peer-to-peer (także wiele połączeń, wiele tych samych ról, role podwójne i mieszane), platformy przez hub oraz przez hub
i bezpośrednio jednocześnie (§3.1–3.8).

## Lokalizacja a OCPP `[OCPI230 §8.1.2–8.1.3]`
- OCPI ma model Location → EVSE → Connector (OCPP 2.0: Charge Point → EVSE → Connector). Przy mapowaniu OCPI preferuje
  **jedną Location dla grupy Charge Pointów** w tym samym miejscu.
- OCPP 1.x nie zna EVSE. Obejście z noty aplikacyjnej OCA: jedno „wirtualne” EVSE na złącze, a niedostępność złącza
  sprzętowego EVSE przenosi się na wszystkie jego wirtualne EVSE.

## Rozszerzenia EVRF (osobne dokumenty) `[EVRF-DL]`
- NAP extension 1.0 dla 2.3.0 i 3.0 (dane AFIR dla krajowych punktów dostępowych) `[OCPI-NAP]`; strona pobrań: „A 100%
  mapping onto OCPI is not possible” `[EVRF-DL]`;
- Tariff Simplification guidelines dla 2.3.0 `[OCPI-TSG]`;
- Accessibility extension dla 2.3.0 i 3.0;
- Booking module v1.1 dla 2.3.0;
- Direct Payment module dla 2.2.1 `[OCPI-DP]`.
Treść rozszerzeń nie jest opracowana w tym skillu. Przed odpowiedzią czytasz właściwy dokument.
