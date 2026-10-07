# Actual SetupAPI mapped-append lifecycle verified

Case002 launched06:36:34UTC7October2026 and returned to dashboard06:39:40UTC.
All owned processes are closed. The trace captured58 complete SetupAPI.log
appends with successful mapping, unmap, truncation, close and outer results.
Every captured mapped append matches its final cold-file range. The175 buffer
references, including the input strings and exact target warning, are verified.

The target warning is record40 in rundll32.exe:

| Operation | Observed value |
|---|---|
| File path |C:\\WINNT\\setupapi.log|
| Old file length |270225|
| Writable mapping maximum |270480;PAGE_READWRITE|
| View |Whole file,FILE_MAP_ALL_ACCESS|
| Correct mapped warning |220 bytes at270225, including111+109|
| Seek target/result |270445 /270445|
| UnmapViewOfFile |Success|
| Mapping CloseHandle |Success|
| SetEndOfFile |Success|
| File CloseHandle |Success|
| Outer routine result |0|

The mapped source220-byte SHA256 is
`bc081ff306c39d32e0e527caa65e76bbea3bd5a4ce68e0b420064b345319cc70`.
The mapping allowance is35 bytes beyond the final target length, consistent with
the27-byte first string plus the8-byte allowance in this observed call. The
second source string and mapped target both contain the exact warning.

Cold verification preserves all5300 appended ASCII bytes, the original prefix
and the220-byte target. Allocation is consistent with zero errors/orphans;
five hives parse; selected binaries, the exact SetupAPI DLL, GPU installation,
event checks and one normal shutdown pass. This is a debugger diagnostic and
does not replace physical qualification or the broader3439-binary/nine-hive audit.

Four candidate entry hits could not read the code window. They were recorded,
stepped without collecting call evidence and remained within the explicit bound.
All58 retained call records have exact code-window validation and complete frame
pairing; no active records or breakpoints remained at teardown. The actual
installer callback path is now confirmed, unlike the earlier unused logger lead.

The examined cleanup sequence has no explicit flush call, but this is not a
complete system-wide flush census or proof of an application/driver bug. Combined
with the separately recorded interrupted-prefix mechanism, it motivates a normal
writable-map/unmap/truncate regression. It does not establish how the original
physical machine was restarted or why its111-byte prefix contained non-ASCII data.

Case001 remains an unreadable-memory coverage failure with zero captured calls;
its exact sources and clean cold run are preserved. No driver, hardware baseline,
release tag or physical recovery bundle was changed by either attempt.
