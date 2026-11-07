---
name: ev-domain-expert
description: Użyj, gdy zadanie z branży EV obejmuje kilka obszarów — dobór domen taksonomii EV Intelligence, skilli i kolejności, luki w bazie, norma kontra praktyka.
metadata:
  przeglad: "2027-05-07"
  katalog: "Użyj na początku zadania z elektromobilności (CPMS, ładowarki, roaming, operacje, taryfy, energia, regulacje), gdy trzeba ustalić, których domen i poddomen taksonomii EV Intelligence ono dotyczy, które skille wczytać i w jakiej kolejności, czego baza jeszcze nie obejmuje (priorytet P2/P3, flaga do weryfikacji) oraz gdzie zapisać nową wiedzę — norma, dokumentacja producenta, obserwacja z wdrożenia czy decyzja produktowa. Nie do merytorycznej odpowiedzi o protokole (skille ev-ocpp-expert, ev-ocpi-roaming-expert) ani do doboru person i składu zespołu (core-problem-routing)."
  slowa: "EV Intelligence, taksonomia EV, które domeny, jakie obszary wiedzy, które skille użyć, od czego zacząć zadanie EV, kolejność skilli, mapa wiedzy EV, czy baza to obejmuje, luka w bazie wiedzy, brak wiedzy w bazie, gdzie zapisać wiedzę, gdzie to umieścić w taksonomii, norma czy praktyka, deklaracja producenta, obserwacja z wdrożenia, vendor quirk, zadanie przekrojowe EV, projekt CPMS, ładowarki i roaming razem, router EV"
---

# EV Domain Expert — router taksonomii

Skill nie odpowiada merytorycznie. Ustala, **których obszarów wiedzy dotyczy zadanie**, które skille wczytać, w jakiej
kolejności i czego baza jeszcze nie ma. Źródło prawdy w repozytorium: `taxonomy/taxonomy.yaml`. Skill ma własne kopie (generowane, nie edytuj):
drzewo `references/taksonomia-drzewo.md` i zasady `references/taksonomia-zasady.md` (granice: sekcja 5). Sieć: brak.

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
4. **Dobierz skille.** Kolumna „Skille” w spisie domen i rejestr skilli na końcu `references/taksonomia-drzewo.md`. Kolejność:
   - najpierw fundament (D00, D01);
   - potem system (D05);
   - potem proces (D07, D06);
   - na końcu scenariusz (D22).
5. **Oznacz luki** — nigdy nie wypełniaj ich pamięcią modelu:
   - poddomena `P2`/`P3` albo skill z `stage: p2` → „luka: brak opracowanej treści”;
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

## Źródła
- `taxonomy/taxonomy.yaml` v1.0.0 i `taxonomy/TAXONOMY.md` (EV Intelligence, 2026-11-07).
