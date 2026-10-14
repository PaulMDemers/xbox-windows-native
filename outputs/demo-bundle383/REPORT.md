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
