# 424: FATX security-state failures reproduced across reboot

Both disposable emulator boots are CLOSED. The unchanged 423 witness completed,
but its user RSA and user DPAPI operations failed. Machine RSA creation failed
too; machine-scoped DPAPI succeeded immediately and after a normal restart.
The same binaries passed all four operations in the owned NTFS control.
This confirms a functional clean-install limitation, not a repaired namespace.

| Operation | NTFS create / reopen | FATX create | FATX reopen |
|---|---|---|---|
| User RSA key | Success / success | 206, filename exceeds range | 206 |
| Machine RSA key | Success / success | `0x80090020` (`NTE_FAIL`) | `0x80090016` (`NTE_BAD_KEYSET`) |
| User DPAPI data | Success / success | Protect fails with 206 | Saved blob absent, error 2 |
| Machine DPAPI data | Success / success | Exact plaintext recovered | Same 226-byte blob decrypts exactly |
| In-memory CSP context | Success / success | Success | Success |
| 41 / 42 byte filenames | Success / success | Exact write/read | Exact persisted read |
| 43 / 69 byte filenames | Success / success | Open fails with 206 | Absent, error 2 |

Each FATX log reports three API failures, with expected filename outcomes counted
separately. The second boot verifies the same user SID. It never creates missing
keys as a substitute for reopening them. Cold file comparison shows the first
run added a machine DPAPI master key/Preferred and the synthetic probe files;
the second added only reopen.log in that namespace. No failed user blob or RSA
public/signature file is silently substituted.

423's NTFS control actually created two new 69-byte RSA filenames, including a
user key beneath a 44-byte SID directory. These are real API-created paths, not
just old installer debris. However, 424 did not trace the exact failing native
file request. Error 206 is strong namespace evidence; the generic machine RSA
creation failure must not be attributed to a particular filename without that
trace. The PC NTFS and Xbox FATX environments also differ in kernel, hardware
and provisioning, despite common Windows media and identical probe binaries.

## Runtime and cold evidence

- emu001: accepted 2026-10-17 00:58:20 UTC, dashboard return 01:00:55 UTC.
- emu002: accepted 01:02:27 UTC, dashboard return 01:06:39 UTC.
- Both: ordinary native restart, one new EventLog 6006, orderly host exit 0,
  no deadline, fallback kill or debugger. Hardware wizards were left unchanged.
- File counts: 6,558 staged, 6,565 after creation, 6,566 after reopening.
  Each cold audit: 279 directories, 257 directory clusters, zero allocation
  errors/orphans, clean QCOW, five clean hives with matching independent raw
  values, 3,149 protected Windows EXE/DLL/SYS files and both probe binaries exact.
- Each run retains Ftdisk 49 and kbdhid 1. The SOFTWARE typed reader still refuses
  custom DRM type 0x404; its 80 raw bytes agree independently. No event or parser
  failure was waived. **Strict qualification remains false.**
- All 224/231 frozen dependency hashes agree. Actual-log negative controls reject
  402 deletions, duplications, malformed completions, counter changes and wrong
  phases across all four NTFS/FATX logs; see actual-review001.json.

The full FATX E file inventories and allocation captures are independent cold
reads. Normal registry/WBEM/event changes remain recorded (18 changed existing
files per boot); this is not whole-disk byte equality or a general restore test.
Raw hives, keys, protected blobs, disks and screenshots remain private under
E:/xwn424. Only original probe source, scripts, hashes and diagnostic records are
included here. No physical Xbox access, driver patch, event suppression, key
renaming or Windows-settings change occurred.

## Preparation and retained failures

assembly002 adds only the exact create.exe/reopen.exe to XWN423BIN on a new child
of the closed 406 assembly. All 6,556 inherited files remain exact. Phase two is
a deliberate persistence continuation of the closed, audited phase-one child;
neither old runtime was relaunched. The probe creates its own XWN423 directory.

prepare001 failed on a missing host `struct` import before disk/output creation;
prepare002 corrects only that import. Invoke001/Run001 were never launched.
Phase two uses separately frozen Invoke003/Run003 and controller files. A late
optional screen004 capture encountered connection refusal after the successful
dashboard return and orderly host closure; no retry was sent. Its missing image
is not presented as evidence. All failed and superseded inputs are retained.

See DESIGN.md for test scope, ../crypto-persistence423/REPORT.md for the NTFS
control and its retained reader failures, and NEXT.md for the file-request trace
needed before designing a compatible storage solution.
