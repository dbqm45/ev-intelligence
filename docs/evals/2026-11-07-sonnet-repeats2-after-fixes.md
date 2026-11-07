# Ewaluacje skilli — 2026-11-07 18:29

Przebiegów: 84 · koszt: $6.80 · zaliczone: 39/84

Uruchomienie = skill wczytany przy pytaniu, które do niego należy. Fałszywe = wczytany przy pytaniu sąsiedniego skilla. Treść = sprawdzenia wiedzy specyficznej w odpowiedzi (także bez uruchomienia).

| Skill | Model | Uruchomienie | Fałszywe | Treść | Zaliczone | Koszt |
|---|---|---|---|---|---|---|
| ev-charging-operations-expert | sonnet | 12/16 | 0/4 | 13/16 | 15/20 | $2.25 |
| ev-charging-operations-expert | sonnet (bez skilli) | 0/16 | 0/0 | 10/16 | 0/16 | $0.86 |
| ev-cpms-architect | sonnet | 5/6 | 0/2 | 6/6 | 7/8 | $0.87 |
| ev-cpms-architect | sonnet (bez skilli) | 0/6 | 0/0 | 4/6 | 0/6 | $0.34 |
| ev-ocpp-expert | sonnet | 16/16 | 0/2 | 15/16 | 17/18 | $1.79 |
| ev-ocpp-expert | sonnet (bez skilli) | 0/16 | 0/0 | 10/16 | 0/16 | $0.69 |

## Protokół: wynik czy koszt

Główny wynik: zadania zaliczone w całości (odpowiedź spełnia wszystkie kryteria — ta sama miara w obu ramionach). Uruchomienie: skill wczytany. Średnia kryteriów to diagnostyka. Koszt na rozwiązane zadanie obejmuje wszystkie przebiegi ramienia. Niestabilne: scenariusz z różnym wynikiem między powtórzeniami (--repeats). Holdout to zamknięty zbiór — nie stroimy pod jego pytania.

| Model | Ramię | Zbiór | Zaliczone w całości | Uruchomienie | Średnia kryteriów | Koszt | Koszt na rozwiązane | Niestabilne |
|---|---|---|---|---|---|---|---|---|
| sonnet | ze skillami | holdout | 8/12 (67%) | 8/12 | 92% | $1.20 | $0.150 | 2 |
| sonnet | ze skillami | strojenie | 26/26 (100%) | 25/26 | 100% | $2.57 | $0.099 | 0 |
| sonnet | bez skilli | holdout | 7/12 (58%) | — | 83% | $0.58 | $0.083 | 3 |
| sonnet | bez skilli | strojenie | 17/26 (65%) | — | 93% | $1.32 | $0.077 | 5 |

## Luka strojenie − holdout

Zaliczone w całości ze skillami na zbiorze strojenia minus na holdoucie. Duża luka znaczy, że opisy i treść skilli dopasowały się do pytań, na których je stroimy. Przewaga = ze skillami minus bez skilli w tym samym zbiorze; różnica przewag nie zależy od trudności pytań. Zmianę skilla przyjmujemy, gdy poprawia strojenie i nie pogarsza holdoutu.

| Model | Strojenie | Holdout | Luka | Przewaga skilli: strojenie | Przewaga skilli: holdout |
|---|---|---|---|---|---|
| sonnet | 100% | 67% | +33% | +35% | +8% |

## Niezaliczone

- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet: nie uruchomił się — użyte skille: ev-cpms-architect
- `ev-cpms-architect` / onboarding-pending / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet: brak: last resort|ostateczn\w* — użyte skille: ev-charging-operations-expert, ev-ocpp-expert
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet: nie uruchomił się — użyte skille: ev-cpms-architect
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet: brak: errat\w* — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / online-sesja-nie-startuje / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / priorytety-alarmow / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / restart-stacji-z-sesjami / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / unlock-przy-trwajacej-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / raport-uptime-dla-inwestora / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / model-statusow-wlasne-i-roaming / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / brama-po-restarcie / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / onboarding-pending / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / remote-start-accepted-bez-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / korelacja-remote-start-201 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / heartbeat-wykrywanie-offline / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / transaction-id-minus-1 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / odswiez-dane-trigger-boot / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-seqno-57 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-evconnecttimeout / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / online-sesja-nie-startuje / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / priorytety-alarmow / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / restart-stacji-z-sesjami / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / unlock-przy-trwajacej-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / raport-uptime-dla-inwestora / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / model-statusow-wlasne-i-roaming / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / brama-po-restarcie / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / onboarding-pending / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / remote-start-accepted-bez-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / korelacja-remote-start-201 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / heartbeat-wykrywanie-offline / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / transaction-id-minus-1 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / odswiez-dane-trigger-boot / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-seqno-57 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-evconnecttimeout / sonnet (bez skilli): nie uruchomił się
