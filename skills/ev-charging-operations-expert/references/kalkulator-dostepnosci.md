# Kalkulator dostępności portów (`scripts/uptime_kpi.py`)

Źródła: 23 CFR 680 (eCFR, stan na 2026-11-24) `[US-23CFR680]`, AFIR w wersji skonsolidowanej `[AFIR]`, rozporządzenie
wykonawcze 2025/655 `[AFIR-655]`, ustawa o elektromobilności `[PL-EMOB]`, OCPP 2.0.1 `[201-P2]` `[201-APP]` i OCPP 1.6
`[16]`. Zdania **Wniosek** to rekomendacje wyprowadzone z cytowanych faktów. Zdania „wybór narzędzia” opisują decyzję
skryptu tam, gdzie tekst reguły czegoś nie określa. Te same wybory skrypt wypisuje w wyniku (`tool_choices`, „choice
of the tool, not the rule”).

## Spis treści
1. Do czego służy
2. Uruchomienie
3. Wejście
4. Wyjście i kody wyjścia
5. Reguły NEVI
6. Wybory narzędzia w trybie NEVI
7. Tryb informacyjny (AFIR, OCPP, Polska)
8. Ograniczenia

## 1. Do czego służy
- Tryb `nevi`: uptime każdego portu wzorem z 23 CFR 680.116(b), za 12 miesięcy kończących się miesiącem raportu,
  z progiem „greater than 97%”. Daje też T_outage, T_excluded i listę przestojów do raportu kwartalnego.
- Tryb `info`: udział minut „operational” w oknie i rozbicie minut „non-operational” według przyczyny. **To nie jest
  metryka prawna.** AFIR, 2025/655 i ustawa o elektromobilności nie definiują wskaźnika ani progu dostępności (pkt 7).
- Tylko biblioteka standardowa Pythona, bez sieci. Strefy czasowe z `zoneinfo` (na Windowsie potrzebny pakiet `tzdata`).

## 2. Uruchomienie
```bash
python3 skills/ev-charging-operations-expert/scripts/uptime_kpi.py <przedzialy.json|.csv> --mode nevi \
    --month 2026-10 [--months 3] [--tz UTC] [--gaps outage|error] [--map STATUS=up|outage ...] [--json]
python3 skills/ev-charging-operations-expert/scripts/uptime_kpi.py <przedzialy.json|.csv> --mode info \
    [--from ISO] [--to ISO] [--gaps outage|error] [--map STATUS=up|outage ...] [--json]
```
- `--month`: miesiąc raportu. Okno to 12 miesięcy kalendarzowych kończących się tym miesiącem.
- `--months 3`: trzy kolejne miesiące kończące się `--month`, czyli dane do raportu kwartalnego
  `[US-23CFR680 §680.112(a)(7)]`.
- `--tz`: strefa granic miesięcy (domyślnie UTC). Reguła jej nie określa.
- `--map`: mapowanie stanu spoza listy (np. `PAUSED=outage`) albo zmiana domyślnego (`offline=up`, `Reserved=outage`).
- Testy: `python3 -m unittest tests.test_uptime_kpi`.

## 3. Wejście
Lista przedziałów w JSON (`[...]` albo `{"intervals": [...]}`) albo CSV z nagłówkiem. Przedział to `[start, end)`.

| Pole | Wymagane | Znaczenie |
|---|---|---|
| `port` | tak | identyfikator portu; port ładuje jeden pojazd naraz, nawet z kilkoma złączami `[US-23CFR680 §680.104]` |
| `start`, `end` | tak | ISO 8601; bez strefy = UTC |
| `state` | tak | `up`, `outage`, `offline` albo status OCPP: `Available`, `Occupied`, `Reserved`, `Unavailable`, `Faulted` `[201-P2 §3.23]`; `Preparing`, `Charging`, `SuspendedEVSE`, `SuspendedEV`, `Finishing` `[16 §7.7]` |
| `cause` | nie | opis przyczyny (rozbicie w trybie `info`) |
| `exclusion` | nie | `utility`, `vehicle`, `maintenance`, `vandalism`, `disaster`, `outside_hours` (pkt 5); inna wartość = błąd wejścia |
| `evidence` | nie | odnośnik do dowodu (zgłoszenie do dostawcy energii, plan konserwacji, protokół policji) |
| `power_ok` | nie | `true`/`false`: port dostarczał energię z mocą minimalną z § 680.106(d) |

Przedziały jednego portu nie mogą się nakładać (błąd wejścia). Minuty bez przedziału to „bez danych” (pkt 6).

