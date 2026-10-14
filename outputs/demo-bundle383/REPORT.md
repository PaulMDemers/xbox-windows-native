# Updated 720p bundle prepared; archive creation held

package.py and merge-system.py prepare distinct new preview/system archives with
the E720p374 launcher, corrected376 drag controls, current menu instructions,
resolution rollback instructions and explicit validation results. Existing379
archives remain immutable. No383 archive has been created.

Both builders require demo-validation382 to be closed with a completed workload.
Its first attempt returned without Windows logs or hive/event changes, so that
condition is false. Do not weaken it to label this validation complete. Once a
fresh successful attempt is available, update the builders to its actual record,
review again and create new archives with complete member readback verification.

The complete system archive remains a reconstruction of the private343 payload,
not a fresh console capture, generic installer or tested full restore. It contains
Windows/user data and must remain private. The add-on archive excludes that data
but still needs component license/source review before publication. Neither
builder modifies hardware. Public source export and immutable tags are unchanged.

Watched retry384 also closed with incomplete workload. User confirms normal boot,
EventLog confirms normal shutdown; only initial BMP COPY persisted, exactly.
No rename/runner/audio/GDI completion. Keep builders gated; do not substitute384
as a successful validation or create archives claiming completed tests.

385 completed graphics/audio/normal shutdown/integrity but CMD MOVE failed;387
returned before startup with no existing-state changes. Both closed; gates remain
false and archives held. No new release or driver promotion.

FATX390 fixes duplicated exact-name enumeration in emulator392; actual CMD393
copy/move/reopen and native API persistence pass with cold integrity. Physical
console still0101;387 observation pending. Do not substitute emulator evidence
for the physical packaging gate. Current720p user text/drag result remains valid.
