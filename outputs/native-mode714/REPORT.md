#714: single CR19 changed-readback and restoration checkpoint

713 completed the unlock-key request, unchanged CR11 check and restoration with
a user-reported green hold.714 now tests exactly one common-setup write from704:
CR19=10, then full-byte readback, then exact restoration to the admitted51 value.
This temporarily changes framebuffer pitch while blanked; it is not a final mode
change and does not program display timings or the encoder.

Native admission retains713 predicates and adds CR19==51 before blanking. After
blank readback and unlock/CR11 checks, it writes10, captures the readback, writes
the saved51 exactly once, and verifies the restored byte, pitch5120 and unchanged
CR11. Restoration is requested even if the test readback fails. Only after those
checks succeed does it run the bounded wait and existing output-restoration pair.
A failure still takes the single visibility-restoration path, never a retry.

CR19 bits7:5 contribute to pitch; the pinned current context has CR13=80 and CR25
bit5 clear. The target10 reduces the pitch to1024 bytes, then51 restores5120.
The temporary smaller stride remains within the retained framebuffer allocation.
No new framebuffer allocation or writes, CR11 write, clock/interrupt programming,
SMBus/encoder access, other timing writes or firmware-state borrowing is added.
See source-review001 for pinned Cromwell and the versioned Linux reference.

Success0x714 requires the test readback and restoration checks.7146 rejects an
unexpected CR19 baseline;7147 reports test readback mismatch;7148 reports register/
pitch/CR11 restoration mismatch.7144 retains priority for visibility/context
restoration failure. GREEN second bar means success; ORANGE a returned rejection.
Pre-call refusal colors remain. Black alone cannot identify the failure phase.
The208-byte result fits the256-byte slot. Raw payload5120 is padded to9916;
17 relocations include four internal absolute32 entries.

## Validation

Fresh131379 ownership cases, four ASan/UBSan page placements,12 diskless CPU cases
(all closed),176 exact relocated instruction models,23 compiled nxdk page cases
and372 compiled ownership cases passed. Exact bridge/payload bytes are embedded
once in the linked binary. Source/binary pins and namespace-only kernel/bridge
changes were reviewed. model-scope001 corrects one inherited report label: CR19
is explicitly a temporary pitch/geometry write, not an absence of geometry writes.
Executed harness and receipts are retained unchanged; no result is promoted.

The models cover rejected baseline, dropped/coerced test write, ignored unlock
with writes locked or already enabled, failed CR19 restoration, CR11 side effect,
combined restore/context failure and prior timer/admission failures. Success would
qualify this specific register transaction, not all extended writes, unlock-key
causality, the complete704 setup, Windows1.6 or the old708/709 failure location.

## Physical lifecycle

Unique E-owned staging, exact readback, no Windows or startup hook. One launch
only; deliberate hold and manual power-cycle required. Native results are optical/
RAM; persisted reports record kernel preparation only. Current state is recorded
in NEXT.md and the exact stage/launch/observation/collection receipts.

One SITE accepted2026-10-27T06:22:35.501782+00:00. User reported "Green, holding". Manual reset and collection completed; see closeout.
This is optical success, not a separately witnessed blank interval or raw RAM read.
No repeat launch.

## Closed physical result

User reported "Green, holding". After the requested manual power-cycle and Ready,
nine preparation reports were collected once/double-read. Source/binary/report
pins, independent aliases, allocation and unrelated-entry checks passed. Kernel
PCI/CRTC/SEQ/geometry/allocation match713 exactly. Last file phase handoff_armed
is preparation; native0x714 success is separately user-observed optical evidence.
No separately witnessed blank interval or raw native result extraction is claimed.
Runtime CLOSED; console at dashboard, no hook or owned host process. Manual reset
is not Windows normal shutdown. Never relaunch/recollect this attempt.

This supports this specific CR19 test and restoration after the key request. It
does not establish that the key caused access, that every extended register is
writable, that all704 setup works, or that native mode switching/Windows1.6 works.
Next capture remaining common PRAMDAC setup registers read-only before selecting
additional changes that can be restored to their independently observed baseline.
