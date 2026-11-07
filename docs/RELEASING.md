# Wersjonowanie i wydania EV Intelligence

Mechanizm jest skopiowany z tf (claude-team-factory, licencja MIT) i dostosowany do tego repozytorium. Baza ma jeden
numer wersji zgodny z [Semantic Versioning 2.0.0](https://semver.org/lang/pl/) w pliku `VERSION`. Wydaną wersję
oznacza tag git `vX.Y.Z`, a do każdego tagu powstaje GitHub Release z wpisem z `CHANGELOG.md`. Serwer MCP podaje wersję
w instrukcjach (`Wersja wiedzy: 0.1.0 (<commit>)`), więc odpowiedź da się przypisać do wydania bazy.

## Commity: Conventional Commits

Każdy commit, który trafia na `main`, ma format [Conventional Commits 1.0.0](https://www.conventionalcommits.org/pl/v1.0.0/).
W tym repozytorium gałąź robocza jest scalana na `main` przez fast-forward, więc liczy się **każdy commit** z gałęzi,
a nie tylko tytuł PR. Opis trafia wprost do CHANGELOG, dlatego piszemy go po angielsku, jak w tf. Treść commita (dlaczego)
może być po polsku.

```
<typ>(<zakres>)!: <opis>

[treść: dlaczego, nie co]

[stopki, np. BREAKING CHANGE: <co i jak migrować>]
```

- **Opis:** po angielsku, w trybie rozkazującym (`add`, `fix`), bez kropki na końcu, najwyżej 72 znaki.
- **Zakres** (opcjonalny), małymi literami: nazwa domeny lub narzędzia, np. `ocpp`, `ocpi`, `afir`, `compliance`,
  `sources`, `ev-kb`, `mcp`, `deploy`, `release`.

| Typ | Kiedy | Wpływ na wersję |
|---|---|---|
| `feat` | nowy skill, nowy plik references, nowe źródło w rejestrze, nowe narzędzie lub polecenie | MINOR (w 0.y.z: PATCH) |
| `fix` | poprawka błędnego faktu, cytatu, sekcji, błędu w narzędziu | PATCH |
| `perf` | szybciej, bez zmiany wyników | PATCH |
| `refactor`, `test`, `docs`, `style`, `build`, `ci`, `chore`, `revert` | bez zmiany wiedzy ani zachowania narzędzi | brak |
| `!` albo stopka `BREAKING CHANGE:` | zmiana niezgodna: usunięty lub przemianowany skill, identyfikator źródła, narzędzie MCP | MAJOR (w 0.y.z: MINOR) |

**Publiczne API bazy** (od niego zależy rodzaj podbicia): nazwy skilli, identyfikatory źródeł używane w znacznikach,
nazwy i parametry narzędzi MCP, polecenia `tools/ev_kb.py`.

Sprawdzanie:
- **Lokalnie** (raz na klon): `git config core.hooksPath .githooks` włącza hook `commit-msg`. Pojedynczy komunikat:
  `python3 scripts/check_commit_message.py "feat(ocpi): add OICP 2.3 reference"`.
- **CI:** workflow `checks` sprawdza wszystkie commity od ostatniego tagu, a `pr-title` tytuł PR.

## Bramka tf w CI

`tools/factory_check.py` korzysta z narzędzi fabryki (`core/factory/install.py`, `factory/build.py`,
`factory/skill_gate.py`), które leżą w repozytorium `dbqm45/tf`. Lokalnie to klon `../tf`. Na GitHub Actions runner
pobiera tylko ev-intelligence, a domyślny token przebiegu nie ma dostępu do innego prywatnego repozytorium. Job
`factory` w `checks.yml` pobiera tf, gdy w ustawieniach repozytorium jest sekret **`TF_READ_TOKEN`**:
1. GitHub → Settings → Developer settings → Fine-grained tokens: nowy token, repozytorium tylko `dbqm45/tf`,
   uprawnienie *Contents: Read-only*.
2. ev-intelligence → Settings → Secrets and variables → Actions → *New repository secret* `TF_READ_TOKEN`.

Bez sekretu job wypisuje uwagę i się pomija; pozostałe kontrole działają.

## Faza 0.y.z

Startujemy od `0.1.0`. W fazie 0.y.z zmiana niezgodna podbija MINOR, a `feat` i `fix` podbijają PATCH. Wersję `1.0.0`
ustawia się świadomie, ręcznie (np. po ewaluacji na modelu i wdrożeniu serwera MCP): `python3 scripts/release.py 1.0.0`.

## Jak podbijana jest wersja (automatycznie)

Po każdym pushu na `main` workflow `release` (`.github/workflows/release.yml`):
1. **Liczy wersję** (`python3 scripts/release.py --ci`) z commitów od ostatniego tagu. Bez `feat`, `fix`, `perf` i zmian
   niezgodnych nie ma nowej wersji. Inaczej zapisuje `VERSION` i wpis na górze `CHANGELOG.md` (sekcje *Breaking*,
   *Added*, *Fixed*).
2. **Sprawdza** bazę (testy, `tools/ev_kb.py check skills knowledge`) i commituje `chore(release): X.Y.Z` jako
   `github-actions[bot]`. Ten push nie uruchamia kolejnego wydania.
3. **Taguje** `vX.Y.Z` i tworzy **GitHub Release** z wpisem CHANGELOG (`python3 scripts/release_notes.py X.Y.Z`).

Gdy `VERSION` ma wersję bez tagu (pierwsze wydanie `0.1.0` albo wydanie ręczne), workflow wydaje ją bez liczenia,
o ile `CHANGELOG.md` ma wpis `## [X.Y.Z]`.

W zwykłej pracy **nie zmieniasz** `VERSION` ani nagłówków w `CHANGELOG.md`: robi to CI. Po wydaniu na `main` jest nowy
commit `chore(release)`, więc przed kolejnym merge'em gałąź roboczą trzeba zaktualizować z `main`.

### Wydanie ręczne

Gdy wynik z commitów trzeba nadpisać (źle oznaczony commit, przeredagowany CHANGELOG, świadome `1.0.0`):
1. `python3 scripts/release.py --dry-run`, potem `python3 scripts/release.py minor` (albo `major`, `patch`, `X.Y.Z`).
2. Przejrzyj `CHANGELOG.md`, uruchom `python3 tools/factory_check.py --tf ../tf`.
3. Commit `chore(release): X.Y.Z` i merge na `main`. Workflow otaguje wersję.

**Wydanej wersji się nie zmienia.** Tagu nie przesuwamy ani nie usuwamy; błąd naprawia kolejna wersja.

## Ustawienia repozytorium na GitHubie

- *Settings → Actions → General*: Actions włączone; workflow `release` deklaruje `contents: write`.
- Reguła ochrony `main` (jeśli jest) musi pozwalać `github-actions[bot]` na push commitu wydania.
