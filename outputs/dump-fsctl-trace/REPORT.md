# Candidate dump setup reaches an unsupported FATX control request

2026-10-07. `trace001` is CLOSED and cold-audited. This is a debugger
diagnostic, not an ordinary regression or a physical result. No driver,
registry, service, dump setting or device policy was changed in this kit.

The single launch at 10:01:49 UTC returned to the dashboard at 10:04:13.
Nineteen events and 23 relocated resident-byte pins identify the loaded
candidate0102 HAL, original FATX0101 and owned NT5 kernel. All paired calls
returned, every breakpoint was removed, and the guest resumed normally.
`trace-verification.json` independently replays those pins and call boundaries.

The observed sequence is now specific:

1. In-path dump usage notification (major1b/minor16, type3) returns success.
   Dump-stack setup, file reference and standard-information query succeed.
2. `IopCompleteDumpInitialization` issues `0x9003b` with an eight-byte input
   containing 65536 and a four-byte output slot. FATX receives the identical
   code, lengths and input pointer/bytes in a KernelMode request.
3. The matched `VfatFileSystemControl` returns `0xc0000010`
   (`STATUS_INVALID_DEVICE_REQUEST`). The filesystem-control call, complete-
   initialization routine and caller all return the same status. No pending
   completion branch is taken in this run.
4. Input and output slot remain unchanged. The caller IOSB also retains the
   preceding successful 24-byte query result; it is not evidence of FSCTL
   success. The immediate error is carried in EAX and tested by the caller.
5. Cold event deltas contain Ftdisk44/error4 and Ftdisk49/error3, matching the
   ordinary candidate run. Strict qualification remains **FALSE**.

The matched source has no `FSCTL_QUERY_RETRIEVAL_POINTERS` case, so this
runtime boundary agrees with its default invalid-device-request return.
`contract-review.json` pins the source and owned kernel instruction windows.
The missing request is distinct from supported `FSCTL_GET_RETRIEVAL_POINTERS`.

The follow-on workload completed 792 appends, 32 allocation shrinks, 132 reopens
and 11 exact cold files, with normal shutdown/dashboard return. Full allocation
was consistent: 323 directories, 6765 files, 324 directory clusters, no errors
or orphan clusters. Five hives parsed; protected hashes, payloads and inherited
emulator configuration matched. HidServ remained running (4/0/0). Those checks
do not waive the two event errors or qualify real dump writing/recovery.

Host verification notes: an initial invocation of the Linux-dependent evidence
verifier under Windows failed to import `fatx_stage_boot`; the WSL invocation
passed. The new trace verifier initially used an incorrect major-function
constant and incorrectly expected IOSB replacement on an immediate failure.
Both verifier assumptions were corrected against the captured raw stack and
buffer bytes; frozen capture, guest evidence and qualification gates were not
edited or rerun.

## Contract sources and remaining work

The [Microsoft control-code documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/fsctl-query-retrieval-pointers)
describes terminated mapping pairs. Its current text has inconsistent code,
unit and pool descriptions, so it is insufficient alone for an NT5 handler.
The owned ReactOS source includes the Microsoft-derived FastFAT implementation
at `drivers/filesystems/fastfat/fsctrl.c:4700`; its source hash is pinned.
It checks a kernel paging-file caller, requests a byte range, allocates nonpaged
storage and returns byte-length/volume-byte-offset pairs through a pointer slot.
The pinned NT5 consumer confirms the pointer indirection, retained array and
zero termination. Do not substitute the public GET buffer layout.

Before implementing support, establish paging-file identity, exact FATX cluster
to volume-byte translation, resource/worker rules and bounded allocation/error
cleanup. Test the actual helper against fragmented chains, partial last runs,
bad/short/cyclic chains, overflow, allocation failure and rejected caller/buffer
contracts. Only a new isolated candidate can be compared with the unchanged
control, followed by resident mapping capture and an independent cold extent
check. A successful setup is still not a recovered crash dump.

Physical0101/video0093, original0088 and immutable0.1.0 remain unchanged. The
original physical 111 non-ASCII bytes and first restart method remain unresolved.
Intentional interrupted-writeback evidence is a separate mechanism.
