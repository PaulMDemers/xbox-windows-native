#539: entry-footprint review and post-stack-marker ablation

The exact ordinary374 and recorder490 images do not contain wholly different
Xromwell programs. Their first288316 payload bytes differ only at offsets f0-f4:
the original MOV ESP,02800000 is replaced with a jump to a diagnostic LED stub.
The recorder also adds235972 zero bytes and a574-byte stub at payload80000.
Both allocate1MiB; their first copies initialize288316 and524862 bytes respectively.
The later loader copies1MiB. Uninitialized-tail behavior is a possible independent
variable, not an established defect or physical explanation.

The extra post-stack stub is introduced by466, with corrected470 SMBus masks
integrated by471. It restores the original stack instruction, saves registers
and flags, performs two bounded LED transactions, then resumes at026000f5.
Its failure path halts.536 CPU receipts precede this hook and cannot measure it.
The wrapper's earlier LED operation, allocation guards, memory comparisons and
three diagnostic file lifecycles are additional variables versus ordinary374.

Candidate539b restores exactly five original instruction bytes. It retains the
long image, padding, inactive stub, copy length, allocation requests, wrapper
guards, pre-handoff LED operation and file IO. Path namespace and section digest
also change. The inverse patch reconstructs exact490.539a is a namespace-only
host control and is not scheduled for console execution.

One fresh539b launch is planned after user confirmation that the console remains
at UnleashX after536's normal Windows Restart, without intervening launch/reset.
Only the new /E/Applications/XWNBoot539b directory is staged. All ten selected
baseline files must match retained536 after2 and again match immediately before
launch. The controller journals before a single20-second SITE request and refuses
retries after accepted or uncertain requests. No startup hook is installed.

If Windows reaches the desktop, request normal Windows Restart and wait for the
user's dashboard observation. Collect only539's new run, audit five hives/events,
and decode its pre-handoff packets. No second launch is admitted. A successful
boot would show that the added post-stack hook was unnecessary for this single
instrumented warm boot; it would not establish a fix or cause for ordinary532's
failure. A failure would also be only one observation. Host memory/device/API
models do not prove physical kernel, cache, interrupt, SMBus or boot behavior.

Preserve prefix-host001's pointer-comparison failure and workflow001's redundant
replacement failure. Neither reached hardware. Corrected unique successors are
prefix-host002 and workflow002. The prior536 and earlier runtime records remain
closed.720p, ordinary launcher/startup, protected drivers and recovery stay intact.
Xbox C is not accessed. No driver patch or D3D/GPU/game/release claim is made.
