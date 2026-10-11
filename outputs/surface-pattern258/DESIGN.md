# A dedicated buffer before renderer references

The prior222/224 CPU lease can free its buffer in IRP_MJ_CLEANUP. Its safety
depends on never exposing it to GPU/renderer references. Reusing that lease for
the257 pixel test would invalidate that assumption even if the ordinary run
kept its handle open. An application failure must not cause a use-after-free.

New258 is a separate emulator-only demand diagnostic driver. It allocates at
most one16KiB noncached contiguous buffer, validates every physical page inside
the established allowed range, and retains both allocation and FileObject until
reboot. There is no published-buffer free operation and no unload callback.
Failed translation can discard only an unpublished allocation. Any failed
allocation attempt is consumed rather than retried under the same case.

No command maps arbitrary memory or reads/writes GPU registers. Only the owning
FileObject/generation can read the fixed buffer or write one of two counted
patterns, with eight reads/eight writes maximum. Cleanup never touches payload
or frees references. A failed cleanup lock wait also leaves memory and owner
held. Later accesses after close are rejected; the one bounded hold is
intentional, not an acceptable general-purpose allocation strategy.

The baseline probe must complete genuine guest CPU read/write verification,
close its handle, and prove quarantine. Exported checkpoints are future host
attachment points; a host-free baseline must pass first. Host unit tests and
successful compilation do not prove NT5 runtime ABI or actual xemu callbacks.
The driver is not a replacement for the installed video driver and is never
authorized for physical deployment by this kit.

The later renderer half must independently attest the live arena owner, physical
mapping, source bytes and lifetime; a returned physical address alone does not
grant reuse. Use a fresh child for each one-shot allocation. Retirement must
remove GL references and actual CPU callbacks before any new release design.
Reboot-held memory does not waive callback/context teardown or latest-pixel
checks. No native GPU ownership, speedup or physical qualification is implied.
