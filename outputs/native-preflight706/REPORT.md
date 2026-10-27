# 706: kernel-only preparation preflight

This probe checks the larger allocation needed by 705 and records the incoming
1.6's baseline state. It does not enter native code or program a native video
mode. The normal kernel prepares 1280x720, as in the closed 701 control.

It captures ten PCI fields through the kernel read API, 30 CRTC bytes, five
sequencer bytes and pre-file-write CPU registers. CRTC/sequencer selectors are
restored and read back. PCI slot encoding matches the project's hardware-report
tool. No direct CF8 write, SMBus transfer or encoder programming is performed.

The ownership test requests a 1 MiB source allocation, a 32 KiB contiguous
allocation below 32 MiB, and its low virtual reservation. Each of eight alias
pages is translated at its first and last byte. The unchanged 705 admission
function checks all extents and overlaps before writing page-distinct marker
data. Both full copies are compared; marker data is never executed. Allocations
are released before showing the result. Green means allocation/copy/cleanup
passed; red means refusal or failure. Neither color qualifies native mode setup.

The nxdk build is pinned by build001.json. The actual compiled ownership object
passes 372 fresh Unicorn cases against the retained independent integer oracle.
Kernel API execution is not tested by that host model. Source review and exact
staging hashes are in review001.json and stage001.json. Kernel calls can block;
the intended ten-second display and automatic dashboard return are not an
enforced upper bound on the entire application.

One SITE launch was accepted at 2026-10-27T04:54:00.684085+00:00. The dashboard
returned; nine reports were collected twice with exact readback. The terminal
record is restart_requested/complete, allocation refusal bits are zero, both
32 KiB copies matched and all allocations were released successfully. The
independent interval audit passed. This kernel-only probe does not run Windows.

The collected LPC BAR0 is 0 and configuration84 is 0x8001. CR11=0x09 has its
lock bit clear; CR21=0xff and CR44=0. GPU/SMBus identities and base registers match
the candidate's expected functions. These are kernel-time observations, not
proof that the state will survive a future native transition. The next bridge
must check again and reject conflicting decode values.

Source allocation is 0x01f00000/1 MiB, native candidate allocation is
0x01ef8000/32 KiB, and framebuffer is 0x03c5c000/3,686,400 bytes. The returned
virtual reservation is 64 KiB; the requested subrange is contained. Its eight
backing pages are noncontiguous, including low physical pages owned by that
reservation. All first/last translations and disjoint extents passed.

Runtime706 is CLOSED and must not be relaunched or recollected. The user's
visual top-bar observation remains pending; no optical result is inferred from
the report. No startup hook or host process remains. All writes were in owned E
paths; console C and the ordinary Windows launcher are untouched. Staged bytes
and unrelated directory entries are unchanged. See audit001.json and closure001.json.
