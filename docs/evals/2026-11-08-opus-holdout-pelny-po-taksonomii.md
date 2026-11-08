# Ewaluacja skilli — claude-opus-5-5 — holdout-pelny-po-taksonomii

Data: 2026-11-08 · koszt: 5.53 USD · scenariusze: 55 · zaliczone: 34

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-billing-tariff-expert | 5 | 5/5 | 3/4 | 4/5 |
| ev-charging-operations-expert | 5 | 3/5 | 4/5 | 2/5 |
| ev-compliance-expert | 5 | 5/5 | 3/4 | 4/5 |
| ev-cpms-architect | 3 | 1/3 | 2/3 | 1/3 |
| ev-domain-expert | 3 | 3/3 | 3/3 | 3/3 |
| ev-energy-smart-charging-expert | 5 | 5/5 | 1/4 | 2/5 |
| ev-evse-diagnostics-expert | 3 | 2/3 | 3/3 | 2/3 |
| ev-evse-hardware-expert | 3 | 2/3 | 2/3 | 1/3 |
| ev-integration-architect | 5 | 3/5 | 2/4 | 1/5 |
| ev-iso15118-pki-expert | 5 | 5/5 | 3/4 | 4/5 |
| ev-ocpi-roaming-expert | 3 | 2/3 | 3/3 | 2/3 |
| ev-ocpp-expert | 5 | 5/5 | 5/5 | 5/5 |
| ev-product-designer | 5 | 3/5 | 3/4 | 3/5 |

## Niezaliczone

- `ev-billing-tariff-expert/ho-bill-min-price`: brak: [['before_taxes'], ['after_taxes'], ['(nie\\s+jest|NOT)\\s+.{0,40}(wymog|wymagani|requirement|obowiąz)', 'konsument\\w*', 'consumer']]; zakazane: []
- `ev-charging-operations-expert/ho-hard-reset-kolejka`: brak: [['(utrac|przepad|zgub|lost)\\w*']]; zakazane: []
- `ev-charging-operations-expert/ho-trigger-boot-po-reconnect`: routing → ev-ocpp-expert
- `ev-charging-operations-expert/ho-afir-minuta-status`: routing → ev-compliance-expert
- `ev-compliance-expert/ho-comp-osd-operator`: brak: [['nie mo(że|żemy|gą).{0,80}(operator|właściciel|dostawc)', 'zakaz\\w*.{0,80}(operator|właściciel|dostawc)']]; zakazane: []
- `ev-cpms-architect/ho-cpms-lc-utrata-stacji`: routing → ev-ocpp-expert
- `ev-cpms-architect/ho-cpms-identyfikator-url`: routing → ev-ocpp-expert
- `ev-energy-smart-charging-expert/ho-en-stack-201`: brak: [['wyższ\\w*\\s+stackLevel', 'stackLevel.{0,40}wyższ', 'najwyższ\\w*\\s+stackLevel', 'higher\\s+stackLevel', 'highest\\s+stackLevel']]; zakazane: []
- `ev-energy-smart-charging-expert/ho-en-limit-dso`: brak: [['\\bSO\\b', 'System\\s+Operator'], ['ClearedChargingLimit']]; zakazane: []
- `ev-energy-smart-charging-expert/ho-en-16-fazy`: brak: [['connectorId\\W{0,4}(=|:)?\\W{0,3}0\\b', 'connector\\w*\\s+0\\b', 'złącz\\w*\\s+0\\b'], ['napięci\\w*\\s+(nominaln|znamionow|ustawion|sieci|zadan)', 'nie\\s+(zmierzon|mierzon)', 'set\\s+voltage', 'line\\s+voltage']]; zakazane: []
- `ev-evse-diagnostics-expert/ho-diag-co-rozstrzyga`: routing → ev-ocpp-expert
- `ev-evse-hardware-expert/ho-hw-ac22-2026`: brak: [['8 (stycznia|January) 2026|2026-01-08|08\\.01\\.2026']]; zakazane: []
- `ev-evse-hardware-expert/ho-hw-capability-pnc`: routing → ev-iso15118-pki-expert
- `ev-integration-architect/ho-int-migracja-201-sp2`: routing → ev-ocpp-expert
- `ev-integration-architect/ho-int-multiconnector-16`: routing → ev-ocpp-expert
- `ev-integration-architect/ho-int-rozszerzenia`: brak: [['additionalProperties']]; zakazane: []
- `ev-integration-architect/ho-int-brama-naglowki`: brak: [['X-Correlation-ID.{0,80}(ten\\s+sam|tą\\s+samą|tę\\s+samą|takim\\s+samym|tym\\s+samym|same|bez\\s+zmian|niezmienion|zachow)', '(ten\\s+sam|tą\\s+samą|tę\\s+samą|same|zachow\\w*|przekaz\\w*\\s+bez\\s+zmian).{0,40}X-Correlation-ID']]; zakazane: []
- `ev-iso15118-pki-expert/ho-pki-firmware-podpis`: brak: [['InvalidCertificate']]; zakazane: []
- `ev-ocpi-roaming-expert/ho-ocpi-step-size-przyszlosc`: routing → ev-billing-tariff-expert
- `ev-product-designer/ho-prod-publish-flota`: routing → ev-ocpi-roaming-expert
- `ev-product-designer/ho-prod-displaymessage`: routing → ev-ocpp-expert