## 4. Wyjście i kody wyjścia
- `nevi`: dla każdego miesiąca i portu `uptime_pct`, `meets` (µ > 97), `t_outage_min`, `t_excluded_min`, `no_data_min`,
  `exclusion_without_evidence_min`, `below_min_power_min`. Dalej `outages_in_reported_months` (początek, koniec, czas
  każdego przestoju i ile z niego wyłączono `[US-23CFR680 §680.112(a)(8)]`), `below_threshold`, `tool_choices`,
  `warnings`.
- `info`: `operational_share_pct`, minuty `operational` / `non_operational` / bez danych, `availability_min`
  (`in_use`, `reserved`, `not_in_use`, `unspecified`), `non_operational_by_cause_min`, `legal_metric: null` i nota.
- Kod wyjścia: 0 (policzone; w `nevi` każdy port w każdym miesiącu powyżej 97 %), 1 (`nevi`: co najmniej jeden port
  w co najmniej jednym miesiącu nie powyżej 97 %), 2 (błąd wejścia: zły JSON/CSV, nieznany stan, nakładanie,
  `--gaps error` przy brakach, brak `--month`, nieznana strefa). Tryb `info` nie ma progu, więc nie zwraca 1.

## 5. Reguły NEVI
| Reguła | Źródło | W narzędziu |
|---|---|---|
| każdy port ma średni roczny uptime „greater than 97%” | `[US-23CFR680 §680.116(b)]` | porównanie ostre: 97,0000 nie spełnia |
| port jest „up”, gdy sprzęt i oprogramowanie są „online”, port jest dostępny albo w użyciu i dostarcza energię z mocą minimalną | `[US-23CFR680 §680.116(b)(1)]` | `power_ok: false` = przestój; brak `power_ok` = stan zadeklarowany, z ostrzeżeniem |
| moc minimalna: DCFC przy korytarzach AFC 150 kW na port na żądanie pojazdu, AC Level 2 6 kW na port | `[US-23CFR680 §680.106(d)]` | nie mierzy mocy; ocenę daje `power_ok` |
| uptime liczony co miesiąc za poprzednie dwanaście miesięcy | `[US-23CFR680 §680.116(b)(2)]` | okno 12 miesięcy kalendarzowych (pkt 6) |
| µ = ((525 600 − (T_outage − T_excluded)) / 525 600) × 100; T_outage = minuty przestoju w poprzednim roku | `[US-23CFR680 §680.116(b)(3)]` | tak, podstawa 525 600 zawsze |
| T_excluded: przerwy w dostawie energii, wina pojazdu, planowana konserwacja, wandalizm, klęski żywiołowe, „provided that the charging station operator can demonstrate that the charging port would otherwise be operational” | `[US-23CFR680 §680.116(b)(3)]` | wyłączenie tylko z niepustym `evidence` |
| „Also excluded are hours outside of the identified hours of operation of the charging station” | `[US-23CFR680 §680.116(b)(3)]` | `outside_hours`, bez `evidence` (pkt 6) |
| raport kwartalny: uptime, T_outage i T_excluded za każdy z 3 poprzednich miesięcy oraz czas każdego przestoju | `[US-23CFR680 §680.112(a)]` | `--months 3`, `outages_in_reported_months` |

Rozbieżności i miejsca do interpretacji w tekście:
- „Average annual uptime” `[US-23CFR680 §680.116(b)]` i „calculated on a monthly basis for the previous twelve months”
  `[US-23CFR680 §680.116(b)(2)]`. Tekst nie mówi, czy „średnia” to µ z okna 12 miesięcy, czy średnia z 12 wartości
  miesięcznych. Wzór operuje na minutach „in previous year”, więc narzędzie porównuje z progiem µ okna.
- „Online” w § 680.116(b)(1) a § 680.114(e): ładowarka ma rozpoczynać i kończyć sesje z mocą minimalną także przy
  przerwie w łączności z siecią `[US-23CFR680 §680.114(e)]`. Tekst nie rozstrzyga, czy port bez łączności z CSMS, który
  ładuje, jest „up”. Narzędzie domyślnie liczy `offline` jako przestój; `--map offline=up`, gdy masz dowód ładowania.
- Stacje przy korytarzach AFC mają być dostępne 24/7, pozostałe co najmniej w godzinach pracy gospodarza lokalizacji
  `[US-23CFR680 §680.106(e)]`. **Wniosek:** `outside_hours` dotyczy w praktyce stacji poza korytarzami; godziny pracy
  stacji to też pole danych dla stron trzecich `[US-23CFR680 §680.116(c)(7)]`.

## 6. Wybory narzędzia w trybie NEVI
Tekst reguły tego nie określa. Każdy punkt jest w wyniku jako `tool_choices`:
- **Okno:** 12 miesięcy kalendarzowych kończących się miesiącem raportu, granice miesięcy w `--tz` (domyślnie UTC).
- **Minuty:** sekundy liczone dokładnie, części minut jako ułamki. Bez zaokrąglania przed porównaniem z progiem.
  Wynik ma 4 miejsca po przecinku. Reguła nie podaje zaokrąglania.
