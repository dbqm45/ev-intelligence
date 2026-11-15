# Ramki RPC (OCPP-J) i kody błędów

Źródła: `[J16]`, `[J16E]`, `[201-P4]`, `[21-P4]` (znaczniki jak w `SKILL.md`).

## Typy ramek
| Typ | Numer | Wersje | Źródło |
|---|---|---|---|
| CALL | 2 | 1.6, 2.0.1, 2.1 | `[J16 §4.1.3]` `[201-P4 §4.1.3]` |
| CALLRESULT | 3 | 1.6, 2.0.1, 2.1 | j.w. |
| CALLERROR | 4 | 1.6, 2.0.1, 2.1 | j.w. |
| CALLRESULTERROR | 5 | tylko 2.1: „Error response to a response message” | `[21-P4 §4.1.3]` |
| SEND | 6 | tylko 2.1: komunikat bez odpowiedzi (nazwa akcji nie kończy się na „Request”) | `[21-P4 §4.1.3]` |

- Postać CALLERROR: `[<MessageTypeId>, "<UniqueId>", "<errorCode>", "<errorDescription>", {<errorDetails>}]` `[J16 §4.2.3]`.
- `messageId` w CALLRESULT i CALLERROR MUST być równy identyfikatorowi CALL `[J16 §4.1.3]`.
- 1.6: ramkę z nieznanym numerem typu serwer SHALL zignorować `[J16 §4.1.3]`. 2.0.1: odbiorca odpowiada CALLERROR
  `MessageTypeNotSupported`, a nadawca SHALL zamknąć połączenie albo wrócić do CALL / CALLRESULT / CALLERROR `[201-P4 §4.4]`.
- 2.0.1: gdy nie da się odczytać `MessageId`, CALLERROR SHALL zawierać `"-1"` jako identyfikator `[201-P4 §4.2.3]`.
- „Failure to process the message” serwer zgłasza przez CALLERROR `[201-P4 §4.2.3]`. W 1.6 CallError stosuje się przy
  błędzie transportu albo przy treści niespełniającej wymagań komunikatu `[J16 §4.2.3]`.

## Jedno CALL naraz
- 1.6: strona „SHOULD NOT send a CALL message to the other party unless all the CALL messages it sent before have been
  responded to or have timed out” `[J16 §4.1.1]`.
- 2.0.1: „SHALL NOT”, a reguła obowiązuje **per połączenie OCPP-J** (CSMS może w tym czasie pisać do innych stacji)
  `[201-P4 §4.1.1]`.
- Timeout: „implementation-dependent”; zalecenie: uwzględnić rodzaj sieci (sieci komórkowe mają dłuższe czasy) `[J16 §4.1.1]`
  `[201-P4 §4.1.1]`. Specyfikacja nie podaje wartości liczbowej. W 2.0.1 czas ten konfiguruje
  `OCPPCommCtrlr.MessageTimeout` („specifies after which time a message times out”) `[201-CSV]`.
- Obie strony mogą otrzymać CALL drugiej strony w trakcie czekania na odpowiedź, bo komunikaty mogą się minąć
  `[J16 §4.1.1]` `[201-P4 §4.1.1]`.

## Identyfikator wiadomości (`messageId`)
- 1.6J: `messageId` CALL MUST różnić się od wszystkich wcześniej użytych przez tego nadawcę dla CALL „on the same
  WebSocket connection”, maks. 36 znaków; CALLRESULT/CALLERROR niosą id swojego CALL `[J16 §4.1.4]`.
- Errata OCPP-J 1.6 (wpis oznaczony **[DRAFT]**) doprecyzowuje zamiar: unikalność wobec **każdego** połączenia
  z tym samym URL połączenia, bo ponowne użycie id po reconnect psuje kolejkowanie komunikatów `[J16E §3.7]`.

**Wniosek:** generuj UUID i nie zeruj licznika id po ponownym połączeniu; deduplikację po stronie CSMS opieraj na
parze (identyfikator stacji, `messageId`) (skill `ev-integration-architect`).

## Kody CALLERROR
| Kod | 1.6 | 2.0.1 / 2.1 |
|---|---|---|
| `NotImplemented` | ✓ | ✓ |
| `NotSupported` | ✓ | ✓ |
| `InternalError` | ✓ | ✓ |
| `ProtocolError` | ✓ | ✓ |
| `SecurityError` | ✓ | ✓ |
| `FormationViolation` | ✓ | — |
| `FormatViolation` | — | ✓ |
| `PropertyConstraintViolation` | ✓ | ✓ |
| `OccurenceConstraintViolation` | ✓ | — |
| `OccurrenceConstraintViolation` | — | ✓ |
| `TypeConstraintViolation` | ✓ | ✓ |
| `GenericError` | ✓ | ✓ |
| `MessageTypeNotSupported` | — | ✓ |
| `RpcFrameworkError` | — | ✓ |
Źródła: 1.6 `[J16 §4.2.3]`, 2.0.1 `[201-P4 §4.3]`, 2.1 `[21-P4 §4.3]`.

Errata OCPP-J 1.6 opisuje literówkę `OccurenceConstraintViolation` i błędną nazwę `FormationViolation`, ale umieszcza je
w sekcji „Known issues that will not be fixed” z uzasadnieniem „Do not fix, this is a message level change, might break
implementations” `[J16E §5.1–5.2]`. W 1.6 obowiązują więc nazwy oryginalne.
