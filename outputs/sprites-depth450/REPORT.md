# Full rung 04 sprite control passes on Windows 2000 at 24-bit

All six default/HEL × indexed8/RGB565/RGB32 cases passed, four stages each, with
174,080 exact source, destination, palette and GDI-converted bytes. All six process
exit receipts are 0. This covers keyed/clipped sprites, indexed palette updates
and overlapping copies in both directions. It does not qualify physical scanout,
GPU acceleration, D3D or a game.

The sample is the unchanged444 binary, SHA256
`23fcd2208b74a80feaf55d6a52be1b4a34a4138da859fa10bc06d5867862776f`.
The original 444 16-bit RGB32 failures remain failures. The new controller adds the
exact 447 mode transaction to the original444 six-case controller; both components
reconstruct byte-exactly. Actual mode inventory contained 105 entries, selecting
index 58. Requested/active mode was 640×480×24 at 60Hz/flags0; CDS_TEST, apply and
restore returned 0, and a fresh query verified restoration to 16-bit. Each sample's
independently obtained DirectDraw mode agreed with the active 24-bit controller state.

The checker previously admitted only 16/32-bit desktop metadata. Its sole acceptance
change adds24-bit; the oracle and surface constraints are unchanged. Three test
groups passed, including supported desktop depths, unsupported/malformed depths
and changed capture rejection.153 synthetic mode negatives passed. The launch gate
is byte-identical to the tested446/447 gate;59 inherited cases were not rerun.
The controller/probe match 26/29 actual NT5 imports; the leased controller build
was warning-free. No SDK, physical console, display driver or DLL was changed.

One fresh 404 child completed normal guest restart; QEMU exited 0 with no deadline,
host quit, terminate or kill. Cold audit hashed 6,514 files in 309 directories:
39 additions (38 owned test files plus the generated Internet Explorer desktop
file), zero removals. Five hives were clean with independent raw-value agreement;
protected Windows binaries, parent and floppy were unchanged; QCOW checks passed.
A new 6006 supports normal shutdown. The second read-only NTFS3G implementation
matched 48 selected files, unmounted and left the disk unchanged.

The independent checker rejected 2,520 mutations of actual reports/capture bytes
and lengths; originals are unchanged. 147 frozen inputs were archived privately,
316 private files rehashed. All owned processes and mounts are closed. No child
or consumed output is reusable. Full NTFS allocation ownership and inherited
SOFTWARE DRM typed-value decoding remain outside the audit.
