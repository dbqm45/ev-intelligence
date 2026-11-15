# Płatność ad hoc: terminal, QR, rozliczenie i blokada środków

Zakres: jak płatność kartą albo przez stronę płatności łączy się z transakcją OCPP. Fakty z OCPP 2.1 Edition 2
(blok C, przypadki C18–C25) i dyrektywy PSD2. OCPP 1.6 i 2.0.1 tych przypadków nie mają: w 2.1 są oznaczone „New in
OCPP 2.1” `[21-P2 C18]`. Moduł Payments z OCPI 2.3.0 (terminal po stronie CPO, `preauthorize_amount`) opisuje
`references/cdr-i-wycena.md`, a wymagania AFIR dla ad hoc `references/ceny-afir-ocpp.md`.

Spis:
1. Trzy warianty płatności ad hoc
2. Terminal zintegrowany: autoryzacja (C18)
3. Anulowanie przed i po starcie transakcji (C19, C20)
4. Rozliczenie, paragon, odrzucenie (C21, C22)
5. Zwiększanie kwoty autoryzacji (C23)
6. Terminal wolnostojący i kod QR (C24, C25)
7. Blokada środków na karcie: PSD2 art. 75–76
8. Rozbieżności w dokumencie i luki

## 1. Trzy warianty płatności ad hoc `[21-P2 C §2.9]`
| Wariant | Kto łączy się z PSP | Co opisuje OCPP |
|---|---|---|
| terminal zintegrowany w stacji | terminal, własnym połączeniem | C18–C23; API terminal ↔ stacja jest własnościowe i poza OCPP |
| terminal wolnostojący (kiosk) dla kilku stacji | kiosk → CSMS | C24; interfejs kiosk ↔ CSMS poza specyfikacją |
| strona płatności przez kod QR | CSMS → strona PSP | C25; OCA zaleca dynamiczny QR (ochrona przed podmienioną naklejką) |

## 2. Terminal zintegrowany: autoryzacja (C18)
- Stacja SHALL zlecić terminalowi rezerwację kwoty z `PaymentCtrlr.AuthorizationAmount` `[21-P2 C18.FR.01]`.
- Referencja płatności z PSP (`PspRef`) staje się `idToken` z `type = DirectPayment`; dane karty (np. `cardBin`,
  `cardLast4Digits`) idą w `additionalInfo`. Listę pól ustawia CSMS w `PaymentCtrlr.PaymentDetails` `[21-P2 C18]`.
- `PaymentCtrlr.AuthorizeDirectPayment = false`: stacja sama dopuszcza ładowanie po akceptacji PSP
  `[21-P2 C18.FR.03]`. `= true`: stacja wysyła `AuthorizeRequest` z `PspRef`, a CSMS może odmówić albo podać taryfę
  inną niż domyślna `[21-P2 C18.FR.04]`. Przy odmowie stacja SHALL zwolnić kwotę i anulować płatność
  `[21-P2 C18.FR.07]`.
- Pierwszy `TransactionEventRequest` ma `idToken = <PspRef>`, `type = DirectPayment` i
  `transactionLimit.maxCost` równe kwocie autoryzacji `[21-P2 C18.FR.06]`.
- Warunek wstępny: domyślna taryfa ad hoc ustawiona na stacji (I07). Przy wycenie po stronie CSMS przypadek działa,
  ale „it will not be possible to stop exactly at the maxCost amount” `[21-P2 C18]`.
- Opcjonalnie stacja sprawdza w CSMS numer VAT do paragonu (`VatNumberValidationRequest`) `[21-P2 C18.FR.08]`.

## 3. Anulowanie przed i po starcie transakcji (C19, C20)
- Kierowca kończy przed startem transakcji albo minął czas na podłączenie (`TxCtrlr.EVConnectionTimeOut`): stacja SHALL
  zwolnić kwotę `[21-P2 C19.FR.01]`. Przy `AuthorizeDirectPayment = true` wysyła `NotifySettlementRequest` ze
  `status = Canceled` `[21-P2 C19.FR.02]`. Przy `false` CSMS nie wie o tej płatności `[21-P2 C19]`.
