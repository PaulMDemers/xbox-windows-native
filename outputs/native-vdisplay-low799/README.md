# Native CR12 display-end low-byte control799

This isolated diagnostic adds CR12 `CF -> DF -> CF` after the CR07 display-end
overflow control. It restores its own saved CR12 before undoing the earlier CR07
change and checks eight neighboring CRTC registers. A failed recovery inhibits
output restoration. It does not replay a complete video mode or boot Windows.

Source-only inputs are closed native797 and closed kernel798. No closed runtime
is reused. Kernel798 independently returned CF/DF/CF on the physical1.6; native799
requires its own held-picture observation and subsequent preparation-file audit.

The13-row optical report contains the signature, final code, eight selected
recovery masks, and CR12 before/after/restored. Nineteen other recovery masks are
aggregate-only through the final code; their raw values and neighboring register
values cannot be inferred from the photograph. Same-value operations elsewhere
in the prefix cannot distinguish an effective write from a dropped write.

`payload006.json` preserves the initial size rejection:23416 raw bytes exceeded
the23040-byte candidate reservation. `rejected-layout001/` retains those sources.
Fresh payload007 uses23424 bytes inside the same32768-byte owned allocation.
The640-word result ends at0x75c0; a64-byte guard separates it from the2048-byte
IDT, followed by a512-byte stack. Admission requires independent layout checks,
full-path write bounds and stack measurement, fresh diskless CPU fixtures and
exact linked executable checks. The larger reservation is not a gate waiver.

Build/test order uses the existing build and emulator leases:

1. `payload_build007.py`, then `host_build006.py` and `cpu003.py build` in WSL.
2. `model.py`, `integration010.py`, `optical_review003.py`, and `cpu003.py run`.
3. `build010.py`, compiled-object/page/plan/link checks, and `source_review004.py`.
4. `review_prepare006.py` freezes source and receipts before `physical007.py stage`.
5. One bounded launch after exact readback and authenticated dashboard admission.

Use unique private `C:/xwn799` inputs and the owned console path
`E:\Applications\XWNMode799`. No startup hook, dashboard C access or ordinary
launcher change is involved. The native result deliberately holds for a photo;
power-cycle afterward, then collect once. Dashboard FTP and preparation files
alone do not prove native success or a normal Windows shutdown.
