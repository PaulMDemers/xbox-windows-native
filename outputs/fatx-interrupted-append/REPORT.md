# Interrupted persistence can expose the observed boundary

Case003 establishes an emulator mechanism for a file-visible111-byte old prefix
followed by109 correct bytes in the actual SetupAPI warning at270225. It is an
intentional interruption, not a normal shutdown or reproduction of the original
physical byte contents. The normal-shutdown control preserves the complete
warning. FATX0101, video0093 and the immutable fixture were unchanged.

| Case | Intervention/result | Cold file size | Target | Allocation |
|---|---|---:|---|---|
|001|Stop after initial109-byte suffix write|269718|Raw split beyond file EOF|One invalid chain, one orphan|
|002|Host recorder failed; guest resumed|271860|Full warning intact|Consistent|
|003|Stop after later1524-byte page write|271385|File-visible111 zero/109 correct|Consistent|
|Normal paging002 control|Windows normal shutdown|271860|Full warning intact|Consistent|

The controlled cases stop at successful VfatWrite returns, keep the guest
paused, remove all breakpoints, then quit the owned emulator. No speculative
driver patch or physical access was used. The later case shows that a complete
allocation audit and parsable hives can coexist with incompletely persisted log
data. These checks must remain independent of normal-shutdown and exact-byte
gates in future tests.

The hardware's original bad111 bytes were not zeros. Its first reboot method
and raw target contents before that write are unknown. Do not infer power loss,
hardware failure or a cache/driver defect from this result alone. The next useful
step is to observe the actual application mapping/unmapping/truncation sequence
and distinguish its durability contract from normal driver writeback behavior.

Case002 preserves the original and recovered host trace records, not a rerun.
Bounded atomic replacement now survives a tested Windows reader sharing conflict
and preserves complete old/new records on permanent failure. Every owned guest,
observer and reader from this kit is closed. See per-case reports, source pins,
audits, `verify-evidence.py` and `NEXT.md` for exact evidence and limitations.
