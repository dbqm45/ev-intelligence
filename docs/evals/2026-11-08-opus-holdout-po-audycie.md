# Ewaluacja skilli — claude-opus-5-5 — holdout-po-audycie

Data: 2026-11-08 · koszt: 4.06 USD · scenariusze: 55 · zaliczone: 41

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-billing-tariff-expert | 6 | 6/6 | 4/5 | 5/6 |
| ev-charging-operations-expert | 5 | 3/5 | 5/5 | 3/5 |
| ev-compliance-expert | 5 | 5/5 | 4/4 | 5/5 |
| ev-cpms-architect | 3 | 1/3 | 3/3 | 1/3 |
| ev-domain-expert | 3 | 3/3 | 3/3 | 3/3 |
| ev-energy-smart-charging-expert | 5 | 5/5 | 4/4 | 5/5 |
| ev-evse-diagnostics-expert | 2 | 2/2 | 2/2 | 2/2 |
| ev-evse-hardware-expert | 3 | 2/3 | 3/3 | 2/3 |
| ev-integration-architect | 4 | 3/4 | 2/3 | 2/4 |
| ev-iso15118-pki-expert | 5 | 5/5 | 3/4 | 4/5 |
| ev-ocpi-roaming-expert | 3 | 3/3 | 2/3 | 2/3 |
| ev-ocpp-expert | 8 | 8/8 | 4/8 | 4/8 |
| ev-product-designer | 3 | 3/3 | 2/2 | 3/3 |

## Niezaliczone

- `ev-billing-tariff-expert/ho-bill-step-size`: brak: []; zakazane: ['6[,.]2\\s*kWh']
- `ev-charging-operations-expert/ho-trigger-boot-po-reconnect`: routing → ev-ocpp-expert
- `ev-charging-operations-expert/ho-afir-minuta-status`: routing → ev-compliance-expert
- `ev-cpms-architect/ho-cpms-lc-utrata-stacji`: routing → ev-ocpp-expert
- `ev-cpms-architect/ho-cpms-identyfikator-url`: routing → ev-ocpp-expert
- `ev-evse-hardware-expert/ho-hw-capability-pnc`: routing → ev-iso15118-pki-expert
- `ev-integration-architect/ho-int-migracja-201-sp2`: routing → ev-ocpp-expert
- `ev-integration-architect/ho-int-brama-naglowki`: brak: [['(nie\\s+(wolno|może|można|mogą)|SHALL\\s+NOT|zakaz\\w*).{0,100}CALL', 'jedn\\w*\\s+(oczekując\\w*|niepotwierdzon\\w*|outstanding|otwart\\w*)\\s+CALL', 'one\\s+(outstanding\\s+)?CALL']]; zakazane: []
- `ev-iso15118-pki-expert/ho-pki-firmware-podpis`: brak: [['SHA-?256']]; zakazane: []
- `ev-ocpi-roaming-expert/ho-prod-publish-flota`: brak: [['wszystki\\w*\\s+(ustawion\\w*\\s+)?pol', 'all\\s+(the\\s+)?(set\\s+)?fields', 'wszystkie\\s+pola']]; zakazane: []
- `ev-ocpp-expert/ho-seqno-57`: brak: [['(ciągł\\w*|continuously)[^.\\n]{0,60}(dozwol|allowed|dopuszcz)|dozwolon\\w*[^.\\n]{0,60}ciągł']]; zakazane: []
- `ev-ocpp-expert/ho-diag-co-rozstrzyga`: brak: [['przykład\\w*[^.\\n]{0,80}(ilustrac\\w*|najniż\\w*|na końcu|ostatni\\w*)']]; zakazane: []
- `ev-ocpp-expert/ho-int-multiconnector-16`: brak: [['(własn|osobn|wirtualn|virtual|own|odrębn)\\w*\\s+(\\"|„)?EVSE', 'każde\\w*\\s+złącz\\w*.{0,60}(jak|jako|tak\\s+jakby).{0,40}EVSE', 'EVSE\\s+(na|per)\\s+(każde\\s+)?(złącze|connector)']]; zakazane: []
- `ev-ocpp-expert/ho-prod-displaymessage`: brak: [['AlwaysFront'], ['InFront'], ['NormalCycle'], ['RFC[\\s-]?5646', 'en-US'], ['angielsk', 'English']]; zakazane: []
