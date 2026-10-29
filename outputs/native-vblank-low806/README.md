# Native CR15 vertical-blank-start low byte (806)

Fresh source-only continuation of closed native804 and kernel805. The latter
physically read CR15 CF -> DF -> CF with all30 recovery masks clear. This attempt
checks that operation after the native handoff, admitting its own saved baseline
and recovering CR15 before CR07 blank-start overflow and earlier operations.

No Windows boot, complete mode switch, native disk log, or acceleration claim.
Native result is a held optical report; kernel reports describe preparation only.

The selected code shares CRTC read/write helpers and compacts only sentinel
initialization. Original and selected native ELF executions must match every
result word and device read/write/port trace across934 cases. Instruction timing
and modeled peripheral behavior do not establish physical hardware behavior.

The existing32KiB allocation is retained. The payload now starts at0xb00 rather
than0x1000, following the bridge code (bounded below0x800), tables/status, and
512 zero bytes at0x900..0xb00. Payload23744 bytes ends0x67c0; request60 bytes;
4-byte request guard;730-word result0x6800..0x7368;408-byte result guard;
IDT0x7500..0x7d00; unchanged768-byte stack0x7d00..0x8000.

Active preparation uses payload_build008.py, host_build009.py, cpu006.py,
build013.py, integration012.py and physical009.py. Gates include fresh CPU
fixtures, exact relocations and linked bytes, full-framebuffer renderer checks,
independent source/layout/schema review, frozen sources, and staged readback.
See NEXT.md for actual completion and launch state.

Preserve measure001 compiler failure and qualification-failure001/002. The first
derivation referred to a nonexistent flags member; the correction retains the
native entry-IF rejection using the local saved flags. measure002 was a size
study only. measure003 and later builds use the corrected guard. cpu005 fixtures
were built but never run; cpu006 expands payload-preservation checking to0xb00.
No failed or superseded build is admitted to hardware.
