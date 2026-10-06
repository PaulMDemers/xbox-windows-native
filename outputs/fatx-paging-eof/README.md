# Candidate0098: regular-file paging EOF tail

The installed display package exposed nonzero sector slack after logical EOF in
the FATX paging-read path. Windows rejected the odd-length miniport's otherwise
correct checksum before DriverEntry. The preceding investigation and exact-byte
comparison are in [video-nt5-load-trace](../video-nt5-load-trace/README.md).

`0098-vfat-paging-eof-zero.patch` zeroes only completed paging-read bytes past
regular-file EOF. It uses the existing paging resource and mapped caller buffer,
keeps the completion length, excludes directory/FAT/raw-volume streams, and does
not write the disk or change the image checksum. Short MDLs are not extended.

The source replay follows the existing ordered manifest, then applies 0098. A fresh
RosBE build of vfatfs uses the established `_WIN2K_COMPAT_SLIST_USAGE` define.
Source tree: `873d6b4ff9505e71da119abd99aba301013e1749`.
Full executable SHA256:
`beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd`.
`build-report.json`, `inputs.json` and `binary-review.json` pin the commands,
compiler/tools, flags, source patches, PE checksum and imports. No stripped file
or newly rebuilt video driver was substituted.

Rebuild under the shared Windows build lease, using WSL:

```sh
XWN_BUILD_LEASE=held python3 outputs/fatx-paging-eof/build.py \
  --source-cache /home/paul/xbox-windows-native/sources/reactos-extended \
  --rosbe /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1 \
  --output /home/paul/xbox-windows-native/build/fatx-paging-eof-NEW \
  --profile fatx --jobs 4
```

Host regression: `test-read.py` extracts the actual old/new VfatCommonRead source
and compiles it with bounded I/O mocks. Sixty-three cases cover sector/page EOF
boundaries, short completions, failed reads, nonpaging reads, directories, FAT and
raw-volume exclusions, with guard bytes around the request. The old function
fails ten cases; the fixed function passes all 63. This is a source-level host
test, not an NT ABI, real cache-manager or concurrency test.

Ordinary emulator fixtures:

- **001:** inherits the prior installed package plus Start=1 diagnostic.
- **002:** inherits the actual installed package with Start=3, without that registry edit.

Each fresh child changes only `F:/winnt/system32/drivers/xwnfatx.sys`. The miniport,
display DLL, registry hives and runner remain unchanged. The ordinary runner uses
the next exclusive `xwnlag02` output, performs graphics correctness/timing probes,
waits two minutes and requests a normal restart. No debugger breakpoints or data
edits are used for these boots. `audit.py` checks cold payloads, registry binding,
event-log deltas, normal shutdown and all graphics stages. See the case audit
files and summary for actual results; reaching the desktop alone is insufficient.

Both fixtures inherit the earlier diagnostic audio installation flags and owned
synthetic xemu PCI model. No physical console access or deployment occurred.
FATX0088, video0093 and release0.1.0 remain the physical baseline. This candidate
still needs broader mapped-file/persistence stress and hardware validation; the
display stack's general PnP stop/remove/restart ownership remains a separate task.

Both ordinary runs passed their cold audits: all four graphics correctness stages
and five timing loops completed, payloads matched, one normal shutdown per run,
no new popup or unexpected error. Start=1 was retained in 001 and the installation's
Start=3 in 002. The previous start-type hypothesis is not needed to explain or fix
this checksum failure. Timing values are not physical performance results.

Next: exercise poisoned EOF tails through real file mappings across sector/page/
cluster boundaries and extend persistence stress before a controlled hardware
trial. Separately finish display PnP lifetime ownership and quiescence. Do not
promote0098 or the0096/0097 display package merely from these two emulator passes.
