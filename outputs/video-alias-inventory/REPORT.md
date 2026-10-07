# Framebuffer alias inventory: diagnostic PASS

The desktop has two retained 4 MiB framebuffer views in every one of the 20
active process address spaces captured on October 7, 2026. Boot-video owns the
direct-RAM view; the desktop uses the GPU aperture. Both views have PCD and PWT
set, with PAT clear. A desktop-only cache flag change would therefore leave a
second owner and mapping to account for. No cache policy or driver was changed.

## Runtime evidence

`trace001` accepted at 19:10:27 UTC and closed at 19:12:29 UTC. The observer took
one coherent 64 MiB physical-memory snapshot at the first probe107 marker, then
removed its breakpoint and resumed the guest. The offline walk examined 20,480
PDEs and 3,948,544 PTEs across 20 distinct active CR3 roots. It found 40,960
matching entries, with no large PDEs in these roots.

| Owner/view | Virtual start | Physical start | Extent | PTE policy |
| --- | --- | --- | --- | --- |
| Desktop GPU aperture | FC23E000 | F3C00000 | 4 MiB | PCD=1, PWT=1, PAT=0, supervisor |
| Boot-video direct RAM | FCED6000 | 03C00000 | 4 MiB | PCD=1, PWT=1, PAT=0, supervisor |

Each root contains exactly these two ranges into the searched physical windows.
No additional present mappings into those windows, including the former loader
identity/high aliases, were found. This is a point-in-time inventory of linked
active processes and the current CR3, not a TLB, inactive-process, future-lifetime
or current-MSR inventory. The aperture-to-RAM relationship is a platform contract;
page translation alone does not establish that relationship.

The loaded `bootvid.dll` matches the actual E-partition loader override
`Applications/XWNFBoot/loader/xboxbvid.dll`, SHA256
`2196f646653c4c944d73fee4944ee3d056c82cf01903e4f435e67d63c03ed4b7`.
Verification checked its image identity and all 4,440 relocated text bytes,
then resolved the pinned executable's `_FrameBufferStart` and `_BackBuffer`
symbols. The former points to FCED6000/physical03C00000; the latter is inside
the reserved 4 MiB. The system32 Microsoft bootvid copy is not this loaded
override. Cold reads of the actual override before and after are identical.

`verification.json` and `alias-summary.json` pass. The full private entry inventory
is retained as `alias-scan.json`, SHA256
`25c16baa55d1955aa1245979bd5cb924d527cef36ae711ba4fc66c8470d521d4`.
The private RAM snapshot is pinned by the summary; neither RAM nor executable
payloads are committed. `source-inventory.json` pins indexed/working source bytes
and tree identities for the static contracts below.

## Reservation and lifetime contracts

| Component | Source contract | Consequence |
| --- | --- | --- |
| Loader | Validates supported pitch/geometry and the 03C00000..04000000 reserve; requires a covering LoaderFirmwarePermanent descriptor; preflight installs identity/high mappings with flags1b | Reservation and early mappings must remain consistent with any new policy |
| HAL | Early display mapping checks and MM free-page exclusions protect the reserved window; root aperture resources cover F0000000 onward | Source branches are not proof that every conditional hook ran in this boot |
| Miniport0093 | Retains firmware mode; maps 4 MiB through VideoPortMapMemory with MEMORY flag0; unmaps through VideoPortUnmapMemory | API flag behavior must be established for the installed NT5 implementation |
| Boot-video | MmMapIoSpace of direct RAM with MmNonCached; retains FrameBufferStart and hidden backbuffer; VidCleanUp fills but does not unmap | This owner survives desktop use and participates in shutdown/error display |

The boot-video source explicitly uses direct RAM because the PCI aperture may
be disabled before the final shutdown bitmap. The loader/bootvid reconstruction
tree is source-contract evidence, not a newly demonstrated byte-identical full
rebuild. Runtime bootvid text/global matching is separately established above.

Historical0094/0096 observations include PAT `0007010600070106`, with UC at
index3, and different MTRR types covering RAM and the aperture. They are not a
measurement of the MSRs in this snapshot. Historical0094 had two rundll32 popups
and remains a failed strict physical trial;0093 was restored. The ordinary0096
direct-RAM comparison did not demonstrate a convincing emulator speed gain.

Intel's memory-type rules require consistent alias treatment and appropriate
cache/TLB coordination during policy changes. Its Pentium III-era guidance does
not support conflicting memory types for aliases of a physical page. See the
[Intel system programming manual](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366821.pdf),
printed pages10-47/10-48. This supports treating both framebuffer views as a
single coordinated policy decision, not changing only the desktop mapping.

The [Microsoft VideoPortMapMemory contract](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/video/nf-video-videoportmapmemory)
documents P6CACHE for write combining and consistent flags across mappings.
It directs physical main-memory framebuffers toward MmMapIoSpace. That contract
does not prove how the installed Microsoft NT5 videoprt resolves a particular
request, nor whether xemu timing predicts real Xbox performance.

## Validation and limits

The unchanged workload completed 54 cases and 162 RGB stages, followed by normal
restart/dashboard return. Cold checks found 324 directories, 6,755 files and325
directory clusters, with zero allocation errors or orphans. Five structural
hives, protected hashes, configuration and the 96 MiB pagefile mapping/content
passed. Warning/error and application event deltas were empty. The synthetic
walker tests cover 4 KiB/4 MiB mappings, bounds, PAT, absent tables, unsupported
PSE36 bits and range merging.

This is a debugger diagnostic PASS, `ordinary_qualified=false`. It is not a
performance fix, independent scanout validation or physical qualification.
Physical0101/video0093, original0088 rollback, immutable0.1.0 and completed128GiB
dump recovery remain unchanged. The inherited emulator-only null/unsupported
device policy is unchanged. The original physical111-byte anomaly is unresolved.

All owned sessions are closed: prepare51121, runner40136, tracer84676,
supervisor96339, audit46373. The retained guest disk is
`work/runs/nt5-valias-trace001/hdd.qcow2`; its hash and cleanup are in
`trace001/closure.json`. Never relaunch or recollect this case. See `NEXT.md`.
