# Ewaluacje skilli — 2026-11-07 18:48

Przebiegów: 100 · koszt: $7.30 · zaliczone: 36/100

Uruchomienie = skill wczytany przy pytaniu, które do niego należy. Fałszywe = wczytany przy pytaniu sąsiedniego skilla. Treść = sprawdzenia wiedzy specyficznej w odpowiedzi (także bez uruchomienia).

| Skill | Model | Uruchomienie | Fałszywe | Treść | Zaliczone | Koszt |
|---|---|---|---|---|---|---|
| ev-charging-operations-expert | sonnet | 4/10 | 0/0 | 8/10 | 4/10 | $1.07 |
| ev-charging-operations-expert | sonnet (bez skilli) | 0/10 | 0/0 | 4/10 | 0/10 | $0.49 |
| ev-cpms-architect | sonnet | 4/6 | 0/0 | 4/6 | 4/6 | $0.63 |
| ev-cpms-architect | sonnet (bez skilli) | 0/6 | 0/0 | 4/6 | 0/6 | $0.32 |
| ev-domain-expert | sonnet | 5/6 | 0/0 | 6/6 | 5/6 | $0.62 |
| ev-domain-expert | sonnet (bez skilli) | 0/6 | 0/0 | 0/6 | 0/6 | $0.46 |
| ev-evse-diagnostics-expert | sonnet | 5/6 | 0/0 | 4/6 | 3/6 | $0.46 |
| ev-evse-diagnostics-expert | sonnet (bez skilli) | 0/6 | 0/0 | 2/6 | 0/6 | $0.25 |
| ev-evse-hardware-expert | sonnet | 6/6 | 0/0 | 4/6 | 4/6 | $0.56 |
| ev-evse-hardware-expert | sonnet (bez skilli) | 0/6 | 0/0 | 0/6 | 0/6 | $0.26 |
| ev-ocpi-roaming-expert | sonnet | 6/6 | 0/0 | 6/6 | 6/6 | $0.51 |
| ev-ocpi-roaming-expert | sonnet (bez skilli) | 0/6 | 0/0 | 2/6 | 0/6 | $0.30 |
| ev-ocpp-expert | sonnet | 10/10 | 0/0 | 10/10 | 10/10 | $0.98 |
| ev-ocpp-expert | sonnet (bez skilli) | 0/10 | 0/0 | 5/10 | 0/10 | $0.39 |

## Protokół: wynik czy koszt

Główny wynik: zadania zaliczone w całości (odpowiedź spełnia wszystkie kryteria — ta sama miara w obu ramionach). Uruchomienie: skill wczytany. Średnia kryteriów to diagnostyka. Koszt na rozwiązane zadanie obejmuje wszystkie przebiegi ramienia. Niestabilne: scenariusz z różnym wynikiem między powtórzeniami (--repeats). Holdout to zamknięty zbiór — nie stroimy pod jego pytania.

| Model | Ramię | Zbiór | Zaliczone w całości | Uruchomienie | Średnia kryteriów | Koszt | Koszt na rozwiązane | Niestabilne |
|---|---|---|---|---|---|---|---|---|
| sonnet | ze skillami | holdout | 42/50 (84%) | 40/50 | 95% | $4.83 | $0.115 | 0 |
| sonnet | bez skilli | holdout | 17/50 (34%) | — | 71% | $2.47 | $0.145 | 5 |

## Niezaliczone

- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet: nie uruchomił się — użyte skille: ev-cpms-architect
- `ev-charging-operations-expert` / ho-ops-wylacz-evse-na-noc / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert, ev-cpms-architect
- `ev-cpms-architect` / ho-cpms-identyfikator-url / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-domain-expert` / ho-dom-model-zle-statusy / sonnet: nie uruchomił się — użyte skille: ev-evse-diagnostics-expert
- `ev-evse-diagnostics-expert` / ho-diag-schematy-z-biblioteki / sonnet: brak: oficjaln\w*; niepożądane: (to )?wystarczy — użyte skille: ev-evse-diagnostics-expert
- `ev-evse-hardware-expert` / ho-hw-klasy-mocy / sonnet: brak: (Medium|średni\w*) — użyte skille: ev-evse-hardware-expert
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet: nie uruchomił się — użyte skille: ev-cpms-architect
- `ev-charging-operations-expert` / ho-ops-wylacz-evse-na-noc / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert, ev-cpms-architect
- `ev-cpms-architect` / ho-cpms-identyfikator-url / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-evse-diagnostics-expert` / ho-diag-schematy-z-biblioteki / sonnet: brak: oficjaln\w*; niepożądane: (to )?wystarczy — użyte skille: ev-evse-diagnostics-expert
- `ev-evse-diagnostics-expert` / ho-diag-co-rozstrzyga / sonnet: nie uruchomił się — użyte skille: ev-ocpp-expert
- `ev-evse-hardware-expert` / ho-hw-klasy-mocy / sonnet: brak: (Medium|średni\w*) — użyte skille: ev-evse-hardware-expert
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-evcommerror-faulted / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-wylacz-evse-na-noc / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / ho-cpms-lc-utrata-stacji / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / ho-cpms-identyfikator-url / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / ho-cpms-datex / sonnet (bez skilli): nie uruchomił się
- `ev-domain-expert` / ho-dom-afir-minuta / sonnet (bez skilli): odczyt poza katalogiem testu (wynik bez skilli niewiarygodny): /root
- `ev-domain-expert` / ho-dom-pantograf / sonnet (bez skilli): nie uruchomił się
- `ev-domain-expert` / ho-dom-model-zle-statusy / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / ho-diag-schematy-z-biblioteki / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / ho-diag-firmware-inny-niz-cert / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / ho-diag-co-rozstrzyga / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-ac22-2026 / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-klasy-mocy / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-capability-pnc / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / ho-ocpi-request-correlation-id / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / ho-ocpi-4003-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / ho-ocpi-step-size-przyszlosc / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-seqno-57 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-evconnecttimeout / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-profil-rezerwacji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-call-naraz-sila / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-hard-reset-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-trigger-boot-po-reconnect / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-afir-minuta-status / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-evcommerror-faulted / sonnet (bez skilli): nie uruchomił się
- `ev-charging-operations-expert` / ho-ops-wylacz-evse-na-noc / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / ho-cpms-lc-utrata-stacji / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / ho-cpms-identyfikator-url / sonnet (bez skilli): nie uruchomił się
- `ev-cpms-architect` / ho-cpms-datex / sonnet (bez skilli): nie uruchomił się
- `ev-domain-expert` / ho-dom-afir-minuta / sonnet (bez skilli): odczyt poza katalogiem testu (wynik bez skilli niewiarygodny): /root/.claude
- `ev-domain-expert` / ho-dom-pantograf / sonnet (bez skilli): nie uruchomił się
- `ev-domain-expert` / ho-dom-model-zle-statusy / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / ho-diag-schematy-z-biblioteki / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / ho-diag-firmware-inny-niz-cert / sonnet (bez skilli): nie uruchomił się
- `ev-evse-diagnostics-expert` / ho-diag-co-rozstrzyga / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-ac22-2026 / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-klasy-mocy / sonnet (bez skilli): nie uruchomił się
- `ev-evse-hardware-expert` / ho-hw-capability-pnc / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / ho-ocpi-request-correlation-id / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / ho-ocpi-4003-kolejka / sonnet (bez skilli): nie uruchomił się
- `ev-ocpi-roaming-expert` / ho-ocpi-step-size-przyszlosc / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-heartbeatinterval-1-6 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-seqno-57 / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-evconnecttimeout / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-profil-rezerwacji / sonnet (bez skilli): nie uruchomił się
- `ev-ocpp-expert` / ho-ocpp-call-naraz-sila / sonnet (bez skilli): nie uruchomił się
