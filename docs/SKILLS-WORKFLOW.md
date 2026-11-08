# Budowa i walidacja skilli

EV Intelligence ma własną strukturę i własną bramkę jakości (`tools/skill_check.py`). Projekt **nie zależy** od fabryki
tf: bramka działa bez sieci i bez innych repozytoriów. Projekt może współdziałać z tf: tf korzysta z wiedzy przez serwer
MCP, a `tools/factory_check.py` to opcjonalna kontrola zgodności z formatem skilli tf, gdy obok jest jej klon.

## Zasada źródeł

Każdy fakt w skillu pochodzi ze źródła oficjalnego zapisanego w `sources/*.yaml` i ma znacznik
`[dokument §sekcja]`. Nic z pamięci modelu (szczegóły: `CLAUDE.md`). Bramka sprawdza, czy znacznik wskazuje dokument
z rejestru i istniejącą sekcję. Czy zdanie wiernie oddaje treść, sprawdza autor, czytając fragment z `ev_kb cite`.

## Układ w tym repozytorium

```
skills/<nazwa>/SKILL.md            ← skill (prefiks ev-), opcjonalnie references/ i scripts/
evals/skill_evals/<nazwa>.json     ← scenariusze ewaluacji
evals/skill_evals/holdout/…        ← zamknięty zbiór pomiarowy (opcjonalnie; autor zmian go nie czyta)
evals/skill_evals/dev/…            ← zbiór roboczy routingu (pisze go inny agent; autor stroi na nim opisy)
evals/skill-gate.json              ← rejestr bramki (odcisk treści + data) — zapisuje go skill_check.py
taxonomy/taxonomy.yaml → skills    ← rejestr skilli; każdy skill musi tu być
```

## Bramka: `tools/skill_check.py`

```bash
python3 tools/skill_check.py                         # wszystkie skille
python3 tools/skill_check.py --skills ev-ocpp-expert
python3 tools/skill_check.py --strict-routing        # ostrzeżenia routingu jako błędy
```

| Krok | Co sprawdza |
|---|---|
| taxonomy | `render_taxonomy.py --check`: pliki generowane zgodne z `taxonomy.yaml` |
| registry | skill w `taxonomy.yaml → skills`, prefiks `ev-`, plik scenariuszy |
| unit tests | `python3 -m unittest discover tests` |
| citations | `ev_kb.py check skills knowledge`: dokument w rejestrze, sekcja w lokalnej kopii (gdy jest) |
| structure | frontmatter (`name` = katalog, `description` ≤170 znaków i „Użyj…”, `metadata.katalog` z „Nie do …”, `metadata.slowa`, `metadata.przeglad` jako data), akapity **Zasada źródeł**, **Źródła niedostępne**, **Cytowanie w odpowiedzi**, sekcje Procedura, Przykład, Pułapki, Źródła, zgodność listy `references/` z plikami |
| scenarios | JSON, unikalne `id`, ≥2 `trigger` z `checks.all` (poprawne wyrażenia regularne), ≥1 `no-trigger` z `neighbor` |
| routing | ostrzeżenie, gdy `ev_kb route` nie daje skilla w pierwszej trójce dla jego scenariusza `trigger` albo stawia go przed sąsiadem w `no-trigger` |

Wynik kończy linia `RESULT: PASS|FAIL`. Przy PASS bramka zapisuje odcisk treści skilla w `evals/skill-gate.json`.
CI (`.github/workflows/checks.yml`) uruchamia ją przy każdym pushu.

Sąsiad (`neighbor`) spoza prefiksu `ev-` oznacza skill zewnętrzny (np. w kliencie, który korzysta z bazy przez MCP);
bramka nie sprawdza jego istnienia ani routingu.

## Kolejność pracy nad nowym skillem

