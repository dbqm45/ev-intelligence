# Metrologia prawna: MID, Eichrecht, podpisane wartości pomiarowe

Źródła: dyrektywa MID 2014/32/UE `[MID]`, MessEG § 33 `[DE-MESSEG-33]`, nota aplikacyjna OCA „Signed Meter Values in
OCPP” v1.0 `[OCA-AN-SMV]`, OCPI 2.3.0 `[OCPI230]`, ustawa o elektromobilności `[PL-EMOB]`. **Niedostępne:** MessEV (w
tym załącznik 7), wymagania PTB, OCMF, Prawo o miarach (PL) (`sources/niedostepne.yaml`). Zdania **Wniosek** to
interpretacja, nie opinia prawna.

## Spis treści
1. MID: zakres i opcjonalność
2. MI-003: liczniki energii czynnej
3. Niemcy: MessEG § 33
4. Podpisane wartości w OCPP (nota OCA)
5. Podpisane dane w OCPI
6. Polska
7. Czego nie opracowano

## 1. MID: zakres i opcjonalność
- MID określa wymagania dla przyrządów pomiarowych wprowadzanych do obrotu lub użytkowania do zadań z art. 3 ust. 1
  `[MID art. 1]`. Obejmuje przyrządy z załączników III–XII, w tym liczniki energii elektrycznej czynnej (MI-003)
  `[MID art. 2]`.
- **Opcjonalność:** państwa członkowskie MOGĄ wymagać przyrządów pomiarowych do zadań pomiarowych, gdy uznają to za
  uzasadnione m.in. ochroną konsumentów i uczciwym obrotem. Jeśli nie wymagają, informują Komisję i inne państwa o
  powodach `[MID art. 3]`.

**Wniosek:** to, czy licznik w stacji ładowania musi spełniać MID, rozstrzyga prawo krajowe, a nie sama dyrektywa. Dla
Polski tego przepisu (Prawo o miarach i akty wykonawcze) baza nie zawiera.

## 2. MI-003: liczniki energii czynnej `[MID Annex V]`
- Dotyczy liczników energii elektrycznej czynnej do zastosowań mieszkaniowych, handlowych i lekko przemysłowych. Nie
  obejmuje przekładników.
- Licznik mierzy energię czynną zużytą w obwodzie. Producent określa klasę: A, B albo C. Energia jest wyświetlana w kWh
  albo MWh.
- Oddanie do użytkowania:
  - gdy państwo wymaga pomiaru w zastosowaniach mieszkaniowych, dopuszcza każdy licznik klasy A, a do określonych celów
    może wymagać klasy B;
  - w handlowych i lekko przemysłowych dopuszcza klasę B, a do określonych celów może wymagać klasy C.
- Ocena zgodności: procedury B + F, B + D albo H1.
- Dyrektywa nie mówi wprost o licznikach prądu stałego. Definicje MI-003 posługują się częstotliwością i współczynnikiem
  mocy (cos φ). **Wniosek:** stosowanie MI-003 do pomiaru DC w ładowarkach wymaga potwierdzenia w prawie krajowym albo
  w wytycznych organu metrologicznego; baza takiego dokumentu nie zawiera.

## 3. Niemcy: MessEG § 33 `[DE-MESSEG-33 § 33]`
- (1) Wartości mierzonych wielkości wolno w obrocie gospodarczym lub urzędowym podawać i stosować tylko wtedy, gdy do
  ich wyznaczenia użyto przyrządu pomiarowego zgodnie z przeznaczeniem i wartości dają się odnieść do wyniku pomiaru.
- (2) Kto stosuje wartości pomiarowe, ma się w miarę możliwości upewnić, że przyrząd spełnia wymagania prawne, i uzyskać
  potwierdzenie od użytkownika przyrządu, że ten wypełnia swoje obowiązki.
- (3) Kto stosuje wartości pomiarowe, zapewnia, że rachunek oparty na pomiarach może w prosty sposób zweryfikować jego
  adresat, i w razie potrzeby udostępnia do tego odpowiednie narzędzia.

**Wniosek:** dla CPO i eMSP w Niemczech wymóg „prostej weryfikacji rachunku” jest powodem przesyłania podpisanych
wartości pomiarowych aż do faktury. Kategorie rozwiązań i szczegóły (MessEV, PTB) są niedostępne.

## 4. Podpisane wartości w OCPP (nota OCA)
- Zakres noty: **tylko transport** podpisanych wartości między stacją a CSMS, dla OCPP 1.6, 2.0.1 i 2.1. Poza zakresem:
  identyfikacja klienta, płatności ad hoc, przekazanie danych do MSP, sposób weryfikacji przez klienta `[OCA-AN-SMV §1]`.
- Według noty, żeby spełnić Eichrecht, CSMS musi dostać co najmniej podpisane wartości początkowe i końcowe. W 1.6
  wystarczy `SampledDataSignReadings = true` (wartości w `StopTransaction.req`). `SampledDataSignStartedReadings`
  dodaje podpisaną wartość początkową w `MeterValues.req` (1.6) albo `TransactionEvent(Started)` (2.x)
  `[OCA-AN-SMV §2.1]`.
