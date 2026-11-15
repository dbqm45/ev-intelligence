---
name: ev-billing-tariff-expert
description: Użyj przy taryfach i rozliczaniu ładowania EV — wycena z taryfy OCPI, step_size, CDR i koszty, ceny ad hoc (AFIR), koszt w OCPP 2.0.1, płatność kartą, przerwana sesja.
metadata:
  przeglad: "2027-02-07"
  katalog: "Użyj przy projektowaniu i sprawdzaniu taryf oraz wyceny sesji ładowania — struktura taryfy OCPI 2.3.0 (TariffElement, PriceComponent, ograniczenia czasu, dni, kWh, mocy i czasu trwania, rezerwacje), pierwszeństwo elementów i wymiar bez ceny, step_size liczony raz na sesję, min_price i max_price, zmiana taryfy w trakcie sesji, wytyczne EVRF uproszczenia taryf, pola kosztów CDR i ChargingPeriod, dane podpisane, terminal płatniczy i preautoryzacja (moduł Payments), wymagania cenowe AFIR art. 5 (ad hoc, kWh, opłata za zajętość, kolejność składników, niedyskryminacja, ceny MSP), taryfa i koszt w OCPP 2.0.1 (blok I, totalCost, CostUpdated, komunikaty zastępcze), płatność ad hoc w OCPP 2.1 (terminal zintegrowany i wolnostojący, QR, rozliczenie NotifySettlement, anulowanie, zwiększanie kwoty) i blokada środków na karcie według PSD2 art. 75–76, przerwana sesja od zdarzenia na stacji do CDR i płatności (odłączenie kabla, utrata zasilania i wznowienie, offline, sesja bez energii). Każdy fakt z cytatem ze źródła oficjalnego. Nie do mechaniki OCPI: rejestracji, push i pull, wysyłki CDR (ev-ocpi-roaming-expert), przepisów i metrologii prawnej (ev-compliance-expert), komunikatów OCPP poza kosztem (ev-ocpp-expert) ani publikacji danych do NAP (ev-cpms-architect)."
  slowa: "taryfa, cennik, cena ładowania, wycena sesji, silnik wyceny, rating, rozliczenie sesji, koszt sesji, Tariff, TariffElement, PriceComponent, TariffRestrictions, start_time, end_time, day_of_week, min_kwh, max_duration, min_power, step_size, zaokrąglenie, zaokrąglanie ceny, ENERGY, TIME, PARKING_TIME, FLAT, opłata startowa, opłata za postój, idle fee, blocking fee, opłata za zajętość, min_price, max_price, preauthorize_amount, preautoryzacja, tax_included, VAT w taryfie, AD_HOC_PAYMENT, taryfa ad hoc, taryfa bezpłatna, zmiana taryfy w trakcie sesji, tariff simplification, uproszczenie taryf, CDR, total_cost, total_energy_cost, total_parking_cost, total_fixed_cost, ChargingPeriod, CdrDimension, signed_data, Eichrecht, OCMF, credit CDR korekta kosztu, terminal płatniczy, PTP, moduł Payments, Financial Advice Confirmation, invoice_reference_id, faktura, AFIR art. 5, cena za kWh, cena za minutę, niedyskryminacja, ceny MSP, koszty e-roamingu, totalCost, CostUpdated, TariffFallbackMessage, TotalCostFallbackMessage, personalMessage, koszt na wyświetlaczu ładowarki, płatność kartą, płatność ad hoc OCPP 2.1, DirectPayment, PspRef, PaymentCtrlr, AuthorizationAmount, NotifySettlement, Settled, Canceled, rozliczenie nieudane, paragon, receiptUrl, VatNumberValidation, IncrementalAuthorizationAmount, kiosk płatniczy, terminal wolnostojący, płatność QR, dynamiczny QR, TOTP, NotifyWebPaymentStarted, blokada środków, zwolnienie blokady, PSD2, art. 75, przerwana sesja, przerwane ładowanie, odłączenie kabla, EVDisconnected, utrata zasilania, PowerLoss, wznowienie transakcji, TxResumed, TxResumptionTimeout, sesja bez energii, INVALID, Credit CDR, dane niepełne, kalkulator taryfy, ocpi_tariff_calc, przelicz koszt sesji, before_taxes, taxes, tax_included, PriceLimit, min_current, max_current, granice restrykcji, błąd w przykładzie OCPI, Terminal, Financial Advice Confirmation, credit CDR"
---

# Billing & Tariff Expert — taryfy, wycena sesji, ceny

