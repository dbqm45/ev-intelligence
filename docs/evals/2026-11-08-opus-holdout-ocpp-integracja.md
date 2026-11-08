# Ewaluacja skilli — claude-opus-5-5 — holdout-ocpp-integracja

Data: 2026-11-08 · koszt: 1.16 USD · scenariusze: 12 · zaliczone: 9

| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |
|---|---|---|---|---|
| ev-integration-architect | 4 | 3/4 | 2/3 | 2/4 |
| ev-ocpp-expert | 8 | 8/8 | 7/8 | 7/8 |

## Niezaliczone

- `ev-ocpp-expert/ho-diag-co-rozstrzyga`: brak: [['przykład\\w*[^.\\n]{0,80}(ilustrac\\w*|najniż\\w*|na końcu|ostatni\\w*)']]; zakazane: []
- `ev-integration-architect/ho-int-migracja-201-sp2`: routing → ev-ocpp-expert
- `ev-integration-architect/ho-int-brama-naglowki`: brak: [['(nie\\s+(wolno|może|można|mogą)|SHALL\\s+NOT|zakaz\\w*).{0,100}CALL', 'jedn\\w*\\s+(oczekując\\w*|niepotwierdzon\\w*|outstanding|otwart\\w*)\\s+CALL', 'one\\s+(outstanding\\s+)?CALL', 'nie\\s+wysył\\w*\\s+(kolejn\\w*|następn\\w*|drugi\\w*|now\\w*)\\s+CALL', 'CALL[^.\\n]{0,120}SHALL\\s+NOT']]; zakazane: []
