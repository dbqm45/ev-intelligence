# Ewaluacja skilli — claude-opus-5-5 — pozostale-skille

Data: 2026-11-07 · koszt: 4.58 USD · scenariusze: 49 · zaliczone: 40

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-billing-tariff-expert | 5 | 5/5 | 4/4 | 5/5 |
| ev-charging-operations-expert | 8 | 7/8 | 4/6 | 5/8 |
| ev-cpms-architect | 4 | 4/4 | 2/3 | 3/4 |
| ev-domain-expert | 4 | 3/4 | 3/3 | 3/4 |
| ev-energy-smart-charging-expert | 6 | 6/6 | 5/5 | 6/6 |
| ev-evse-diagnostics-expert | 4 | 4/4 | 3/3 | 4/4 |
| ev-evse-hardware-expert | 6 | 5/6 | 4/5 | 4/6 |
| ev-iso15118-pki-expert | 5 | 5/5 | 4/4 | 5/5 |
| ev-ocpp-expert | 7 | 6/7 | 5/6 | 5/7 |

## Niezaliczone

- `ev-charging-operations-expert/priorytety-alarmow`: brak: [['Faulted|StatusNotification|errorCode']]; zakazane: []
- `ev-charging-operations-expert/unlock-przy-trwajacej-sesji`: brak: [['SHOULD NOT|nie (powinno|służy|należy)[^.\\n]{0,60}(zatrzym|stop)']]; zakazane: []
- `ev-charging-operations-expert/raport-uptime-dla-inwestora`: routing → ev-domain-expert
- `ev-cpms-architect/brama-po-restarcie`: brak: [['BootNotification[^.\\n]{0,160}(SHOULD NOT|nie powinn\\w*|nie wysyła|tylko gdy|chyba że|unless)']]; zakazane: []
- `ev-domain-expert/dobor-persony`: routing → ev-domain-expert
- `ev-evse-hardware-expert/wymagania-sprzetowe-afir-dc`: brak: [['8 (stycznia|January) 2026|2026-01-08|08\\.01\\.2026'], ['1 (stycznia|January) 2027|2027-01-01|01\\.01\\.2027']]; zakazane: []
- `ev-evse-hardware-expert/klasy-mocy-ac5-dc120`: routing → ev-compliance-expert
- `ev-ocpp-expert/transaction-id-minus-1`: brak: [['StartTransaction(\\.conf|Response)?[^.\\n]{0,120}(nie dotar|nie (został|zostało) dostarcz|nie otrzyma|nie dostała|not deliver|zgubi)']]; zakazane: []
- `ev-ocpp-expert/identyfikator-stacji-url-auth`: routing → ev-iso15118-pki-expert
