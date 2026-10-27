#720: one saved-value CR1b write control

718's explicit85->05->85 attempt read back05 after restoration.719 read six85
samples across setup without writing CR1b. Both runtimes are closed.720 tests
one freshly saved85 write after confirming unchanged prewrite setup samples.
No05 target, second CR1b write, mismatch retry, bitmask or functional driver fix.

Native admission and output blank/restore remain. A changed setup sample refuses
the write. After one byte write85, immediate readback is captured, then output
is restored once and final sequencer/context/pitch/CR11 checked. No pending-bit,
clock, timing, encoder, geometry orCR22 writes. A mismatch is reported and held;
manual power-cycle is recovery. A green result does not prove an identical write
was accepted: an ignored write also leaves85, covered explicitly by host tests.

Result224bytes fits existing256-byte owned slot.13-row optical panel:7200000d,
bridge phase/checkpoint/return, payload phase/error, initialCR1b, prewriteCR1b,
writtenCR1b, immediate readback, after-output-restoreCR1b, write-attempt flag,
samplemask. Full mask7f denotes six setup reads plus immediate write readback.
Unobserved postwrite field isFFFFFFFF after admission setup, not a device value.
Bridge phase4/checkpoint5 means returned call. Raw photo is required before reset.

Green720 requires unchanged readings and final checks.7208 is immediate write
mismatch;7207 changed setup/final sample;7204 final sequencer/context/pitch/CR11
failure;7205 unlockCR11 check;7202 blank check;7201/7206 baseline rejection.
Final7204 can supersede earlier error; raw write fields remain. No code alone
proves why physical bit7 changes or resolves717/708/709 retrospectively.

Fresh validation:204 instruction models,76 isolated optical cases,12 diskless
CPU cases(all closed),23 nxdk page,372 compiled ownership and131379 host ownership
cases. Payload5100 padded9916;16 relocations/four absolute; bridge code end558.
Exact built bridge/payload embedded in XBE. Decimal719 geometry retained by
specific identifier/path and diagnostic-code renaming, not global substitution.
No failed build or test in720 preparation. Prior failures remain immutable.

See source-review001.json for primary references retained from717/719 and limits.
Host models verify access scope, count/order, refusal/restore flow, report and
ownership. They do not prove hardware bit semantics or Windows1.6 mode support.

One SITE accepted2026-10-27T16:00:54.986132+00:00 after exact staged readback.
User Orange, holding. Photo requested; exact failed check unknown until raw
values decoded. No reset request, repeat launch or collection.

#720 photo decoded: same-value write mismatch; held orange, reset pending

Photo001 signature7200000d; bridge phase4/checkpoint5/return7208; payload
phase5/error7208. CR1b saved85, prewrite85, requested85, immediate05,
after-output-restore05; write-attempted1, samples mask7f. All416bits agree
across three thresholds/five offsets;352 middle-row bits independently agree
using adjacent-row interpolation. Original photo remains private C:/xwn720.

The single same-value85 request sufficed for this observed readback change;
it did not require first requesting05.719's no-write setup retained85.
This does not establish bit7 semantics, the cause, or full-mode708/709 failure.
No second CR1b write/retry/mask/driver patch.7208 survived final checks rather
than being superseded by7204; this is bounded code-path evidence, not broad
hardware restoration proof. Native saved-value control FAILED.

Manual power-cycle requested after photo preservation; await explicitReady at
UnleashX. Then
collect720 ONCE and audit preparation/pins separately from native failure.
No new launch or closed-runtime recollection. No startup hook or owned host
process. Console currently held; normal Windows shutdown not applicable.

#720 CLOSED: saved-value CR1b write mismatch; preparation audit passed

User power-cycled and replied Ready. Collected nine fresh preparation records
ONCE, double-read exact; staged owner/XBE unchanged and unrelated E-root/apps
entries unchanged. Source/binary/photo/schema pins and independent allocation/
alias bounds checks passed. Kernel PCI/CRTC/sequencer/geometry/allocation values
match closed718 and719. These are preparation observations, not native readback.

Native photo7200000d: phase4/checkpoint5, payloadphase5, return/error7208;
saved85/prewrite85/request85/immediate05/post-output05; attempted1, mask7f.
The native saved-value control FAILED. No initial05 target or second CR1b write.
719's setup-only samples remained85;720 narrows the observed difference to the
single write/readback operation. Why bit7 reads differently remains unresolved.
Do not infer bit7 semantics, a corrected mode driver, or708/709's root cause.

Console is at UnleashX after MANUAL power-cycle, not normal Windows shutdown.
No startup hook or owned host process; all12 CPU fixtures closed. Build/xemu
leases released; hardware ticket retained. Original720p baseline protected.
No new launch. Never rerun, recollect, or parent this closed physical runtime.

Next: review the exact CR1b indexed read/write access and documented register
semantics before designing a fresh bounded discriminator. Use retained source
and immutable observations only; no speculative bit7 mask, retry/restore loop,
CR22 write, encoder/timing change or functional driver promotion. Any new
hardware probe needs fresh namespace, host validation, staged-byte readback,
and available watcher/reset. Networking/bootintermittency/1080i remain tabled.
