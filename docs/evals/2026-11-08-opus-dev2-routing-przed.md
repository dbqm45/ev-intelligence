# Ewaluacja skilli — claude-opus-5-5 — dev2-routing-przed

Data: 2026-11-08 · koszt: 3.63 USD · scenariusze: 117 · zaliczone: 95

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-billing-tariff-expert | 9 | 8/9 | 0/0 | 8/9 |
| ev-charging-operations-expert | 9 | 5/9 | 0/0 | 5/9 |
| ev-compliance-expert | 9 | 8/9 | 0/0 | 8/9 |
| ev-cpms-architect | 9 | 9/9 | 0/0 | 9/9 |
| ev-domain-expert | 9 | 6/9 | 0/0 | 6/9 |
| ev-energy-smart-charging-expert | 9 | 8/9 | 0/0 | 8/9 |
| ev-evse-diagnostics-expert | 9 | 4/9 | 0/0 | 4/9 |
| ev-evse-hardware-expert | 9 | 9/9 | 0/0 | 9/9 |
| ev-integration-architect | 9 | 5/9 | 0/0 | 5/9 |
| ev-iso15118-pki-expert | 9 | 8/9 | 0/0 | 8/9 |
| ev-ocpi-roaming-expert | 9 | 9/9 | 0/0 | 9/9 |
| ev-ocpp-expert | 9 | 8/9 | 0/0 | 8/9 |
| ev-product-designer | 9 | 8/9 | 0/0 | 8/9 |

## Niezaliczone

- `ev-billing-tariff-expert/restrictions-dzien-tygodnia-parser`: routing → ev-billing-tariff-expert
- `ev-charging-operations-expert/granica-przeglady-udt-80-lokalizacji`: routing → ev-compliance-expert
- `ev-charging-operations-expert/dzialka-przy-obwodnicy`: routing → ev-product-designer
- `ev-charging-operations-expert/granica-stacja-postawiona-co-dalej`: routing → ev-domain-expert
- `ev-charging-operations-expert/stycznik-sesja-2-sekundy`: routing → ev-charging-operations-expert
- `ev-compliance-expert/granica-historia-ladowan-rodo`: routing → none
- `ev-domain-expert/granica-operator-id-niemcy`: routing → ev-compliance-expert
- `ev-domain-expert/granica-od-karty-do-pieniedzy`: routing → ev-ocpi-roaming-expert
- `ev-domain-expert/emsp-czy-cpo-inwestor`: routing → ev-ocpi-roaming-expert
- `ev-energy-smart-charging-expert/stack-level-zlozony-harmonogram`: routing → ev-energy-smart-charging-expert
- `ev-evse-diagnostics-expert/granica-noc-evcommunicationerror`: routing → ev-charging-operations-expert
- `ev-evse-diagnostics-expert/granica-reklamacja-40kw-na-150`: routing → ev-evse-hardware-expert
- `ev-evse-diagnostics-expert/kod-producenta-bez-dokumentacji`: routing → ev-charging-operations-expert
- `ev-evse-diagnostics-expert/100-procent-dalej-1kw`: routing → ev-ocpp-expert
- `ev-evse-diagnostics-expert/logi-online-nie-przyjmuje-sesji`: routing → ev-charging-operations-expert
- `ev-integration-architect/testy-przed-firmware-600-stacji`: routing → ev-evse-diagnostics-expert
- `ev-integration-architect/granica-tabela-model-plus-wersja`: routing → ev-evse-diagnostics-expert
- `ev-integration-architect/granica-pierwszy-plugfest`: routing → ev-evse-diagnostics-expert
- `ev-integration-architect/kafka-stop-przed-startem`: routing → ev-cpms-architect
- `ev-iso15118-pki-expert/granica-wifi-norma-en-cyber`: routing → ev-evse-hardware-expert
- `ev-ocpp-expert/przetarg-certyfikat-zgodnosci`: routing → ev-evse-diagnostics-expert
- `ev-product-designer/agent-ai-zgloszenia-noc`: routing → ev-charging-operations-expert
