# 527 standalone nxdk dispatch control

This is a separate standard nxdk runtime, not a Xromwell patch or causal
equivalence test. One unique /E/Applications/XWNDispatch527 directory holds the
candidate and owner record. No Windows hook, display mode, PCI, EEPROM, raw
hardware write, or console C access. Existing E aliases must match standard
Partition1; a different alias is refused, never replaced. An absent E alias may
be created by nxdk, then queried and checked before any file creation.

The app creates begin.bin, writes 48 bytes, flushes, closes once, reopens, reads
up to 49 bytes and requires exactly 48 matching bytes, then closes once. Only
after that completed sequence does it construct and similarly save entry.bin.
CREATE_NEW prevents overwriting; no retry, rollback or deletion. Failures retain
partial files and stop further receipt operations. Each acquired handle receives
one close attempt; a failed close does not authorize retry or claim closure.

Fixed little-endian 12-word schema: ASCII X527; version1; bytes48; attempt527;
stage1(begin)/2(entry); kernel Major, Minor, Build, Qfe; flags0/1 (prior begin
sequence complete); reserved0; FNV1a32 over bytes0..43. Decoder requires kernel
major1/minor0, build1..65535 and qfe0..65535. Kernel identity is observed, not a
physical-console whitelist. A complete entry receipt proves earlier begin
operations and runtime entry. It cannot prove its own final close, the subsequent
Sleep or firmware-return call, normal Windows restart, or Windows stability.

After the bounded-count I/O sequence (including failure), request a two-second
Sleep and HalReturnToFirmware(HalRebootRoutine). Blocking kernel APIs mean this
is not a hard guest deadline. The host owns bounded supervision, records any
timeout, and never repeats an accepted/uncertain SITE request. No boot is queued
by host tests. Actual controller transport is exercised with modeled FTP; engine
tests execute the actual portable C engine with modeled callbacks and failures.

Before a physical run, build under the pinned SDK lease without shared rebuild,
then qualify these exact bytes on a fresh unused emulator fixture. The emulator
and physical records must remain distinct. Preserve failed 525/526 and all prior
evidence. 720p baseline remains protected. Projected20GiB host/WSL guard; no E
host allocation. 13:50UTC review only;14UTC close and pause automation.