Skill odpowiada, **ile kosztuje sesja i dlaczego**: jak czytać taryfę, jak ją wycenić, co trafia do CDR i jakie zasady
cenowe narzuca AFIR. Taksonomia: D09.01–D09.03, D10 (tylko dane podpisane w CDR). Sieć: brak.

**Zasada źródeł.** Fakty mają znacznik `[dokument §]` i pochodzą z `sources/*.yaml`: OCPI 2.3.0 i wytyczne uproszczenia
taryf (EVRF), OCPP 2.0.1 Edition 4 i OCPP 2.1 Edition 2 (OCA), AFIR (wersja skonsolidowana), PSD2 art. 75–76. **VAT,
fakturowanie, PCI DSS, SCA i polska ustawa o usługach płatniczych nie są opracowane; MID, Eichrecht i podpisane wartości pomiarowe opisuje skill `ev-compliance-expert`.** Wtedy mówisz, że trzeba sięgnąć do prawa lub normy, a nie odpowiadasz z pamięci.

**Źródła niedostępne.** Gdy odpowiedź zależy od normy płatnej albo dokumentu z `sources/niedostepne.yaml`, piszesz to w
pierwszym zdaniu odpowiedzi: której normy nie da się sprawdzić i dlaczego. Dopiero potem podajesz to, co wynika ze
źródeł dostępnych.

**Cytowanie w odpowiedzi.** Przy znaczniku podawaj słowami rodzaj i wersję dokumentu, np. „specyfikacja OCPI 2.3.0
§11.3.1 `[OCPI230 §11.3.1]`”, „wytyczne EVRF uproszczenia taryf, cz. 2 pkt 1 `[OCPI-TSG cz. 2 pkt 1]`”, „OCPP 2.0.1
I03.FR.04 `[201-P2 I03.FR.04]`”, „AFIR art. 5 ust. 4”. Sam skrót znacznika nic nie mówi czytelnikowi.

## Czytaj references, gdy…
| Plik | Kiedy |
|---|---|
| `references/taryfy-ocpi.md` | struktura taryfy, pierwszeństwo elementów, ograniczenia, `step_size`, zmiana taryfy, wytyczne EVRF i rozbieżności |
| `references/cdr-i-wycena.md` | pola kosztów CDR, `ChargingPeriod`, dane podpisane, terminal płatniczy, procedura silnika wyceny |
| `references/ceny-afir-ocpp.md` | AFIR art. 5 (ad hoc, kWh, minuta, kolejność, niedyskryminacja, MSP), OCPP 2.0.1 blok I i `TariffCostCtrlr` |
| `references/platnosc-ad-hoc.md` | płatność kartą lub QR w OCPP 2.1 (C18–C25): autoryzacja, anulowanie, rozliczenie i jego odrzucenie, zwiększanie kwoty; blokada środków PSD2 |
| `references/kalkulator.md` | wycena sesji skryptem `scripts/ocpi_tariff_calc.py` (OCPI 2.3.0 i 2.2.1): wejście, wynik, reguły, ograniczenia, błędy w przykładach specyfikacji |
| `references/sesja-przerwana.md` | przerwana sesja: odłączenie kabla, utrata zasilania i wznowienie (2.1 E17), offline, sesja bez energii; co trafia do wyceny, CDR i płatności; lista kontrolna przeglądu |

## Procedura
1. **Kontekst:** kto ustala cenę (CPO, MSP, ad hoc), protokół i wersja (OCPI 2.2.1 / 2.3.0, OCPP 2.0.1), moc punktu i
   data uruchomienia. Od mocy i daty zależą zasady AFIR `[AFIR art. 5 ust. 4]`.
2. **Taryfa:** czy każdy wymiar ma cenę w każdej chwili. Pierwszy pasujący element na wymiar, brak elementu oznacza
   brak kosztu, więc dodajesz element domyślny bez ograniczeń na końcu `[OCPI230 §11.3.1]`.
3. **Wycena:** okresy w punktach zmiany ceny, `step_size` raz na sesję z sumy zużycia `[OCPI230 §10.3.1]`, potem
   `min_price` / `max_price`. Zaokrąglenie kwot według prawa i umowy, bo OCPI go nie określa `[OCPI230 §11.3.1]`.
4. **CDR:** pola `total_*`, `charging_periods` z `tariff_id`, taryfa z chwili startu sesji `[OCPI230 §10.3.1]`.
5. **Prezentacja ceny:** AFIR (przed sesją, kolejność składników, niedyskryminacja) i stacja OCPP 2.0.1 (`totalCost`,
   komunikaty zastępcze) (`references/ceny-afir-ocpp.md`).
