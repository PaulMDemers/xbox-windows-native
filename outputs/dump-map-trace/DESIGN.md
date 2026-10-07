# Verify the actual NT5 dump mapping

This new emulator-only diagnostic follows the ordinary FATX0103 comparison.
It does not change drivers, dump settings, services or inherited synthetic
null/unsupported-device policy. It is not a physical or ordinary qualification.

The unique trace001 child stages the same candidate0103 FATX, candidate0102
HAL, video0093 and restored owned HidServ used by the successful ordinary run.
Preparation, preflight and source snapshots pin their identities and parents.
The independent cold FAT reader records the pagefile chain before launch.

The bounded tracer observes paired NT5 initialization calls and the matching
FATX dispatch. Resident instructions are compared with the actual PE bytes,
including relocations. It records the request's counted input/output buffers,
immediate status and any pending completion, then reads a successful output
pointer and at most 64 length/volume-offset pairs. Positive extents must cover
exactly the requested range, remain within the volume and end with a zero pair.
They must match the independent cold oracle. No register or guest-memory
values are substituted to obtain success.

At the final caller, a separately pinned NT5 consumer identifies the retained
dump context and its mapping pointer, byte count and requested length. The
retained bytes must match the returned array. All breakpoints are removed and
the guest resumes before the standard append/shrink/reopen workload. The final
disk receives a full allocation scan, exact-file readback, hive/protected hash
checks, unchanged-configuration check and strict event audit. The verifier
replays raw evidence and source hashes without editing capture records.

The first 65536 bytes are independently expected at volume-relative byte
offset 140436013056, followed by a zero terminator. This exceeds 128 GiB and
must remain 64-bit throughout. Correct setup and retained extents do not
establish that the dump miniport can write that LBA or that reboot recovery
can consume the dump. A later disposable controlled-crash protocol is needed.
