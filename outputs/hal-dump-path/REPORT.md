# Root dump-path implementation: clean workloads, later dump failure

2026-10-07. Both ordinary emulator cases are closed and cold-audited. Neither
is strictly qualified, and no physical deployment occurred.

0102 implements separate, bounded paging/dump counters in the fixed-root HAL,
protects stop/remove and device disable while either is in use, and retains
resident, permanently powered root behavior. Hibernation remains unsupported.
See DESIGN.md for the contract, host boundary/concurrency tests and limitations.
This is an experimental root capability, not a change that forces lower drivers
or filesystem calls to succeed.

Fresh, matched RosBE builds use the same flags, compiler pins and source series
except0102. Exact HALs:

- Control: `44a6d83116b3fc056c81159905f9c635bd1aebfda21a7da37cf7a4fc14826c45`.
- Candidate: `7c6a3bfb9b6794c3b6fbce95fb76dc57d003843c19512b3ddb186604f668ed08`.

`hal-review.json` verifies owned kernel imports, disabled diagnostic exports,
checksums and resident PnP/power functions. The candidate source tree is
`8beed93598b97994a7836ab91285df1fcb8af27c`. These binaries are not claimed to be
byte-identical to the old installed HAL. The rebuilt control isolates that
reconstruction difference from0102. The actual counter function passes boundary
checks and400000 concurrent add/remove pairs in the host harness; this does not
establish guest power or end-to-end dump support.

| Observation | Rebuilt control001 | Candidate001 |
|---|---|---|
| Single launch UTC | 09:38:28 | 09:42:34 |
| Workload | 792 appends,32 shrinks,132 reopens | same |
| Exact cold files | 11 | 11 |
| Normal shutdown/dashboard return | yes | yes |
| Allocation | 323dirs,6765files,324dirclusters;0errors/orphans | same |
| Hives/protected hashes | five parsed,all matched | same |
| HidServ | running4/0/0 at start/end | same |
| New strict errors | Ftdisk49,unique error3 | Ftdisk44,unique error4;Ftdisk49,error3 |
| Strict qualification | false | false |

The comparison preserves identical helper bytes, initial hives, fixture parents,
startup and mode0. Only HAL differs among protected payloads; FATX0101/video0093
remain unchanged. `verify-pair.py` checks these conditions without waiving the
new event or the recurring one. Frozen scripts, closed disks and raw bytes also
pass `verify-evidence.py` for each case. No debugger or manual UI action occurred.

The new Ftdisk44 is consistent with advancing to a later dump-configuration
failure. It is not yet runtime proof of a specific failing FSCTL, input shape,
status or allocation. The next diagnostic must observe that call chain directly.
No real dump has been written or recovered, and this HAL must not be promoted
as complete dump support. Both strict failures remain intact.

Build001 was stopped by the unchanged20GiB free-space guard before any output
directory was created. The retry used a new ID and explicit nested exit-code
checking. Four closed standalone runs were offloaded/readback-verified to E:;
original paths remain junctions, with a complete file/hash manifest in
../task-storage-offload/manifest-20261007.json. No QCOW backing chain was moved.

Physical0101/video0093, original0088 rollback, immutable0.1.0, prior failures and
the installed HAL remain unchanged. Original physical111non-ASCII prefix damage
and first restart remain unresolved; intentional interrupted-writeback evidence
is separate. Inherited emulator-only synthetic null/unsupported-device policy
is unchanged and does not establish physical device support.