- Transakcja już ruszyła, ale bez kosztu: `TransactionEvent(Ended)` z `triggerReason = StopAuthorized` albo
  `EVConnectTimeout` `[21-P2 C20.FR.01]` `[21-P2 C20.FR.02]`. Przy wycenie centralnej CSMS SHALL odpowiedzieć
  `totalCost = 0` `[21-P2 C20.FR.03]`, przy lokalnej stacja wysyła `costDetails` z `totalCost = 0` i
  `totalUsage = 0` `[21-P2 C20.FR.06]`. Potem zwolnienie kwoty i `NotifySettlementRequest` ze `status = Canceled`
  `[21-P2 C20.FR.04]` `[21-P2 C20.FR.05]`.

## 4. Rozliczenie, paragon, odrzucenie (C21, C22)
- `PaymentCtrlr.SettlementByCSMS` brak albo `false`: stacja SHALL rozliczyć całkowity koszt przez terminal
  `[21-P2 C21.FR.01]`, potem wysyła `NotifySettlementRequest` ze statusem, kwotą, czasem, `transactionId` i `pspRef`
  `[21-P2 C21.FR.02]`.
- `SettlementByCSMS = true`: rozlicza CSMS bezpośrednio u PSP (referencja w `idToken`), a stacja SHALL NOT rozliczać
  przez terminal `[21-P2 C21.FR.05]` `[21-P2 C21.FR.06]`.
- Paragon: `ReceiptByCSMS = true` → CSMS zwraca `receiptUrl` w `NotifySettlementResponse` `[21-P2 C21.FR.03]`;
  `false` → stacja sama podaje `receiptUrl` i `receiptId` `[21-P2 C21.FR.04]`.
- Statusy rozliczenia (`PaymentStatusEnumType`): `Settled`, `Canceled` (brak części do zapłaty), `Rejected` (odmowa
  PSP), `Failed` (po ostatniej nieudanej próbie z powodu łączności) `[21-P2 §3.76]`.
- `Rejected` i `Failed` stacja zgłasza bez danych paragonu `[21-P2 C22.FR.01]` `[21-P2 C22.FR.02]`. OCPP nie
  przewiduje ponowienia: CSO „can try to capture the amount” u PSP, podając `PspRef` `[21-P2 C22]`.

## 5. Zwiększanie kwoty autoryzacji (C23)
- Gdy istnieje `PaymentCtrlr.IncrementalAuthorizationAmount > 0`, stacja SHALL poprosić terminal o zwiększenie, gdy
  koszt przekroczy bieżącą kwotę minus `IncrementalAuthorizationThreshold`. Bez progu próg ustala implementacja
  `[21-P2 C23.FR.01]`.
- Po udanym zwiększeniu stacja wysyła `TransactionEvent` z nowym `transactionLimit.maxCost` (rozbieżność nazwy
  `triggerReason`: sekcja 8) `[21-P2 C23.FR.02]`.

## 6. Terminal wolnostojący i kod QR (C24, C25)
- Kiosk: po autoryzacji karty CSMS SHALL wysłać `RequestStartTransactionRequest` z `idToken = <PspRef>`, `type =
  DirectPayment` `[21-P2 C24.FR.01]` i ustawić limit transakcji w odpowiedzi na `TransactionEvent(Started)`
  (`maxCost`, `maxEnergy`, `maxTime` albo `maxSoC`) `[21-P2 C24.FR.02]`. Po `Ended` CSMS SHALL zlecić rozliczenie
  kioskowi albo PSP `[21-P2 C24.FR.10]`.
- QR dynamiczny: stacja pokazuje URL z hasłem jednorazowym zależnym od czasu (TOTP) `[21-P2 C25.FR.01]`. CSMS SHALL
  sprawdzić hasło `[21-P2 C25.FR.07]`; przy nieważnym nie kieruje do PSP i nie autoryzuje `[21-P2 C25.FR.08]`.
  Dla QR statycznego wymagania TOTP nie obowiązują `[21-P2 C25]`.
