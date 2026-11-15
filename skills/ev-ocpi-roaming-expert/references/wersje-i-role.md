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

## Rewizje dokumentu: 2.2.1 → 2.2.1-d2 `[OCPI221 §1.1]` `[OCPI221 §17.1]`
- 2.2.1-d2 to „documentation release”: nie zmienia wymagań wobec 2.2.1, tylko opisuje je jaśniej `[OCPI221 §1.1]`.
- Zmiany według changelogu `[OCPI221 §17.1]` (ta sama lista w `[OCPI230 §18.2]`), m.in.:
  - przeredagowana i przepisana dokumentacja Tariffs i `step_size`;
  - usunięty z modułu CDRs wymóg, by każdy `charging_period` miał inną taryfę (sprzeczny z innymi zdaniami modułu);
  - nota wyjaśniająca Base64 w nagłówku `Authorization` i dokładniejszy opis kodowania;
  - wyjaśnienie, dlaczego moduł Tariffs nic nie mówi o zaokrąglaniu cen;
  - nota, że CPO powinni unikać sprzętowych identyfikatorów jako `EVSE.uid`;
  - bardziej praktyczna rada, jak ustawić `role` w obiekcie Endpoint dla modułu credentials;
  - eMSP może zastąpić `session_id` nadany przez CPO przy wymianie profili ładowania ze SCSP;
  - przykłady bez końcowych ukośników w URL, poprawione przykłady i diagramy (m.in. „GET” → „PUT” na diagramie
    Broadcast Push).
- `[OCPI221-CH]` opisuje zmiany **2.2 → 2.2.1** (np. kod 4000, `country_code` i `party_id` w `CdrToken`), a nie
  2.2.1 → d2. Te same zmiany są w `[OCPI221 §17.2]`.
- Treści pierwotnego dokumentu 2.2.1 (sprzed d2) w rejestrze nie ma. Porównań „2.2.1 vs d2” poza changelogiem nie da
  się sprawdzić.
- Tagów i edycji repozytorium github.com/ocpi/ocpi rejestr nie obejmuje. Nie są tu opisane.

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

Changelog 2.2.1-d2 → 2.3.0 `[OCPI230 §18.1]` dodaje do tej listy pole EVSE z kontraktami eMSP, które są akceptowane,
i pole Location z numerem telefonu wsparcia.

### Hub w Credentials: 2.3.0 a 2.2.1
| | 2.2.1 `[OCPI221 §7.3.1]` | 2.3.0 `[OCPI230 §7.3.1]` |
|---|---|---|
| `hub_party_id` | brak pola | `CiString(5)`, opcjonalne: kod kraju (2) i `party_id` (3) huba sklejone w jeden ciąg |
| `roles` huba | „A Hub SHALL only reports itself as role: Hub” i SHALL NOT zgłaszać tam innych stron | platformy huba „are expected to include” w `roles` strony osiągalne przez hub |
| strony za hubem | SHALL być raportowane przez moduł HubClientInfo | w `roles`; moduł HubClientInfo nadal istnieje `[OCPI230 §15]` |
| obowiązek | — | platforma z funkcją huba i nagłówkami routingu SHALL podać kraj i party ID huba w `hub_party_id` |
Cel pola według §1.1: platformy z obsługą huba mogą łączyć się z platformami, które funkcji huba nie implementują.
Changelog: „make hub clients be reported as normal credentials roles” `[OCPI230 §18.1]`. W 2.3.0 zdanie o braku związku
`party_id` z EVSE ID i Contract ID mówi o formacie „eMI3/IDACS”, a w 2.2.1 o „eMI3”.

### Migracja 2.2.1 → 2.3.0 (Wniosek)
Procedura wyprowadzona z cytowanych faktów, nie wymaganie specyfikacji:
1. Najpierw parser i walidatory tolerujące nieznane pola i nieznane wartości `OpenEnum`. W 2.3.0 odrzucanie z powodu
   nieopisanych pól jest zabronione `[OCPI230 §4.1.8]`, a 2.2.1 tej reguły nie ma (`references/transport.md`).
