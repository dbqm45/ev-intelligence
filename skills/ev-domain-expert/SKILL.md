---
name: ev-domain-expert
description: Użyj, gdy zadanie EV obejmuje kilka obszarów — dobór domen taksonomii, skilli i kolejności, luki w bazie, norma kontra praktyka. Nie do doboru person i zespołu.
metadata:
  przeglad: "2027-05-07"
  katalog: "Użyj na początku zadania z elektromobilności (CPMS, ładowarki, roaming, operacje, taryfy, energia, regulacje), gdy trzeba ustalić, których domen i poddomen taksonomii EV Intelligence ono dotyczy, które skille wczytać i w jakiej kolejności, czego baza jeszcze nie obejmuje (priorytet P2/P3, flaga do weryfikacji) oraz gdzie zapisać nową wiedzę — norma, dokumentacja producenta, obserwacja z wdrożenia czy decyzja produktowa. Nie do merytorycznej odpowiedzi o protokole (skille ev-ocpp-expert, ev-ocpi-roaming-expert) ani do doboru person i składu zespołu (core-problem-routing)."
  slowa: "EV Intelligence, taksonomia EV, które domeny, jakie obszary wiedzy, które skille użyć, od czego zacząć zadanie EV, kolejność skilli, mapa wiedzy EV, czy baza to obejmuje, luka w bazie wiedzy, brak wiedzy w bazie, gdzie zapisać wiedzę, gdzie to umieścić w taksonomii, norma czy praktyka, deklaracja producenta, obserwacja z wdrożenia, vendor quirk, zadanie przekrojowe EV, projekt CPMS, ładowarki i roaming razem, router EV"
---

# EV Domain Expert — router taksonomii

Skill nie odpowiada merytorycznie. Ustala, **których obszarów wiedzy dotyczy zadanie**, które skille wczytać, w jakiej
kolejności i czego baza jeszcze nie ma. Źródło prawdy w repozytorium: `taxonomy/taxonomy.yaml`. Skill ma własne kopie (generowane, nie edytuj):
drzewo `references/taksonomia-drzewo.md` i zasady `references/taksonomia-zasady.md` (granice: sekcja 5). Sieć: brak.

**Zasada źródeł.** Skill nie podaje faktów o protokołach ani przepisach. Domeny, poddomeny, priorytety i flagi
bierzesz wyłącznie z taksonomii, a fakty dostarczają wskazane skille ze znacznikami `[dokument §sekcja]`
(`sources/*.yaml`). Czego taksonomia nie zawiera, nazywasz luką, a nie uzupełniasz z pamięci.

**Źródła niedostępne.** Gdy odpowiedź zależy od normy płatnej albo dokumentu z `sources/niedostepne.yaml`, piszesz to w
pierwszym zdaniu odpowiedzi: której normy nie da się sprawdzić i dlaczego. Dopiero potem podajesz to, co wynika ze
źródeł dostępnych.

**Cytowanie w odpowiedzi.** Poddomenę podajesz z identyfikatorem i nazwą, np. „D01.01 OCPP”, a skill pełną nazwą,
np. `ev-ocpp-expert`. Sam identyfikator nic nie mówi czytelnikowi.

## Procedura
1. **Rozpoznaj zadanie.** Wypisz rzeczowniki z zadania (komunikaty, obiekty, role, procesy), np. `Heartbeat`, `CDR`,
   `eMSP`, `przyłącze`. Brakuje wersji protokołu, roli rynkowej albo rynku (PL/UE)? Dopytaj albo zapisz założenie.
2. **Znajdź poddomeny.** Szukaj każdego hasła w drzewie:
   `grep -n -i "<hasło>" references/taksonomia-drzewo.md` (w repozytorium także `taxonomy/TAXONOMY-TREE.md`). Zapisz identyfikatory `Dnn.mm`, a nie same nazwy.