- Kierowca może przed pokazaniem QR wpisać limit (`maxtime` w s, `maxenergy` w Wh, `maxcost`), który stacja dopisuje
  do URL i egzekwuje `[21-P2 C25.FR.04]` `[21-P2 C25.FR.05]` `[21-P2 C25.FR.06]`.
- `NotifyWebPaymentStartedRequest` pozwala stacji zablokować EVSE dla startu lokalnego na `timeout` sekund, do
  zdalnego startu `[21-P2 C25.FR.21]` `[21-P2 C25.FR.22]`.

## 7. Blokada środków na karcie: PSD2 art. 75–76
- Gdy kwota nie jest znana w chwili zgody (transakcja kartą inicjowana przez odbiorcę), dostawca płatnika może
  zablokować środki „only if the payer has given consent to the exact amount of the funds to be blocked”
  `[PSD2 art. 75]`.
- Zablokowane środki dostawca płatnika zwalnia „without undue delay” po otrzymaniu dokładnej kwoty, najpóźniej zaraz
  po otrzymaniu zlecenia płatniczego `[PSD2 art. 75]`.
- Zwrot z transakcji inicjowanej przez odbiorcę przysługuje, gdy autoryzacja nie określała dokładnej kwoty, a kwota
  przekroczyła to, czego płatnik mógł rozsądnie oczekiwać `[PSD2 art. 76]`.

**Wniosek:**
- kwota `AuthorizationAmount` i każde zwiększenie (C23) to blokada, na którą kierowca musi się zgodzić w dokładnej
  wysokości. Kwotę pokazujesz przed przyłożeniem karty i przed każdym zwiększeniem;
- szybkie rozliczenie po `Ended` (C21) i anulowanie przy sesji bez kosztu (C19, C20) zwalniają blokadę po stronie
  banku. Rozliczenie, które czeka (np. `Failed` bez ponowienia), trzyma środki kierowcy.

## 8. Rozbieżności w dokumencie i luki
- **`LimitSet` czy `LimitChanged`:** wymaganie mówi „triggerReason = LimitSet” `[21-P2 C23.FR.02]`, a diagram C23
  pokazuje `LimitChanged` `[21-P2 C23]`. W `TriggerReasonEnumType` jest tylko `LimitSet` („Limit of
  cost/time/energy/SoC for transaction has set or changed”) `[21-P2 §3.104]`. Rozstrzygnięcie: `LimitSet` (enum).
- Niezdefiniowane w OCPP: protokół terminal ↔ PSP, API terminal ↔ stacja, kiosk ↔ CSMS, CSMS ↔ PSP
  `[21-P2 C §2.9]` `[21-P2 C25.FR.20]`.
- Nieopracowane w bazie: silne uwierzytelnianie (SCA, rozporządzenie delegowane 2018/389), PCI DSS, VAT, polska
  transpozycja PSD2 (ustawa o usługach płatniczych). Pytanie o nie → mówisz, że baza tego nie obejmuje.
  - SCA: PSD2 jest w rejestrze, ale przepisu o silnym uwierzytelnianiu baza nie opracowała, a rozporządzenia
    2018/389 nie ma w rejestrze. Czy płatność inicjowana przez kierowcę wymaga SCA i jak traktować późniejsze dobicie
    kwoty, baza nie rozstrzyga.
  - PCI DSS jest w `sources/niedostepne.yaml` (niezarejestrowana). Wymagań co do tego, które dane karty może widzieć
    CSMS, baza nie podaje. Jakie dane karty trafiają do CSMS w OCPP 2.1, opisuje sekcja 2 (`PaymentCtrlr.PaymentDetails`).
  - Zasady schematów kartowych (capture, void, refund, chargeback i ich terminy) nie są w rejestrze.
- Moduł Payments z OCPI 2.3.0 (terminal po stronie PTP, potwierdzenie capture) opisuje `references/cdr-i-wycena.md` §5.