2. Obie platformy wystawiają 2.3.0 w endpoint versions. Jedna wysyła PUT na credentials **w wersji 2.3.0**. PUT przełącza
   połączenie na wersję, do której należy endpoint, a serwer pobiera endpointy na nowo `[OCPI230 §7.1.2]`
   `[OCPI230 §7.2.3]`.
3. Hub: wypełnia `hub_party_id` i raportuje strony w `roles` `[OCPI230 §7.3.1]`. Partnerzy na 2.2.1 dalej dostają
   strony przez HubClientInfo `[OCPI221 §7.3.1]`.
4. Rejestr partnerów: partner, `country_code`/`party_id`, uzgodniona wersja i data PUT credentials.
Specyfikacja nie opisuje równoległego utrzymywania połączeń 2.2.1 i 2.3.0 z tym samym partnerem.


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

## Versions: wersje i endpointy `[OCPI230 §6]`
- Moduł konfiguracyjny i punkt startowy połączenia. CPO i eMSP MUST implementować oba endpointy: version information
  i version details `[OCPI230 §6.1]` `[OCPI230 §6.2]`.
- Struktura URL jest dowolna. Dokładny adres endpointu versions przekazuje się partnerowi poza OCPI (offline)
  `[OCPI230 §6.1]`.
- Version information: lista `Version` (`version`, `url`) `[OCPI230 §6.1.2]`. Version details: `version` i lista
  `Endpoint` (`identifier`, `role`, `url`) `[OCPI230 §6.2.1–6.2.2]`.
- `role` (`InterfaceRole`): `SENDER` (interfejs właściciela danych, z którego Receiver robi pull) albo `RECEIVER`
  (interfejs odbiorcy, na który Sender robi push) `[OCPI230 §6.2.3]`. Pole wprowadziło OCPI 2.2 `[OCPI230 §6.2]`.
- Dla modułu credentials `role` nie ma znaczenia. Zalecane: wysyłać `SENDER` dla własnego endpointu i ignorować `role`
  w endpointach credentials innych platform `[OCPI230 §6.2.2]`.
- Strona, która jest CPO i eMSP (albo hub), może wystawić jeden endpoint wersji dla obu ról. Dwie takie strony
  potrzebują jednego połączenia OCPI `[OCPI230 §6.2]`.
- `ModuleID`: wymagany jest tylko `credentials`, pozostałe moduły są opcjonalne, choć mogą od siebie zależeć
  `[OCPI230 §6.2.4]`. `VersionNumber`: 2.0, 2.1 (DEPRECATED), 2.1.1, 2.2 (DEPRECATED), 2.2.1, 2.3.0 `[OCPI230 §6.2.5]`.
- Moduły własne: rozszerzenie `ModuleID`, wysyłane MAY tylko partnerom z umową na ten moduł. Zalecany prefiks, np.
  kod kraju + `party_id` (`nltnm-tokens`) `[OCPI230 §6.2.5.1]`.
- Zmiana listy endpointów w bieżącej wersji: PUT na credentials partnera w tej wersji, a partner pobiera endpointy
  ponownie `[OCPI230 §6.2]` `[OCPI230 §7.1.3]`.
- Przejście na nowszą wersję: gdy obie platformy ją wdrożyły, jedna wysyła PUT na endpoint credentials drugiej w nowej
  wersji `[OCPI230 §7.1.2]`. PUT przełącza wersję, jeśli jest inna niż bieżąca. Serwer MUST pobrać endpointy klienta
  ponownie, także bez zmiany wersji, i wygenerować nowy credentials token. PUT od niezarejestrowanego klienta → HTTP
  405 `[OCPI230 §7.2.3]`.
Zdania z §6.2.2, §6.2.5.1 i §7.2.3 mają identyczne brzmienie w `[OCPI221]` (porównanie ciągów 2026-11-15). W 2.2.1
`ModuleID` i `VersionNumber` są typu `enum` `[OCPI221 §6.2.4–6.2.5]`, w 2.3.0 `OpenEnum`.

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
