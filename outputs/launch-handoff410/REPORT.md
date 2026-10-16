# 410: physical relocated-copy preparation passed

One FTP launch accepted at 2026-10-16 01:06:47 UTC. Dashboard returned with a
complete 144-byte report at 01:07:10; one collection completed with all 62
protected file hashes, diagnostic and owner exact. No Windows boot, C access,
original launcher/driver/Startup change or full disk-allocation audit.

Actual payload VA 0x81f00000 / PA 0x01f00000; contiguous loader VA 0x82000000 /
PA 0x02000000. The separately committed low virtual address 0x02000000 has
physical backing 0x00086000. That distinct backing is consistent with the
original dual-copy transition, not an observed allocation error. The complete
288316-byte original payload and both 1024-byte loader copies matched, including
expected patched target 0x02000050 in both. The required loader/GDT span is 224
bytes. No refusal, mismatched copy or wrong target was observed.

The probe stops before the jump to relocated code. It does not execute CLI,
paging disable, CR3 clear, GDT/IDT replacement or Cromwell entry. Historical407
failure cause and ordinary boot reliability remain unresolved. Do not present
this successful instrumented preparation as proof that later handoff works.

Build002 d1b86685ccb4789a7dca02cf3cc89a68ce4774c7ca7afa175f2fad0b5c0c8c2c
retains the original footprint/header/embedded payload. The exact original two
copy/fixup source block and relocated loader were reviewed. Host002 executed
actual compiled x86 for 21 cases with kernel/file effects modeled, including
mapping refusals, payload/copy/target corruption, and write/flush failures.
Independent decoder rejected 225 malformed/partial cases. No emulator run or
sanitizer claim. Stage inputs and host evidence rehashed after collection.

Build001/host001 failure is retained and was never deployed: a diagnostic read
used a compound GAS address expression that encoded without its intended
74-byte displacement. The host target assertion caught it. Build002 only fixes
that reader using an explicit register. It is not a fix to the installed loader.
Final-flush failure remains indistinguishable from complete bytes alone in the
host model; physical retained readback is separate evidence.

Private source, executables, host captures and physical report: E:/xwn410.
All original407 source pins and rollback files unchanged. Six true FATX long
paths and strict fresh-install event failures remain open; no public release.
