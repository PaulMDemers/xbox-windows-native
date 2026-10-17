# Identical RGB32 key probe passes on a 24-bit NT5 desktop

Both default and HEL processes completed all twelve operations with exit 0 and
zero mismatches. All 92,160 captured source/destination bytes match the unchanged
independent oracle. This includes all three color keys, with and without clipping,
as well as plain copies. All API/layout and final zero-reference checks passed.

The exact same probe executable failed on the 16-bit desktop in
[446](../key-semantics446/REPORT.md). Its SHA256 remains
`0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c`.
No public sample/checker, runtime DLL or driver changed. The new controller is
15,146 bytes, SHA256 `bb7b8cf06d9473f6c9d7daaf1f7fdaecdcf21f53776ad20ef88fe9b743098c34`;
26 actual NT5 import matches, warning-free build, never executed on the host.

Actual mode receipts show:

| Boundary | Width × height | Bits | Hz | Flags |
|---|---|---:|---:|---:|
| Original | 640 × 480 | 16 | 60 | 0 |
| Selected, tested and applied | 640 × 480 | 24 | 60 | 0 |
| Active, queried before samples | 640 × 480 | 24 | 60 | 0 |
| Restored, independently queried | 640 × 480 | 16 | 60 | 0 |

The controller enumerated 105 modes and selected index 58. Both probes' independent
enumerations agree with that index and count. Test, apply and restore all returned
success. No registry-update flag was used. Mode handling follows
[ChangeDisplaySettings](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-changedisplaysettingsa).
The receipt checker rejects 153 synthetic missing, failed, truncated, wrong-mode
or unrestored cases; these are parser tests, not injected driver failures.

The previous low16-only comparison model now disagrees with 134 destination pixels
per backend, while the full-width expected comparison matches every pixel. The
matched fixtures support desktop-depth dependence in this NT5 PC configuration.
They do not identify the responsible runtime/driver instructions or demonstrate
behavior on a 32-bit desktop. The original 446 failures remain unchanged.

One fresh child of the closed404 NTFS installation; no executed-runtime parent.
Completed atomic preflight preceded launch, with 147 exact dependencies. The
launch gate is byte-identical to 446 and inherits its 59 host refusal checks;
inherited-gate-tests001.json is a copied historical receipt, not a new execution.

The guest requested normal restart, and QEMU exited 0 with no deadline, host quit,
terminate or kill. Cold audit: 6,486 files, 309 directories, five clean hives with
independent raw-value agreement, protected Windows binaries/parent/floppy unchanged,
clean QCOW check and one new EventLog 6006. Eleven added files comprise ten owned
test files and the user's generated Internet Explorer desktop.htt. The read-only
NTFS3G reader independently matched 20 selected files, unmounted and left the disk
unchanged. All owned processes are closed.

11,416 mutations of actual reports, sources, plain-stage destination pixels and
lengths were rejected, originals unchanged. That script's inherited scope text
about retaining keyed failures refers to historical 446; all current keyed cases
passed. The 147 dependencies were archived privately and 231 private files rehashed.

This qualifies the narrow RGB32 diagnostic on this 24-bit PC desktop. It does not
qualify every rung04 sprite operation, the Xbox, scanout, GPU acceleration, D3D,
performance or a game. Full NTFS allocation ownership and the inherited SOFTWARE
DRM typed-value decode limitation remain outside the audit. Xbox files unchanged.
