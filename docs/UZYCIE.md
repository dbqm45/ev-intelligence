# Jak korzystać z EV Intelligence

Baza odpowiada na pytania o ładowanie pojazdów elektrycznych (OCPP, OCPI, OICP, CPMS/CSMS, taryfy i płatności, smart
charging, ISO 15118, AFIR, przepisy PL) i sprawdza story, projekty i kod pod kątem tych standardów. Każdy fakt ma
znacznik źródła oficjalnego.

## 1. Sposoby dostępu
| Sposób | Dla kogo | Jak |
|---|---|---|
| **Serwer MCP w Claude Code / Claude Desktop** (zalecany) | praca na swoim komputerze, także w repozytorium projektu w firmie | instalacja: [integrations/claude-code/README.md](../integrations/claude-code/README.md) |
| komendy skilli `/ev-intelligence:<skill>` | gdy chcesz wskazać konkretny obszar | dostępne po instalacji serwera MCP |
| wiersz poleceń `tools/ev_kb.py` | szybkie wyszukiwanie bez modelu, sprawdzanie znaczników | [docs/EV-KB.md](EV-KB.md) |
| konektor w claude.ai (przeglądarka, telefon) | dopiero po postawieniu serwera publicznego | [docs/DEPLOY.md](DEPLOY.md), [docs/EV-KB-MCP.md](EV-KB-MCP.md) |

Po instalacji MCP nie musisz nic wywoływać ręcznie: Claude widzi katalog skilli w instrukcjach serwera i sam sięga do
bazy (`ev_route` → `ev_skill` → `ev_search` / `ev_cite`). Fragment [CLAUDE-fragment.md](../integrations/claude-code/CLAUDE-fragment.md)
w `~/.claude/CLAUDE.md` sprawia, że robi to za każdym razem, zamiast odpowiadać z pamięci.

## 2. Tryby pracy

### Pytanie, gdy coś rozważasz
Pytasz zwykłym językiem. Najlepiej podać wersję protokołu, rolę (CPO, eMSP, hub) i kraj, bo od nich zależy odpowiedź.
```
Jak liczona jest cena sesji przy taryfie OCPI 2.3.0 z opłatą za kWh i za postój? Od czego zależy step_size?
Co dzieje się w OCPP 2.0.1, gdy kierowca odłączy kabel od auta w trakcie ładowania?
Jakie wymogi AFIR dotyczą płatności ad hoc na stacji 150 kW uruchomionej w 2025 r.?
Czym różni się autoryzacja przez aplikację od Plug & Charge?
```

### Przegląd story albo wymagań
Wklejasz story albo wskazujesz plik i prosisz o konkretny wynik:
```
/ev-intelligence:ev-product-designer Sprawdź to story pod kątem OCPI 2.3.0 i AFIR. Wypisz osobno:
niezgodności (ze źródłem), pominięte przypadki brzegowe, rzeczy, których źródła nie rozstrzygają.
<story>
```
Claude przechodzi procedurę i sekcję **Pułapki** skilla, czyli typowe przeoczenia ze źródłami.

### Przegląd kodu lub projektu
W repozytorium projektu:
```
/ev-intelligence:ev-ocpp-expert Przejrzyj obsługę TransactionEvent w src/ocpp/. Co jest niezgodne z OCPP 2.0.1,
co może nie działać po utracie łączności albo restarcie stacji, czego brakuje?
```
```
/ev-intelligence:ev-billing-tariff-expert Przejrzyj silnik wyceny w src/billing/ z taryfami OCPI 2.3.0:
pierwszeństwo elementów, step_size, min/max, przerwana sesja.
```
Kod czyta Claude w Twoim repozytorium; z bazy bierze tylko wiedzę o standardach. Treść Twojego kodu trafia do
Claude jak przy każdej pracy w Claude Code, więc stosujesz zasady firmy dotyczące narzędzi AI.

### Projekt nowego rozwiązania
```
/ev-intelligence:ev-cpms-architect Projektuję moduł połączeń OCPP-J dla 5000 stacji. Jakie wymagania
i pułapki muszę uwzględnić (identyfikacja stacji, ponowne łączenie, restart CSMS)?
```

Który skill do czego: tabela w [integrations/claude-code/README.md](../integrations/claude-code/README.md#jak-używać).
Bez komendy Claude wybiera skill sam; komenda przydaje się, gdy pytanie leży na granicy dwóch obszarów.

## 3. Jak czytać odpowiedź
| W odpowiedzi | Znaczy |
|---|---|
| `[OCPI230 §10.3.1]`, `[201-P2 E13]`, `[AFIR art. 5 ust. 4]` | fakt ze źródła: dokument z rejestru `sources/*.yaml` i sekcja, którą sprawdzono w tekście |
| **Wniosek** | rekomendacja wyprowadzona z faktów, nie cytat; decyzja należy do Ciebie |
| pierwsze zdanie: „zależy od normy …, której nie da się sprawdzić” | norma płatna albo niedostępna (np. ISO 15118, IEC 61851); dalsza część opiera się tylko na źródłach dostępnych |
| „baza tego nie obejmuje” / „źródło nie określa” | luka: nie ma tego w bazie albo standard tego nie definiuje (np. reguła biznesowa CPO) |

Sprawdzenie cytatu: poproś „pokaż fragment źródła dla [OCPI230 §10.3.1]” (narzędzie `ev_cite`) albo w terminalu
`python3 tools/ev_kb.py cite "[OCPI230 §10.3.1]"`. Fragment pojawi się tylko, gdy masz lokalną kopię dokumentu;
bez niej dostaniesz adres, wersję i licencję dokumentu.

Znaczniki w tekście, który sam piszesz (opis PR, dokument projektowy), sprawdzisz poleceniem „sprawdź znaczniki w tym
tekście” (`ev_check`) albo `python3 tools/ev_kb.py check plik.md`.

## 4. Dobre praktyki
- Podawaj wersję: OCPP 1.6 i 2.0.1 różnią się w wielu miejscach (np. koniec transakcji, nazwy zmiennych).
- Proś o podział na niezgodności, przypadki brzegowe i luki. Lista bez podziału łatwo miesza fakty z opiniami.
- Przy decyzji o pieniądzach, przepisach albo certyfikacji czytaj źródło ze znacznika, nie tylko odpowiedź.
  Ostatni niezależny pomiar (holdout) dał ok. 84% poprawnych odpowiedzi (`docs/evals/`).
- Gdy odpowiedź nie ma znaczników albo twierdzi coś bez źródła, poproś o źródło. Brak źródła znaczy, że to nie
  pochodzi z bazy.

## 5. Zakres
Obszary i ich skille: `taxonomy/TAXONOMY.md`. Tematy jeszcze bez skilla (RODO, NIS2, wybór lokalizacji, serwis terenowy,
CHAdeMO, OpenADR i inne) i nieopracowane płatności (SCA, PCI DSS, polska ustawa o usługach płatniczych):
`docs/DO-ZROBIENIA.md`.

## 6. Aktualizacja
`git -C ~/ev-intelligence pull`, potem restart Claude Code. Wersję wiedzy serwer podaje w instrukcjach (`VERSION` i
commit), a zmiany opisuje `CHANGELOG.md`.
