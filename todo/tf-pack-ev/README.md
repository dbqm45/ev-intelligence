# Wiedza z nakładki pack-ev fabryki tf — do przeniesienia albo odrzucenia

**To nie jest źródło wiedzy.** Katalog przechowuje treść nakładki `pack-ev` z repozytorium fabryki tf (`dbqm45/tf`,
`packs/pack-ev`, stan z `main` po commicie `ff2b08c` z 2026-11-13, wersja nakładki 1.1.0) na czas jej scalania ze
skillami EV Intelligence. Właściciel zdecydował (2026-11-15):
- EV Intelligence zostaje w swojej pierwotnej postaci: skille `ev-*`, bez nakładki fabryki i bez person;
- skille `ev-*` uzupełniamy o to, czego w nich brakuje, a co jest w pack-ev;
- przenosimy tylko fakty sprawdzone w źródle oficjalnym z rejestru `sources/*.yaml` (zasada źródeł z `CLAUDE.md`);
- rzeczy niepotwierdzone i niepasujące zostają tutaj z adnotacją; po scaleniu pack-ev zniknie z fabryki.

Pack-ev **nie ma żadnego znacznika `[id §sekcja]`** i opiera się na źródłach wtórnych (libocpp, josev, blogi) oraz na
„wiedzy ogólnej autora”. Z tego katalogu bierzesz więc **temat**. Fakt opracowujesz od nowa z dokumentu w rejestrze
i cytujesz. Niczego nie kopiujesz dosłownie do `skills/` ani `knowledge/`. W około 60 miejscach pack-ev jest sprzeczny
z EV Intelligence, i prawie zawsze rację ma EV Intelligence (lista w `analiza/luki-*.md`, sekcje „Konflikty”).

## Zawartość
| Ścieżka | Co to jest |
|---|---|
| `zrodlo/skills/dom-ev-*/` | 36 skilli pack-ev (SKILL.md, references/, scripts/) bez zmian |
| `zrodlo/tests/` | testy skryptów (styl fabryki tf, nie `unittest`), scenariusze `skill_evals/`, egzamin `ev_exam/` |
| `zrodlo/examples/` | przykłady pack-ev (mini-CSMS 1.6, zajezdnia, taryfa→CDR) |
| `analiza/luki-podsumowanie.md` | podsumowanie analizy luk (≈500 luk: F/P/R), proponowana kolejność, decyzje |
| `analiza/luki-A.md` … `luki-F.md` | tabele luk: pozycja w pack-ev → cel w `ev-*`, klasa, źródło oficjalne |
| `STATUS.md` | co już przeniesiono (z celem) i co odrzucono albo czeka |

Kod w `zrodlo/` nie jest uruchamiany przez bramkę (`tools/skill_check.py` sprawdza `skills/`, `knowledge/`, `tests/`).
Persony, role i `pack.yaml` nakładki nie zostały skopiowane: to elementy fabryki, nie wiedza.

## Jak pracować z pozycją
1. Znajdź pozycję w `analiza/luki-*.md` (klasa F = fakt, P = praktyka bez źródła, R = procedura).
2. F: przeczytaj sekcję dokumentu z rejestru (`python3 tools/ev_kb.py cite "[id §…]"`). Napisz treść w skillu `ev-*`
   z cytatem, dodaj scenariusz, uruchom bramkę `tools/skill_check.py`.
3. P i R: przenieś tylko jako **Wniosek** wyprowadzony z faktów z cytatem. Inaczej pozycja zostaje tu z adnotacją
   w `STATUS.md`.
4. Wpisz wynik do `STATUS.md`. Gdy cały skill pack-ev jest rozliczony, usuń jego katalog z `zrodlo/skills/`.