- **Rok przestępny:** okno z 29 lutego ma 527 040 minut, a wzór używa 525 600. Narzędzie stosuje wzór dosłownie
  i ostrzega.
- **Dowód wyłączenia:** pięć przyczyn wymaga niepustego `evidence`. Bez niego minuty zostają w T_outage, z ostrzeżeniem.
  Narzędzie nie ocenia, czy dowód wystarcza. `outside_hours` nie wymaga dowodu: zastrzeżenie o wykazaniu stoi w zdaniu
  z pięcioma przyczynami, a godziny pracy są w osobnym zdaniu. Wyłączane są tylko minuty przestoju, więc
  T_excluded ≤ T_outage, a µ ≤ 100.
- **Stany:** statusy Operative OCPP = up, Inoperative (`Unavailable`, `Faulted`) = przestój `[201-P2 §3.23]` `[16 §7.7]`.
  `Reserved` i `SuspendedEVSE` = up z ostrzeżeniem (`SuspendedEVSE` to m.in. brak energii z ograniczenia smart charging
  albo zasilania `[16 §7.7]`, czyli możliwy brak mocy minimalnej). `offline` = przestój.
- **Braki danych:** minuty bez przedziału = przestój (`--gaps outage`) albo błąd wejścia (`--gaps error`).

## 7. Tryb informacyjny (AFIR, OCPP, Polska)
- AFIR wymaga danych dynamicznych „Operational status” i „Availability” `[AFIR art. 20 ust. 2 lit. f]`, aktualizowanych
  najpóźniej minutę po zmianie `[AFIR-655 art. 2]`. Procentu dostępności ani progu AFIR i 2025/655 nie zawierają.
- Operational: „can be used in normal conditions during the opening time that is accessible to the public”;
  non-operational: „cannot be used due to a technical problem or maintenance works”. Availability: in use, reserved,
  not in use `[AFIR-655 Annex, tabela F]`.
- „Availability of data” to „the existence of data in a digital machine-readable format” `[AFIR art. 2 pkt 9]`.
  Dotyczy danych, nie ładowarki.
- OCPP 2.0.1: Operative = `Available`, `Reserved`, `Occupied`; Inoperative = `Unavailable`, `Faulted`
  `[201-P2 §3.23]`. Zmienna `AvailabilityState` powtarza wartości `ConnectorStatus` `[201-APP §4]`, a stacja może ją
  wysłać w `NotifyEventRequest` zamiast `StatusNotificationRequest` `[201-P2 G01]`. OCPP 1.6: Operative = `Available`,
  `Preparing`, `Charging`, `SuspendedEVSE`, `SuspendedEV`, `Finishing`, `Reserved` `[16 §7.7]`.
- Polska: rejestr EIPA zawiera dostępność punktów ładowania `[PL-EMOB art. 42 ust. 3]`, a operator przekazuje ją
  „natychmiast po zmianie stanu dostępności” `[PL-EMOB art. 42 ust. 6]`. Ustawa nie definiuje wskaźnika dostępności
  ani progu.
- Wybory narzędzia: Operative OCPP = operational AFIR; `Occupied`, `Preparing`, `Charging`, `Suspended*`, `Finishing`
  = in use; `Reserved` = reserved; `Available` = not in use; `up` bez statusu = „unspecified”; `offline` =
  non-operational. Okno domyślnie od najwcześniejszego początku do najpóźniejszego końca danych. Przyczyna
  przestoju: `cause`, potem `exclusion`, potem `state`; braki danych jako `no_data`.

**Wniosek:** udział „operational” z trybu `info` możesz pokazać w raporcie dla inwestora albo w SLA, ale opisz go jako
miarę umowną. Podstawy prawnej w UE i w Polsce dla takiego wskaźnika nie ma w zarejestrowanych źródłach.

## 8. Ograniczenia
- Narzędzie nie mierzy mocy ani nie ocenia dowodów. `power_ok` i `evidence` są deklaracją z danych wejściowych.
- Nie składa statusów złączy w status portu. Dla EVSE z kilkoma złączami przygotuj jeden przedział na port.
- Nie wylicza godzin pracy stacji z harmonogramu. Przedziały poza godzinami podajesz z `exclusion: outside_hours`.
- Nie liczy MTTR, MTBF ani skuteczności sesji (23 CFR 680 ich nie definiuje).
- Nie tworzy pliku raportu do FHWA. Format przekazu określa FHWA („in a manner prescribed by the FHWA”)
  `[US-23CFR680 §680.112(a)]`, a tego formatu nie ma w rejestrze źródeł.
- Status prawny eCFR jest w rejestrze oznaczony jako niesprawdzony (`sources/us-prawo.yaml`).
