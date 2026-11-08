# Ewaluacja skilli — claude-opus-5-5 — holdout

Data: 2026-11-08 · koszt: 2.62 USD · scenariusze: 25 · zaliczone: 13

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-charging-operations-expert | 5 | 3/5 | 4/5 | 2/5 |
| ev-cpms-architect | 3 | 1/3 | 3/3 | 1/3 |
| ev-domain-expert | 3 | 3/3 | 3/3 | 3/3 |
| ev-evse-diagnostics-expert | 3 | 2/3 | 3/3 | 2/3 |
| ev-evse-hardware-expert | 3 | 2/3 | 2/3 | 1/3 |
| ev-ocpi-roaming-expert | 3 | 2/3 | 1/3 | 0/3 |
| ev-ocpp-expert | 5 | 4/5 | 5/5 | 4/5 |

## Niezaliczone

- `ev-charging-operations-expert/ho-hard-reset-kolejka`: brak: [['(utrac|przepad|zgub|lost)\\w*']]; zakazane: []
- `ev-charging-operations-expert/ho-trigger-boot-po-reconnect`: routing → ev-ocpp-expert
- `ev-charging-operations-expert/ho-afir-minuta-status`: routing → ev-compliance-expert
- `ev-cpms-architect/ho-cpms-identyfikator-url`: routing → ev-ocpp-expert
- `ev-cpms-architect/ho-cpms-datex`: routing → ev-compliance-expert
- `ev-evse-diagnostics-expert/ho-diag-co-rozstrzyga`: routing → ev-ocpp-expert
- `ev-evse-hardware-expert/ho-hw-ac22-2026`: brak: [['8 (stycznia|January) 2026|2026-01-08|08\\.01\\.2026']]; zakazane: []
- `ev-evse-hardware-expert/ho-hw-capability-pnc`: routing → ev-iso15118-pki-expert
- `ev-ocpi-roaming-expert/ho-ocpi-request-correlation-id`: brak: [['X-Correlation-ID[^.\\n]{0,120}(ten sam|tak\\w* sam|zachow|same|bez zmian|kopi)']]; zakazane: []
- `ev-ocpi-roaming-expert/ho-ocpi-4003-kolejka`: brak: [['4003[^.\\n]{0,120}(niepołącz|nie jest połączon|not connected|połączeni\\w*|connection)']]; zakazane: []
- `ev-ocpi-roaming-expert/ho-ocpi-step-size-przyszlosc`: routing → ev-billing-tariff-expert
- `ev-ocpp-expert/ho-heartbeatinterval-1-6`: routing → ev-evse-diagnostics-expert
