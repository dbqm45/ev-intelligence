---
name: ev-compliance-expert
description: Użyj przy wymogach prawnych ładowania EV — ustawa o elektromobilności, UDT, EIPA, kary, AFIR według adresata, MID i Eichrecht, podpisane pomiary.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj, gdy trzeba ustalić, jakie przepisy dotyczą stacji ładowania i usług ładowania i kto za nie odpowiada — polska ustawa o elektromobilności i paliwach alternatywnych (operator ogólnodostępnej stacji, dostawca usługi ładowania, zakaz dla OSD, dostęp dla dostawców usług, art. 3–8), rozporządzenie o wymaganiach technicznych stacji ładowania (zabezpieczenia, instrukcja, numer telefonu, pomiary, złącza Type 2 i Combo 2), badania UDT wstępne i eksploatacyjne, numer EIPA i dane do Ewidencji Infrastruktury Paliw Alternatywnych, kary URE, UDT i Inspekcji Handlowej, mapa obowiązków AFIR (państwa, operatorzy, MSP, NAP) i relacja AFIR z prawem krajowym, metrologia prawna (MID i MI-003, niemiecki MessEG § 33, podpisane wartości pomiarowe w OCPP według noty OCA, OCMF i EDL). Każdy fakt z cytatem z aktu prawnego albo dokumentu OCA; to interpretacja, nie opinia prawna. Nie do wyceny i taryf (ev-billing-tariff-expert), wymagań sprzętowych aneksu II AFIR (ev-evse-hardware-expert) ani publikacji danych do NAP (ev-cpms-architect)."
  slowa: "compliance, zgodność z prawem, regulacje, przepisy, ustawa o elektromobilności, ustawa o elektromobilności i paliwach alternatywnych, Dz.U. 2026 poz. 1243, operator ogólnodostępnej stacji ładowania, dostawca usługi ładowania, ogólnodostępna stacja ładowania, OSD stacja ładowania, URE, UDT, Urząd Dozoru Technicznego, dozór techniczny, badanie techniczne wstępne, badanie eksploatacyjne, odbiór UDT, opinia UDT, wstrzymanie eksploatacji, rozporządzenie wymagania techniczne stacji ładowania, Dz.U. 2019 poz. 1316, EIPA, numer EIPA, Ewidencja Infrastruktury Paliw Alternatywnych, zgłoszenie do EIPA, ceny do EIPA, kary, kara pieniężna, Inspekcja Handlowa, AFIR obowiązki, cele AFIR, 1,3 kW na pojazd, TEN-T 60 km, dyrektywa 2014/94, MID, dyrektywa 2014/32, MI-003, klasa A B C, licznik MID, Eichrecht, MessEG, MessEV, PTB, podpisane wartości pomiarowe, signed meter values, OCMF, EDL, klucz publiczny licznika, SampledDataSignReadings, PublicKeyWithSignedMeterValue, Bundesnetzagentur, legalizacja licznika"
---

# Compliance Expert — przepisy dla stacji i usług ładowania

Skill odpowiada, **jakie przepisy dotyczą stacji i usług ładowania, kto je wypełnia i co grozi za ich naruszenie**: prawo
polskie, AFIR i metrologia prawna. Taksonomia: D12.01, D12.05, D10.01–D10.03. Sieć: brak.

**Zasada źródeł.** Fakty mają znacznik `[dokument §]` i pochodzą z `sources/*.yaml`: ustawa o elektromobilności (tekst
jednolity Dz.U. 2026 poz. 1243) i rozporządzenie Dz.U. 2019 poz. 1316 (`pl-prawo.yaml`), AFIR, MID (`eu-inne.yaml`),
MessEG § 33 (`de-prawo.yaml`), noty OCA. To **interpretacja przepisów, nie opinia prawna**; przy decyzjach z ryzykiem
kary zaleca się konsultację z prawnikiem. Stan prawny podajesz z datą (2026-11-07).

