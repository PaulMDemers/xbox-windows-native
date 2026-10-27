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
