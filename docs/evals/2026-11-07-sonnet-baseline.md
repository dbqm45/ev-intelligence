# Ewaluacje skilli — 2026-11-07 18:06

Przebiegów: 49 · koszt: $4.28 · zaliczone: 26/49

Uruchomienie = skill wczytany przy pytaniu, które do niego należy. Fałszywe = wczytany przy pytaniu sąsiedniego skilla. Treść = sprawdzenia wiedzy specyficznej w odpowiedzi (także bez uruchomienia).

| Skill | Model | Uruchomienie | Fałszywe | Treść | Zaliczone | Koszt |
|---|---|---|---|---|---|---|
| ev-charging-operations-expert | sonnet | 3/3 | 0/1 | 2/3 | 3/4 | $0.79 |
| ev-charging-operations-expert | sonnet (bez skilli) | 0/3 | 0/0 | 3/3 | 0/3 | $0.16 |
| ev-cpms-architect | sonnet | 3/3 | 0/1 | 3/3 | 4/4 | $0.41 |
| ev-cpms-architect | sonnet (bez skilli) | 0/3 | 0/0 | 2/3 | 0/3 | $0.18 |
| ev-domain-expert | sonnet | 3/3 | 0/1 | 3/3 | 4/4 | $0.38 |
| ev-domain-expert | sonnet (bez skilli) | 0/3 | 0/0 | 0/3 | 0/3 | $0.21 |
| ev-evse-diagnostics-expert | sonnet | 3/3 | 0/1 | 3/3 | 4/4 | $0.36 |
| ev-evse-diagnostics-expert | sonnet (bez skilli) | 0/3 | 0/0 | 1/3 | 0/3 | $0.16 |
| ev-evse-hardware-expert | sonnet | 3/3 | 0/1 | 3/3 | 4/4 | $0.38 |
| ev-evse-hardware-expert | sonnet (bez skilli) | 0/3 | 0/0 | 2/3 | 0/3 | $0.18 |
| ev-ocpi-roaming-expert | sonnet | 3/3 | 0/1 | 3/3 | 4/4 | $0.36 |
| ev-ocpi-roaming-expert | sonnet (bez skilli) | 0/3 | 0/0 | 2/3 | 0/3 | $0.14 |
| ev-ocpp-expert | sonnet | 3/3 | 0/1 | 2/3 | 3/4 | $0.43 |
| ev-ocpp-expert | sonnet (bez skilli) | 0/3 | 0/0 | 3/3 | 0/3 | $0.15 |

## Protokół: wynik czy koszt

Główny wynik: zadania zaliczone w całości (odpowiedź spełnia wszystkie kryteria — ta sama miara w obu ramionach). Uruchomienie: skill wczytany. Średnia kryteriów to diagnostyka. Koszt na rozwiązane zadanie obejmuje wszystkie przebiegi ramienia. Niestabilne: scenariusz z różnym wynikiem między powtórzeniami (--repeats). Holdout to zamknięty zbiór — nie stroimy pod jego pytania.

| Model | Ramię | Zbiór | Zaliczone w całości | Uruchomienie | Średnia kryteriów | Koszt | Koszt na rozwiązane | Niestabilne |
|---|---|---|---|---|---|---|---|---|
| sonnet | ze skillami | strojenie | 19/21 (90%) | 21/21 | 98% | $2.24 | $0.118 | 0 |
| sonnet | bez skilli | strojenie | 13/21 (62%) | — | 87% | $1.17 | $0.090 | 0 |

## Niezaliczone

- `ev-charging-operations-expert` / priorytety-alarmow / sonnet: brak: Faulted — użyte skille: ev-charging-operations-expert, ev-ocpp-expert
- `ev-ocpp-expert` / heartbeat-wykrywanie-offline / sonnet: brak: OCPPCommCtrlr|Device Model|SetVariables|ChangeConfiguration — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / online-sesja-nie-startuje / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / priorytety-alarmow / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / restart-stacji-z-sesjami / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / model-statusow-wlasne-i-roaming / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / brama-po-restarcie / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / onboarding-pending / sonnet (bez skilli): nie uruchomił się
- `ev-domain-expert` / heartbeat-dobor-domen / sonnet (bez skilli): nie uruchomił się
- `ev-domain-expert` / luka-p3-refundacja / sonnet (bez skilli): nie uruchomił się
- `ev-domain-expert` / norma-vs-praktyka / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / deklaracja-vs-certyfikat / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / ramka-niezgodna / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / rejestr-odchylen / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / wymagania-sprzetowe-afir-dc / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / typ-zlacza-ocpp-ocpi / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / karta-urzadzenia / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / start-session-bez-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / credentials-401 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / sync-po-awarii / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / remote-start-accepted-bez-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / korelacja-remote-start-201 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / heartbeat-wykrywanie-offline / sonnet (bez skilli): nie uruchomił się