6. **Płatność i przerwanie:** przy karcie lub QR sprawdzasz blokadę, anulowanie i rozliczenie
   (`references/platnosc-ad-hoc.md`), przy nietypowym końcu sesji przechodzisz scenariusze z
   `references/sesja-przerwana.md`.
7. **Luki:** podatki, faktury, SCA, PCI DSS i metrologię prawną wymieniasz jako nieopracowane.

## Przykład
**Pytanie:** „Czas ładowania 5 €/h przed 17:00 i 7 €/h po 17:00, oba ze `step_size` 600. Ładowanie 6 min przed i 22 min
po 17:00. Ile kosztuje czas?”

Fakty:
- `step_size` liczy się raz na sesję z sumy czasu, nie osobno dla okresu po 17:00. Bierze się `step_size` ostatniego
  istotnego składnika `[OCPI230 §10.3.1]`.
- Ten przypadek jest przykładem w specyfikacji: łącznie 28 min → 30 min, więc po 17:00 rozlicza się 24 min, a nie 30
  (co dałoby 36 min łącznie) `[OCPI230 §10.3.1]`.

**Wniosek (obliczenie):** 6/60 × 5 € + 24/60 × 7 € = 0,50 € + 2,80 € = 3,30 €. Żeby uniknąć takich sporów, ustaw
`step_size = 1` (zalecenie przed OCPI 3.0, w którym pola nie ma) `[OCPI230 §11.4.2]`, a zaokrąglenia uzgodnij w umowie
roamingowej `[OCPI-TSG cz. 2 pkt 1]`.

## Pułapki
- `0` w ograniczeniu nie znaczy „brak ograniczenia”: `max_duration: 0` wyłącza składnik, `day_of_week: []` to „w żaden
  dzień” `[OCPI-TSG cz. 2 pkt 6]`.
- Element bez ograniczeń przed elementem z ograniczeniami: ten drugi nigdy nie zadziała `[OCPI-TSG cz. 2 pkt 3]`.
- „Pierwsze 15 minut gratis” przez `PARKING_TIME` + `min_duration` znaczy technicznie „opłata po przekroczeniu 15 minut”
  `[OCPI-TSG cz. 2 pkt 13]`.
- Brak `totalCost` w `TransactionEventResponse` nie oznacza sesji bezpłatnej. Bezpłatna to `totalCost = 0.00`
  `[201-P2 I03.FR.04]`.
- `min_price` i `max_price` obowiązują przed i po podatkach jednocześnie `[OCPI230 §11.3.1]`.
- Blokada na karcie bez zgody kierowcy na dokładną kwotę: PSD2 dopuszcza blokadę tylko w kwocie, na którą płatnik się
  zgodził `[PSD2 art. 75]`, a w OCPP 2.1 to `AuthorizationAmount` i każde zwiększenie `[21-P2 C23.FR.01]`.
- Sesja bez kosztu przy płatności ad hoc musi kończyć się anulowaniem (`status = Canceled`), nie rozliczeniem kwoty 0
  `[21-P2 C20.FR.05]`.
- CDR wysłany z niepełnych danych (kolejka offline) można już tylko skorygować Credit CDR `[OCPI230 §10.1.1]`.
- OCPI nie zabrania zmiany taryfy w trakcie sesji, ale prawo konsumenckie wielu krajów tak `[OCPI230 §11.3.1]`.
  Wytyczne EVRF: nie zmieniać taryfy, która już obowiązywała `[OCPI-TSG cz. 2 pkt 8]`.
- Wytyczne każą pomijać `end_time` zamiast `00:00`, a specyfikacja definiuje `00:00` jako koniec dnia. Rozstrzygnięcie w
  `references/taryfy-ocpi.md`, sekcja 6.

## Źródła
`sources/evrf-ocpi.yaml` (OCPI230 §10, §11, §16, §17; OCPI-TSG), `sources/oca-ocpp.yaml` (201-P2 blok I i §1.11,
201-APP §3.1.17, 201-CSV; 21-P2 blok C §2.9, C18–C25, E17; 16 §4.9, §4.10), `sources/eu-afir.yaml` (AFIR art. 5,
art. 20; AFIR-655), `sources/eu-inne.yaml` (PSD2 art. 75–76, pobrane 2026-11-08). Pobrane 2026-11-07.