1. **Luka:** 2–3 prawdziwe zadania bez skilla. Zapisz, czego modelowi brakuje.
2. **Wpis w taksonomii:** nazwa `ev-…` w `taxonomy.yaml → skills` i w polu `skills` właściwych domen.
3. **Scenariusze przed treścią** (`evals/skill_evals/<nazwa>.json`): co najmniej 2× `trigger` ze sprawdzeniami wiedzy
   (`checks.all`, `checks.none`) i 1× `no-trigger` z `neighbor`.
4. **Treść:**
   - `description` ≤170 znaków w formie „Użyj, gdy … — …”;
   - `metadata.katalog` z granicami („Nie do …”), `metadata.slowa`, `metadata.przeglad`;
   - procedura, `## Przykład`, `## Pułapki`, `## Źródła` z datą.
5. **Cytaty:** `python3 tools/ev_kb.py check skills/<nazwa>` (opis: `docs/EV-KB.md`).
6. **Bramka:** `python3 tools/skill_check.py --skills <nazwa>`, aż do `PASS`.
7. **Ewaluacja na modelu** (płatna) **tylko za zgodą człowieka** — `tools/skill_eval.py`, opis niżej.

## Ewaluacja na modelu: `tools/skill_eval.py`

```bash
python3 tools/skill_eval.py --dry-run                      # plan: liczba scenariuszy i wywołań API, bez kosztu
python3 tools/skill_eval.py --model sonnet --budget 5 --yes --skills ev-ocpi-roaming-expert --label oicp
python3 tools/skill_eval.py --model sonnet --budget 5 --yes --holdout --label holdout
python3 tools/skill_eval.py --model opus --budget 3 --yes --set dev --routing-only --label dev   # tylko routing
```

**Trzy zbiory:** jawne scenariusze (`skill_evals/*.json`) piszesz razem ze skillem; zbiór roboczy (`dev/`) i holdout
(`holdout/`) pisze inny agent niż autor skilli, bez dostępu do ich treści. Opisy skilli stroisz na `dev`; holdout tylko
mierzy wynik i autor nie czyta jego scenariuszy ani listy porażek (tylko zbiorczą tabelę).

Dla każdego scenariusza:
1. **routing**: model dostaje katalog skilli (nazwa i `description`) i wybiera jeden skill albo `none` (structured
   output). `trigger` jest zaliczony, gdy wybrał ten skill; `no-trigger`, gdy wybrał cokolwiek innego;
2. **odpowiedź** (tylko `trigger`): system to `SKILL.md` z plikami `references/`, a odpowiedź musi spełnić
   `checks.all` (każda grupa: co najmniej jeden wzorzec) i nie może pasować do żadnego wzorca z `checks.none`.

**Backendy:**
- `--backend cli` (domyślny): wywołania przez Claude Code CLI (`claude -p`) z logowaniem użytkownika, **bez klucza
  API**. Bez narzędzi, z własnym promptem systemowym, w pustym katalogu tymczasowym. Koszt to `total_cost_usd` z CLI,
  czyli wycena według cennika; przy subskrypcji przebieg zużywa limit planu, a nie generuje faktury.
- `--backend sdk`: SDK `anthropic` z kluczem API (`pip install -r requirements-eval.txt`; `ANTHROPIC_API_KEY` albo
  profil `ant auth login`). Koszt z `usage` odpowiedzi i cennika w skrypcie.
 Przebieg zatrzymuje się po przekroczeniu `--budget`.
Bez `--yes` nic nie jest wysyłane. Odmowa modelu (`refusal`) to wynik scenariusza, bez przełączania na inny model.
Wyniki: `docs/evals/<data>-<model>-<label>.jsonl` i `.md`.

## Ograniczenia

- Bramka bez modelu sprawdza formę, cytaty i routing słów kluczowych, **nie poprawność merytoryczną**. Tę mierzy dopiero
  ewaluacja na modelu i testy wiedzy.
- Routing w bramce to dopasowanie słów (`ev_kb route`), a nie wybór skilla przez model.
