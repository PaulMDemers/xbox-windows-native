# 661: expose the native network admission category

Prepared from closed660's pinned source, not its runtime. The only functional
diagnostic change is final LED classification. The capture, entry indication,
NativeSend656 and its admission checks remain unchanged. No new hardware reads,
state borrowing or safety-check relaxation is introduced. No Windows launch or
automatic reset is intended; the final result deliberately holds for observation.

## Persistent light codes

Observe the final light after at least 15 seconds, with the screen still black.

| Light | Existing result reported |
| --- | --- |
| Red/off | CPU admission category |
| Amber/off | Segment admission category |
| Alternating red/green | Cache admission category |
| Alternating green/amber | PCI admission category |
| Alternating red/amber | DMA admission category |
| Green/off | Unknown nonzero admission code |
| Solid green | Three local completions with safe cleanup, not delivery proof |
| Solid red | Sender used and cleanup unsafe; buffers remain live |
| Solid amber | Entry or timed indication failed; network skipped |
| One red slot, three off | Encoding failed; network skipped |
| Two amber slots, two off | Sender error without unsafe cleanup |
| One green slot, three off | Unexpected/incomplete result |

These codes differ from660. Classification preserves setup-error and unsafe
cleanup precedence. A failed final latch can leave an earlier indication visible;
the source's raw status values are not recovered by a user-observed light. In
particular the initial amber/off and timed green/off are not final evidence.
Unknown/ambiguous observations remain inconclusive.

The packet stays the original frozen display capture. A fresh identity and
180-second receiver are required even if admission rejects again. No received
packet alone cannot identify a firewall or sender failure. The existing persistent
Xbox-only UDP rule remains installed and is verified before launch and at closure.

## Validation and lifecycle

Build, host, exact-linked and artifact receipts are authoritative. Host models
exercise classification and caller flow; they do not qualify native NIC, DMA,
cache, timing or physical boot behavior. Unchanged source and object-section
comparisons protect admission, sender and display code. Fresh paths are
C:/xwn661 and /E/Applications/XWNLatch661. No startup hook or ordinary720p change.

One accepted or uncertain SITE must never be retried. Record the held LED/screen,
then request manual power-cycle before one collection and selected-file/hive/event
audit. Manual recovery is not normal Windows restart. Historical Ftdisk49/Popup26,
closed attempts and frozen releases remain preserved. This is a diagnostic only.

## Qualified artifact

Source tree: `d9c9ebeb092a6d2da01416ab6b8d9e9a3492170d`. XBE SHA256: `c374f9f4d2c4fd5994661768d56b8edc01cba2f4cae36dfead872afa63c62d93`.
1,680 sanitizer cases, 21 exact-linked cases and 39 artifact checks passed.
Twenty old object sections are unchanged. Source pins include every authored
script. Native sender outcomes and raw IN/OUT remain modeled in linked tests.
Controller accepted/uncertain one-shot tests passed. Preparation captured all
28 selected files twice. Stage/readback status is recorded in stage001.json.

## Physical result: closed661

One SITE accepted at22:04:12.914443Z. User reported blinking red on black and
explicitly confirmed equal on/off, distinguishing CPU admission from the brief
red encoding-error code. This matches A656_CPU=1 before send656. Raw status and
which CPU predicate failed remain unknown; no faulty-CPU conclusion follows.
The source checks CR0, IF, CPUID features and later RAM/stack bounds. The later
check is only reached after earlier segment/cache inspection checks succeed.

The fresh identity-matched receiver ran180seconds, covering173.14seconds after
launch, and received zero datagrams. Exit2 means no valid packet; receiver's
launch_sent=false is its own lack of launch authority, not denial of the separate
accepted SITE receipt. Permanent scoped firewall was verified and retained.

After requested manual power-cycle, user replied Ready. One collection and audit
passed:28 selected files unchanged, five hives parse, savedXBOX480 intact, events
unchanged/no new6006. This is manual recovery, not Windows restart or full FATX
proof. All owned processes exited; console at dashboard; no startup hook.
Initial cadence ambiguity and its explicit resolution are preserved in
observation001/002. See reconciliation001 and closure001. Never rerun this attempt.
