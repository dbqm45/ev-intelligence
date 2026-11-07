# Ewaluacje skilli — 2026-11-07 18:13

Przebiegów: 30 · koszt: $2.32 · zaliczone: 12/30

Uruchomienie = skill wczytany przy pytaniu, które do niego należy. Fałszywe = wczytany przy pytaniu sąsiedniego skilla. Treść = sprawdzenia wiedzy specyficznej w odpowiedzi (także bez uruchomienia).

| Skill | Model | Uruchomienie | Fałszywe | Treść | Zaliczone | Koszt |
|---|---|---|---|---|---|---|
| ev-charging-operations-expert | sonnet | 5/7 | 0/1 | 5/7 | 6/8 | $0.90 |
| ev-charging-operations-expert | sonnet (bez skilli) | 0/7 | 0/0 | 5/7 | 0/7 | $0.33 |
| ev-ocpp-expert | sonnet | 7/7 | 0/1 | 5/7 | 6/8 | $0.78 |
| ev-ocpp-expert | sonnet (bez skilli) | 0/7 | 0/0 | 3/7 | 0/7 | $0.31 |

## Protokół: wynik czy koszt

Główny wynik: zadania zaliczone w całości (odpowiedź spełnia wszystkie kryteria — ta sama miara w obu ramionach). Uruchomienie: skill wczytany. Średnia kryteriów to diagnostyka. Koszt na rozwiązane zadanie obejmuje wszystkie przebiegi ramienia. Niestabilne: scenariusz z różnym wynikiem między powtórzeniami (--repeats). Holdout to zamknięty zbiór — nie stroimy pod jego pytania.

| Model | Ramię | Zbiór | Zaliczone w całości | Uruchomienie | Średnia kryteriów | Koszt | Koszt na rozwiązane | Niestabilne |
|---|---|---|---|---|---|---|---|---|
| sonnet | ze skillami | holdout | 3/6 (50%) | 4/6 | 88% | $0.61 | $0.203 | 0 |
| sonnet | ze skillami | strojenie | 7/8 (88%) | 8/8 | 98% | $0.77 | $0.110 | 0 |
| sonnet | bez skilli | holdout | 2/6 (33%) | — | 75% | $0.27 | $0.135 | 0 |
| sonnet | bez skilli | strojenie | 6/8 (75%) | — | 95% | $0.37 | $0.062 | 0 |

## Luka strojenie − holdout

Zaliczone w całości ze skillami na zbiorze strojenia minus na holdoucie. Duża luka znaczy, że opisy i treść skilli dopasowały się do pytań, na których je stroimy. Przewaga = ze skillami minus bez skilli w tym samym zbiorze; różnica przewag nie zależy od trudności pytań. Zmianę skilla przyjmujemy, gdy poprawia strojenie i nie pogarsza holdoutu.

| Model | Strojenie | Holdout | Luka | Przewaga skilli: strojenie | Przewaga skilli: holdout |
|---|---|---|---|---|---|
| sonnet | 88% | 50% | +38% | +12% | +17% |

## Niezaliczone

- `ev-ocpp-expert` / transaction-id-minus-1 / sonnet: brak: errat\w* — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet: nie uruchomił się — użyte skille: ev-cpms-architect
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet: brak: errat\w* — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / online-sesja-nie-startuje / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / priorytety-alarmow / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / restart-stacji-z-sesjami / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / unlock-przy-trwajacej-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / remote-start-accepted-bez-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / korelacja-remote-start-201 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / heartbeat-wykrywanie-offline / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / transaction-id-minus-1 / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-seqno-57 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-evconnecttimeout / sonnet (bez skilli): nie uruchomił się
