# Ewaluacja skilli — claude-opus-5-5 — holdout-7-po-fali1

Data: 2026-11-27 · koszt: 3.83 USD · scenariusze: 30 · zaliczone: 25

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-billing-tariff-expert | 6 | 6/6 | 5/5 | 6/6 |
| ev-charging-operations-expert | 4 | 4/4 | 4/4 | 4/4 |
| ev-compliance-expert | 6 | 5/6 | 5/5 | 5/6 |
| ev-cpms-architect | 2 | 2/2 | 2/2 | 2/2 |
| ev-energy-smart-charging-expert | 5 | 5/5 | 3/4 | 4/5 |
| ev-evse-hardware-expert | 3 | 2/3 | 3/3 | 2/3 |
| ev-integration-architect | 4 | 4/4 | 1/3 | 2/4 |

## Niezaliczone

- `ev-compliance-expert/ho-comp-eichrecht-smv`: routing → ev-ocpp-expert
- `ev-integration-architect/ho-int-rozszerzenia`: brak: [['additionalProperties', 'nieznan\\w*\\s+pol\\w*[^.\\n]{0,30}odrzuc\\w*\\s+schemat', 'schemat\\w*[^.\\n]{0,40}odrzuc\\w*[^.\\n]{0,30}nieznan\\w*\\s+pol']]; zakazane: []
- `ev-integration-architect/ho-int-brama-naglowki`: brak: [['(now\\w*|unikaln\\w*|new|własn\\w*|inn\\w*)\\W.{0,40}X-Request-ID', 'X-Request-ID.{0,80}(now\\w*|nie\\s+(kopi|przepis)|unikaln|new)'], ['X-Correlation-ID.{0,80}(ten\\s+sam|tą\\s+samą|tę\\s+samą|takim\\s+samym|tym\\s+samym|same|bez\\s+zmian|niezmienion|zachow)', '(ten\\s+sam|tą\\s+samą|tę\\s+samą|same|zachow\\w*|przekaz\\w*\\s+bez\\s+zmian).{0,40}X-Correlation-ID', 'X-Correlation-ID`?\\s+(idzie|przechodzi|biegnie)[^.\\n]{0,40}(cał\\w*\\s+łańcuch|przez\\s+hub)']]; zakazane: []
- `ev-energy-smart-charging-expert/ho-en-16-fazy`: brak: [['napięci\\w*\\s+(nominaln|znamionow|ustawion|sieci|zadan)', 'nie\\s+(zmierzon|mierzon)', 'set\\s+voltage', 'line\\s+voltage', 'napięci\\w*\\W{1,5}(nominaln|znamionow)', 'nie\\s+używa\\s+się\\s+napięci\\w*\\s+zmierzon']]; zakazane: []
- `ev-evse-hardware-expert/ho-hw-capability-pnc`: routing → ev-iso15118-pki-expert