- Licznik musi być certyfikowany i wzorcowany; po wygaśnięciu legalizacji zgodność jest tracona. Według noty okres
  ważności wynosi w Niemczech od 4 do 16 lat zależnie od kategorii rozwiązania (odesłanie do załącznika 7 MessEV, który
  jest niedostępny) `[OCA-AN-SMV §2.2]`.
- Zgodność z Eichrecht jest możliwa także bez przesyłania wartości do CSMS (przechowywanie lokalne i wyświetlacz). To
  poza zakresem OCPP `[OCA-AN-SMV §2.2]`.
- Kodowania: najczęściej OCMF i EDL; nota ich nie narzuca `[OCA-AN-SMV §2.2.1]`.
- Klucz publiczny jest właściwy dla licznika; zmienia się tylko przy wymianie lub modyfikacji licznika. Bundesnetzagentur
  wymaga publikacji uruchomionych stacji z kluczami publicznymi (baza niedostępna) `[OCA-AN-SMV §2.2.5]`
  `[OCA-AN-SMV §2.2.6]`.
- Według noty niemiecki Eichrecht wymaga w CDR podpisanych wartości z początku i końca transakcji. Wartości pośrednie
  są obowiązkowe przy zmianie taryfy w trakcie transakcji `[OCA-AN-SMV §2.3.3]`.
- Koszt liczy się zwykle z czasów w podpisanych danych (od pierwszej do ostatniej wartości podpisanej), a nie z
  `timestamp` komunikatów OCPP `[OCA-AN-SMV §2.3.1]`.
- `SignedMeterValueType`: `signedMeterData`, `signingMethod` (pusty, jeśli zawarty w danych), `encodingMethod` (np.
  OCMF, EDL), `publicKey` (pusty albo Base64 ciągu `oca:<encoding>:<content-type>:<klucz>`) `[OCA-AN-SMV §3.2.1]`
  `[OCA-AN-SMV §3.2.2]`. Metody podpisu w tabeli noty: ECDSA na krzywych secp192k1/r1, secp256k1/r1, brainpool256r1,
  secp384r1, brainpool384r1 z SHA-256 `[OCA-AN-SMV §4.2.1]`.
- Konfiguracja `[OCA-AN-SMV §3.3]` `[OCA-AN-SMV §4.3]`:
  - 1.6: klucze `MeterPublicKey[ConnectorID]` (RO), `PublicKeyWithSignedMeterValue` (`Never`, `OncePerTransaction`,
    `EveryMeterValue`), `SampledDataSignReadings`, `SampledDataSignStartedReadings`, `SampledDataSignUpdatedReadings`,
    `AlignedDataSignReadings`, `AlignedDataSignUpdatedReadings`;
  - 2.x: `OCPPCommCtrlr.PublicKeyWithSignedMeterValue`, `FiscalMetering.PublicKey` (zwykle na poziomie EVSE),
    `AlignedDataCtrlr.SignReadings`, `AlignedDataCtrlr.SignUpdatedReadings`, `SampledDataCtrlr.SignReadings`,
    `SampledDataCtrlr.SignStartedReadings`, `SampledDataCtrlr.SignUpdatedReadings`.
  - Przy `Never` po wymianie licznika klucze z historycznych transakcji nie będą już dostępne przez odczyt
    konfiguracji, co według noty może być problemem zgodności.
  - W 1.6 wartość klucza konfiguracji ma limit 500 bajtów, więc dłuższego klucza publicznego nie da się tak odczytać
    `[OCA-AN-SMV §3.3.1]`.

**Wniosek:** w CPMS przechowujesz podpisane wartości i klucz publiczny razem z transakcją. Przy wymianie licznika
zachowujesz stary klucz, bo `Never` nie pozwoli go potem odczytać.

## 5. Podpisane dane w OCPI `[OCPI230 §10.4.7]`
`SignedData` w CDR: `encoding_method`, `public_key`, `signed_values` (`nature` `Start`, `End`, `Intermediate`) i `url`
do weryfikacji przez kierowcę. Szczegóły w skillu `ev-billing-tariff-expert`.

## 6. Polska
- Ustawa wymaga, żeby każdy punkt ładowania na ogólnodostępnej stacji miał system pomiarowy przekazujący dane do systemu
  zarządzania stacją w czasie zbliżonym do rzeczywistego `[PL-EMOB art. 3 ust. 1]` (pkt 4 lit. b). O legalizacji i
  typie licznika ustawa nie mówi.
- Prawo o miarach i przepisy o prawnej kontroli metrologicznej liczników są niezarejestrowane.

## 7. Czego nie opracowano
MessEV i wymagania PTB, OCMF (S.A.F.E.), baza BNetzA, Prawo o miarach, wersja skonsolidowana MID, normy dla liczników
DC. Wszystko w `sources/niedostepne.yaml`.
