# Physical preparation passed; later handoff remains unlocated

One new diagnostic was launched at2026-10-17 22:39:06UTC and dashboard FTP
returned by22:39:34UTC. Its176-byte exclusive report passed independent decoding:
allocation/mapping preconditions,288316 payload bytes, both1024-byte loader copies
and both patched jump targets agreed. The original jump register snapshot is
consistent. These are checks BEFORE final file close and the attempted handoff.
A full report cannot prove final flush/close, the post-log recheck or CR0 execution.
The user was asked what appeared on screen; visual confirmation remains pending.

The actual allocation/address tuple matches historical410, which deliberately
returned before the jump. This comparison does not requalify410 or identify a
failure. No Windows boot or D3D execution is established. Five clean registry
hives, both event logs, existing video trace, normal startup and original launcher
are unchanged. Selected-file agreement is not a full FATX allocation audit.

The new XBE is isolated at `E:\Applications\XWNBoot460a\default.xbe`.
It preserves the embedded Cromwell payload and original paging/loader source.
The ordinary `E:\Applications\XWNEBoot\default.xbe`,720p settings and drivers
were not replaced. No startup hook or automatic Windows restart was installed.
The diagnostic report is one-shot: do not launch it again. No Xbox C access.

Before staging, the actual assembled wrapper passed45 host cases with modeled
kernel/file operations. The successful cases trapped at CLI before executing
privileged instructions and verified restored registers/flags. Negative cases
covered allocation/status/short-I/O/stale-IOSB/close and post-log copy corruption.
296 malformed host-report controls and269 mutations of the actual report were
rejected.24 private captures were rehashed, and five hives passed independent
raw/header checks. There is no ASan or physical paging qualification claim.

Build001 was compiled but rejected in source review because inherited `jns`
accepted positive nonzero virtual-allocation status. Build002 failed before
private-directory creation/compilation because a generator replacement changed
immutable374 input paths. Build003 restores those paths and requires exact zero
status. All predecessors remain preserved and were never launched. Source review
reconstructs the entire pinned original wrapper by reversing11 explicit edits.
Qualified build003 SHA256:
`63e678280c9d5c5c511f7c47562b005134ee2f7147f99a651b91d65d1fc7a51f`.

All owned stage/host/observer/collection processes are closed. No retry is queued.
Evidence: [source review](source-review001.json), [host](host001.json),
[decoder](decoder001.json), [launch](launch001.json),
[collection](collection001.json), [actual review](actual-review001.json).
