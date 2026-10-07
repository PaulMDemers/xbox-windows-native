# Exact recurring event sources

October 7, 2026. Read-only analysis of the closed rendezvous-flush emulator disk,
its hash-matched SYSTEM hive and owned message binaries. No console access,
registry change, service suppression or driver edit.

SCM7000 is the service-start failure template. Its parameter%%2 resolves through
the configured kernel32 message resource to file-not-found. Active ControlSet001
configures HidServ as an automatic standalone service at
%SystemRoot%\system32\hidserv.exe, but that file is absent from this emulator.
No Parameters subkey or explicit dependency value is present. The retained0.1.0
archive's system32 and dllcache copies both contain19,728 identical bytes with
SHA256031a1fb5ca4194284d6ecfbfe8afe63589700c1376873267f131ead06946dc6a.
That is a concrete missing component, not justification to disable the service.
A fresh restoration experiment is tracked separately in ../baseline-hid-restore.
No live physical state was checked or changed; archive presence is historical.

Ftdisk49 is IO_DUMP_PAGE_CONFIG_FAILED: configuring the pagefile for crash-dump
use failed. It is not Ftdisk50/delayed-write failure. The cold configuration has
PagingFiles=C:\pagefile.sys96/192MiB and CrashDumpEnabled=3. The file exists with
100,663,296 bytes. File presence/size does not prove successful active paging or
crash-dump readiness. The observed guest fixture uses64MiB RAM; increasing the
file blindly would not explain the failure. No dump setting was disabled.

The exact pinned kernel contains an event-ID site in IopConfigureCrashDump:
after IopCompleteDumpInitialization returns a negative status, it logs this
event with unique-error value3. The recorded event bytes contain that value.
This is a static matching lead, not a captured runtime return or call stack.
The nearest-public code and instruction bytes are retained in
kernel-static-sites.json; no such immediate was found in executable ftdisk.sys
sections (ftdisk-static-sites.json). An event source name alone does not identify
the code that detected the error.

IopCompleteDumpInitialization's static sequence includes handle reference,
FileStandardInformation query, and FSCTL_QUERY_RETRIEVAL_POINTERS(0x9003b).
Candidate RVAs: entry22e84, handle-return22eaa, query-return22ed8,
FSCTL-call22f46/return22f4b, and final return22ff9. The caller logs at235d0
after return235c8. All addresses require the actual relocated kernel base and
matched resident bytes before instrumentation. A candidate site is not coverage.

The exact0101 VFAT source dispatches FSCTL_GET_RETRIEVAL_POINTERS; an initial
source search found no QUERY_RETRIEVAL_POINTERS dispatch. This is only a lead.
The static kernel path would additionally log IO_DUMP_POINTER_FAILURE on the
FSCTL failure branch, whereas the observed delta contains only49. Capture the
actual earlier return/branch before attributing the failure to an unsupported
FSCTL or implementing anything. No driver patch is warranted by this search.

Next: a NEW owned diagnostic boot can record the handle, query status/IOSB,
FSCTL reachability/status, final return and caller event branch, with pinned
kernel bytes and thread/frame pairing. Bound hits/time and remove all breakpoints
on teardown; ordinary validation remains separate. Do not recollect the closed
workload cases or insert breakpoints into a current ordinary run.
