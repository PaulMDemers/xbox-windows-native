# Caller and basic input observation

This diagnostic uses a new exact copy of rebalance002's immutable veto source.
No installed payload, startup mode, driver policy or existing input handle is
changed. Previous used runtime disks, including failed reopen008, are retained.

1. Reproduce the reopen008 host-dispatch error with `check-branch001.py` and
   verify the corrected nonclass-open, class-open and class-helper paths.
2. Pin NT5 kernel/driver images, PDB-derived thread stack layouts, dependencies
   and source hashes. `Continue-001.ps1` requires the previous run closed and
   cold-audited before preparing this fixture under the build lease.
3. Hold the exclusive xemu lease throughout the bounded run. Use private
   E-drive disk/EEPROM/config/temp/output paths and ports 4884/4885/4886.
   Arm before the single dashboard launch; validate loaded site bytes with
   relocation handling. Read live thread stack bounds, immediate helper return
   addresses, ascending EBP links and at most 4096 raw stack bytes. Preserve
   the HID rejection predicates and contemporaneous CSRSS ownership checks.
4. Remove all breakpoints and resume after both failures. Read-only debugger
   observations remain timing-unqualified. EBP links may omit FPO frames;
   raw stack words and nearest-public symbols alone are not a proven unwind.
5. With a separate `xemu-ui` lease and only while this journaled guest is live,
   capture `input-check.py before`. Inspect that image before `keyboard`
   (Ctrl+Esc). Use `restore` (Escape) only after seeing the Start menu. Then
   `mouse` injects an 80/60 relative movement. No setup-dialog acknowledgement,
   text entry, click, settings change or restart is part of this check.
   Commands and image hashes are retained privately with JSON metadata.
6. Let the 300-second host bound close the guest, then cold-audit under the
   build lease. Validate the existing resource, HAL, lifecycle and cancel/remove
   gates independently of caller/input evidence. No dashboard or normal
   restart claim follows from host closure.

No physical-console access, shared fixture write, root/other-driver integration,
CSRSS handle closure or bypass of valid HID sharing enforcement is authorized
by a diagnostic result. The report must distinguish observed basic response
from full input, ordinary boot, repeated boot and hardware qualification.

## Actual capture path

The planned HMP and raw-framebuffer capture paths failed before input. The
actual input observations used native `sky.get_window_state` screenshots of
the uniquely selected, PID-verified xemu window and HMP commands to the owned
USB devices. See `input-review001.json` for the preserved capture failures,
lease-expiry guard and limited visual results. These fallbacks did not change
the frozen caller trace or guest payload.
