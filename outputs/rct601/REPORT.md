# PC601: real graphics calls and returned interfaces qualified

The original Windows 2000 control passed both pristine and traced execution.
The saved subject logs are byte-identical. The recorder captured106 matched
call/return pairs with complete arguments and an independently checked stack.

The subject verified33 exact8x8x32 BitBlt copies and one64-pixel StretchDIBits
copy after GdiFlush. A deliberately invalid BitBlt and CreateDIBSection returned
failure. The32-entry BitBlt sampling bound retained the failed call and31 valid
calls, then disabled that entry; the independent subject continued to verify the
remaining copies. A cap is not a full frame or call count.

DirectDrawCreate rejected the owned invalid GUID with HRESULT `88760231`, then
successfully returned the default DirectDraw interface. The recorder followed
its actual vtable, normal cooperative-level call and CreateSurface result. The
returned8x8 surface reported16 bits/pixel and caps `00000840` (system memory and
offscreen plain). Its descriptor query and color-fill Blt succeeded, and both
objects were released. This is a PC system-memory control, not Xbox GPU evidence.

The original two-thread recursive probe remains in the subject:20 invocations
and exact arithmetic passed with the new return-breakpoint retirement behavior.
The shared-code host checks and14 adversarial trace mutations passed. See
[review002](review002.json), [oracle tests](oracle-tests001.json) and
[final closure](final001.json). Compile-time SDK assertions check descriptor size
and the interface slots being followed.

## Preserved failures and corrections

- Build001 failed `-Werror=cast-function-type` for FARPROC to CreateDIBSection.
  Build002 uses an explicit same-size function-pointer union conversion;
  warning flags remain unchanged. Both sources/build receipts remain.
- Review001 rejected the cold audit's zero shutdown delta. A blind test-number
  substitution had changed literal6006 to6016 in cold002.py. The saved raw event
  records were intact. `event_review001.py` independently checked each record's
  signature/length/number/timestamps/event/source against the preserved bytes:
  the6006 count is2→3, with new record7. Review002 uses that explicit correction;
  it does not change or rerun the original cold audit. The copied VM mouse default
  became601 pixels (unused), and the recorder bound became60100ms; actual execution
  used that60.1-second bound and completed both subjects in906ms.
- One periodic QMP screenshot raced normal VM exit with FileNotFoundError and
  process_exit0. Its exact receipt remains in ntfs-phase1. No runtime was reopened.

Normal restart was requested, the VM exited0 without host termination, the new
raw6006 record is confirmed, five system hives are clean with independent raw
reader agreement, copied tools match, and protected OS binaries/seed/ISO remain
unchanged. The existing DRM typed-value decoding limitation remains reported;
raw agreement is not a claim that every typed value decoded.

All owned host processes for601 are closed. Its runtime is immutable and must
not be reopened, recollected or used as a parent. The Xbox, save files, ordinary
launcher, protected720p and both transfer ZIPs are untouched. RCT is not in the
ZIPs. This qualifies the scoped recorder for the next fresh game observation;
it is not a game-performance, pristine game-control or acceleration measurement.
