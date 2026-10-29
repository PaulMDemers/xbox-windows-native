# Native CR07 line-compare high-bit checkpoint808

This is a diagnostic checkpoint for the existing1.6 HDMI baseline. It extends
the qualified806 native prefix with the807 kernel-context CR07 operation from
pinned704 `gpu_legacy.c` lines104..107. It is not a Windows driver release.
No firmware state is borrowed. The saved state is recovered before output is
enabled; a failed recovery keeps output disabled. Networking remains tabled.

The CR07 baseline after the preceding operations is3E. Setting line-compare
bit4 for `m=3ff` also gives3E. Admission/readback, coupling and wrong-write
faults are checked, but dropping the correct write or undo is indistinguishable
at this baseline. Report this limitation in every physical result.

## Fresh source derivation

`prepare001.py` reads CLOSED806/807 sources without opening their runtimes.
`compact001.py` and `measure001.py` preserve the initial size study. Its
original28376-byte, offset-table26424-byte, shared-helper24736-byte and
no-unwind24536-byte variants were not admitted as physical payloads.
`bitmap001.py` packs the398 sentinel-field locations into24 words and retains
the original hardware operation tail, with only the CR read/write helpers
marked noinline. `measure002.py` produced a24032-byte ELF binary with the
original unwind settings. No functional register operation was removed.

`model001.py` executes the original native implementation; `model002.py`
executes the bitmap implementation. `equivalence001.py` compares all974 named
cases, every760-word result and all register reads/writes and port traces.
The instruction counts differ and cannot establish hardware timing equivalence.
Independent source review reconstructs all760 bitmap memberships from the
struct declarations and original sentinel assignments.

## Memory and build contract

The single32KiB bridge allocation is retained. Bridge instructions end below
0800; metadata occupies0800..0900. Payload0900..67c0 reserves24256 bytes,
including224 CC padding bytes. Request67c0..67fc and result6800..73e0 do not
overlap it. Guards are67fc..6800 and73e0..7500. The256-entry IDT stays at
7500..7d00 and the768-byte stack stays at7d00..8000.

`payload_build008.py` uses the pinned gcc12 and unchanged32-bit freestanding
flags. `host_build009.py` builds the bridge, relocation recipe and four owned
layouts. `integration012.py` executes the relocated bridge with explicit
fault injection and independent framebuffer expectations. `cpu006.py` builds
and runs12 fresh diskless CPU transition/refusal fixtures; these test CPU and
mapping behavior, not physical GPU semantics or Windows boot.

After those pass, `build013.py` embeds the exact tested bridge/payload in a fresh
nxdk XBE. Page, boundary, plan and linked-byte checks validate the compiled
frontend. `review_prepare001.py` freezes sources only after every required
receipt passes. Always use the project's build/emulator leases and20GiB
projected host reserve. Builders and controllers are single-use; failed runs
must be preserved with fresh identities for subsequent attempts.

## Physical evidence contract

The unique owned path is `E:\Applications\XWNMode808`. The bounded controller
checks frozen sources, build bytes, stage readback and fresh report namespace
before one SITE command. No startup hook or Windows launcher is installed.
The native payload deliberately holds its picture. Disk preparation reports
end at handoff; the photograph is the only source of the native result.

The13-row optical report contains the808 signature, return code, eight recovery
masks, then CR07 before/after/restored. Twenty-three other recovery masks and
neighbor values remain aggregate-only; a passing final status requires all31
masks clear. A green bar alone does not supply the raw values. Preserve the
user's observation separately from decoded photo bits, independently verify
the decoding, then collect preparation reports once after the user's reset.
An authenticated dashboard after that reset is not a normal Windows restart.

See NEXT.md for the latest actual execution and process state. Later CR09bit6,
CR18 and CR1A operations remain separate, unadmitted steps toward full native
mode switching and Windows1.6 desktop support.
