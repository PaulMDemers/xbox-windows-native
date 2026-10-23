# 672: distinguish entry from final status

671 is closed: solid amber on black and zero UDP packets did not establish
whether final status signaling ran. This fresh diagnostic adds a distinct
post-freeze, post-encoding entry signal and a slow, repeated numeric result.
It does not repair the NIC, relax admission, or change ordinary Windows boot.

Host validation passed on the first672 attempts: 2,763 sanitizer assertion
groups, 73 complete waveform codes, 40 linked transport cases, 17 linked export
cases, six linked guard cases and 69 provenance/linkage checks. CPU, timers,
PCI, NIC and SMC responses are models; these are not physical delivery tests.
The full private image retains34 original object text/rodata sections exactly,
including display, sender, admission, PCI, allocator, interrupt and startup.

## Visible protocol

After the original hardware capture returns, the671 owner/freeze boundary,
saved-RAM copy and655 encoding remain in place. Original capture flags, freeze
flags and later transport-entry flags remain separate. Entry signaling occurs
only after successful encoding: dark for two seconds, green/off for eight
seconds, then dark. A failed SMC transaction or timer sample stops this path;
it cannot call NativeSend656. A successful marker adds a deliberate10-second
delay and SMC writes before transport; comparisons must retain that change.

After transport returns to its terminal caller, each of two rounds contains:

1. Two seconds dark.
2. Six seconds of the category color below.
3. Two seconds dark.
4. Slow red flashes, half a second on and half a second off. The count minus
   one is the exact selected value.

The category remains latched after the second round. Require the distinct
entry marker and two matching complete rounds before interpreting a result.
An incomplete sequence or a previously latched color is inconclusive. Even a
fully completed SMC transaction is not proof the user could see the LED.

| Category | Header / final latch | Selected value |
|---|---|---|
| Wrapper | Red/off | Exact669 lifecycle status |
| Admission | Red/green | Exact656 admission error1..5 |
| Send return | Amber/off | Exact native send return1..11 |
| Native result | Green/amber | Native error when send return is zero |
| Cleanup | Red/amber | Exact nonzero cleanup error |
| Local completion | Solid green | Zero: one red pulse per round |
| Invalid record | Solid red | One for bounds/phase; two for contradictory success |

Admission values:1 CPU,2 segment,3 cache,4 PCI,5 DMA. Other exact values remain
defined by the unchanged phase.h and nic.h. One selected field is displayed;
the complete original lifecycle/native outcome stays in RAM. Cleanup is shown
only for the UNSAFE lifecycle outcome with a nonzero cleanup error; an unsafe
outcome with no cleanup code reports the wrapper status instead. All other
ambiguous/incomplete states retain wrapper status. No numeric saturation.

## Bounds and failure behavior

The marker has four SMC transactions and10,000 requested one-millisecond waits.
The longest valid result has55 transactions and44,000 such waits. write658
retains its1,000-sample busy/completion bounds and original error results.
delay656 accepts at most1,000 microseconds; long pauses are explicitly composed
of finite one-millisecond calls. Callback/physical bus completion is assumed,
so these software limits do not promise a wall-clock bound on broken hardware.

Emission storage is atomically claimed before callbacks. Any timer/SMC error
ends that emission, retains its error and denies reuse. The caller holds with
CLI/HLT; it never resumes Windows, restores IF, resets, or retries transmission.
If live IF is unexpectedly enabled before final signaling, it holds without
peripheral reporting. Interrupt producers before the original capture freeze
remain a limitation; CLI does not exclude NMI, SMI or DMA.

## Test evidence and limits

host001 executes the actual portable classifier/emitter and unchanged write658
under ASan/UBSan. An independent event-time oracle checks all73 supported codes,
both rounds, every SMC transaction failure, first/middle/last timer failures,
reentry, busy/error/timeout status, marker failures and malformed inputs.

execute001 uses fresh isolated i386 fixtures against the complete image. It
models an already-completed marker to exercise transport and final reporting
independently. entry001 executes the real marker from XwnExport657 using saved
synthetic producer RAM and checks its complete waveform, no-send failure paths,
original packet preservation and terminal reentry. guards001 verifies that an
absent/failed marker prevents terminal transport and IF/preparation/reentry
guards cannot perform I/O. The original hardware capture itself is not executed
by these function fixtures. Real PCI/SMC port instructions run against models.

All native admission gates remain. Three local descriptor completions are not
UDP receipt, cache coherency, game acceleration or a480p fix. The packet stays
772 bytes with its original capture and identity fields; LED reporting does not
replace or modify packet evidence. Firmware and test binaries remain private.

## Physical lifecycle

Any fresh watched attempt uses only E:/Applications/XWNLatch672 and an exclusive
180-second receiver. One SITE request,20-second reply bound; accepted or
uncertain launches cannot be retried. No Windows startup hook. Deliberate held
black screen requires manual power-cycle. See stage/launch/run/observation
records for actual state; this report does not assume a physical outcome.

Protected720p, normal startup, savedXBOX480, releases/private256 remain intact.
The persistent firewall rule remains. Boot intermittency,1080i,Ftdisk49 and
Popup26 remain unresolved; no change to their conclusions.

## Actual672 launch and receiver failure

One SITE was accepted2026-10-23T00:50:13.182057Z. Receiver9132 exited1;
controller76024 exited0. The receiver published bound readiness BEFORE its
manifest check, which rejected an invalid fixture label. There is no capture
summary and no basis for a zero-datagram or delivery claim. See
receiver-failure001; retain the original private config and scripts unchanged.
No relaunch. The user has been asked for entry/category/pulse observations;
manual recovery and the single672 collection/audit remain outstanding.
No temporary startup hook. Fresh receiver673 host tests address the readiness
contract but have not been wired into a new physical controller.
