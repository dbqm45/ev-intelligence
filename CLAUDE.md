# EV Intelligence — zasady dla agentów

## Zasada źródeł (decyzja właściciela projektu, 2026-11-07)
- **Nic z pamięci modelu.** Każdy fakt w `knowledge/`, `skills/` i `taxonomy/` musi być sprawdzony w źródle oficjalnym:
  dokument właściciela standardu lub protokołu (OCA, EVRoaming Foundation, ISO/IEC, Hubject…), regulatora albo
  instytucji UE. Źródła wtórne (blogi, biblioteki open-source, inne bazy wiedzy) służą tylko jako
  wskazówka, gdzie szukać, a nie jako dowód.
- Każde źródło trafia do rejestru `sources/*.yaml` (URL, data pobrania, SHA-256, licencja). Fakt w treści ma znacznik
  `[id-dokumentu §sekcja]`, a numer sekcji sprawdzasz w tekście dokumentu, nie z pamięci.
- Rekomendacje wyprowadzone z faktów oznaczasz słowem **Wniosek**. Czego źródło nie określa, piszesz wprost.
- Rozbieżność między dokumentami (np. tekst wymagania vs schemat) opisujesz z obydwoma cytatami i rozstrzygnięciem
  (errata, enum w schemacie).
- Brak dostępu do źródła (zablokowany host, płatna norma) → zgłaszasz to człowiekowi. Nie zastępujesz go pamięcią.
  Każdą taką normę lub dokument wpisujesz do `sources/niedostepne.yaml` (co, dlaczego niedostępne, kto przywołuje, w
  których skillach). Wpis nie jest źródłem: nie ma `id` i nie wolno go cytować znacznikiem.
- Odpowiedź, która zależy od takiej normy lub dokumentu, mówi o tym w pierwszym zdaniu (która norma, dlaczego nie da
  się sprawdzić). Narzędzia `ev_kb` / MCP zwracają wtedy pole `unavailable` i status `NIEDOSTEPNE`.

- **Źródła poufne wewnętrznie** (licencja zakazuje ujawniania treści, np. eMIP): rejestr `sources/poufne/*.yaml`, tekst
  tylko lokalnie, sprawdzanie wyłącznie werdyktem `tools/ev_kb_poufne.py` / `ev_confidential_check`. Ich treści nie
  wpisujesz do skills/, knowledge/, commitów ani opisów PR. W odpowiedzi podajesz werdykt, informację o poufności i link.

## Praca ze skillami
- Struktura i bramki: `docs/SKILLS-WORKFLOW.md`. Przed oddaniem: `python3 tools/skill_check.py` (bez zależności od tf).
  Projekt współdziała z tf (serwer MCP, opcjonalnie `tools/factory_check.py`), ale od niego nie zależy.
- Taksonomia (źródło prawdy): `taxonomy/taxonomy.yaml`; po zmianie `python3 tools/render_taxonomy.py`.
- Ewaluacja na modelu jest płatna: tylko za zgodą człowieka.
- **Commity:** Conventional Commits z opisem po angielsku (`feat(ocpi): add OICP 2.3 reference`); każdy commit trafia na
  main, a wersję i CHANGELOG liczy CI (`docs/RELEASING.md`). Hook: `git config core.hooksPath .githooks`.
  `VERSION` i nagłówków `CHANGELOG.md` nie zmieniasz ręcznie, poza wydaniem ręcznym.
- Sprawy odłożone (decyzje właściciela, niedziałające hosty, źródła do przejrzenia): `docs/DO-ZROBIENIA.md`.
