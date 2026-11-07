# Ewaluacje skilli — 2026-11-07 19:22

Przebiegów: 124 · koszt: $9.40 · zaliczone: 61/124

Uruchomienie = skill wczytany przy pytaniu, które do niego należy. Fałszywe = wczytany przy pytaniu sąsiedniego skilla. Treść = sprawdzenia wiedzy specyficznej w odpowiedzi (także bez uruchomienia).

| Skill | Model | Uruchomienie | Fałszywe | Treść | Zaliczone | Koszt |
|---|---|---|---|---|---|---|
| ev-charging-operations-expert | sonnet | 18/22 | 0/4 | 22/22 | 22/26 | $2.81 |
| ev-charging-operations-expert | sonnet (bez skilli) | 0/22 | 0/0 | 12/22 | 0/22 | $1.03 |
| ev-evse-hardware-expert | sonnet | 14/14 | 0/2 | 14/14 | 16/16 | $1.58 |
| ev-evse-hardware-expert | sonnet (bez skilli) | 0/14 | 0/0 | 6/14 | 0/14 | $0.67 |
| ev-ocpp-expert | sonnet | 22/22 | 0/2 | 21/22 | 23/24 | $2.38 |
| ev-ocpp-expert | sonnet (bez skilli) | 0/22 | 0/0 | 14/22 | 0/22 | $0.93 |

## Protokół: wynik czy koszt

Główny wynik: zadania zaliczone w całości (odpowiedź spełnia wszystkie kryteria — ta sama miara w obu ramionach). Uruchomienie: skill wczytany. Średnia kryteriów to diagnostyka. Koszt na rozwiązane zadanie obejmuje wszystkie przebiegi ramienia. Niestabilne: scenariusz z różnym wynikiem między powtórzeniami (--repeats). Holdout to zamknięty zbiór — nie stroimy pod jego pytania.

| Model | Ramię | Zbiór | Zaliczone w całości | Uruchomienie | Średnia kryteriów | Koszt | Koszt na rozwiązane | Niestabilne |
|---|---|---|---|---|---|---|---|---|
| sonnet | ze skillami | holdout | 25/26 (96%) | 22/26 | 99% | $2.52 | $0.101 | 1 |
| sonnet | ze skillami | strojenie | 32/32 (100%) | 32/32 | 100% | $3.18 | $0.099 | 0 |
| sonnet | bez skilli | holdout | 11/26 (42%) | — | 78% | $1.06 | $0.096 | 3 |
| sonnet | bez skilli | strojenie | 21/32 (66%) | — | 90% | $1.57 | $0.075 | 3 |

## Luka strojenie − holdout

Zaliczone w całości ze skillami na zbiorze strojenia minus na holdoucie. Duża luka znaczy, że opisy i treść skilli dopasowały się do pytań, na których je stroimy. Przewaga = ze skillami minus bez skilli w tym samym zbiorze; różnica przewag nie zależy od trudności pytań. Zmianę skilla przyjmujemy, gdy poprawia strojenie i nie pogarsza holdoutu.

| Model | Strojenie | Holdout | Luka | Przewaga skilli: strojenie | Przewaga skilli: holdout |
|---|---|---|---|---|---|
| sonnet | 100% | 96% | +4% | +34% | +54% |

## Niezaliczone

- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet: nie uruchomił się — użyte skille: ev-cpms-architect
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet: brak: errat\w* — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet: nie uruchomił się — użyte skille: ev-cpms-architect
- `ev-charging-operations-expert` / online-sesja-nie-startuje / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / priorytety-alarmow / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / restart-stacji-z-sesjami / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / unlock-przy-trwajacej-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / raport-uptime-dla-inwestora / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / noc-severity1-jedno-evse / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / wymagania-sprzetowe-afir-dc / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / typ-zlacza-ocpp-ocpi / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / karta-urzadzenia / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / klasy-mocy-ac5-dc120 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / remote-start-accepted-bez-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / korelacja-remote-start-201 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / heartbeat-wykrywanie-offline / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / transaction-id-minus-1 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / odswiez-dane-trigger-boot / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / identyfikator-stacji-url-auth / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-evcommerror-faulted / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-wylacz-evse-na-noc / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-ac22-2026 / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-klasy-mocy / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-capability-pnc / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-seqno-57 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-evconnecttimeout / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-profil-rezerwacji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-call-naraz-sila / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / online-sesja-nie-startuje / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / priorytety-alarmow / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / restart-stacji-z-sesjami / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / unlock-przy-trwajacej-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / raport-uptime-dla-inwestora / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / noc-severity1-jedno-evse / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / wymagania-sprzetowe-afir-dc / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / typ-zlacza-ocpp-ocpi / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / karta-urzadzenia / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / klasy-mocy-ac5-dc120 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / remote-start-accepted-bez-sesji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / korelacja-remote-start-201 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / heartbeat-wykrywanie-offline / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / transaction-id-minus-1 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / odswiez-dane-trigger-boot / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / identyfikator-stacji-url-auth / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-evcommerror-faulted / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-wylacz-evse-na-noc / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-ac22-2026 / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-klasy-mocy / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-capability-pnc / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-seqno-57 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-evconnecttimeout / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-profil-rezerwacji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-call-naraz-sila / sonnet (bez skilli): nie uruchomił się
