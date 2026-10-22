# 662: classify captured CPU admission conditions

This diagnostic uses closed661 only as pinned source and observed evidence.
It retains the native inspect/admission/sender and reads the first five fields
already stored in NativeAdmission656 after the existing return. No new hardware
reads, register writes, relaxed guard or borrowed state are introduced.

The stored predicate mask is CR0=1, IF=2, CPUID=4, RAM=8, ESP=16. CpuStage662 is
1 for an early inspect() predicate,2 for later RAM/ESP predicates,0 for no
predicate,3 for a missing pointer. All five fields are assigned before inspect's
first early return. Later descriptor/cache fields may be incomplete and are
not read by this classifier. The raw mask and stage are diagnostic BSS values,
not externally recovered evidence.

When early predicates fail, the displayed result considers those first: the
unchanged inspect() returns before the later RAM/ESP checks. A concurrent RAM or
ESP mismatch is preserved in the BSS mask but is not claimed as the return's
cause. Two or more failing predicates in the relevant stage have a distinct code.

## Persistent LED codes

Observe the lasting pattern after15seconds on the held black screen.

| Pattern | Interpretation conditional on final latch success |
| --- | --- |
| Even red/off | CR0 masked state differs from expected |
| Even amber/off | Captured interrupt flag is set |
| Red/green alternating | Required captured CPUID features absent |
| Green/amber alternating | Captured RAM size outside64/128MiB contract |
| Red/amber alternating | Captured ESP outside expected stack range |
| Even green/off | Multiple mismatches at relevant early/late stage |
| One green slot, three off | CPU category inconsistent with fields, or missing pointer |
| One amber slot, three off | Other/unknown admission category |
| One red slot, three off | Encoding failure, network skipped |
| Solid amber | Entry/timed indication failure, network skipped |
| Solid red | Sender used and unsafe cleanup; buffers remain live |
| Two amber slots, two off | Sender error without unsafe cleanup |
| Two green slots, two off | Unexpected/incomplete result |
| Solid green | Three safe local completions, not packet-delivery proof |

Initial amber/off and timed green/off indications are not final evidence. A
failed final latch can leave a previous state. Ask about cadence if a color alone
is ambiguous, and preserve inconclusive observations. No LED diagnoses a faulty
CPU or recovers exact register values.

## Validation and lifecycle

Build/host/compiled/review receipts are authoritative. Host tests exercise all
32 CPU predicate combinations across result/error precedence, plus boundary and
missing-pointer cases. Exact-linked tests model native sender outputs and raw
IN/OUT, verify captured fields stay unchanged and the final SMC mask written
matches classification. These models do not qualify native NIC/DMA/CPU timing.
Native admission/sender and protected display object sections must be unchanged.

Use fresh C:/xwn662 paths, identity and180-second capture, with one unique
/E/Applications/XWNLatch662 candidate. Verify the permanent scoped firewall and
protected720p/startup/savedXBOX480 files. One20-second-bounded SITE only. No startup
hook, automatic reset or Windows launch. Record observation, request manual
recovery, then one collection/audit. Do not reopen any closed runtime. Preserve
Ftdisk49/Popup26 limitations, immutable releases and private recovery.

## Qualified artifact

Source tree `5439d35bdf4b6d717cacbf83baf539b19869ec5e`; XBE SHA256 `830328312d05658aee415a22e4c2980f03af3ccd2a0ddb4fe6648919bfb46b6f`.
53,760 sanitizer cases plus12 boundary conditions,29 exact-linked cases and41
artifact checks passed.20 old object sections remain unchanged. Native sender
outcomes/rawIN/OUT are modeled; physical classification remains unobserved.

## Physical outcome: closed662, indication failure

One SITE accepted at22:15:34.368933Z. User reported Solid Amber and separately
confirmed Black screen, solid amber. This matches nonzero entry or timed LED
indication error in the final classifier; the native sender is skipped on that
path. Exact error and raw status are unknown. Final-latch success is inferred
from the observed code, not recovered BSS. No CPU predicate was identified.
The661 CPU-category observation remains separate;662 does not override it.

The fresh identity-matched receiver ran180seconds, covering171.85seconds after
launch, and received zero datagrams (exit2). Its launch_sent=false concerns the
receiver's lack of launch authority; the separate SITE was accepted once.
Persistent scoped firewall was verified and retained; no firewall-failure claim.

After requested manual power-cycle the user replied Ready. One collection and
retained audit passed:28 selected files unchanged, five hives parse, savedXBOX480
intact, no newevents/6006. This is manual recovery, not a normal Windows restart
or full FATX audit. All owned host processes exited; no startup hook remains;
console confirmed at dashboard. No retries. See observations001/002, recovery,
collection, audit, reconciliation and closure001. Preserve this failed attempt.
