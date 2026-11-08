# Ewaluacja skilli — claude-opus-5-5 — holdout-po-taksonomii-1-2

Data: 2026-11-08 · koszt: 1.93 USD · scenariusze: 28 · zaliczone: 22

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-charging-operations-expert | 4 | 3/4 | 4/4 | 3/4 |
| ev-compliance-expert | 6 | 6/6 | 4/5 | 5/6 |
| ev-cpms-architect | 2 | 1/2 | 2/2 | 1/2 |
| ev-evse-hardware-expert | 3 | 2/3 | 3/3 | 2/3 |
| ev-integration-architect | 4 | 4/4 | 2/3 | 3/4 |
| ev-ocpp-expert | 9 | 9/9 | 8/9 | 8/9 |

## Niezaliczone

- `ev-charging-operations-expert/ho-trigger-boot-po-reconnect`: routing → ev-ocpp-expert
- `ev-compliance-expert/ho-afir-minuta-status`: brak: [['SLA|umow\\w*']]; zakazane: []
- `ev-cpms-architect/ho-cpms-lc-utrata-stacji`: routing → ev-ocpp-expert
- `ev-ocpp-expert/ho-seqno-57`: brak: [['(ciągł\\w*|continuously)[^.\\n]{0,60}(dozwol|allowed|dopuszcz)|dozwolon\\w*[^.\\n]{0,60}ciągł|dopuszcz\\w*[^.\\n]{0,60}ciągł']]; zakazane: []
- `ev-evse-hardware-expert/ho-hw-capability-pnc`: routing → ev-iso15118-pki-expert
- `ev-integration-architect/ho-int-brama-naglowki`: brak: [['X-Correlation-ID.{0,80}(ten\\s+sam|tą\\s+samą|tę\\s+samą|takim\\s+samym|tym\\s+samym|same|bez\\s+zmian|niezmienion|zachow)', '(ten\\s+sam|tą\\s+samą|tę\\s+samą|same|zachow\\w*|przekaz\\w*\\s+bez\\s+zmian).{0,40}X-Correlation-ID', 'X-Correlation-ID`?\\s+(idzie|przechodzi|biegnie)[^.\\n]{0,40}(cał\\w*\\s+łańcuch|przez\\s+hub)']]; zakazane: []
