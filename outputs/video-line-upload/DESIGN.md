# RAM0110: bound only LineTo uploads

Evidence: unchanged-driver video-upload-bounds measured2359296bytes for a32pixel
line. video-line-bounds recorded18 real LineTo entry/return pairs and conservative
prclBounds containing all host-predicted pixels. Bounds evidence is independently
verified; that whole diagnostic remains failed due to a later nonresident kernel32
header read at process exit. All breakpoints were removed; no failure is waived.

Pass valid prclBounds to existing XwnUpload; its existing screen and clip-bounds
intersection remains in force. Missing, empty or inverted bounds retain NULL/full
clip fallback. EngLineTo arguments and return, ownership and active-state checks,
copy implementation, cursor, cache mode and surface lifetime remain unchanged.
The two read-only identity escape revisions advance109to110. No other source edit.

Host tests compile the exact shadow.c with a minimal engine/owner shim and exercise
241 combinations including extreme signed bounds, offscreen, empty/inverted clip,
fallback, engine failure and inactive/invalid surface. Per-pixel destination and
guard words plus upload counters are checked under ASan/UBSan. This is not a real
engine or binary ABI test; ordinary emulator pixel and cold audits are still needed.

Build reconstructs the pinned109tree, applies only0110, and uses the recorded RosBE
compiler/definitions under the shared build lease and20GiB free-space guard.
Physical0101/video0093, original0088, immutable0.1.0 and all prior failures remain.
