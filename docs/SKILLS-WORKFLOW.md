# Budowa i walidacja skilli (z narzędziami fabryki tf)

EV Intelligence ma **własną strukturę**. Z fabryki [`dbqm45/tf`](https://github.com/dbqm45/tf) korzystamy wyłącznie
jako z **narzędzi kontroli jakości**: reguł struktury skilla, formatu scenariuszy, bramki jakości, regresji
podpowiedzi, lintera polszczyzny i audytu bezpieczeństwa. Nie instalujemy nakładek fabryki (np. `pack-ev`)
i nie przejmujemy jej układu katalogów.

## Układ w tym repozytorium

```
skills/<nazwa>/SKILL.md            ← skill (prefiks ev-), opcjonalnie references/ i scripts/
evals/skill_evals/<nazwa>.json     ← scenariusze ewaluacji (format fabryki)
evals/skill_evals/holdout/…        ← zamknięty zbiór pomiarowy (opcjonalnie; autor zmian go nie czyta)
evals/skill-gate.json              ← rejestr bramki (odcisk treści + data) — zapisuje go factory_check.py
taxonomy/taxonomy.yaml → skills    ← rejestr skilli; każdy skill musi tu być
```

## Jak działa `tools/factory_check.py`

1. Sprawdza lokalnie taksonomię (`render_taxonomy.py --check`) i spójność rejestru: skill ↔ taksonomia ↔ scenariusze.
2. W `.work/factory/` (ignorowane przez git) instaluje **sam rdzeń** fabryki z językiem `pl` i bez nakładek.
3. Rejestruje tam wymiar `ev-`, kopiuje nasze skille, scenariusze, `taxonomy/` i `knowledge/` (żeby działały odwołania).
4. Uruchamia: `build.py check`, `run_skill_evals.py --validate`, a dla każdego skilla `skill_gate.py`. Bramka obejmuje
   strukturę, scenariusze, trafność podpowiedzi, regresję wszystkich skilli, polszczyznę, odwołania i audyt.
5. Zapisuje wynik bramki do `evals/skill-gate.json` i kończy linią `RESULT: PASS|FAIL`.

```bash
python3 tools/factory_check.py --tf ../tf                       # wszystkie skille
python3 tools/factory_check.py --tf ../tf --skills ev-ocpp-expert --fast
```

Fabrykę wskazujesz przez `--tf`, zmienną `TF_DIR` albo klon w `../tf`.

## Kolejność pracy nad nowym skillem

Zasady pochodzą z `core/skills/core-skill-authoring/SKILL.md` w tf. Czytaj je stamtąd, nie kopiuj.

1. **Luka:** 2–3 prawdziwe zadania bez skilla. Zapisz, czego modelowi brakuje.
2. **Wpis w taksonomii:** nazwa `ev-…` w `taxonomy.yaml → skills` i w polu `skills` właściwych domen.
3. **Scenariusze przed treścią** (`evals/skill_evals/<nazwa>.json`): co najmniej 2× `trigger` ze sprawdzeniami wiedzy
   (`checks.all`, `checks.none`) i 1× `no-trigger` z `neighbor`.
4. **Treść:**
   - `description` ≤170 znaków w formie „Użyj, gdy … — …”;
   - `metadata.katalog` z granicami („Nie do …”), `metadata.slowa`, `metadata.przeglad`;
   - procedura, `## Przykład`, `## Źródła` z datą.
5. **Bramka:** `python3 tools/factory_check.py --skills <nazwa>`, aż do `PASS`.
6. **Ewaluacja na modelu** (płatna, ok. $0,10–0,30 za scenariusz i model) **tylko za zgodą człowieka**:
   `python3 tools/factory_check.py --skills <nazwa> --model haiku,sonnet --budget 2 --yes`.

## Ograniczenia

- Ostrzeżenie „nie jest używany przez żadną rolę ani personę” jest oczekiwane: nie używamy ról fabryki.
- Bramka bez modelu sprawdza formę, routing i bezpieczeństwo, **nie poprawność merytoryczną**. Tę mierzy dopiero
  ewaluacja na modelu i nasze testy wiedzy (Etap 2 planu).
- Repozytorium tf jest prywatne. Automatyczna kontrola tego repozytorium na GitHubie wymaga dostępu do tf
  (np. tokenu w sekretach). Na razie kontrolę uruchamiamy lokalnie.