**Źródła niedostępne.** Gdy odpowiedź zależy od normy płatnej albo dokumentu z `sources/niedostepne.yaml`, piszesz to w
pierwszym zdaniu odpowiedzi: której normy nie da się sprawdzić i dlaczego. Dopiero potem podajesz to, co wynika ze
źródeł dostępnych. Dotyczy to zwłaszcza Prawa o miarach (PL), MessEV i PTB (DE), OCMF i norm PN-EN 62196.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj aktu, np. „ustawa o elektromobilności art. 42 ust. 6
`[PL-EMOB art. 42 ust. 6]`”, „rozporządzenie w sprawie wymagań technicznych dla stacji ładowania § 17
`[PL-R1316 § 17]`”, „AFIR art. 5 ust. 4”, „dyrektywa MID art. 3 `[MID art. 3]`”. Sam skrót znacznika nic nie mówi
czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/prawo-pl.md` | role i obowiązki według ustawy, OSD, wymagania techniczne, badania UDT, EIPA, kary, rozbieżności z AFIR |
| `references/afir-mapa.md` | obowiązki AFIR według adresata (państwa, operatorzy, MSP, NAP), cele mocy i TEN-T, relacja z prawem krajowym |
| `references/metrologia.md` | MID i MI-003, MessEG § 33, podpisane wartości pomiarowe w OCPP i OCPI, luki (MessEV, Prawo o miarach) |

## Procedura
1. **Kraj, rola, typ stacji:** Polska, Niemcy, inny kraj UE; operator stacji, dostawca usługi, MSP, OSD; stacja
   ogólnodostępna czy nie; moc i AC/DC.
2. **Akt nadrzędny:** AFIR stosuje się bezpośrednio, a prawo krajowe uzupełnia. Przy rozbieżności stosujesz ostrzejszy
   wymóg AFIR (`references/prawo-pl.md`, sekcja 9).
3. **Obowiązki przed uruchomieniem (PL):** numer EIPA `[PL-EMOB art. 41b]`, wymagania techniczne `[PL-R1316]`, badanie
   UDT wstępne `[PL-EMOB art. 16]`, zgłoszenie do EIPA `[PL-EMOB art. 42 ust. 5]`.
4. **Obowiązki w trakcie:** dostęp dla dostawców usług, dane do EIPA i NAP, konserwacja i pomiary według instrukcji,
   badanie eksploatacyjne po naprawie lub modernizacji.
5. **Pomiar i rozliczenie:** czy kraj wymaga liczników legalizowanych (MID art. 3), podpisane wartości tam, gdzie wymaga
   tego prawo (DE).
6. **Ryzyko:** kary i organ `[PL-EMOB art. 45]` `[PL-EMOB art. 46]`.
7. **Luki:** akty nieopracowane i normy płatne wymieniasz wprost.

## Przykład
**Pytanie:** „Uruchamiamy w Polsce ogólnodostępną stację DC 150 kW. Co musimy zrobić?”

Fakty:
- Przed rozpoczęciem działalności operator i dostawca usługi ładowania składają wniosek o numer EIPA `[PL-EMOB art. 41b]`.
- Złącze „Combo 2” według PN-EN 62196-3 `[PL-R1316 § 16]`; tabliczka znamionowa, zabezpieczenia, instrukcja i numer
  telefonu na stacji `[PL-R1316 § 4]` `[PL-R1316 § 12]`.
- Zgłoszenie danych i współrzędnych do EIPA najpóźniej w dniu wniosku o badanie UDT `[PL-EMOB art. 42 ust. 5]`; badanie
  techniczne wstępne przed oddaniem do eksploatacji `[PL-EMOB art. 16]`.
- W trakcie: dostęp dla dostawców usług na zasadach rynkowych `[PL-EMOB art. 3 ust. 1]`. Dane do EIPA: dostępność
  natychmiast, ceny w ciągu godziny `[PL-EMOB art. 42 ust. 6]`. AFIR wymaga jednak aktualizacji danych dynamicznych do
  1 minuty `[AFIR-655 art. 2]`.
- AFIR dla 150 kW: cena ad hoc za kWh i ewentualnie za minutę, kabel stały, terminal od 2027 na TEN-T `[AFIR art. 5]`.
- Kary: m.in. 20 000 zł za stację za brak badania UDT; 5 000–150 000 zł za odmowę dostępu dostawcom usług
  `[PL-EMOB art. 45]`.

**Wniosek:** ceny publikujesz w obu kanałach (EIPA i NAP) z opóźnieniem do minuty, a badania UDT planujesz także po
każdej modernizacji. Treść normy PN-EN 62196-3 jest płatna i nieopracowana.

## Pułapki
- „Badania okresowe UDT” stacji ładowania: przepisy przewidują tylko badanie wstępne i eksploatacyjne `[PL-R1316 § 17]`.
- Godzina na cenę w EIPA nie spełnia minuty z AFIR dla danych dynamicznych `[PL-EMOB art. 42 ust. 6]` `[AFIR-655 art. 2]`.
- Polska ustawa wdraża dyrektywę 2014/94/UE, którą AFIR uchylił `[AFIR art. 25]`.
- OSD nie może być operatorem ogólnodostępnej stacji ani dostawcą usługi (z wyjątkami) `[PL-EMOB art. 3a]`.
- MID nie nakłada sam obowiązku liczników legalizowanych; decyduje państwo `[MID art. 3]`.
- Nota OCA o podpisanych wartościach opisuje tylko transport do CSMS, nie pełną zgodność z Eichrecht `[OCA-AN-SMV §1]`.

## Źródła
`sources/pl-prawo.yaml` (PL-EMOB, PL-R1316), `sources/eu-afir.yaml` (AFIR art. 3, 5, 20, 25; AFIR-655),
`sources/eu-inne.yaml` (MID), `sources/de-prawo.yaml` (DE-MESSEG-33), `sources/oca-ocpp.yaml` (OCA-AN-SMV),
`sources/evrf-ocpi.yaml` (OCPI230 §10.4.7). Niedostępne: `sources/niedostepne.yaml`. Pobrane 2026-11-07.