3. **Wyznacz właściciela tematu** według tabeli granic (`references/taksonomia-zasady.md`, sekcja 5):
   - komunikat i parametr → D01;
   - zachowanie w systemie → D05;
   - praca operatora → D07;
   - rzeczywiste zachowanie urządzenia → D21;
   - scenariusz end-to-end → D22.
   Dopisz domeny z `depends_on` tylko wtedy, gdy zadanie bez nich jest niezrozumiałe.
4. **Dobierz skille.** Właściciel poddomeny to linia „Skill:” pod poddomeną w `references/taksonomia-drzewo.md`;
   gdy jej nie ma, kolumna „Skille” w spisie domen. Kolejność:
   - najpierw fundament (D00, D01);
   - potem system (D05);
   - potem proces (D07, D06);
   - na końcu scenariusz (D22).
5. **Oznacz luki** — nigdy nie wypełniaj ich pamięcią modelu:
   - poddomena z „Skill: brak skilla” albo `P2`/`P3` bez skilla → „luka: brak opracowanej treści”;
   - flaga ⚠️ (`verify: true`) → wersje i daty do sprawdzenia w źródle pierwotnym.
6. **Gdzie zapisać nową wiedzę.** Rozdziel informacje według rodzaju:
   - wymóg normy → `knowledge_type: normative`, klasa A;
   - deklaracja producenta → `vendor`, klasa B, D03;
   - obserwacja z wdrożenia → `implementation`, klasa D, D21, z modelem i wersją firmware;
   - decyzja produktowa → `product`, poza wiedzą normatywną.

## Format wyniku
```
Domeny: D01.01 OCPP, D05.04 Statusy i dostępność, D07.01 Monitoring i NOC
Skille (kolejno): ev-ocpp-expert → ev-cpms-architect → ev-charging-operations-expert
Scenariusz: D22.02 Łączność i dostępność
Luki: <poddomeny P2/P3, skille p2, flagi ⚠️>
Założenia: <wersja protokołu, rola, rynek>
```

## Przykład
**Zadanie:** „Zaprojektuj w CPMS wykrywanie ładowarek, które przestały wysyłać Heartbeat, z obsługą incydentu.”
1. Hasła: `Heartbeat`, `utrata komunikacji`, `incydent`, `status`. Wersja OCPP nieznana → założenie: 1.6J i 2.0.1.
2. `grep` daje:
   - D01.01 (komunikaty, HeartbeatInterval);
   - D07.01 (wykrywanie utraty komunikacji);
   - D05.04 (offline vs unavailable vs faulted);
   - D07.03 (incydenty);
   - D22.02 (scenariusz).
3. Właściciele: interwał i komunikat to D01.01, reguła statusu w CPMS to D05.04, alert i eskalacja to D07.
4. Skille: `ev-ocpp-expert` → `ev-cpms-architect` → `ev-charging-operations-expert`.
   Przy fałszywych alarmach od konkretnego modelu dochodzi `ev-evse-diagnostics-expert` (D21).
5. Luki: D01.01 ma flagę ⚠️ (wersja 2.1). D21 zawiera tylko wiedzę z wdrożeń — jeśli nie ma wpisu dla modelu,
   napisz to wprost.

## Pułapki
- Odpowiedź merytoryczna zamiast routingu: skill wskazuje domeny i skille, a fakty zostawia im.
- Pominięcie luk: poddomena z priorytetem P2/P3 albo skill bez treści oznacza, że baza tego nie obejmuje, i trzeba to
  napisać wprost.
- Ręczna edycja plików `taksonomia-drzewo.md` i `taksonomia-zasady.md` w references: to pliki generowane z `taxonomy/taxonomy.yaml`
  (`python3 tools/render_taxonomy.py`).

## Źródła
- `taxonomy/taxonomy.yaml` v1.2.0 i `taxonomy/TAXONOMY.md` (EV Intelligence, 2026-11-08; właściciel poddomeny w polu `skills`).
