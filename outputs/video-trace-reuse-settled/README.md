# Candidate0093: physical repeat boots qualified

**Two hardware boots passed**, including the second using the first boot's trace
without a host reset. Normal startup is restored, the console is at UnleashX,
and candidate0093 remains installed. See [qualification.json](qualification.json),
[physical.json](physical.json), and the two per-cycle qualification reports.
No emulator, observer, build or automatic test remains active.

Both runs passed four graphics pixel checks, five bounded timing loops, normal
restart/EventLog6006, expected driver/helper hashes, and valid trace records.
Neither introduced a popup or unexpected error. FATX, HAL, loader and geometry
are unchanged. The mode is still1024x576 at32bpp; this is not a speed or mode fix.
These tests do not repeat the full allocation/hive audit or extended storage soak.

## Implementation and reproducibility

Miniport SHA256:3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf.
The exact source tree, ordered patch lock, compiler pins, build report and compiled
trace/PnP tests are in [../video-trace-reuse](../video-trace-reuse/README.md).
Patch0093 preserves file I/O, diagnostic PCI reads, PnP forwarding and geometry.
After file-length and marker checks it clears old records in RAM. A valid existing
4096-byte trace file is still required; missing/invalid files retain their guards.

This folder's runner is the same graphics helper with a30-second settling pause
before requesting normal restart. Its imports were verified against NT5 exports.
The final promotion gate is the strict passing two-boot audit in
[../video-trace-reuse-clean-start](../video-trace-reuse-clean-start/README.md),
with matching driver, runner and initial clean seed. Physical deployment seeds
once, while cycle2 verifies and reuses the exact trace collected after cycle1.
Only these two launches occurred; no third test was started.

## Retained failed attempts and controls

- Candidate0092 passed xemu but failed hardware STOP0xB4. It was collected and
  rolled back; no second hardware0092 run. See ../video-repeat-boot.
- The initial0093 two-boot series and this folder's original two-boot series
  completed their workloads but failed strict no-popup audits on rundll32 DLL
  initialization during window-station shutdown. Those reports remain false.
- Captured-original and reconstructed-baseline controls each passed once without
  the popup. Earlier qualified Paint replay evidence nevertheless contains the
  identical popup using the exact original miniport. The mechanism is unresolved.
- control-assessment.json and historical-assessment.json retain that investigation.
  The later clean-start series passed the full strict audit; **no popup exception
  was used for the actual physical promotion gate**. Passing that series does not
  prove that initial trace content caused the earlier intermittent popup.

## Recovery

Original miniport: /F/winnt/system32/drivers/xboxvnt5.trace011, verified against
captured0.1.0. The local before-files and both boot traces/logs are retained under
artifacts/physical. physical.py rollback preserves the current trace and restores
the original driver/startup and a clean seed without launching Windows. The old
miniport still needs a fresh seed before each subsequent boot.

A readback-verified private overlay/rollback ZIP is recorded in
[recovery-overlay.json](recovery-overlay.json), at
E:/Codex-archive/xbox-windows-native/postrelease-video-reuse-20261005.
This is a small driver overlay, not a full system image or tested archive restore.
The v0.1.0 source tag and original recovery bundles are unchanged.
