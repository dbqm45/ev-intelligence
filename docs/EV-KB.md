# `tools/ev_kb.py` — dostęp do wiedzy i kontrola cytatów

Rdzeń integracji EV Intelligence z innymi narzędziami (np. tryb Talos w fabryce tf). Kolejne warstwy, czyli serwer
MCP (`tools/ev_kb_mcp.py`, opis: `docs/EV-KB-MCP.md`) i plugin, wywołują te same funkcje. Zależności: Python 3, PyYAML; do indeksowania PDF `pdftotext`.

| Polecenie | Co robi |
|---|---|
| `route "<zadanie>"` | skille (po `description` i `metadata.slowa`) i poddomeny taksonomii; pokazuje skille jeszcze nieopracowane |
| `search "<pytanie>"` | fragmenty skilli i `knowledge/` razem ze znacznikami źródeł; brak trafień = baza tego nie obejmuje |
| `cite "[ID §…]"` | metadane z `sources/*.yaml` (URL, data, SHA-256, licencja) i fragment sekcji z lokalnej kopii |
| `check <plik/katalog/->` | każdy znacznik: dokument w rejestrze? sekcja w tekście dokumentu? |
| `index <pliki…>` | dodaje kopie dokumentów do `.cache/ev-kb/`; plik przyjmowany **tylko** przy zgodnym SHA-256 z rejestru |

Wszystkie polecenia mają `--json`. Katalog kopii: `--docs`, `EV_KB_DOCS` albo `.cache/ev-kb/` (ignorowany przez git).

## Statusy `check`
- `OK`: dokument w rejestrze, a każda sprawdzalna część lokalizatora jest w tekście (poza spisem treści).
- `NIEZNANY_DOKUMENT`: identyfikatora nie ma w `sources/*.yaml`. **Błąd.**
- `NIEDOSTEPNE`: znacznik wskazuje normę albo dokument z `sources/niedostepne.yaml` (np. ISO 15118). **Błąd.**
  `search`, `cite` i `check` (także w MCP) zwracają wtedy pole `unavailable` z komunikatem, który odpowiedź ma podać
  w pierwszym zdaniu.
- `NIE_ZNALEZIONO`: sekcji, artykułu, ustępu lub wymagania nie ma w tekście. **Błąd.**
- `BRAK_TEKSTU`: brak lokalnej kopii; błąd tylko z `--require-text`.
- `NIESPRAWDZONE`: lokalizator, którego narzędzie nie umie sprawdzić (np. „tabela F”).

Rozpoznawane lokalizatory: `§10.3.1`, `§8.4.5–8.4.6`, `§2` (także „Chapter 2”), `rozdz. 8`, `I03.FR.04`, `E13`,
`N02–N06`, blok `I`, `art. 5 ust. 4`, `Annex II`, `cz. 2 pkt 6`, `Preface`, kotwica AsciiDoc `#eRoamingAuthorizeStart`
(OICP, wiersz `[[eRoamingAuthorizeStart]]`) albo tytuł nagłówka Markdown `#CDRInfo` (OCHP, wiersz `### CDRInfo *class*`). Kilka części rozdziela przecinek.

**Ograniczenie:** `check` potwierdza, że sekcja **istnieje**, a nie że zdanie w skillu wiernie oddaje jej treść. To
nadal sprawdza autor, czytając fragment z `cite`.

## Pliki źródłowe
Dokumentów nie ma w repozytorium (licencje, rozmiar). Pobierz je z adresów w `sources/*.yaml` (pakiety OCA rozpakuj),
potem:

```bash
python3 tools/ev_kb.py index ~/pobrane/OCPI-2.3.0.pdf ~/pobrane/OCPP-2.0.1_all_files/*.pdf
```

Bez kopii `check` sprawdza tylko rejestr. `factory_check.py` uruchamia `check skills knowledge` w każdym przebiegu.
