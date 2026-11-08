<!-- Fragment do ~/.claude/CLAUDE.md albo CLAUDE.md projektu: korzystanie z bazy EV Intelligence w trakcie pracy. -->
## Elektromobilność (EV Intelligence)
- Przy każdym pytaniu, story, projekcie albo kodzie z ładowania pojazdów elektrycznych (OCPP, OCPI, OICP, CPMS/CSMS,
  taryfy i rozliczenia, płatność, smart charging, ISO 15118, AFIR, przepisy PL) korzystaj z serwera MCP
  `ev-intelligence`: najpierw `ev_route`, potem `ev_skill` dla wskazanego skilla. Nie odpowiadaj z pamięci.
- Fakty podawaj ze znacznikami `[ID §sekcja]` z bazy. Własne wnioski oznaczaj słowem **Wniosek**. Czego baza nie
  obejmuje albo co zależy od normy niedostępnej, powiedz w pierwszym zdaniu.
- Przy przeglądzie story albo kodu sprawdź go z procedurą i sekcją **Pułapki** skilla. Wypisz osobno: niezgodności z
  protokołem lub przepisem (ze znacznikiem), pominięte przypadki brzegowe (np. utrata połączenia, przerwanie sesji,
  odrzucona autoryzacja) i miejsca, gdzie źródło nie rozstrzyga.
