# Current action: capture697 displayed raw values before reset

697 launch accepted once at2026-10-27T02:26:54.767389Z. User reports "Green
holding". Success predicate supports a four-byte response with no bus error and
final known busy/terminal flags clear. No raw word captured yet; no reset requested.

1. Ask for a photo of the held screen with all ten bit rows visible. Use ordinary
   chat for the attachment request, not the text-only async question tool. Preserve
   photo privately; decode optical rows independently of expected values and keep
   any calibration/decoding failure. A photo is not a register dump.
2. Record raw word, status, result, poll count and block length only to the extent
   visible. Do not treat raw word as unique ID without supported semantics. If no
   photo can be supplied, retain the success-indication-only limitation explicitly.
3. Then request manual power-cycle, wait for dashboard confirmation, write
   collection-ready001.json and run physical.py collect once. No hook cleanup is
   needed. Verify exact records/staged bytes/unrelated entries. File CPU sample
   is pre-file-write; native values are RAM/display only. No normal shutdown claim.
4. Close this runtime after evidence/collection; choose the next read/initialization
   investigation from actual results. No gate waiver or encoder recipe transplant.

No repeat launch. All ten host VMs closed, no owned host process. Hardware ticket
retained, build/emulator leases released, automation paused. Original720p and
ordinary launcher untouched; networking679/1080i/boot intermittency tabled.
