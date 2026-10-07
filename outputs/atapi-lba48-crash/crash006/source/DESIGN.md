# Candidate0105 controlled dump

Crash006 is a unique fresh sacrificial emulator child, gated on both strict
ordinary ATAPI control/candidate passes. It retains FATX0103/HAL0102/video0093,
NVNet0104, HidServ and inherited emulator device policy. Only the pinned ATAPI
dump selector is changed from the earlier crash005. Physical devices are not
accessed. Older failed crash disks remain closed and must not be booted.

Capture the intended one-shot E058D103 cookie, NVNet callback return, actual
candidate image identity, all105 resident selector bytes, capability/command
decision, extended address bytes and final dump return. For every dump-writer
call, pair entry/return by stack/thread, capture the complete MDL payload into
private artifacts, and enforce a65536-byte total bound. Remove entry breakpoints
before running and rearm only after the paired return; tear down everything.

Independent qualification requires the exact payload bytes at the intended
high-LBA pagefile, unchanged low alias,48-bit wire commands with correct address
and count, and all block writes after the first dump command contained exactly
within the expected64KiB extent. Preserve the full crash image, normal cold
allocation/protected/hive/configuration checks, and no forced successful status.
A successful write permits a separate recovery child; it does not itself prove
dump recovery, general filesystem safety, or physical qualification.
